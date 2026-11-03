#!/usr/bin/env python3
"""Build docs/plants/data/ — the plant catalogue behind docs/plantsIndex.html.

Fetched, never typed: photograph, introduction, binomial, conservation status.
Written by hand: order, family, habitats, regions, form.

Edibility is not written by hand either. Each card is classified from the words
the encyclopaedia uses about eating the plant ("edible", "cooked", "poisonous",
"deadly"), and the sentence that decided the verdict is stored with it, so the
page can always show the evidence beside the answer.

Fungi are not plants and are not here.
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
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

UA = {"User-Agent": "devblog-plants/1.0 (https://blog.odicforcesounds.com; contact via site)"}
OUT = "docs/plants/data"

# title | order | family | habitats | regions | form
SPEC = """
Apple|Rosales|Rosaceae|farmland,woodland|europe,asia|tree
Pear|Rosales|Rosaceae|farmland,woodland|europe,asia|tree
Plum|Rosales|Rosaceae|farmland,woodland|europe,asia|tree
Cherry|Rosales|Rosaceae|farmland,woodland|europe,asia,americas|tree
Peach|Rosales|Rosaceae|farmland|asia|tree
Almond|Rosales|Rosaceae|farmland,desert|asia,europe,africa|tree
Strawberry|Rosales|Rosaceae|farmland,woodland|worldwide|herb
Raspberry|Rosales|Rosaceae|woodland,alpine|europe,asia,americas|shrub
Blackberry|Rosales|Rosaceae|woodland,farmland|worldwide|climber
Rose|Rosales|Rosaceae|woodland,farmland,urban|worldwide|shrub
Common hawthorn|Rosales|Rosaceae|woodland,farmland|europe,asia|shrub
Rowan|Rosales|Rosaceae|forest,alpine|europe,asia|tree
Quince|Rosales|Rosaceae|farmland|asia,europe|tree
Apricot|Rosales|Rosaceae|farmland|asia,europe|tree
Loquat|Rosales|Rosaceae|woodland,farmland|asia|tree
Medlar|Rosales|Rosaceae|woodland,farmland|europe,asia|tree
European crab apple|Rosales|Rosaceae|woodland|europe|tree
Prunus spinosa|Rosales|Rosaceae|woodland,farmland|europe,asia|shrub
Cherry laurel|Rosales|Rosaceae|woodland,urban|europe,asia|shrub
Cannabis|Rosales|Cannabaceae|farmland,grassland|asia|herb
Hop|Rosales|Cannabaceae|wetland,farmland|europe,asia,americas|climber
Common fig|Rosales|Moraceae|farmland,urban|africa,asia,europe|tree
Mulberry|Rosales|Moraceae|farmland,urban|asia,americas|tree
Breadfruit|Rosales|Moraceae|forest,farmland|oceania,asia|tree
Jackfruit|Rosales|Moraceae|forest,farmland|asia|tree
Urtica dioica|Rosales|Urticaceae|woodland,farmland,urban|worldwide|herb
Pedunculate oak|Fagales|Fagaceae|forest,woodland|europe,asia|tree
Cork oak|Fagales|Fagaceae|woodland|europe,africa|tree
European beech|Fagales|Fagaceae|forest|europe,asia|tree
Sweet chestnut|Fagales|Fagaceae|forest,farmland|europe,asia|tree
English walnut|Fagales|Juglandaceae|farmland,woodland|europe,asia,americas|tree
Hazel|Fagales|Betulaceae|woodland|europe,asia|shrub
Silver birch|Fagales|Betulaceae|forest,alpine|europe,asia|tree
Black alder|Fagales|Betulaceae|wetland|europe,asia|tree
Shagbark hickory|Fagales|Juglandaceae|forest|americas|tree
Pecan|Fagales|Juglandaceae|farmland|americas|tree
Sweet orange|Sapindales|Rutaceae|farmland|asia,americas,africa|tree
Lemon|Sapindales|Rutaceae|farmland|asia,europe|tree
Lime (fruit)|Sapindales|Rutaceae|farmland|asia|tree
Grapefruit|Sapindales|Rutaceae|farmland|americas|tree
Mandarin orange|Sapindales|Rutaceae|farmland|asia|tree
Kumquat|Sapindales|Rutaceae|farmland,urban|asia|shrub
Mango|Sapindales|Anacardiaceae|farmland,forest|asia,americas,africa|tree
Cashew|Sapindales|Anacardiaceae|farmland|americas,africa,asia|tree
Pistachio|Sapindales|Anacardiaceae|desert,farmland|asia,europe|tree
Poison ivy|Sapindales|Anacardiaceae|woodland|americas|climber
Lychee|Sapindales|Sapindaceae|farmland|asia|tree
Rambutan|Sapindales|Sapindaceae|farmland|asia|tree
Sugar maple|Sapindales|Sapindaceae|forest|americas|tree
Acer pseudoplatanus|Sapindales|Sapindaceae|forest,urban|europe,asia|tree
Aesculus hippocastanum|Sapindales|Sapindaceae|woodland,urban|europe,asia|tree
Neem|Sapindales|Meliaceae|woodland,farmland|asia,africa|tree
Frankincense|Sapindales|Burseraceae|desert|africa,asia|tree
Cacao|Malvales|Malvaceae|forest,farmland|americas,africa|tree
Durian|Malvales|Malvaceae|forest,farmland|asia|tree
Okra|Malvales|Malvaceae|farmland|africa,asia,americas|herb
Cotton|Malvales|Malvaceae|farmland|worldwide|shrub
Hibiscus|Malvales|Malvaceae|woodland,urban|asia,africa|shrub
Adansonia digitata|Malvales|Malvaceae|desert,grassland|africa|tree
Tilia|Malvales|Malvaceae|forest,urban|europe,asia|tree
Eucalyptus|Myrtales|Myrtaceae|forest,woodland|oceania|tree
Guava|Myrtales|Myrtaceae|farmland,woodland|americas|tree
Clove|Myrtales|Myrtaceae|forest,farmland|asia,africa|tree
Pomegranate|Myrtales|Lythraceae|farmland,desert|asia,africa,europe|shrub
Allspice|Myrtales|Myrtaceae|forest|americas|tree
Cabbage|Brassicales|Brassicaceae|farmland|europe,asia|herb
Broccoli|Brassicales|Brassicaceae|farmland|europe|herb
Kale|Brassicales|Brassicaceae|farmland|europe|herb
Brussels sprout|Brassicales|Brassicaceae|farmland|europe|herb
Radish|Brassicales|Brassicaceae|farmland|asia,europe|herb
Brassica nigra|Brassicales|Brassicaceae|farmland|europe,asia,africa|herb
Turnip|Brassicales|Brassicaceae|farmland|europe,asia|herb
Arabidopsis thaliana|Brassicales|Brassicaceae|grassland,urban|europe,asia,africa|herb
Papaya|Brassicales|Caricaceae|farmland|americas,africa|tree
Caper|Brassicales|Capparaceae|desert,woodland|europe,africa,asia|shrub
Horseradish|Brassicales|Brassicaceae|farmland|europe,asia|herb
Wasabi|Brassicales|Brassicaceae|wetland,forest|asia|herb
Watercress|Brassicales|Brassicaceae|wetland|worldwide|herb
Tomato|Solanales|Solanaceae|farmland|americas,worldwide|herb
Potato|Solanales|Solanaceae|farmland,alpine|americas,worldwide|herb
Aubergine|Solanales|Solanaceae|farmland|asia,africa|herb
Capsicum annuum|Solanales|Solanaceae|farmland|americas|herb
Capsicum chinense|Solanales|Solanaceae|farmland|americas|herb
Atropa belladonna|Solanales|Solanaceae|woodland|europe,asia,africa|herb
Nicotiana tabacum|Solanales|Solanaceae|farmland|americas|herb
Petunia|Solanales|Solanaceae|grassland,urban|americas|herb
Mandragora officinarum|Solanales|Solanaceae|grassland,desert|europe,asia|herb
Datura stramonium|Solanales|Solanaceae|farmland,urban|worldwide|herb
Sweet potato|Solanales|Convolvulaceae|farmland|americas,asia,africa|climber
Ipomoea purpurea|Solanales|Convolvulaceae|farmland,urban|americas|climber
Peppermint|Lamiales|Lamiaceae|wetland,farmland|europe,asia|herb
Basil|Lamiales|Lamiaceae|farmland,urban|asia,africa|herb
Rosemary|Lamiales|Lamiaceae|coastal,woodland|europe,africa|shrub
Salvia officinalis|Lamiales|Lamiaceae|grassland,urban|europe,africa|herb
Thyme|Lamiales|Lamiaceae|grassland,alpine|europe,asia,africa|herb
Oregano|Lamiales|Lamiaceae|grassland,alpine|europe,asia|herb
Lavender|Lamiales|Lamiaceae|grassland,alpine|europe,africa|shrub
Olive|Lamiales|Oleaceae|farmland,desert|europe,africa,asia|tree
Fraxinus excelsior|Lamiales|Oleaceae|forest,urban|europe,asia|tree
Jasminum officinale|Lamiales|Oleaceae|woodland,urban|asia|climber
Digitalis purpurea|Lamiales|Plantaginaceae|woodland,alpine|europe,africa|herb
Antirrhinum majus|Lamiales|Plantaginaceae|woodland,urban|europe,africa|herb
Sesame|Lamiales|Pedaliaceae|farmland,grassland|africa,asia|herb
Sunflower|Asterales|Asteraceae|farmland,grassland|americas|herb
Lettuce|Asterales|Asteraceae|farmland|europe,asia|herb
Globe artichoke|Asterales|Asteraceae|grassland,farmland|europe,africa|herb
Chicory|Asterales|Asteraceae|grassland,farmland|europe,asia,africa|herb
Dandelion|Asterales|Asteraceae|grassland,urban|worldwide|herb
German chamomile|Asterales|Asteraceae|farmland,grassland|europe,asia|herb
Chrysanthemum|Asterales|Asteraceae|grassland,urban|asia|herb
Leucanthemum vulgare|Asterales|Asteraceae|grassland,farmland|europe,asia|herb
Ambrosia artemisiifolia|Asterales|Asteraceae|farmland,urban|americas,europe|herb
Stevia rebaudiana|Asterales|Asteraceae|grassland|americas|herb
Helianthus tuberosus|Asterales|Asteraceae|farmland,grassland|americas|herb
Achillea millefolium|Asterales|Asteraceae|grassland,alpine|europe,asia,americas|herb
Carrot|Apiales|Apiaceae|farmland|europe,asia|herb
Parsley|Apiales|Apiaceae|farmland,urban|europe,asia|herb
Celery|Apiales|Apiaceae|wetland,farmland|europe,asia|herb
Parsnip|Apiales|Apiaceae|farmland|europe,asia|herb
Fennel|Apiales|Apiaceae|coastal,grassland|europe,asia,africa|herb
Dill|Apiales|Apiaceae|farmland,grassland|asia,africa|herb
Coriander|Apiales|Apiaceae|farmland|asia,europe|herb
Cumin|Apiales|Apiaceae|farmland,desert|asia|herb
Conium maculatum|Apiales|Apiaceae|wetland,urban|europe,asia,africa|herb
Ginseng|Apiales|Araliaceae|forest|asia,americas|herb
Hedera helix|Apiales|Araliaceae|woodland,urban|europe,asia|climber
Heracleum mantegazzianum|Apiales|Apiaceae|wetland,urban|europe|herb
Pea|Fabales|Fabaceae|farmland|asia,europe|climber
Common bean|Fabales|Fabaceae|farmland|americas|climber
Lentil|Fabales|Fabaceae|farmland|asia,africa|herb
Chickpea|Fabales|Fabaceae|farmland|asia,africa|herb
Soybean|Fabales|Fabaceae|farmland|asia,americas|herb
Peanut|Fabales|Fabaceae|farmland|americas|herb
Alfalfa|Fabales|Fabaceae|farmland,grassland|asia,europe|herb
White clover|Fabales|Fabaceae|grassland,farmland|europe,asia,americas|herb
Acacia|Fabales|Fabaceae|desert,woodland|africa,oceania,asia|tree
Liquorice|Fabales|Fabaceae|farmland,desert|asia,europe|herb
Lupinus|Fabales|Fabaceae|grassland,farmland|americas,europe|herb
Robinia pseudoacacia|Fabales|Fabaceae|woodland,urban|americas|tree
Cucumber|Cucurbitales|Cucurbitaceae|farmland|asia|climber
Melon|Cucurbitales|Cucurbitaceae|farmland|asia,africa|climber
Watermelon|Cucurbitales|Cucurbitaceae|farmland|africa|climber
Pumpkin|Cucurbitales|Cucurbitaceae|farmland|americas|climber
Squash (plant)|Cucurbitales|Cucurbitaceae|farmland|americas|climber
Zucchini|Cucurbitales|Cucurbitaceae|farmland|americas|climber
Momordica charantia|Cucurbitales|Cucurbitaceae|farmland,forest|asia,africa|climber
Begonia|Cucurbitales|Begoniaceae|forest,urban|americas,asia,africa|herb
Grape|Vitales|Vitaceae|farmland,woodland|worldwide|climber
Ginger|Zingiberales|Zingiberaceae|forest,farmland|asia|herb
Turmeric|Zingiberales|Zingiberaceae|forest,farmland|asia|herb
Cardamom|Zingiberales|Zingiberaceae|forest|asia|herb
Banana|Zingiberales|Musaceae|farmland,forest|asia,africa,americas|herb
Plantain (fruit)|Zingiberales|Musaceae|farmland|africa,americas|herb
Strelitzia|Zingiberales|Strelitziaceae|coastal,urban|africa|herb
Canna|Zingiberales|Cannaceae|wetland,urban|americas|herb
Onion|Asparagales|Amaryllidaceae|farmland|asia,europe|herb
Garlic|Asparagales|Amaryllidaceae|farmland|asia|herb
Leek|Asparagales|Amaryllidaceae|farmland|europe,africa|herb
Asparagus|Asparagales|Asparagaceae|grassland,coastal|europe,asia|herb
Vanilla|Asparagales|Orchidaceae|forest,farmland|americas,africa|climber
Agave|Asparagales|Asparagaceae|desert|americas|succulent
Hyacinth|Asparagales|Asparagaceae|grassland,urban|asia,europe|bulb
Crocus sativus|Asparagales|Iridaceae|grassland|asia,europe|bulb
Aloe vera|Asparagales|Asphodelaceae|desert,urban|africa,asia|succulent
Convallaria majalis|Asparagales|Asparagaceae|woodland,urban|europe,asia|herb
Lilium lancifolium|Liliales|Liliaceae|woodland,farmland|asia|bulb
Tulip|Liliales|Liliaceae|grassland,urban|asia,europe|bulb
Colchicum autumnale|Liliales|Colchicaceae|grassland,wetland|europe|bulb
Bread wheat|Poales|Poaceae|farmland|worldwide|grass
Rice|Poales|Poaceae|wetland,farmland|asia,africa,americas|grass
Maize|Poales|Poaceae|farmland|americas|grass
Barley|Poales|Poaceae|farmland,grassland|europe,asia,africa|grass
Oat|Poales|Poaceae|farmland|europe,asia|grass
Rye|Poales|Poaceae|farmland|europe,asia|grass
Sugarcane|Poales|Poaceae|farmland|asia,americas,africa|grass
Bamboo|Poales|Poaceae|forest,farmland|asia,americas,africa|grass
Pineapple|Poales|Bromeliaceae|farmland|americas|herb
Papyrus|Poales|Cyperaceae|wetland|africa|grass
Cymbopogon citratus|Poales|Poaceae|grassland,farmland|asia|grass
Coconut|Arecales|Arecaceae|coastal,farmland|asia,oceania,americas|tree
Date palm|Arecales|Arecaceae|desert,farmland|africa,asia|tree
Oil palm|Arecales|Arecaceae|forest,farmland|africa,asia|tree
Areca catechu|Arecales|Arecaceae|farmland|asia|tree
Black pepper|Piperales|Piperaceae|forest,farmland|asia|climber
Kava|Piperales|Piperaceae|forest,farmland|oceania|shrub
Aristolochia|Piperales|Aristolochiaceae|woodland,urban|worldwide|climber
Avocado|Laurales|Lauraceae|farmland,forest|americas|tree
Cinnamomum verum|Laurales|Lauraceae|forest,farmland|asia|tree
Laurus nobilis|Laurales|Lauraceae|woodland,urban|europe,africa,asia|tree
Sassafras|Laurales|Lauraceae|forest|americas|tree
Nutmeg|Magnoliales|Myristicaceae|forest,farmland|asia|tree
Magnolia|Magnoliales|Magnoliaceae|forest,urban|asia,americas|tree
Cherimoya|Magnoliales|Annonaceae|farmland,forest|americas|tree
Soursop|Magnoliales|Annonaceae|farmland,forest|americas,africa|tree
Papaver somniferum|Ranunculales|Papaveraceae|farmland|europe,asia|herb
Papaver rhoeas|Ranunculales|Papaveraceae|farmland,grassland|europe,asia|herb
Ranunculus|Ranunculales|Ranunculaceae|wetland,grassland|worldwide|herb
Aconitum napellus|Ranunculales|Ranunculaceae|alpine,woodland|europe|herb
Aquilegia|Ranunculales|Ranunculaceae|woodland,alpine|europe,asia,americas|herb
Berberis vulgaris|Ranunculales|Berberidaceae|woodland,farmland|europe,asia|shrub
Beetroot|Caryophyllales|Amaranthaceae|farmland|europe,africa|herb
Spinach|Caryophyllales|Amaranthaceae|farmland|asia,europe|herb
Quinoa|Caryophyllales|Amaranthaceae|alpine,farmland|americas|herb
Amaranthus|Caryophyllales|Amaranthaceae|farmland,urban|worldwide|herb
Opuntia|Caryophyllales|Cactaceae|desert|americas|succulent
Carnation|Caryophyllales|Caryophyllaceae|grassland,urban|europe,asia|herb
Venus flytrap|Caryophyllales|Droseraceae|wetland|americas|herb
Drosera|Caryophyllales|Droseraceae|wetland|worldwide|herb
Bougainvillea|Caryophyllales|Nyctaginaceae|urban,coastal|americas|climber
Rhubarb|Caryophyllales|Polygonaceae|farmland,alpine|asia,europe|herb
Buckwheat|Caryophyllales|Polygonaceae|farmland|asia,europe|herb
Tea|Ericales|Theaceae|farmland,forest|asia,africa|shrub
Blueberry|Ericales|Ericaceae|woodland,alpine|americas|shrub
Cranberry|Ericales|Ericaceae|wetland|americas,europe|shrub
Rhododendron|Ericales|Ericaceae|alpine,woodland|asia,europe,americas|shrub
Azalea|Ericales|Ericaceae|woodland,urban|asia,americas|shrub
Kiwifruit|Ericales|Actinidiaceae|forest,farmland|asia|climber
Persimmon|Ericales|Ebenaceae|farmland,woodland|asia,americas|tree
Brazil nut|Ericales|Lecythidaceae|forest|americas|tree
Sarracenia|Ericales|Sarraceniaceae|wetland|americas|herb
Cassava|Malpighiales|Euphorbiaceae|farmland|americas,africa,asia|shrub
Hevea brasiliensis|Malpighiales|Euphorbiaceae|forest,farmland|americas,asia|tree
Ricinus communis|Malpighiales|Euphorbiaceae|farmland,urban|africa,asia|shrub
Flax|Malpighiales|Linaceae|farmland|europe,asia|herb
Salix alba|Malpighiales|Salicaceae|wetland|europe,asia|tree
Passiflora edulis|Malpighiales|Passifloraceae|forest,farmland|americas|climber
Hypericum perforatum|Malpighiales|Hypericaceae|grassland,woodland|europe,asia,africa|herb
Poinsettia|Malpighiales|Euphorbiaceae|forest,urban|americas|shrub
Pelargonium|Geraniales|Geraniaceae|grassland,urban|africa|herb
Macadamia|Proteales|Proteaceae|forest,farmland|oceania|tree
Nelumbo nucifera|Proteales|Nelumbonaceae|wetland|asia,oceania|aquatic
Platanus|Proteales|Platanaceae|urban,wetland|europe,americas|tree
Viscum album|Santalales|Viscaceae|woodland|europe,asia|shrub
Averrhoa carambola|Oxalidales|Oxalidaceae|farmland|asia|tree
Cornus florida|Cornales|Cornaceae|forest,urban|americas|tree
Sambucus nigra|Dipsacales|Adoxaceae|woodland,urban|europe,asia,africa|shrub
Lonicera|Dipsacales|Caprifoliaceae|woodland,urban|europe,asia,americas|climber
Viburnum opulus|Dipsacales|Adoxaceae|woodland,wetland|europe,asia|shrub
Ilex aquifolium|Aquifoliales|Aquifoliaceae|woodland,urban|europe,africa|tree
Coffea arabica|Gentianales|Rubiaceae|forest,farmland|africa,americas,asia|shrub
Cinchona|Gentianales|Rubiaceae|forest|americas|tree
Nerium oleander|Gentianales|Apocynaceae|wetland,urban|europe,asia,africa|shrub
Plumeria|Gentianales|Apocynaceae|urban,coastal|americas|tree
Catharanthus roseus|Gentianales|Apocynaceae|coastal,urban|africa|herb
Asclepias|Gentianales|Apocynaceae|grassland,farmland|americas|herb
Gardenia|Gentianales|Rubiaceae|forest,urban|asia,africa,oceania|shrub
Borago officinalis|Boraginales|Boraginaceae|farmland,urban|europe,africa|herb
Symphytum|Boraginales|Boraginaceae|farmland,wetland|europe,asia|herb
Taro|Alismatales|Araceae|wetland,farmland|asia,oceania,africa|herb
Monstera deliciosa|Alismatales|Araceae|forest,urban|americas|climber
Lemna|Alismatales|Araceae|wetland|worldwide|aquatic
Zantedeschia aethiopica|Alismatales|Araceae|wetland,urban|africa|herb
Arum maculatum|Alismatales|Araceae|woodland|europe|herb
Yam|Dioscoreales|Dioscoreaceae|farmland,forest|africa,asia,americas|climber
Nymphaea alba|Nymphaeales|Nymphaeaceae|wetland|europe,asia,africa|aquatic
Scots pine|Pinales|Pinaceae|forest,alpine|europe,asia|conifer
Norway spruce|Pinales|Pinaceae|forest,alpine|europe|conifer
Taxus baccata|Pinales|Taxaceae|woodland,urban|europe,africa,asia|conifer
Juniperus communis|Pinales|Cupressaceae|alpine,grassland|europe,asia,americas|conifer
Ginkgo biloba|Ginkgoales|Ginkgoaceae|urban|asia|tree
Cycas revoluta|Cycadales|Cycadaceae|coastal,urban|asia|shrub
Bracken|Polypodiales|Dennstaedtiaceae|woodland,grassland|worldwide|fern
Dryopteris filix-mas|Polypodiales|Dryopteridaceae|forest,woodland|europe,asia,americas|fern
Equisetum arvense|Equisetales|Equisetaceae|wetland,farmland|europe,asia,americas|herb
Sphagnum|Sphagnales|Sphagnaceae|wetland|worldwide|moss
"""

FOOD_CUE = re.compile(r"\b(edible|culinary|eaten|cooked|eatable|food crop|cash crop|staple|vegetable|"
                      r"spice|herb|flavou?ring|eaten raw|eaten fresh|used as food|source of food)\b", re.I)
TOXIC_CUE = re.compile(r"\b(poisonous|toxic|inedible|unpalatable|not edible|harmful|dangerous)\b", re.I)
DEADLY_CUE = re.compile(r"\b(deadly|lethal|fatal|highly toxic|extremely toxic|death)\b", re.I)
COOKED_CUE = re.compile(r"\b(must be cooked|needs? cooking|boiled|roasted|detoxif|leach|processed before|"
                        r"after (?:cooking|boiling|soaking))\b", re.I)
MED_CUE = re.compile(r"\b(medicinal|medicine|herbal|pharmacolog|traditional remedy|used to treat)\b", re.I)

SENTENCES = re.compile(r"(?<=[.!?])\s+(?=[A-Z(])")


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
                time.sleep(6 * (attempt + 1))
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
    parts = SENTENCES.split(text)
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
    name = re.sub(r"^\d+px-", "", img_url.rsplit("/", 1)[-1])
    return "https://commons.wikimedia.org/wiki/File:" + name


def edibility(extract):
    """Classify what the article says about eating the plant, with the evidence."""
    if not extract:
        return "none", ""
    sentences = [s.strip() for s in SENTENCES.split(extract) if s.strip()]

    def first(cue):
        for sentence in sentences:
            if cue.search(sentence):
                return sentence[:240]
        return ""

    toxic_sentence = first(TOXIC_CUE)
    deadly_sentence = first(DEADLY_CUE)
    food_sentence = first(FOOD_CUE)
    cooked_sentence = first(COOKED_CUE)
    med_sentence = first(MED_CUE)

    if deadly_sentence:
        return "deadly", deadly_sentence
    if toxic_sentence and food_sentence:
        return "mixed", toxic_sentence
    if toxic_sentence:
        return "toxic", toxic_sentence
    if food_sentence and cooked_sentence:
        return "cooked", cooked_sentence
    if food_sentence:
        return "eaten", food_sentence
    if med_sentence:
        return "medicine", med_sentence
    return "none", sentences[0][:240] if sentences else ""


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
        if len(bits) < 3:
            continue
        bits += [""] * (6 - len(bits))
        rows.append({
            "title": bits[0], "order": bits[1], "family": bits[2],
            "habitats": [h for h in bits[3].split(",") if h],
            "regions": [r for r in bits[4].split(",") if r],
            "forms": [f for f in bits[5].split(",") if f],
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
            time.sleep(0.25)

    # polite second pass, one at a time, for anything the rate limit took
    for _ in range(2):
        if not failed:
            break
        print("retrying", len(failed), "missing plants")
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

    orders = {}
    seen = set()
    for row, summary in resolved:
        url = (summary.get("content_urls", {}).get("desktop", {}).get("page")
               or "https://en.wikipedia.org/wiki/" + urllib.parse.quote(row["title"].replace(" ", "_")))
        if url in seen:          # redirects can land two names on one article
            continue
        seen.add(url)
        entry = {
            "n": summary.get("title") or row["title"],
            "u": url,
            "d": clean_extract(summary.get("extract") or ""),
            "h": row["habitats"],
            "r": row["regions"],
            "t": row["forms"],
            "fam": row["family"],
            "ord": row["order"],
        }
        thumb = image_url((summary.get("thumbnail") or {}).get("source"))
        if thumb:
            entry["i"] = thumb
            entry["ic"] = file_page(thumb)
        verdict, evidence = edibility(summary.get("extract") or "")
        entry["ed"] = verdict
        if evidence:
            entry["eq"] = evidence
        orders.setdefault(row["order"], {}).setdefault(row["family"], []).append(entry)

    qids = [summary.get("wikibase_item") for _, summary in resolved if summary.get("wikibase_item")]
    status, taxon = wikidata(qids) if qids else ({}, {})
    for row, summary in resolved:
        qid = summary.get("wikibase_item")
        for family in orders.get(row["order"], {}).values():
            for entry in family:
                if entry["u"] != (summary.get("content_urls", {}).get("desktop", {}).get("page")
                                  or "https://en.wikipedia.org/wiki/" + urllib.parse.quote(row["title"].replace(" ", "_"))):
                    continue
                if qid and qid in taxon:
                    entry["s"] = taxon[qid]
                if not entry.get("s"):
                    binomial = re.search(r"\(([A-Z][a-z]+ [a-z-]+)\)", summary.get("extract") or "")
                    if binomial:
                        entry["s"] = binomial.group(1)
                if qid and qid in status:
                    entry["st"] = status[qid]

    os.makedirs(OUT, exist_ok=True)
    facets = {"edibility": {}, "habitat": {}, "region": {}, "form": {}, "status": {}}
    groups = []
    total = photos = statuses = 0
    for order in sorted(orders, key=lambda o: (-sum(len(v) for v in orders[o].values()), o)):
        families = orders[order]
        plants = [p for fam in families.values() for p in fam]
        key = slug(order)
        payload = {"key": key, "title": order, "families": [
            {"n": fam, "c": len(families[fam]), "s": sorted(families[fam], key=lambda p: p["n"])}
            for fam in sorted(families, key=lambda f: (-len(families[f]), f))
        ]}
        with open(os.path.join(OUT, key + ".json"), "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=1)
        total += len(plants)
        photos += sum(1 for p in plants if p.get("i"))
        statuses += sum(1 for p in plants if p.get("st"))
        for plant in plants:
            facets["edibility"][plant["ed"]] = facets["edibility"].get(plant["ed"], 0) + 1
            for value in plant["h"]:
                facets["habitat"][value] = facets["habitat"].get(value, 0) + 1
            for value in plant["r"]:
                facets["region"][value] = facets["region"].get(value, 0) + 1
            for value in plant["t"]:
                facets["form"][value] = facets["form"].get(value, 0) + 1
            if plant.get("st"):
                facets["status"][plant["st"]] = facets["status"].get(plant["st"], 0) + 1
        groups.append({"key": key, "num": "%02d" % (len(groups) + 1), "title": order,
                       "plants": len(plants), "families": len(families),
                       "photos": sum(1 for p in plants if p.get("i")),
                       "food": sum(1 for p in plants if p["ed"] in ("eaten", "cooked")),
                       "poison": sum(1 for p in plants if p["ed"] in ("toxic", "deadly", "mixed"))})

    index = {
        "generated": time.strftime("%Y-%m-%d"),
        "source": "en.wikipedia.org + wikidata.org",
        "plants": total,
        "families": len({p["fam"] for fam in orders.values() for f in fam.values() for p in f}),
        "orders": len(orders),
        "photos": photos,
        "statuses": statuses,
        "edible": sum(1 for fam in orders.values() for f in fam.values() for p in f if p["ed"] in ("eaten", "cooked")),
        "poisonous": sum(1 for fam in orders.values() for f in fam.values() for p in f if p["ed"] in ("toxic", "deadly", "mixed")),
        "facets": facets,
        "groups": groups,
    }
    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as fh:
        json.dump(index, fh, ensure_ascii=False, indent=1)
    print(json.dumps({k: index[k] for k in ("plants", "families", "orders", "photos", "edible", "poisonous")}))
    print("edibility:", index["facets"]["edibility"])
    if failed:
        print("still missing:", [row["title"] for row, _ in failed])


if __name__ == "__main__":
    main()
