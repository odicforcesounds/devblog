#!/usr/bin/env python3
"""Category 01, expanded: Category -> Awesome list -> theme -> tool card.

Every unique link from the shell lists gets a card: number, summary from its own
README, a real example where one can be given honestly, and the source. Links are
deduplicated across the whole page; a tool listed twice keeps one card.
"""

import os as _os

_os.chdir(_os.path.abspath(_os.path.join(
    _os.path.dirname(_os.path.abspath(__file__)),
    "..", "..", "..", "..")))

import html
import json
import re
import sys
from urllib.parse import urlparse

SRC = "tmp/tools.json"
OUT = "docs/awesome-01-shell.html"
ORIGIN = "https://blog.odicforcesounds.com"
IMG = ORIGIN + "/images/peace.jpg"

TITLE = "Awesome 01 — Shell, Terminal and One-Liners, Expanded"
DESC = ("Category 01 opened up: every shell list on this blog, each tool in its own card "
        "with a summary and a real example where one exists.")

# ---------------------------------------------------------------- buckets
BUCKETS = {
    "Bash": [
        ("Docs, guides, style", ["wiki", "guide", "manual", "faq", "pitfall", "handbook",
                                 "style", "book", "intro", "how-to", "strict mode", "defensive",
                                 "pure bash", "explainshell", "safe ways", "stack overflow",
                                 "reddit", "#bash", "one-liners", "commandlinefu"]),
        ("Prompts and themes", ["prompt", "theme", "lscolors", "liquidprompt", "oh-my-git",
                                "sexy", "powerline", "gittify", "progress-bar"]),
        ("History, navigation, shortcuts", ["ble.sh", "commacd", "forkrun", "has", "hstr",
                                           "sshrc", "zoxide", "bashmarks", "bashmount",
                                           "bashhub", "aliases"]),
        ("Plugins and package managers", ["oh-my-bash", "bash-it", "basher", "bpkg",
                                         "homeshick", "bash-modules", "lobash"]),
        ("Servers and web toys", ["bocker", "git-sh", "mkdkr", "web-server", "bashttpd",
                                  "httpd", "ngincat", "sherver", "xiringuito", "dropbox",
                                  "pushbullet", "bashblog"]),
        ("Scripting libraries and testers", ["ansi", "argbash", "assert.sh", "async-bash",
                                            "bats", "bash3boilerplate", "bashful", "bashify",
                                            "bashing", "bashly", "bashmanager", "bashmatic",
                                            "bunit", "infinity", "bashunit", "lobash", "mo",
                                            "semver", "shellcheck", "shellharden", "shfmt",
                                            "shunit2", "devops-bash", "modernish", "json.bash",
                                            "timep", "alinex", "utility"]),
        ("Games and screensavers", ["2048", "minesweeper", "wordle", "screensaver", "pokeget",
                                    "balls"]),
    ],
    "CLI Apps": [
        ("Music and audio", ["music", "mpd", "mpv", "cmus", "ncmpcpp", "beets", "spot", "song",
                             "radio", "piano", "tunein", "dzr", "ytm", "somafm", "musik",
                             "audio", "itunes", "streamlink", "youtube", "yt-dlp", "podcast"]),
        ("Video, film and reading", ["video", "movie", "cinema", "capcut", "editly", "epr",
                                     "speedread", "medium", "bible", "ebook", "read", "book"]),
        ("Chat, mail and news", ["chat", "irc", "weechat", "irssi", "signal", "telgram", "tlgr",
                                 "newsboat", "neomutt", "mail", "wiki"]),
        ("Productivity, tasks and time", ["task", "todo", "timewarrior", "watson", "timetrap",
                                          "calcurse", "gcalcli", "khal", "remind", "calendar",
                                          "birthday", "kanban", "journal", "note", "note", "dnote",
                                          "td-cli", "taskbook", "focus", "meetup", "slack",
                                          "jira", "linear", "over time", "overtime", "pomodoro",
                                          "habit", "simplenote", "nb", "yapsnap", "tock",
                                          "timelog", "timing", "doing", "timep", "clock"]),
        ("Money and ledgers", ["ledger", "hledger", "moeda", "cash", "cointop", "ticker",
                               "crypto", "invoice", "budget", "bill"]),
        ("Dev, build and release", ["npm", "yarn", "release", "boilr", "cookiecutter", "yo",
                                    "mevn", "scaffold", "serve", "shellspec", "bats", "step ci",
                                    "gdb", "loadtest", "semantic", "np ", "vmn", "updates",
                                    "clean-modules", "gitmoji", "clog", "czg"]),
        ("Databases and SQL", ["sql", "mysql", "pgcli", "mycli", "iredis", "usql", "squix",
                               "pgx", "sqlline", "db", "cassandra", "sqlite"]),
        ("Web, APIs and networking", ["http", "curl", "httrack", "wget", "aria2", "rclone",
                                      "ngrok", "localtunnel", "tunnel", "gotty", "upterm",
                                      "mosh", "xxh", "ssh", "tldx", "acmetool", "certificate",
                                      "scp", "ping", "is-up", "reachable", "net", "wifi",
                                      "speedtest", "bandwhich", "download", "upload", "s3",
                                      "drive", "deploy", "splash", "wallpaper"]),
        ("Docker, cloud and ops", ["docker", "k9s", "ctop", "kubernetes", "pm2", "kool",
                                    "decompose", "dockly", "ipfs", "helm", "cron", "ops",
                                    "s3cmd", "s5cmd", "updatecli", "pipeexec"]),
        ("Files, disk and backup", ["file", "disk", "duf", "dust", "ncdu", "trash", "rename",
                                    "organize", "entr", "watch", "chokidar", "backup", "plakar",
                                    "f2", "recover", "shallow", "gzip", "pdf", "imgp", "korkut",
                                    "scc", "chkbit", "diskonaut", "dua", "dutree", "darya",
                                    "file-type", "unix-permissions", "transmission",
                                    "webtorrent", "croc", "ffsend", "sharing", "google-drive"]),
        ("Find, search and navigate", ["find", "ripgrep", "fzf", "fselect", "fd", "broot",
                                       "rare", "skim", "ast-grep", "television", "srgn",
                                       "rawhide", "grep", "zoxide", "autojump", "pathpicker",
                                       "goto", "z.lua", "jump", "tree", "eza", "lsd", "ranger",
                                       "nnn", "lf", "clifm", "vifm", "yazi", "xplr", "elio",
                                       "midnight"]),
        ("Git and GitHub", ["git", "gh", "hub", "lazygit", "gitui", "tig", "gita", "gitlab",
                            "commit", "branch", "label", "github"]),
        ("Data, JSON and CSV", ["jq", "yq", "dasel", "yaml", "xq", "fx", "gron", "visidata",
                                "sc-im", "nless", "q ", "parse-columns", "json", "groq",
                                "ramda", "underscore", "diff", "validator"]),
        ("Images, docs and slides", ["image", "gif", "asciinema", "ttygif", "ttystudio",
                                     "carbon", "svgo", "pageres", "optimizt", "freeze",
                                     "rclip", "img2ascii", "pdfjuicer", "decktape", "mdp",
                                     "marp", "sent", "slides", "markdown", "glow", "mdv",
                                     "doctoc", "grip", "gtree", "pandoc"]),
        ("Terminal art and fun", ["cmatrix", "pipes", "yulelog", "fireplace", "mandelbrot",
                                  "pastel", "lowcharts", "quote", "fortune", "ponysay", "yosay",
                                  "lolcat", "effect", "meme", "dankcli", "ricksay", "emoj",
                                  "figlet", "stegcloak", "gitlogue", "drift", "cbirds"]),
        ("AI agents and assistants", ["ai", "agent", "gpt", "llm", "opencode", "nanocoder",
                                      "bot", "chatbot", "codex", "copilot"]),
        ("Meta: lists and directories", ["awesome", "terminal trove", "terminals-are-sexy",
                                         "x-cmd", "csv", "cheatsheet"]),
    ],
    "Cheat Sheets": [
        ("Languages", ["python", "javascript", "typescript", "java", "kotlin", "rust", "go",
                       "ruby", "php", "perl", "lua", "r-", "racket", "scala", "scheme",
                       "clojure", "dart", "elixir", "erlang", "elm", "haskell", "f#", "ocaml",
                       "swift", "objective-c", "smalltalk", "solidity", "rebol", "ada",
                       "c#", "c++", "c-ansi", "coffeescript", "assembly", "matlab", "octave"]),
        ("Web and front-end", ["css", "html", "sass", "scss", "flex", "bootstrap", "react",
                               "angular", "vue", "jquery", "ember", "webpack", "redux",
                               "font-awesome", "tailwind", "favicon", "easings", "page-load"]),
        ("Back-end, databases, queues", ["django", "rails", "ror", "express", "laravel",
                                         "nodejs", "fastapi", "web2py", "couchdb", "db2",
                                         "elasticsearch", "mongo", "mysql", "oracle",
                                         "postgres", "sql", "kafka", "rest"]),
        ("Systems, shell and editors", ["shell", "bash", "fish", "zsh", "awk", "sed",
                                        "curl", "vim", "emacs", "paredit", "tmux", "mac",
                                        "linux", "windows", "eclipse", "atom", "netbeans",
                                        "sublime", "phpstorm", "notepad", "vscode", "unix",
                                        "sysadmin", "systemtap", "dtrace", "zypper",
                                        "mobaxterm", "markdown"]),
        ("Git and workflow", ["git", "svn", "github", "git-flow", "gitflow"]),
        ("Security", ["security", "owasp", "pentest", "oauth", "html5"]),
        ("CS theory and network", ["bigo", "acm", "theoretical", "regular-expression",
                                   "network", "operating-system", "syscall", "data-structure",
                                   "machine-learning", "math-as-code", "api-", "video streaming"]),
        ("Process and product", ["agile", "scrum", "kanban", "lean", "waterfall", "testing",
                                 "rspec", "jest"]),
    ],
    "The Book of Secret Knowledge": [
        ("OpenSSL and certificates", ["openssl", "certificate", "rfc", "oid"]),
    ],
    "Console Services": [
        ("Downloaders", ["aria2", "curl", "httpie", "wget", "httrack", "rclone"]),
        ("Windows tools", ["bitsadmin", "powershell"]),
    ],
}

