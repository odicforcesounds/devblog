#!/usr/bin/env python3
"""Build docs/insects/data/ — the catalogue behind docs/insectsIndex.html.

Insects first, then everything similar: spiders, scorpions, ticks and mites,
centipedes, millipedes, woodlice, springtails, harvestmen and velvet worms.

Hand-written: group, order, family, metamorphosis, habitats, regions, roles.
Fetched and cited: photograph, introduction, binomial and IUCN status.
"""

import os as _os

_os.chdir(_os.path.abspath(_os.path.join(
    _os.path.dirname(_os.path.abspath(__file__)),
    "..", "..", "..", "..")))

import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

UA = {"User-Agent": "devblog-insects/1.0 (https://blog.odicforcesounds.com; contact via site)"}
OUT = "docs/insects/data"

# title | group | order | family | metamorphosis | habitats | regions | roles
SPEC = """
Seven-spot ladybird|insect|Coleoptera|Coccinellidae|complete|farmland,urban,woodland|europe,asia|predator
Harlequin ladybird|insect|Coleoptera|Coccinellidae|complete|urban,farmland|asia|predator,invasive
Stag beetle|insect|Coleoptera|Lucanidae|complete|forest,woodland|europe,asia|
Goliath beetle|insect|Coleoptera|Scarabaeidae|complete|forest|africa|
Hercules beetle|insect|Coleoptera|Scarabaeidae|complete|forest|americas|
Japanese rhinoceros beetle|insect|Coleoptera|Scarabaeidae|complete|forest,farmland|asia|
Dung beetle|insect|Coleoptera|Scarabaeidae|complete|grassland,farmland|worldwide|decomposer
Scarabaeus sacer|insect|Coleoptera|Scarabaeidae|complete|desert,grassland|africa|decomposer
Bombardier beetle|insect|Coleoptera|Carabidae|complete|woodland,grassland|worldwide|predator,chemical-defence
Ground beetle|insect|Coleoptera|Carabidae|complete|farmland,woodland|worldwide|predator
Firefly|insect|Coleoptera|Lampyridae|complete|wetland,woodland|worldwide|bioluminescent
Common glow-worm|insect|Coleoptera|Lampyridae|complete|grassland,woodland|europe,asia|bioluminescent
Colorado potato beetle|insect|Coleoptera|Chrysomelidae|complete|farmland|americas|pest
Japanese beetle|insect|Coleoptera|Scarabaeidae|complete|urban,farmland|asia,americas|pest
Deathwatch beetle|insect|Coleoptera|Ptinidae|complete|woodland,urban|europe|
Asian longhorn beetle|insect|Coleoptera|Cerambycidae|complete|woodland,urban|asia|pest
Giraffe weevil|insect|Coleoptera|Attelabidae|complete|forest|africa|
Bark beetle|insect|Coleoptera|Curculionidae|complete|forest|worldwide|pest
Whirligig beetle|insect|Coleoptera|Gyrinidae|complete|wetland,lake|worldwide|predator
Monarch butterfly|insect|Lepidoptera|Nymphalidae|complete|farmland,urban|americas|migratory
Painted lady|insect|Lepidoptera|Nymphalidae|complete|grassland,farmland|worldwide|migratory
Red admiral|insect|Lepidoptera|Nymphalidae|complete|woodland,urban|europe,asia,americas|migratory
Peacock butterfly|insect|Lepidoptera|Nymphalidae|complete|woodland,urban|europe,asia|
Small tortoiseshell|insect|Lepidoptera|Nymphalidae|complete|grassland,urban|europe,asia|migratory
Brimstone butterfly|insect|Lepidoptera|Pieridae|complete|woodland,grassland|europe|
Large white|insect|Lepidoptera|Pieridae|complete|farmland,urban|europe,asia|pest
Orange-tip|insect|Lepidoptera|Pieridae|complete|wetland,woodland|europe|
Swallowtail butterfly|insect|Lepidoptera|Papilionidae|complete|wetland,grassland|europe,asia|
Blue morpho|insect|Lepidoptera|Nymphalidae|complete|forest|americas|
Owl butterfly|insect|Lepidoptera|Nymphalidae|complete|forest|americas|mimic
Glasswing butterfly|insect|Lepidoptera|Nymphalidae|complete|forest|americas|camouflage
Atlas moth|insect|Lepidoptera|Saturniidae|complete|forest|asia|
Death's-head hawkmoth|insect|Lepidoptera|Sphingidae|complete|farmland,woodland|europe,asia,africa|migratory
Hummingbird hawkmoth|insect|Lepidoptera|Sphingidae|complete|urban,grassland|europe,asia,africa|migratory
Silkworm|insect|Lepidoptera|Bombycidae|complete|farmland|asia|silk
Gypsy moth|insect|Lepidoptera|Erebidae|complete|forest|europe,asia,americas|pest,invasive
Clothes moth|insect|Lepidoptera|Tineidae|complete|urban|worldwide|pest
Codling moth|insect|Lepidoptera|Tortricidae|complete|farmland|worldwide|pest
Luna moth|insect|Lepidoptera|Saturniidae|complete|forest|americas|
Western honey bee|insect|Hymenoptera|Apidae|complete|farmland,urban|worldwide|pollinator,social
Eastern honey bee|insect|Hymenoptera|Apidae|complete|farmland,forest|asia|pollinator,social
Buff-tailed bumblebee|insect|Hymenoptera|Apidae|complete|farmland,grassland|europe,africa|pollinator,social
Garden bumblebee|insect|Hymenoptera|Apidae|complete|grassland,urban|europe,asia|pollinator,social
Red mason bee|insect|Hymenoptera|Megachilidae|complete|urban,woodland|europe|pollinator
Leafcutter bee|insect|Hymenoptera|Megachilidae|complete|urban,woodland|worldwide|pollinator,builder
Orchid bee|insect|Hymenoptera|Apidae|complete|forest|americas|pollinator
Cuckoo bee|insect|Hymenoptera|Apidae|complete|grassland|europe,americas|kleptoparasite
Paper wasp|insect|Hymenoptera|Vespidae|complete|urban,woodland|worldwide|social,builder
Asian hornet|insect|Hymenoptera|Vespidae|complete|urban,woodland|asia|predator,social,invasive
European hornet|insect|Hymenoptera|Vespidae|complete|woodland,urban|europe,asia|predator,social
Common wasp|insect|Hymenoptera|Vespidae|complete|urban,farmland|europe,asia|social
Fig wasp|insect|Hymenoptera|Agaonidae|complete|forest|worldwide|pollinator,symbiosis
Velvet ant|insect|Hymenoptera|Mutillidae|complete|desert,grassland|worldwide|parasite,venomous
Ichneumon wasp|insect|Hymenoptera|Ichneumonidae|complete|woodland,grassland|worldwide|parasite
Leafcutter ant|insect|Hymenoptera|Formicidae|complete|forest|americas|social,fungus-farming
Army ant|insect|Hymenoptera|Formicidae|complete|forest|americas|predator,social
Bullet ant|insect|Hymenoptera|Formicidae|complete|forest|americas|venomous,social
Red imported fire ant|insect|Hymenoptera|Formicidae|complete|grassland,urban|americas|venomous,social,invasive
Weaver ant|insect|Hymenoptera|Formicidae|complete|forest,urban|asia,oceania|social,builder
Argentine ant|insect|Hymenoptera|Formicidae|complete|urban,woodland|worldwide|social,invasive
Acacia ant|insect|Hymenoptera|Formicidae|complete|grassland|americas|symbiosis
Honeypot ant|insect|Hymenoptera|Formicidae|complete|desert|americas,africa|social
Termite|insect|Blattodea|Termitidae|incomplete|grassland,forest|worldwide|social,decomposer
Housefly|insect|Diptera|Muscidae|complete|urban,farmland|worldwide|pest
Mosquito|insect|Diptera|Culicidae|complete|wetland,urban|worldwide|parasite
Anopheles|insect|Diptera|Culicidae|complete|wetland|worldwide|parasite
Aedes aegypti|insect|Diptera|Culicidae|complete|urban|worldwide|parasite
Tsetse fly|insect|Diptera|Glossinidae|complete|woodland,grassland|africa|parasite
Hoverfly|insect|Diptera|Syrphidae|complete|farmland,urban|worldwide|pollinator,mimic
Marmalade hoverfly|insect|Diptera|Syrphidae|complete|farmland,urban|europe,asia|pollinator,migratory
Drosophila melanogaster|insect|Diptera|Drosophilidae|complete|urban,farmland|worldwide|model-organism
Mediterranean fruit fly|insect|Diptera|Tephritidae|complete|farmland|africa,americas|pest
Botfly|insect|Diptera|Oestridae|complete|grassland,farmland|americas|parasite
Crane fly|insect|Diptera|Tipulidae|complete|wetland,urban|europe,asia|
Robber fly|insect|Diptera|Asilidae|complete|woodland,grassland|worldwide|predator
Blowfly|insect|Diptera|Calliphoridae|complete|urban,farmland|worldwide|decomposer
Emperor dragonfly|insect|Odonata|Aeshnidae|incomplete|wetland,lake|europe,asia|predator
Southern hawker|insect|Odonata|Aeshnidae|incomplete|wetland,woodland|europe|predator
Common darter|insect|Odonata|Libellulidae|incomplete|wetland,grassland|europe,asia|predator
Globe skimmer|insect|Odonata|Libellulidae|incomplete|wetland,coastal|worldwide|migratory
Banded demoiselle|insect|Odonata|Calopterygidae|incomplete|river|europe,asia|
Beautiful demoiselle|insect|Odonata|Calopterygidae|incomplete|river,woodland|europe,africa|
Blue-tailed damselfly|insect|Odonata|Coenagrionidae|incomplete|wetland|europe,asia|
Migratory locust|insect|Orthoptera|Acrididae|incomplete|grassland,farmland|africa,asia|migratory,pest
Desert locust|insect|Orthoptera|Acrididae|incomplete|desert,grassland|africa,asia|migratory,pest
Field cricket|insect|Orthoptera|Gryllidae|incomplete|grassland,farmland|europe,asia|
House cricket|insect|Orthoptera|Gryllidae|incomplete|urban|asia|singer
Mole cricket|insect|Orthoptera|Gryllotalpidae|incomplete|farmland,wetland|worldwide|burrower
Wart-biter|insect|Orthoptera|Tettigoniidae|incomplete|grassland|europe|
Great green bush-cricket|insect|Orthoptera|Tettigoniidae|incomplete|woodland,grassland|europe|
Katydid|insect|Orthoptera|Tettigoniidae|incomplete|forest|americas|mimic
Praying mantis|insect|Mantodea|Mantidae|incomplete|grassland,urban|worldwide|predator,camouflage
Orchid mantis|insect|Mantodea|Hymenopodidae|incomplete|forest|asia|predator,camouflage
Common stick insect|insect|Phasmatodea|Phasmatidae|incomplete|forest|oceania|camouflage
Giant prickly stick insect|insect|Phasmatodea|Phasmatidae|incomplete|forest|oceania|camouflage
Leaf insect|insect|Phasmatodea|Phylliidae|incomplete|forest|asia|mimic
American cockroach|insect|Blattodea|Blattidae|incomplete|urban|worldwide|pest
German cockroach|insect|Blattodea|Ectobiidae|incomplete|urban|worldwide|pest
Madagascar hissing cockroach|insect|Blattodea|Blaberidae|incomplete|forest|africa|
Common earwig|insect|Dermaptera|Forficulidae|incomplete|urban,farmland|europe,asia|
Aphid|insect|Hemiptera|Aphididae|incomplete|farmland,urban|worldwide|pest
Periodical cicada|insect|Hemiptera|Cicadidae|incomplete|woodland|americas|singer
Bed bug|insect|Hemiptera|Cimicidae|incomplete|urban|worldwide|parasite
Kissing bug|insect|Hemiptera|Reduviidae|incomplete|forest,farmland|americas|parasite
Assassin bug|insect|Hemiptera|Reduviidae|incomplete|woodland,grassland|worldwide|predator
Shield bug|insect|Hemiptera|Pentatomidae|incomplete|woodland,farmland|worldwide|pest
Spotted lanternfly|insect|Hemiptera|Fulgoridae|incomplete|woodland,urban|asia|pest,invasive
Cochineal|insect|Hemiptera|Dactylopiidae|incomplete|desert|americas|dye
Flea|insect|Siphonaptera|Pulicidae|complete|urban|worldwide|parasite
Head louse|insect|Phthiraptera|Pediculidae|incomplete|urban|worldwide|parasite
Silverfish|insect|Zygentoma|Lepismatidae|none|urban|worldwide|
Bristletail|insect|Archaeognatha|Machilidae|none|coastal,woodland|worldwide|
Thrips|insect|Thysanoptera|Thripidae|incomplete|farmland,urban|worldwide|pest
Stonefly|insect|Plecoptera|Perlidae|incomplete|river|worldwide|indicator-species
Garden spider|spider|Araneae|Araneidae|na|woodland,urban|europe,asia|silk
Golden silk orb-weaver|spider|Araneae|Araneidae|na|forest,urban|asia,americas,africa|silk
Black widow|spider|Araneae|Theridiidae|na|desert,urban|americas|venomous,silk
Brown recluse|spider|Araneae|Sicariidae|na|urban,woodland|americas|venomous
Goliath birdeater|spider|Araneae|Theraphosidae|na|forest|americas|predator
Mexican redknee tarantula|spider|Araneae|Theraphosidae|na|desert,forest|americas|predator
Jumping spider|spider|Araneae|Salticidae|na|urban,woodland|worldwide|predator
Wolf spider|spider|Araneae|Lycosidae|na|grassland,woodland|worldwide|predator
Huntsman spider|spider|Araneae|Sparassidae|na|forest,urban|oceania,asia|predator
Harvestman|harvestman|Opiliones|Phalangiidae|na|woodland,urban|worldwide|scavenger
Camel spider|solifuge|Solifugae|Solpugidae|na|desert|africa,asia|predator
Emperor scorpion|scorpion|Scorpiones|Scorpionidae|na|forest,desert|africa|venomous,burrower
Deathstalker|scorpion|Scorpiones|Buthidae|na|desert|africa,asia|venomous
Arizona bark scorpion|scorpion|Scorpiones|Buthidae|na|desert|americas|venomous
Deer tick|tick|Ixodida|Ixodidae|na|woodland,grassland|americas|parasite
Castor bean tick|tick|Ixodida|Ixodidae|na|woodland,grassland|europe,asia|parasite
Varroa destructor|mite|Mesostigmata|Varroidae|na|farmland|worldwide|parasite
House dust mite|mite|Sarcoptiformes|Pyroglyphidae|na|urban|worldwide|allergen
Spider mite|mite|Trombidiformes|Tetranychidae|na|farmland,urban|worldwide|pest
Giant centipede|centipede|Scolopendromorpha|Scolopendridae|na|forest|americas|venomous,predator
House centipede|centipede|Scutigeromorpha|Scutigeridae|na|urban|worldwide|predator
Giant African millipede|millipede|Spirostreptida|Spirostreptidae|na|forest|africa|decomposer
Pill millipede|millipede|Glomerida|Glomeridae|na|woodland|europe|decomposer,roller
Yellow-spotted millipede|millipede|Polydesmida|Xystodesmidae|na|forest|americas|chemical-defence
Common woodlouse|woodlouse|Isopoda|Porcellionidae|na|urban,woodland|worldwide|decomposer
Pill bug|woodlouse|Isopoda|Armadillidiidae|na|woodland,urban|europe|decomposer,roller
Sea slater|woodlouse|Isopoda|Ligiidae|na|coastal|europe|decomposer
Springtail|springtail|Entomobryomorpha|Entomobryidae|none|woodland,farmland|worldwide|decomposer
Snow flea|springtail|Poduromorpha|Hypogastruridae|none|alpine,woodland|worldwide|cold-tolerant
Velvet worm|velvet-worm|Onychophora|Peripatidae|na|forest|americas|predator
"""


