import asyncio
import json
import re
from datetime import datetime, timedelta, timezone
import aiohttp
import feedparser

# Configuration
INPUT_FILE = "rssSites.html"
OUTPUT_FILE = "rssSites_cleaned.html"
CONCURRENCY_LIMIT = 100  # Number of concurrent requests
TIMEOUT_SECONDS = 10     # Request timeout per feed
CUTOFF_DATE = datetime.now(timezone.utc) - timedelta(days=365)


def get_latest_entry_date(feed_content: bytes) -> datetime | None:
    """Parses RSS/Atom content and extracts the newest entry/feed date."""
    try:
        parsed = feedparser.parse(feed_content)
        dates = []

        # Check overall feed update date
        if hasattr(parsed.feed, "updated_parsed") and parsed.feed.updated_parsed:
            dates.append(datetime(*parsed.feed.updated_parsed[:6], tzinfo=timezone.utc))

        # Check entry/item dates
        for entry in parsed.entries:
            for field in ("published_parsed", "updated_parsed", "created_parsed"):
                val = getattr(entry, field, None)
                if val:
                    dates.append(datetime(*val[:6], tzinfo=timezone.utc))
                    break

        return max(dates) if dates else None
    except Exception:
        return None


async def check_feed(session: aiohttp.ClientSession, semaphore: asyncio.Semaphore, url: str) -> tuple[str, bool]:
    """Fetches a feed URL and checks if it updated within the last 365 days."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) FeedChecker/1.0"
    }
    async with semaphore:
        try:
            async with session.get(url, headers=headers, timeout=TIMEOUT_SECONDS, allow_redirects=True) as resp:
                if resp.status != 200:
                    return url, False

                content = await resp.read()
                latest_date = get_latest_entry_date(content)

                if latest_date and latest_date >= CUTOFF_DATE:
                    return url, True
                return url, False
        except Exception:
            return url, False


async def main():
    print(f"Reading {INPUT_FILE}...")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Locate window.FEED_DATA JSON object
    match = re.search(r"window\.FEED_DATA\s*=\s*(\{.*?\});", html_content, re.DOTALL)
    if not match:
        print("Error: Could not locate 'window.FEED_DATA' in the HTML file.")
        return

    feed_data = json.loads(match.group(1))

    # Deduplicate all feed URLs across categories
    all_urls = sorted(list({url for urls in feed_data.values() for url in urls}))
    total_urls = len(all_urls)
    print(f"Found {total_urls} unique feed URLs across categories.")

    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    connector = aiohttp.TCPConnector(limit=CONCURRENCY_LIMIT, ssl=False)

    valid_urls = set()
    completed = 0

    print(f"Testing feeds (Concurrency limit: {CONCURRENCY_LIMIT})...\n")

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [check_feed(session, semaphore, url) for url in all_urls]

        for future in asyncio.as_completed(tasks):
            url, is_valid = await future
            completed += 1
            if is_valid:
                valid_urls.add(url)

            if completed % 100 == 0 or completed == total_urls:
                print(f"Progress: {completed}/{total_urls} checked | Valid: {len(valid_urls)}")

    # Filter original data structure
    cleaned_feed_data = {}
    for category, urls in feed_data.items():
        active = [u for u in urls if u in valid_urls]
        if active:
            cleaned_feed_data[category] = active

    # Update HTML file content
    new_json_str = json.dumps(cleaned_feed_data, ensure_ascii=False)
    cleaned_html = html_content[:match.start(1)] + new_json_str + html_content[match.end(1):]

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(cleaned_html)

    print(f"\nDone! Saved {len(valid_urls)} active feeds to '{OUTPUT_FILE}'.")


if __name__ == "__main__":
    asyncio.run(main())