# ---------------------------------------------------------------- examples
# Only commands that are correct as written. A tool without an entry gets no example.
EXAMPLES = {
    "bat": "bat README.md",
    "fzf": "git ls-files | fzf",
    "ripgrep": "rg -n 'TODO' src/",
    "fd": "fd -e md --changed-within 1w",
    "fselect": "fselect path, size from /var/log where size > 100m",
    "broot": "broot ~/src",
    "skim": "git branch | sk",
    "ast-grep": "ast-grep -p 'console.log($A)' src/",
    "zoxide": "z blog",
    "autojump": "j devblog",
    "z": "z src",
    "eza": "eza -l --git --tree --level 2",
    "lsd": "lsd -l --tree --depth 2",
    "exa": "exa -l --git",
    "ranger": "ranger ~/Downloads",
    "nnn": "nnn -d",
    "lf": "lf ~/src",
    "yazi": "yazi",
    "vifm": "vifm .",
    "clifm": "clifm",
    "midnight-commander": "mc",
    "jq": "curl -s https://api.github.com/repos/jqlang/jq | jq '.stargazers_count'",
    "yq": "yq '.services.web.image' docker-compose.yml",
    "dasel": "dasel -f package.json '.scripts.test'",
    "fx": "curl -s https://example.com/data.json | fx .items[0]",
    "gron": "curl -s https://example.com/data.json | gron | grep name",
    "xq": "xq '.html.body.h1' page.html",
    "visidata": "vd data.csv",
    "sc-im": "sc-im budget.csv",
    "q": "q \"select count(*) from data.csv\"",
    "httpie": "http GET https://example.com",
    "curl": "curl -sSL https://example.com -o page.html",
    "wget": "wget -r -np -k https://example.com",
    "wget2": "wget2 -q -O page.html https://example.com",
    "aria2": "aria2c -x8 -s8 https://example.com/big.iso",
    "rclone": "rclone sync ~/photos remote:photos --progress",
    "httrack": "httrack https://example.com -O ./site",
    "mosh": "mosh user@host",
    "sshuttle": "sshuttle -r user@host 0.0.0.0/0",
    "ngrok": "ngrok http 8000",
    "gotty": "gotty -w bash",
    "upterm": "upterm host -- bash",
    "entr": "ls *.go | entr -c go test ./...",
    "chokidar-cli": "chokidar 'src/**/*.js' -c 'npm run build'",
    "tldr": "tldr tar",
    "howdoi": "howdoi extract a tar.gz",
    "how2": "how2 list files by size",
    "the fuck": "fuck",
    "navi": "navi widget bash",
    "shellcheck": "shellcheck install.sh",
    "shfmt": "shfmt -w -i 2 script.sh",
    "shellharden": "shellharden --replace script.sh",
    "bats": "bats tests/",
    "bats-core": "bats --recursive tests/",
    "bashunit": "bashunit tests/",
    "shellspec": "shellspec",
    "shunit2": "shunit2 tests/unit.sh",
    "bashly": "bashly init --minimal",
    "argbash": "argbash script.m4 -o script.sh",
    "bpkg": "bpkg install user/repo",
    "basher": "basher install user/repo",
    "homeshick": "homeshick clone user/dotfiles",
    "bash-it": "bash-it enable plugin git",
    "hstr": "hstr",
    "bashttpd": "bashttpd",
    "bocker": "bocker run alpine uname -a",
    "bashttpd ": "bashttpd",
    "todo.sh": "todo.sh add 'write the page'",
    "newsboat": "newsboat",
    "weechat": "weechat",
    "irssi": "irssi",
    "signal-cli": "signal-cli -u +351000000000 send -m 'hello' +351111111111",
    "yt-dlp": "yt-dlp -f 'bv*+ba' -o '%(title)s.%(ext)s' URL",
    "youtube-dl": "youtube-dl -x --audio-format mp3 URL",
    "mpv": "mpv --no-video music.opus",
    "mpd": "mpd ~/.config/mpd/mpd.conf",
    "ncmpcpp": "ncmpcpp",
    "cmus": "cmus",
    "beets": "beet import ~/Music",
    "streamlink": "streamlink URL best",
    "asciinema": "asciinema rec demo.cast",
    "gifsicle": "gifsicle -O3 --colors 128 in.gif -o out.gif",
    "imagemagick": "magick input.png -resize 800x -strip out.png",
    "cmatrix": "cmatrix -ab",
    "pipes.sh": "pipes.sh -t 0",
    "lolcat": "ls -la | lolcat",
    "figlet": "figlet -f big 'shell'",
    "fortune": "fortune -s",
    "ponysay": "ponysay 'hello'",
    "pastel": "pastel color '#54e3c4'",
    "glow": "glow README.md",
    "mdv": "mdv README.md",
    "k9s": "k9s -n default",
    "ctop": "ctop",
    "lazydocker": "lazydocker",
    "dockly": "dockly",
    "glances": "glances --percpu",
    "duf": "duf",
    "dust": "dust -d 2 -r 20",
    "ncdu": "ncdu /var",
    "dua-cli": "dua interactive",
    "diskonaut": "diskonaut",
    "dutree": "dutree -d 2",
    "trash-cli": "trash-put notes.txt",
    "f2": "f2 -f 'IMG_(\\d+)' -r 'photo_$1' -x",
    "scc": "scc --by-file --sort code",
    "tig": "tig log --all",
    "lazygit": "lazygit",
    "gitui": "gitui",
    "gh": "gh pr list --state open",
    "hub": "hub pull-request -m 'Fix the parser'",
    "git-extras": "git summary",
    "git-standup": "git standup -d 7",
    "git-secret": "git secret hide",
    "gita": "gita ll",
    "gitmoji-cli": "gitmoji -c",
    "czg": "czg",
    "semantic-release": "npx semantic-release --dry-run",
    "release-it": "release-it --dry-run",
    "np": "np --no-tests",
    "npm-check-updates": "ncu -u",
    "serve": "serve dist -l 3000",
    "simplehttp": "simplehttp 8000",
    "shell2http": "shell2http /date 'date -Iseconds'",
    "khal": "khal list today 7d",
    "calcurse": "calcurse",
    "gcalcli": "gcalcli agenda",
    "task": "task add 'review the PR' project:blog +today",
    "timewarrior": "timew start writing",
    "watson": "watson start blog",
    "ledger": "ledger -f books.ledger bal",
    "hledger": "hledger balance --tree",
    "cointop": "cointop",
    "ticker": "ticker --watch --show-percent",
    "visidata ": "vd data.csv",
    "pass": "pass insert mail/gmail",
    "gopass": "gopass show -c mail/gmail",
    "starship": "eval \"$(starship init bash)\"",
    "oh-my-posh": "oh-my-posh init bash --config ~/.config/oh-my-posh.json | source",
    "themer": "themer -c theme.yml -o dist/",
    "task-spooler": "ts bash -c 'make -j4'",
    "awk-nawk-and-gawk-cheat-sheet": "awk -F: '$3 >= 1000 {print $1}' /etc/passwd",
    "sed-stream-editor-cheat-sheet": "sed -n '10,20p' file.txt",
    "openssl": "openssl req -new -newkey rsa:4096 -nodes -keyout key.pem -out csr.pem -subj '/CN=example.com'",
    "curl (cheat sheet)": "curl -sS -I https://example.com",
}