def slug(text):
    text = text.lower()
    for a, b in (("ā", "a"), ("ō", "o"), ("ū", "u"), ("é", "e"), ("á", "a"), ("í", "i"),
                 ("ó", "o"), ("ñ", "n"), ("ü", "u")):
        text = text.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def fetch(url, tries=5):
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=45) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 500, 502, 503, 504) and attempt < tries - 1:
                time.sleep(7 * (attempt + 1))
                continue
            return {"__error__": "HTTP %s" % exc.code}
        except Exception as exc:  # noqa: BLE001
            if attempt < tries - 1:
                time.sleep(3 * (attempt + 1))
                continue
            return {"__error__": str(exc)}
    return {"__error__": "gave up"}


def clean_extract(text):
    text = re.sub(r"\s*\((?=[^)]*(?:ˈ|ˌ|ə|ʉ|ɨ|/|-[⁠\u2060]))[^)]*\)", "", text)
    text = re.sub(r"\s{2,}", " ", text).strip()
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z(])", text)
    out = " ".join(parts[:2]).strip()
    if len(out) > 330:
        out = out[:327].rsplit(" ", 1)[0] + "…"
    return out


def image_url(thumb):
    if not thumb:
        return None
    url = thumb.split("?utm_source")[0].replace("https://thumb.wikimedia.org", "https://upload.wikimedia.org")
    return re.sub(r"/\d+px-", "/500px-", url, count=1)


