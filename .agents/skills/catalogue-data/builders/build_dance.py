#!/usr/bin/env python3
"""Build the dance catalogue JSON from Wikipedia.

Defines the taxonomy (shelf -> group -> style) and asks the Wikipedia API for
each page's canonical title, first sentence and URL, so no description in the
data is invented. The culture and the era written beside each style are this
catalogue's own attribution; the sentence is the article's first sentence.
Writes docs/dance/data/index.json and one file per shelf. Re-runnable.
"""

import os as _os

_os.chdir(_os.path.abspath(_os.path.join(
    _os.path.dirname(_os.path.abspath(__file__)),
    "..", "..", "..", "..")))

import json
import os
import re
import sys
import time
import urllib.parse

OUT = "docs/dance/data"
API = "https://en.wikipedia.org/w/api.php"
UA = "MonkeyBlogDanceCatalogue/1.0 (https://blog.odicforcesounds.com; oscar@odicforcesounds.com)"

D = "dance"

TAXONOMY = [
    ("ritual", "01", "Ritual and temple", "Dance offered before an image or a fire: the temple traditions of India and Southeast Asia, the masked processions of Japan and Tibet, and the trance forms that carry a body out of its own voice.", [
        ("Temple dance of India", [
            ("Bharatanatyam", "Tamil Nadu, India", "2nd c. BCE text · revived 19th c."),
            ("Kathak", "North India", "16th c. Mughal courts"),
            ("Kathakali", "Kerala, India", "17th c."),
            ("Odissi", "Odisha, India", "2nd c. BCE reliefs · revived 20th c."),
            ("Mohiniyattam", "Kerala, India", "16th c."),
            ("Kuchipudi", "Andhra Pradesh, India", "17th c. dance-drama"),
            ("Manipuri dance", "Manipur, India", "18th c. Gaudiya Vaishnavism"),
            ("Sattriya", "Assam, India", "15th c. Vaishnava monasteries"),
            ("Chhau dance", "Odisha, Jharkhand, West Bengal", "18th c. martial and folk"),
        ]),
        ("Southeast Asian courts", [
            ("Balinese dance", "Bali, Indonesia", "9th c. inscriptions"),
            ("Javanese dance", "Java, Indonesia", "8th c. temple reliefs"),
            ("Khmer classical dance", "Cambodia", "7th c. inscriptions"),
            ("Apsara Dance", "Cambodia", "1960s revival"),
            ("Khon", "Thailand", "15th c. Ayutthaya court"),
            ("Yakshagana", "Karnataka, India", "16th c."),
        ]),
        ("East Asian ritual", [
            ("Kagura", "Japan", "8th c. chronicles"),
            ("Bugaku", "Japan, from Tang China", "7th c."),
            ("Gigaku", "Japan", "7th c."),
            ("Cham dance", "Tibet and Mongolia", "8th c."),
            ("Awa Dance Festival", "Tokushima, Japan", "16th c."),
        ]),
        ("Trance, possession and religion", [
            ("Sufi whirling", "Turkey, Mevlevi order", "13th c."),
            ("Zār", "Egypt, Sudan, Horn of Africa", "19th c. record"),
            ("Trance Dance", "worldwide", "prehistoric, recorded 19th c."),
            ("Candomblé", "Bahia, Brazil", "19th c."),
            ("Santería", "Cuba", "19th c."),
            ("Haitian Vodou", "Haiti", "18th c."),
            ("Umbanda", "Brazil", "20th c."),
            ("Kecak", "Bali, Indonesia", "1930s"),
            ("Sun Dance", "Plains peoples, North America", "recorded 19th c."),
            ("Ghost Dance", "Northern Paiute and Plains peoples", "1889"),
            ("Kachina", "Hopi, Arizona", "pre-colonial"),
            ("Gule Wamkulu", "Chewa, Malawi", "pre-colonial"),
            ("Zaouli", "Guro, Côte d'Ivoire", "20th c."),
        ]),
    ]),
    ("court", "02", "Court and classical stage", "The forms a court paid for: ballet from the Italian halls to the Russian stage, the theatre dances of Japan and Java, and the modern schools that broke the story in order to keep the body.", [
        ("Ballet and its descendants", [
            ("Ballet", "Italian and French courts", "15th c. · Académie 1661"),
            ("Baroque dance", "France", "17th c."),
            ("Ballet d'action", "France", "18th c."),
            ("Romantic ballet", "France and Denmark", "19th c."),
            ("Classical ballet", "Russia and Denmark", "19th c."),
            ("Neoclassical ballet", "United States", "20th c."),
            ("Contemporary ballet", "Europe and the United States", "20th c."),
            ("Bolero (Spanish dance)", "Spain", "18th c."),
            ("Flamenco", "Andalusia, Spain", "18th c. · Romany and Andalusian"),
        ]),
        ("The modern schools", [
            ("Modern dance", "United States and Germany", "early 20th c."),
            ("Expressionist dance", "Germany", "early 20th c."),
            ("Postmodern dance", "United States", "1960s"),
            ("Contemporary dance", "Europe and the United States", "mid 20th c."),
            ("Contact improvisation", "United States", "1972"),
            ("Butoh", "Japan", "1959"),
        ]),
        ("Asian classical theatre", [
            ("Noh", "Japan", "14th c."),
            ("Kabuki", "Japan", "17th c."),
            ("Korean court dance", "Korea", "15th c. Joseon court"),
            ("Chinese classical dance", "China", "1950s · Han and Tang sources"),
        ]),
        ("Arabic and Persian courts", [
            ("Raqs sharqi", "Egypt", "19th c. Cairo"),
            ("Persian dance", "Iran", "ancient · recorded 19th c."),
        ]),
    ]),
    ("folk", "03", "Folk and national", "What a village does at a wedding, a harvest or a saint's day — and what a nation later adopts as its own face. The steps are old, the borders on them are new.", [
        ("Europe", [
            ("Waltz", "Austria and Germany", "18th c. from the Ländler"),
            ("Polka", "Bohemia", "1830s"),
            ("Mazurka", "Poland", "17th c."),
            ("Polonaise", "Poland", "16th c."),
            ("Csárdás", "Hungary", "19th c."),
            ("Tarantella", "Southern Italy", "17th c. record"),
            ("Fandango", "Spain", "18th c."),
            ("Jota", "Aragon, Spain", "18th c."),
            ("Sardana", "Catalonia, Spain", "19th c."),
            ("Irish dance", "Ireland", "18th c. record"),
            ("Highland Fling", "Scotland", "19th c."),
            ("Morris dance", "England", "15th c."),
            ("Farandole", "Provence, France", "medieval"),
            ("Hopak", "Ukraine", "16th c. record"),
            ("Khorovod", "Russia", "medieval"),
            ("Kolo", "the Balkans", "19th c."),
            ("Hora", "Romania and Moldova", "19th c."),
            ("Syrtos", "Greece", "ancient · recorded 19th c."),
            ("Zeybek", "Western Anatolia, Turkey", "19th c."),
            ("Debke", "the Levant", "19th c."),
        ]),
        ("The Americas", [
            ("Samba", "Brazil", "1910s Rio de Janeiro"),
            ("Cumbia", "Colombia", "19th c."),
            ("Joropo", "Venezuela and Colombia", "18th c."),
            ("Marinera", "Peru", "19th c."),
            ("Cueca", "Chile", "19th c."),
            ("Zamba", "Argentina", "19th c."),
        ]),
        ("Asia and the Pacific", [
            ("Bhangra", "Punjab", "1940s harvest dance"),
            ("Garba", "Gujarat, India", "medieval"),
            ("Lavani", "Maharashtra, India", "18th c."),
            ("Ghoomar", "Rajasthan, India", "folk · recorded 19th c."),
            ("Hula", "Hawaii", "ancient · recorded 19th c."),
            ("Kapa haka", "Māori, New Zealand", "19th c. revival"),
            ("Corroboree", "Aboriginal Australia", "recorded 19th c."),
            ("Adumu", "Maasai, Kenya and Tanzania", "pre-colonial"),
        ]),
    ]),
    ("social", "04", "Social and partner", "Two people, one room, a band: the couple dances a city invents when it has a night off — from the Viennese ballroom to the Caribbean port, and the codes that decide who may ask whom.", [
        ("Ballroom and Latin", [
            ("Ballroom dance", "England", "1920s codification"),
            ("Tango", "Argentina and Uruguay", "1880s"),
            ("Milonga", "Argentina", "19th c."),
            ("Cha-cha-cha", "Cuba", "1950s"),
            ("Mambo", "Cuba", "1930s"),
            ("Rumba", "Cuba", "19th c."),
            ("Son cubano", "Cuba", "19th c."),
            ("Salsa", "the Caribbean and New York", "1960s"),
            ("Bachata", "Dominican Republic", "20th c."),
            ("Merengue", "Dominican Republic", "19th c."),
            ("Swing", "United States", "1920s"),
            ("Lindy Hop", "Harlem, New York", "1920s"),
            ("Foxtrot", "United States", "1910s"),
            ("Charleston", "United States", "1920s"),
            ("Jive", "United States", "1940s"),
            ("Tap dance", "United States", "19th c."),
            ("Blues dance", "United States", "early 20th c."),
        ]),
        ("Africa and its diaspora", [
            ("Kizomba", "Angola", "1980s"),
            ("Semba", "Angola", "20th c."),
            ("Zouk", "French Caribbean", "1980s"),
            ("Lambada", "Brazil", "1980s"),
            ("Forró", "Northeast Brazil", "20th c."),
        ]),
    ]),
    ("street", "05", "Street and club", "The forms made by people with a pavement and a record player: the Bronx, Los Angeles, Kingston, Lagos, Johannesburg. No school fees, a name given on the floor, and a battle instead of an exam.", [
        ("African American street forms", [
            ("Breaking", "the Bronx, New York", "1970s"),
            ("Locking", "Los Angeles", "1970s"),
            ("Popping", "Fresno, California", "1970s"),
            ("Waacking", "Los Angeles", "1970s"),
            ("Voguing", "Harlem ballroom, New York", "1980s"),
            ("House dance", "Chicago and New York", "1980s"),
            ("Hip-hop dance", "United States", "1970s"),
            ("Jazz dance", "United States", "20th c."),
            ("Krump", "Los Angeles", "2000s"),
            ("Litefeet", "Harlem, New York", "2000s"),
            ("Turfing", "Oakland, California", "2000s"),
            ("Gangsta Walking", "Memphis, Tennessee", "1980s"),
        ]),
        ("Caribbean and African club", [
            ("Dancehall", "Jamaica", "1980s"),
            ("Azonto", "Ghana", "2010s"),
            ("Coupé-décalé", "Côte d'Ivoire", "2000s"),
            ("Ndombolo", "Democratic Republic of the Congo", "1990s"),
            ("Kwassa kwassa", "Democratic Republic of the Congo", "1980s"),
            ("Pantsula", "South Africa", "1950s"),
            ("Amapiano", "South Africa", "2010s"),
        ]),
        ("Europe, Asia and the ballroom floor", [
            ("Disco", "United States", "1970s"),
            ("Hustle", "United States", "1970s"),
            ("Twist", "United States", "1960"),
            ("Line dance", "United States", "20th c."),
            ("Square dance", "United States", "19th c."),
            ("Contra dance", "England and New England", "17th c."),
            ("Para Para", "Japan", "1980s"),
        ]),
    ]),
    ("martial-east", "06", "Martial arts of East Asia", "The other half of the same training: a form rehearsed until the body forgets it is deciding. Japan's schools, China's families and Korea's national sports, each with the century it was founded.", [
        ("Japan", [
            ("Judo", "Japan", "1882 · Kanō Jigorō"),
            ("Jujutsu", "Japan", "16th c. Sengoku schools"),
            ("Aikido", "Japan", "1920s · Ueshiba Morihei"),
            ("Karate", "Okinawa, Japan", "17th c. roots · named 1930s"),
            ("Kobudō", "Okinawa, Japan", "17th c."),
            ("Kendo", "Japan", "18th c. shinai · older roots"),
            ("Iaido", "Japan", "16th c."),
            ("Kyūdō", "Japan", "16th c. schools"),
            ("Sumo", "Japan", "8th c. records"),
            ("Ninjutsu", "Japan", "15th c. · later mythologised"),
            ("Shorinji Kempo", "Japan", "1947"),
        ]),
        ("China", [
            ("Chinese martial arts", "China", "ancient · recorded from the Han"),
            ("Shaolin Kung Fu", "Henan, China", "5th c. tradition · 16th c. record"),
            ("Tai chi", "China", "17th c. · Chen Wangting"),
            ("Baguazhang", "China", "19th c. · Dong Haichuan"),
            ("Xingyiquan", "China", "17th c. · Ji Longfeng"),
            ("Wing Chun", "Foshan, China", "18th c."),
            ("Hung Ga", "Guangdong, China", "19th c."),
            ("Choy Li Fut", "Guangdong, China", "19th c."),
            ("Bajiquan", "Hebei, China", "18th c."),
            ("Shuai jiao", "China", "ancient · Song court"),
            ("Wushu", "China", "1950s codification"),
            ("Sanda (sport)", "China", "20th c."),
        ]),
        ("Korea", [
            ("Taekwondo", "Korea", "1950s"),
            ("Tang Soo Do", "Korea", "1940s"),
            ("Hapkido", "Korea", "1940s · Choi Yong-sool"),
            ("Taekkyeon", "Korea", "Joseon · 18th c. record"),
            ("Ssireum", "Korea", "ancient"),
        ]),
    ]),
    ("martial-south", "07", "Martial arts of South and Southeast Asia", "Empty hand, stick, blade and rope, taught in a kalari, a village square or a temple courtyard: Kerala's gymnasiums, the Philippine stick schools, the ring sports of Thailand and Myanmar.", [
        ("India", [
            ("Kalaripayattu", "Kerala, India", "11th c. record"),
            ("Silambam", "Tamil Nadu, India", "ancient · recorded 19th c."),
            ("Gatka", "Punjab", "17th c. · Sikh"),
            ("Thang-ta", "Manipur, India", "17th c."),
            ("Malla-yuddha", "India", "ancient"),
            ("Pehlwani", "India and Persia", "Mughal era"),
            ("Mallakhamba", "India", "19th c."),
            ("Lathi khela", "Bengal", "medieval"),
            ("Varma kalai", "Tamil Nadu, India", "ancient"),
        ]),
        ("Southeast Asia", [
            ("Pencak silat", "Indonesia and Malaysia", "14th c."),
            ("Arnis", "the Philippines", "16th c. record"),
            ("Muay Thai", "Thailand", "16th c. Ayutthaya"),
            ("Muay boran", "Thailand", "older than the ring sport"),
            ("Krabi-Krabong", "Thailand", "Ayutthaya"),
            ("Lethwei", "Myanmar", "11th c. record"),
            ("Bando", "Myanmar", "9th c. tradition"),
            ("Vovinam", "Vietnam", "1938 · Nguyễn Lộc"),
        ]),
    ]),
    ("martial-west", "08", "Martial arts of Europe, Africa and the Americas", "The wrestling and swordplay Europe wrote down in manuals, the stick and fist sports of Africa and Egypt, and the ring sports the Americas made out of both — up to the cage.", [
        ("Europe", [
            ("Boxing", "England", "18th c. · Broughton 1743"),
            ("Bare-knuckle boxing", "England", "18th c."),
            ("Greco-Roman wrestling", "Greece and Rome", "704 BCE Olympics"),
            ("Freestyle wrestling", "Britain and the United States", "19th c."),
            ("Catch wrestling", "England", "19th c."),
            ("Fencing", "Italy and France", "16th c. schools"),
            ("Historical European martial arts", "Europe", "14th c. manuals"),
            ("German school of fencing", "Holy Roman Empire", "14th c. · Liechtenauer"),
            ("Italian school of swordsmanship", "Italy", "14th c. · Fiore"),
            ("Savate", "France", "19th c."),
            ("Bartitsu", "England", "1898"),
            ("Ringen", "German lands", "medieval"),
            ("Glima", "Iceland", "medieval"),
            ("Jogo do pau", "Portugal", "medieval"),
            ("Cornish wrestling", "Cornwall, England", "17th c. record"),
            ("Pankration", "ancient Greece", "648 BCE"),
            ("Systema", "Russia", "20th c."),
            ("Sambo", "Soviet Union", "1930s"),
        ]),
        ("Africa and the Middle East", [
            ("Tahtib", "Egypt", "2000 BCE record"),
            ("Dambe", "Hausa, Nigeria", "pre-colonial"),
            ("Senegalese wrestling", "Senegal", "pre-colonial"),
            ("Nguni stick-fighting", "Southern Africa", "pre-colonial"),
            ("Krav Maga", "Israel", "1940s · Imi Lichtenfeld"),
        ]),
        ("The Americas", [
            ("Capoeira", "Brazil", "18th c. · enslaved Africans"),
            ("Vale tudo", "Brazil", "20th c."),
            ("Mixed martial arts", "United States", "1993 · UFC"),
            ("Okichitaw", "Plains Cree, Canada", "20th c. revival"),
        ]),
    ]),
]