def esc(t):
    return html.escape(t or "", quote=False)


def slug(t):
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


def noex(url):
    """Honest one-liner for the cards that are not a runnable command."""
    host = urlparse(url).netloc.lower()
    low = url.lower()
    if low.endswith(".pdf"):
        return "A PDF, not a command: download it and keep it next to the terminal."
    if "web.archive.org" in host:
        return "An archived page — read it for the original wording, not for a command."
    if "wikipedia.org" in host:
        return "Background reading, not a binary."
    if "stackoverflow.com" in host or "reddit.com" in host:
        return "A thread of answers — the examples are inside, in other people's words."
    if host in ("man7.org", "gnu.org", "www.gnu.org", "tldp.org", "wiki.bash-hackers.org",
                "mywiki.wooledge.org", "bash-hackers.org"):
        return "Documentation: `man` and `help` give you the same text offline."
    if "github.com" in host:
        return "A repository: its README is the example."
    return "No command to show — the source has the details."


def bucket_of(list_name, tool_name):
    for title, keys in BUCKETS.get(list_name, []):
        low = tool_name.lower()
        for key in keys:
            if key in low:
                return title
    return "Everything else"


def main():
    data = json.load(open(SRC, encoding="utf-8"))["shell"]

    # dedupe by URL: first card wins, later appearances are recorded on it
    repo_of = {lst["list"]: lst["repo"] for lst in data}
    seen, order, dupes = {}, [], {}
    for lst in data:
        for tool in lst["tools"]:
            key = tool["url"].rstrip("/")
            if key in seen:
                dupes.setdefault(key, []).append(lst["list"])
                continue
            seen[key] = True
            order.append((lst["list"], tool))

    lists = {}
    for list_name, tool in order:
        lists.setdefault(list_name, []).append(tool)

    body, total, with_ex = [], 0, 0
    for list_name, tools in lists.items():
        buckets = {}
        for tool in tools:
            buckets.setdefault(bucket_of(list_name, tool["name"]), []).append(tool)
        parts = []
        for title, items in buckets.items():
            cards = []
            for tool in items:
                total += 1
                n = tools.index(tool) + 1
                host = urlparse(tool["url"]).netloc.replace("www.", "")
                example = EXAMPLES.get(tool["name"].strip().lower())
                if example:
                    with_ex += 1
                extra = ""
                key = tool["url"].rstrip("/")
                if key in dupes:
                    extra = ('<p class="also">also listed in %s</p>'
                             % esc(", ".join(sorted(set(dupes[key])))))
                cards.append("""
      <details class="tool">
        <summary><span class="num">%02d</span> <span class="tn">%s</span><span class="host">%s</span></summary>
        <div class="card">
          %s%s%s
          <p class="src"><a href="%s" target="_blank" rel="noopener noreferrer">open the source →</a></p>
        </div>
      </details>""" % (
                    n, esc(tool["name"]), esc(host),
                    ('<p class="what">%s</p>' % esc(tool["desc"])) if tool["desc"]
                    else '<p class="what muted">The list gives no description — the link is the description.</p>',
                    ('<pre><code><span class="p">$</span> %s</code></pre>' % esc(example)) if example
                    else '<p class="noex">%s</p>' % esc(noex(tool["url"])),
                    extra,
                    tool["url"]))
            parts.append("""
    <details class="bucket">
      <summary>%s<span class="cnt">%d</span></summary>
%s
    </details>""" % (esc(title), len(items), "".join(cards)))
        # One href per destination: a list that links to itself already has that
        # repository as a card, so the source line would repeat it.
        repo_url = "https://github.com/" + repo_of[list_name]
        src_line = ""
        if repo_url not in seen:
            src_line = ('<p class="about">Source: <a href="%s" target="_blank" '
                        'rel="noopener noreferrer">%s</a></p>'
                        % (esc(repo_url), esc("github.com/" + repo_of[list_name])))
        body.append("""
  <details class="list">
    <summary><span class="lid">%s</span><span class="cnt">%d tools</span></summary>
    %s
%s
  </details>""" % (esc(list_name), len(tools), src_line, "".join(parts)))

    assert len(seen) == total, (len(seen), total)
    if not 110 <= len(DESC) <= 155:
        sys.exit("description is %d chars" % len(DESC))

    doc = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; img-src 'self' data:; style-src 'unsafe-inline'">