def file_page(img_url):
    if not img_url:
        return None
    return "https://commons.wikimedia.org/wiki/File:" + re.sub(r"^\d+px-", "", img_url.rsplit("/", 1)[-1])


def gather(row):
    page = row["title"].replace(" ", "_")
    summary = fetch("https://en.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(page))
    if "__error__" in summary or summary.get("type") in ("disambiguation", "no-extract"):
        return row, None, summary.get("__error__", summary.get("type", "missing"))
    return row, summary, None


def wikidata(qids):
    status, taxon = {}, {}
    for start in range(0, len(qids), 40):
        batch = qids[start:start + 40]
        query = """
SELECT ?item ?taxon ?statusLabel WHERE {
  VALUES ?item { %s }
  OPTIONAL { ?item wdt:P141 ?status }
  OPTIONAL { ?item wdt:P225 ?taxon }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}""" % " ".join("wd:" + q for q in batch)
        data = fetch("https://query.wikidata.org/sparql?" +
                     urllib.parse.urlencode({"format": "json", "query": query}))
        for binding in data.get("results", {}).get("bindings", []):
            qid = binding["item"]["value"].rsplit("/", 1)[-1]
            if "statusLabel" in binding:
                status.setdefault(qid, binding["statusLabel"]["value"])
            if "taxon" in binding and " " in binding["taxon"]["value"]:
                taxon.setdefault(qid, binding["taxon"]["value"])
    return status, taxon


def spec_rows():
    rows = []
    for line in SPEC.strip().splitlines():
        bits = [b.strip() for b in line.split("|")]
        if len(bits) < 5:
            continue
        bits += [""] * (8 - len(bits))
        rows.append({
            "title": bits[0], "grp": bits[1], "order": bits[2], "family": bits[3],
            "meta": bits[4],
            "habitats": [h for h in bits[5].split(",") if h],
            "regions": [r for r in bits[6].split(",") if r],
            "roles": [r for r in bits[7].split(",") if r],
        })
    return rows


def main():
    rows = spec_rows()
    print("spec rows:", len(rows))

    resolved, failed = [], []
    with ThreadPoolExecutor(max_workers=3) as pool:
        for row, summary, error in pool.map(gather, rows):
            if not summary:
                failed.append((row, error))
                print("  !", row["title"], "->", error)
                continue
            resolved.append((row, summary))
            print("  +", row["title"])
            time.sleep(0.2)

    for round_ in range(3):
        if not failed:
            break
        print("retry round", round_ + 1, "for", len(failed))
        still = []
        for row, _error in failed:
            time.sleep(4)
            row2, summary, error = gather(row)
            if summary:
                resolved.append((row2, summary))
                print("  +", row["title"])
            else:
                still.append((row, error))
        failed = still
    print("resolved:", len(resolved), "failed:", len(failed))
    if failed:
        print("missing:", [row["title"] for row, _ in failed])

    qids = [summary.get("wikibase_item") for _, summary in resolved if summary.get("wikibase_item")]
    status, taxon = wikidata(qids) if qids else ({}, {})

    orders, seen = {}, set()
    for row, summary in resolved:
        url = (summary.get("content_urls", {}).get("desktop", {}).get("page")
               or "https://en.wikipedia.org/wiki/" + urllib.parse.quote(row["title"].replace(" ", "_")))
        if url in seen:
            continue
        seen.add(url)
        qid = summary.get("wikibase_item")
        entry = {
            "n": summary.get("title") or row["title"],
            "s": taxon.get(qid, "") if qid else "",
            "u": url,
            "d": clean_extract(summary.get("extract") or ""),
            "h": row["habitats"], "r": row["regions"], "t": row["roles"],
            "m": row["meta"],
            "fam": row["family"], "ord": row["order"], "grp": row["grp"],
        }
        if not entry["s"]:
            binomial = re.search(r"\(([A-Z][a-z]+ [a-z-]+)\)", summary.get("extract") or "")
            if binomial:
                entry["s"] = binomial.group(1)
        thumb = image_url((summary.get("thumbnail") or {}).get("source"))
        if thumb:
            entry["i"] = thumb
            entry["ic"] = file_page(thumb)
        if qid and qid in status:
            entry["st"] = status[qid]
        orders.setdefault(row["order"], {}).setdefault(row["family"], []).append(entry)

    os.makedirs(OUT, exist_ok=True)
    facets = {"group": {}, "metamorphosis": {}, "habitat": {}, "region": {}, "role": {}, "status": {}}
    sections = []
    total = photos = statuses = 0
    for order in sorted(orders, key=lambda o: (-sum(len(v) for v in orders[o].values()), o)):
        families = orders[order]
        beings = [b for fam in families.values() for b in fam]
        key = slug(order)
        with open(os.path.join(OUT, key + ".json"), "w", encoding="utf-8") as fh:
            json.dump({"key": key, "title": order, "families": [
                {"n": fam, "c": len(families[fam]), "s": sorted(families[fam], key=lambda b: b["n"])}
                for fam in sorted(families, key=lambda f: (-len(families[f]), f))
            ]}, fh, ensure_ascii=False, indent=1)
        total += len(beings)
        photos += sum(1 for b in beings if b.get("i"))
        statuses += sum(1 for b in beings if b.get("st"))
        for being in beings:
            facets["group"][being["grp"]] = facets["group"].get(being["grp"], 0) + 1
            facets["metamorphosis"][being["m"]] = facets["metamorphosis"].get(being["m"], 0) + 1
            for value in being["h"]:
                facets["habitat"][value] = facets["habitat"].get(value, 0) + 1
            for value in being["r"]:
                facets["region"][value] = facets["region"].get(value, 0) + 1
            for value in being["t"]:
                facets["role"][value] = facets["role"].get(value, 0) + 1
            if being.get("st"):
                facets["status"][being["st"]] = facets["status"].get(being["st"], 0) + 1
        sections.append({"key": key, "num": "%02d" % (len(sections) + 1), "title": order,
                         "beings": len(beings), "families": len(families),
                         "photos": sum(1 for b in beings if b.get("i"))})

    index = {
        "generated": time.strftime("%Y-%m-%d"),
        "source": "en.wikipedia.org + wikidata.org",
        "beings": total,
        "families": len({b["fam"] for fam in orders.values() for f in fam.values() for b in f}),
        "orders": len(orders),
        "groups": len({b["grp"] for fam in orders.values() for f in fam.values() for b in f}),
        "photos": photos,
        "statuses": statuses,
        "facets": facets,
        "sections": sections,
    }
    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as fh:
        json.dump(index, fh, ensure_ascii=False, indent=1)
    print(json.dumps({k: index[k] for k in ("beings", "families", "orders", "groups",
                                            "photos", "statuses")}))
    print("groups:", index["facets"]["group"])
    print("metamorphosis:", index["facets"]["metamorphosis"])


if __name__ == "__main__":
    main()