def api(params):
    params = dict(params)
    params["format"] = "json"
    params["formatversion"] = "2"
    url = API + "?" + urllib.parse.urlencode(params)
    import subprocess
    out = subprocess.run(["curl", "-sS", "-A", UA, url], capture_output=True, text=True)
    if not out.stdout:
        raise RuntimeError(out.stderr[:300])
    return json.loads(out.stdout)


def fetch(titles):
    data = {}
    for start in range(0, len(titles), 20):
        chunk = titles[start:start + 20]
        res = api({
            "action": "query",
            "titles": "|".join(chunk),
            "prop": "extracts|info",
            "exintro": 1,
            "explaintext": 1,
            "exsentences": 2,
            "exlimit": "max",
            "redirects": 1,
            "inprop": "url",
        })
        query = res.get("query", {})
        pages = {p.get("title"): p for p in query.get("pages", [])}
        norm = {}
        for item in query.get("normalized", []):
            norm[item.get("from")] = item.get("to")
        redir = {}
        for item in query.get("redirects", []):
            redir[item.get("from")] = item.get("to")
        for title in chunk:
            key = norm.get(title, title)
            key = redir.get(key, key)
            page = pages.get(key)
            if not page or page.get("missing"):
                data[title] = None
                continue
            extract = re.sub(r"\s+", " ", (page.get("extract") or "")).strip()
            first = extract.split(". ")[0]
            first = re.sub(r"\(\s*;", "(", first)
            first = re.sub(r"\(\s*\)", "", first)
            if len(first) > 230:
                first = first[:227].rstrip() + "…"
            elif first and not first.endswith("."):
                first += "."
            data[title] = {
                "n": page.get("title"),
                "u": page.get("fullurl") or ("https://en.wikipedia.org/wiki/" +
                                             urllib.parse.quote(page.get("title", "").replace(" ", "_"))),
                "s": first,
            }
        time.sleep(0.3)
    return data