<meta name="X-Content-Type-Options" content="nosniff">
<meta name="X-Frame-Options" content="DENY">
<meta name="Referrer-Policy" content="no-referrer">
<title>__TITLE__ | Monkey Blog</title>
<meta name="description" content="__DESC__">
<link rel="canonical" href="__URL__">
<meta property="og:title" content="__TITLE__">
<meta property="og:description" content="__DESC__">
<meta property="og:type" content="article">
<meta property="og:url" content="__URL__">
<meta property="og:site_name" content="Monkey Blog">
<meta property="og:image" content="__IMG__">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="__TITLE__">
<meta name="twitter:description" content="__DESC__">
<meta name="twitter:image" content="__IMG__">
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "BlogPosting",
      "@id": "__URL__#article",
      "headline": "__TITLE__",
      "name": "__TITLE__",
      "description": "__DESC__",
      "url": "__URL__",
      "mainEntityOfPage": {"@type": "WebPage", "@id": "__URL__"},
      "image": {"@type": "ImageObject", "url": "__IMG__", "width": 1496, "height": 960},
      "inLanguage": "en",
      "author": {"@type": "Person", "name": "Oscar", "url": "https://blog.odicforcesounds.com/", "sameAs": ["https://mastodon.social/@TaoExpression"]},
      "publisher": {"@type": "Organization", "name": "Monkey Blog", "url": "https://blog.odicforcesounds.com/", "logo": {"@type": "ImageObject", "url": "https://blog.odicforcesounds.com/images/three.jpg", "width": 1024, "height": 1024}},
      "isPartOf": {"@type": "Blog", "name": "Monkey Blog", "url": "https://blog.odicforcesounds.com/"},
      "articleSection": "Programming & Development",
      "keywords": "shell, terminal, bash, cli apps, cheatsheets, one-liners",
      "wordCount": __WORDS__,
      "datePublished": "2026-11-02",
      "dateModified": "2026-11-02"
    },
    {
      "@type": "BreadcrumbList",
      "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://blog.odicforcesounds.com/"},
        {"@type": "ListItem", "position": 2, "name": "Programming & Development", "item": "https://blog.odicforcesounds.com/#category-programming-and-development"},
        {"@type": "ListItem", "position": 3, "name": "__TITLE__", "item": "__URL__"}
      ]
    }
  ]
}
</script>
<style>
:root{--bg:#070b10;--ink:#e9f0f7;--dim:#a9b7c6;--muted:#7d8d9f;--line:rgba(126,163,196,.15);
--line2:rgba(126,163,196,.3);--accent:#54e3c4;--warm:#ffbe6b;
--sans:system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;
--mono:ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace}
*{box-sizing:border-box}
html{scroll-behavior:smooth;-webkit-text-size-adjust:100%}
body{margin:0;color:var(--ink);font-family:var(--sans);font-size:15.5px;line-height:1.6;
background:radial-gradient(60rem 38rem at 50% -14%,rgba(84,227,196,.07),transparent 62%),var(--bg)}
.topbar{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:12px;
max-width:1000px;margin:0 auto;padding:18px 20px 14px;border-bottom:1px solid var(--line)}
.brand{font-family:var(--mono);font-size:13px;color:var(--accent);text-decoration:none}
.note{font-family:var(--mono);font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
main{max-width:1000px;margin:0 auto;padding:30px 20px 90px}
.kicker{font-family:var(--mono);font-size:10.5px;letter-spacing:.22em;text-transform:uppercase;color:var(--accent);margin:0 0 10px}
h1{margin:0 0 12px;font-size:clamp(1.9rem,5vw,2.8rem);line-height:1.06;letter-spacing:-.02em}
.lede{margin:0 0 10px;max-width:74ch;color:var(--dim)}
.lede.small{font-size:13.5px;color:var(--muted);margin-bottom:20px}
.stats{font-family:var(--mono);font-size:11.5px;color:var(--muted);margin:0 0 22px}
details{border-top:1px solid var(--line)}
details summary{cursor:pointer;list-style:none;padding:10px 2px;display:flex;align-items:baseline;gap:10px}
details summary::-webkit-details-marker{display:none}
details summary::before{content:"▸";color:var(--accent);font-size:11px;transition:transform .15s}
details[open] > summary::before{content:"▾"}
.list{margin:26px 0 0;border-top:1px solid var(--line2)}
.list > summary{font-size:1.2rem;font-weight:650}
.lid{color:var(--ink)}
.cnt{margin-left:auto;font-family:var(--mono);font-size:10.5px;color:var(--muted);text-transform:uppercase;letter-spacing:.06em}
.about{margin:0 0 6px;font-family:var(--mono);font-size:10.5px;color:var(--muted)}
.about a{color:var(--muted)}
.bucket{margin:6px 0 0;border-top:1px dashed var(--line)}
.bucket > summary{font-family:var(--mono);font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--dim)}
.tool{border-top:1px solid rgba(126,163,196,.07)}
.tool > summary{font-size:14.5px}
.num{font-family:var(--mono);font-size:10.5px;color:var(--accent);min-width:20px}
.tn{font-weight:600}
.host{font-family:var(--mono);font-size:10px;color:var(--muted);margin-left:auto;text-transform:none}
.card{padding:2px 0 14px 22px;max-width:80ch}
.what{margin:0 0 10px;color:var(--dim);font-size:14px}
.muted{color:var(--muted);font-style:italic}
pre{margin:0 0 10px;padding:10px 12px;background:#0b131b;border:1px solid var(--line);
border-left:2px solid var(--accent);border-radius:6px;overflow-x:auto}
code{font-family:var(--mono);font-size:12.5px;color:var(--ink)}
.p{color:var(--accent)}
.noex{margin:0 0 10px;font-size:13px;color:var(--muted)}
.also{margin:0 0 8px;font-size:12px;color:var(--warm)}
.src{margin:6px 0 0;font-family:var(--mono);font-size:11px}
.src a{color:var(--accent);text-decoration:none}
.page-foot{margin-top:56px;padding-top:18px;border-top:1px solid var(--line);color:var(--muted);font-size:13.5px}
.page-foot a{color:var(--accent)}
@media print{.topbar{display:none}body{background:#fff;color:#111}details{display:block}}
</style>
</head>
<body>
<header class="topbar">
  <a class="brand" href="awesomeIndex.html">◀ Awesome Index</a>
  <span class="note">01 · shell · __TOTAL__ links</span>
</header>
<main>
  <p class="kicker">Category 01 · expanded</p>
  <h1>Shell, terminal and one-liners</h1>
  <p class="lede">Every link the shell lists point at, opened one level further: category, then list, then the tool's own card — what it is, and a command you can actually type. A tool that appears in two lists keeps one card, and says so.</p>
  <p class="lede small">Read it as a workbench: open a list, then a drawer, then a tool. Cards that are a document instead of a program say so instead of inventing a command.</p>
  <p class="stats">__NF__ lists · __TOTAL__ unique links · __WITHEX__ with a runnable example · duplicated links collapsed</p>
__BODY__
  <footer class="page-foot">
    <p>Built from the public README of each list. Summaries are the list's own words; examples are written by hand and kept to commands that run as shown.</p>
    <p><a href="awesome-tools-shell.html">flat list</a> · <a href="awesome_story.html">the story</a></p>
  </footer>
</main>
</body>
</html>
"""
    words = len(re.sub(r"<[^>]+>", " ", "".join(body)).split()) + 120
    pairs = [("TITLE", esc(TITLE)), ("DESC", esc(DESC)), ("URL", ORIGIN + "/awesome-01-shell.html"),
             ("IMG", IMG), ("TOTAL", str(total)), ("WITHEX", str(with_ex)), ("NF", str(len(lists))),
             ("WORDS", str(words)), ("BODY", "".join(body))]
    for k, v in pairs:
        doc = doc.replace("__" + k + "__", v)
    open(OUT, "w", encoding="utf-8").write(doc)
    print("wrote %s: %d lists, %d unique tools, %d examples" % (OUT, len(lists), total, with_ex))


if __name__ == "__main__":
    main()