def main():
    titles = []
    for _, _, _, _, groups in TAXONOMY:
        for _, items in groups:
            for article, _, _ in items:
                if article not in titles:
                    titles.append(article)
    print("titles:", len(titles))
    fetched = fetch(titles)
    missing = [t for t, v in fetched.items() if not v]
    print("missing:", len(missing))
    for t in missing:
        print("   ", t)

    os.makedirs(OUT, exist_ok=True)
    index = {"styles": 0, "groups": 0, "cultures": 0, "categories": []}
    taken = set()
    cultures = set()
    for key, num, title, blurb, groups in TAXONOMY:
        out_groups = []
        total = 0
        for name, items in groups:
            entries = []
            for article, culture, era in items:
                page = fetched.get(article)
                if not page or page["u"] in taken:
                    continue
                taken.add(page["u"])
                cultures.add(culture)
                entries.append({"n": page["n"], "u": page["u"], "s": page["s"],
                                "c": culture, "e": era})
            if not entries:
                continue
            out_groups.append({"name": name, "items": entries})
            total += len(entries)
        doc = {"key": key, "num": num, "title": title, "blurb": blurb,
               "groups": out_groups}
        with open(os.path.join(OUT, key + ".json"), "w", encoding="utf-8") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=0)
        index["categories"].append({
            "key": key, "num": num, "title": title, "blurb": blurb, "slug": key,
            "styles": total, "groups": len(out_groups),
        })
        index["styles"] += total
        index["groups"] += len(out_groups)
    index["cultures"] = len(cultures)
    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as fh:
        json.dump(index, fh, ensure_ascii=False, indent=0)
    blank = [(article, page["n"]) for article, page in fetched.items()
             if page and not page["s"]]
    if blank:
        print("no text:", len(blank))
        for article, title in blank:
            print("   ", article, "->", title)
    print("shelves:", len(index["categories"]), "groups:", index["groups"],
          "styles:", index["styles"], "cultures:", index["cultures"])
    for c in index["categories"]:
        print("   %s %-38s %3d styles in %d groups" %
              (c["num"], c["title"], c["styles"], c["groups"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
