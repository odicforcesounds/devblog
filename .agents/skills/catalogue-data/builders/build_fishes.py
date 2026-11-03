#!/usr/bin/env python3
"""Build docs/fishes/data/ — the aquatic catalogue behind docs/fishesIndex.html.

Fishes first, then everything else that lives in water: sharks, rays, marine
mammals, cephalopods, crustaceans, jellyfish, corals, echinoderms, molluscs,
aquatic reptiles and amphibians, worms, water insects and sponges.

Hand-written: group, order, family, salinity, zone, regions, traits.
Fetched and cited: photograph, introduction, binomial, IUCN status, mass,
length, and a recording where the article has one.
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

UA = {"User-Agent": "devblog-fishes/1.0 (https://blog.odicforcesounds.com; contact via site)"}
OUT = "docs/fishes/data"

# title | group | order | family | salinity | zones | regions | traits
SPEC = """
Atlantic salmon|fish|Salmoniformes|Salmonidae|both|river,open-sea,coastal|europe,americas|migratory,game-fish
Brown trout|fish|Salmoniformes|Salmonidae|fresh|river,lake|europe,asia|game-fish
Rainbow trout|fish|Salmoniformes|Salmonidae|both|river,lake|americas|game-fish
Atlantic cod|fish|Gadiformes|Gadidae|marine|coastal,open-sea|europe,americas|shoaling
Haddock|fish|Gadiformes|Gadidae|marine|open-sea,seabed|europe,americas|shoaling
Atlantic mackerel|fish|Scombriformes|Scombridae|marine|open-sea,coastal|europe,americas|migratory,shoaling
Atlantic bluefin tuna|fish|Scombriformes|Scombridae|marine|open-sea|worldwide|migratory,predator
Swordfish|fish|Carangiformes|Xiphiidae|marine|open-sea,deep-sea|worldwide|predator
Sailfish|fish|Carangiformes|Istiophoridae|marine|open-sea|worldwide|predator
Atlantic herring|fish|Clupeiformes|Clupeidae|marine|open-sea,coastal|europe,americas|shoaling,migratory
European pilchard|fish|Clupeiformes|Clupeidae|marine|coastal,open-sea|europe,africa|
European anchovy|fish|Clupeiformes|Engraulidae|marine|coastal|europe,africa|
European seabass|fish|Perciformes|Moronidae|both|coastal,estuary|europe,africa|
Nile tilapia|fish|Cichliformes|Cichlidae|fresh|river,lake,wetland|africa|mouthbrooder
Common carp|fish|Cypriniformes|Cyprinidae|fresh|river,lake,wetland|europe,asia|
Goldfish|fish|Cypriniformes|Cyprinidae|fresh|lake,river|asia|
Zebrafish|fish|Cypriniformes|Cyprinidae|fresh|river|asia|model-organism
Red-bellied piranha|fish|Characiformes|Serrasalmidae|fresh|river,lake|americas|predator,shoaling
Electric eel|fish|Gymnotiformes|Gymnotidae|fresh|river,wetland|americas|electric
Anglerfish|fish|Lophiiformes|Lophiidae|marine|deep-sea,seabed|worldwide|predator,lure
Ocean sunfish|fish|Tetraodontiformes|Molidae|marine|open-sea|worldwide|
Pufferfish|fish|Tetraodontiformes|Tetraodontidae|marine|coastal,reef|worldwide|venomous
Seahorse|fish|Syngnathiformes|Syngnathidae|marine|coastal,reef|worldwide|male-pregnancy
Leafy seadragon|fish|Syngnathiformes|Syngnathidae|marine|reef,coastal|oceania|camouflage
Clownfish|fish|Perciformes|Pomacentridae|marine|reef|oceania,asia|symbiosis
Regal blue tang|fish|Acanthuriformes|Acanthuridae|marine|reef|oceania,asia|
Moorish idol|fish|Acanthuriformes|Zanclidae|marine|reef|oceania,asia,africa|
French angelfish|fish|Perciformes|Pomacanthidae|marine|reef|americas|
Discus|fish|Cichliformes|Cichlidae|fresh|river,lake|americas|parental-care
Guppy|fish|Cyprinodontiformes|Poeciliidae|fresh|river,wetland|americas|live-bearer
Siamese fighting fish|fish|Anabantiformes|Osphronemidae|fresh|wetland,river|asia|bubble-nest
Arapaima|fish|Osteoglossiformes|Arapaimidae|fresh|river,lake|americas|air-breather
Arowana|fish|Osteoglossiformes|Osteoglossidae|fresh|river,wetland|asia,americas|air-breather
Coelacanth|fish|Coelacanthiformes|Latimeriidae|marine|deep-sea|africa|living-fossil
Queensland lungfish|fish|Ceratodontiformes|Ceratodontidae|fresh|river,wetland|oceania|air-breather
Beluga sturgeon|fish|Acipenseriformes|Acipenseridae|both|river,open-sea|europe,asia|migratory
European eel|fish|Anguilliformes|Anguillidae|both|river,open-sea|europe,americas|migratory
Moray eel|fish|Anguilliformes|Muraenidae|marine|reef,coastal|worldwide|predator
Giant grouper|fish|Perciformes|Serranidae|marine|reef|asia,oceania,africa|predator
Green humphead parrotfish|fish|Labriformes|Scaridae|marine|reef|oceania,asia,africa|herbivore
Lionfish|fish|Scorpaeniformes|Scorpaenidae|marine|reef,coastal|asia,oceania|venomous,predator
Reef stonefish|fish|Scorpaeniformes|Synanceiidae|marine|reef,seabed|asia,oceania|venomous,camouflage
Whale shark|shark|Orectolobiformes|Rhincodontidae|marine|open-sea,reef|worldwide|filter-feeder
Basking shark|shark|Lamniformes|Cetorhinidae|marine|open-sea,coastal|europe,americas|filter-feeder
Great white shark|shark|Lamniformes|Lamnidae|marine|coastal,open-sea|worldwide|predator
Shortfin mako|shark|Lamniformes|Lamnidae|marine|open-sea|worldwide|predator
Tiger shark|shark|Carcharhiniformes|Carcharhinidae|marine|coastal,reef|worldwide|predator
Bull shark|shark|Carcharhiniformes|Carcharhinidae|both|coastal,estuary,river|worldwide|predator
Blue shark|shark|Carcharhiniformes|Carcharhinidae|marine|open-sea|worldwide|migratory
Great hammerhead|shark|Carcharhiniformes|Sphyrnidae|marine|coastal,open-sea|worldwide|predator
Nurse shark|shark|Orectolobiformes|Ginglymostomatidae|marine|reef,seabed|americas,africa|nocturnal
Greenland shark|shark|Squaliformes|Somniosidae|marine|deep-sea,polar|europe,americas|long-lived
Manta ray|ray|Myliobatiformes|Myliobatidae|marine|open-sea,reef|worldwide|filter-feeder
Blue-spotted stingray|ray|Myliobatiformes|Dasyatidae|marine|reef,seabed|asia,oceania|venomous
Electric ray|ray|Torpediniformes|Torpedinidae|marine|seabed,coastal|worldwide|electric
Common skate|ray|Rajiformes|Rajidae|marine|seabed|europe,americas|
Smalltooth sawfish|ray|Rhinopristiformes|Pristidae|both|coastal,estuary|americas,africa|
Blue whale|mammal|Cetacea|Balaenopteridae|marine|open-sea|worldwide|migratory
Humpback whale|mammal|Cetacea|Balaenopteridae|marine|open-sea,coastal|worldwide|migratory,singing
Sperm whale|mammal|Cetacea|Physeteridae|marine|deep-sea,open-sea|worldwide|predator,diving
Orca|mammal|Cetacea|Delphinidae|marine|open-sea,coastal|worldwide|predator,social
Common bottlenose dolphin|mammal|Cetacea|Delphinidae|marine|coastal,open-sea|worldwide|social,echolocation
Beluga whale|mammal|Cetacea|Monodontidae|marine|polar,coastal|europe,asia,americas|social,echolocation
Narwhal|mammal|Cetacea|Monodontidae|marine|polar,open-sea|europe,asia,americas|social,diving
Harbour porpoise|mammal|Cetacea|Phocoenidae|marine|coastal|europe,americas|echolocation
West Indian manatee|mammal|Sirenia|Trichechidae|both|river,coastal,wetland|americas|herbivore
Dugong|mammal|Sirenia|Dugongidae|marine|coastal|oceania,asia,africa|herbivore
Walrus|mammal|Carnivora|Odobenidae|marine|polar,seabed|europe,asia,americas|social,diving
Grey seal|mammal|Carnivora|Phocidae|marine|coastal|europe,americas|diving
Harbour seal|mammal|Carnivora|Phocidae|marine|coastal,estuary|europe,americas|
Northern elephant seal|mammal|Carnivora|Phocidae|marine|open-sea,coastal|americas|diving,migratory
California sea lion|mammal|Carnivora|Otariidae|marine|coastal|americas|social
Sea otter|mammal|Carnivora|Mustelidae|marine|coastal|americas|tool-user,keystone
Common octopus|cephalopod|Octopoda|Octopodidae|marine|reef,seabed|worldwide|predator,camouflage
Giant Pacific octopus|cephalopod|Octopoda|Enteroctopodidae|marine|coastal,seabed|oceania,asia,americas|predator
Blue-ringed octopus|cephalopod|Octopoda|Octopodidae|marine|reef,coastal|oceania|venomous
Mimic octopus|cephalopod|Octopoda|Octopodidae|marine|seabed,estuary|asia|mimic,camouflage
Common cuttlefish|cephalopod|Sepiida|Sepiidae|marine|coastal,seabed|europe,asia,africa|camouflage
Giant squid|cephalopod|Oegopsida|Architeuthidae|marine|deep-sea|worldwide|predator
Colossal squid|cephalopod|Oegopsida|Cranchiidae|marine|deep-sea,polar|antarctica|
Humboldt squid|cephalopod|Oegopsida|Ommastrephidae|marine|deep-sea,open-sea|americas|predator,social
Chambered nautilus|cephalopod|Nautilida|Nautilidae|marine|reef,deep-sea|oceania,asia|nocturnal
Vampire squid|cephalopod|Vampyromorpha|Vampyroteuthidae|marine|deep-sea|worldwide|bioluminescent
European lobster|crustacean|Decapoda|Nephropidae|marine|seabed,coastal|europe|nocturnal
American lobster|crustacean|Decapoda|Nephropidae|marine|seabed,coastal|americas|nocturnal
Red king crab|crustacean|Decapoda|Lithodidae|marine|seabed,deep-sea|europe,asia,americas|migratory
Coconut crab|crustacean|Decapoda|Coenobitidae|marine|coastal,reef|oceania,asia|predator
Hermit crab|crustacean|Decapoda|Paguridae|marine|coastal,seabed|worldwide|shell-user
Mantis shrimp|crustacean|Stomatopoda|Squillidae|marine|reef,seabed|worldwide|predator,colour-vision
Antarctic krill|crustacean|Euphausiacea|Euphausiidae|marine|polar,open-sea|antarctica|shoaling,keystone
Common shrimp|crustacean|Decapoda|Palaemonidae|both|estuary,coastal|europe,africa|
Blue crab|crustacean|Decapoda|Portunidae|both|estuary,coastal|americas|migratory
Japanese spider crab|crustacean|Decapoda|Majidae|marine|deep-sea,seabed|asia|long-legged
Acorn barnacle|crustacean|Cirripedia|Balanidae|marine|coastal,seabed|worldwide|sessile,filter-feeder
Moon jellyfish|jellyfish|Semaeostomeae|Ulmaridae|marine|coastal,open-sea|worldwide|drifting
Lion's mane jellyfish|jellyfish|Semaeostomeae|Cyaneidae|marine|coastal,polar|worldwide|venomous,drifting
Box jellyfish|jellyfish|Chirodropida|Chirodropidae|marine|coastal,reef|oceania,asia|venomous
Portuguese man o' war|jellyfish|Siphonophorae|Physaliidae|marine|open-sea,coastal|worldwide|venomous,colony
By-the-wind sailor|jellyfish|Anthoathecata|Porpitidae|marine|open-sea|worldwide|colony,drifting
Sea nettle|jellyfish|Semaeostomeae|Pelagiidae|marine|coastal,estuary|worldwide|venomous
Brain coral|jellyfish|Scleractinia|Mussidae|marine|reef|americas|colony,reef-builder
Staghorn coral|jellyfish|Scleractinia|Acroporidae|marine|reef|oceania,asia,africa|colony,reef-builder
Magnificent sea anemone|jellyfish|Actiniaria|Stichodactylidae|marine|reef|asia,oceania|symbiosis,venomous
Bubble-tip anemone|jellyfish|Actiniaria|Stichodactylidae|marine|reef|asia,oceania|symbiosis
Common starfish|echinoderm|Forcipulatida|Asteriidae|marine|coastal,seabed|europe,americas|predator
Crown-of-thorns starfish|echinoderm|Valvatida|Acanthasteridae|marine|reef|oceania,asia|predator,venomous
Sea urchin|echinoderm|Camarodonta|Echinidae|marine|seabed,reef|worldwide|herbivore
Sea cucumber|echinoderm|Synallactida|Stichopodidae|marine|seabed,reef|worldwide|detritivore
Brittle star|echinoderm|Ophiurida|Ophiuridae|marine|seabed,reef|worldwide|nocturnal
Feather star|echinoderm|Comatulida|Antedonidae|marine|reef,deep-sea|worldwide|filter-feeder
Blue mussel|mollusc|Mytilida|Mytilidae|marine|coastal,seabed|europe,americas|filter-feeder,colony
Pacific oyster|mollusc|Ostreida|Ostreidae|marine|coastal,estuary|asia,oceania|filter-feeder
Giant clam|mollusc|Venerida|Cardiidae|marine|reef|oceania,asia|symbiosis,long-lived
Queen conch|mollusc|Littorinimorpha|Strombidae|marine|reef,seabed|americas,africa|herbivore
Common scallop|mollusc|Pectinida|Pectinidae|marine|seabed,coastal|europe,americas|swimmer
Red abalone|mollusc|Lepetellida|Haliotidae|marine|coastal,seabed|americas|herbivore
Sea hare|mollusc|Aplysiomorpha|Aplysiidae|marine|reef,coastal|worldwide|herbivore
Spanish dancer|mollusc|Nudibranchia|Hexabranchidae|marine|reef|asia,oceania,africa|swimmer
Shipworm|mollusc|Myida|Teredinidae|marine|coastal,estuary|worldwide|wood-borer
Green sea turtle|reptile|Testudines|Cheloniidae|marine|reef,coastal|worldwide|migratory,herbivore
Leatherback sea turtle|reptile|Testudines|Dermochelyidae|marine|open-sea|worldwide|migratory,diving
Hawksbill sea turtle|reptile|Testudines|Cheloniidae|marine|reef|worldwide|migratory
Marine iguana|reptile|Squamata|Iguanidae|marine|coastal|americas|herbivore,diving
Saltwater crocodile|reptile|Crocodilia|Crocodylidae|both|estuary,coastal,river|asia,oceania|predator
Banded sea krait|reptile|Squamata|Elapidae|marine|reef,coastal|asia,oceania|venomous
Yellow-bellied sea snake|reptile|Squamata|Elapidae|marine|open-sea|worldwide|venomous
Alligator snapping turtle|reptile|Testudines|Chelydridae|fresh|river,lake|americas|ambush
Axolotl|amphibian|Caudata|Ambystomatidae|fresh|lake,wetland|americas|regeneration
Chinese giant salamander|amphibian|Caudata|Cryptobranchidae|fresh|river|asia|nocturnal
Common frog|amphibian|Anura|Ranidae|fresh|wetland,lake|europe,asia|
American bullfrog|amphibian|Anura|Ranidae|fresh|lake,wetland|americas|predator
African clawed frog|amphibian|Anura|Pipidae|fresh|river,wetland|africa|
Bobbit worm|worm|Eunicida|Eunicidae|marine|seabed,reef|worldwide|predator,ambush
Christmas tree worm|worm|Sabellida|Serpulidae|marine|reef|worldwide|sessile,filter-feeder
Giant tube worm|worm|Sabellida|Siboglinidae|marine|deep-sea,polar|worldwide|chemosynthesis,colony
Medicinal leech|worm|Hirudinida|Hirudinidae|fresh|wetland,lake|europe|blood-feeder
Planarian|worm|Tricladida|Planariidae|fresh|river,wetland|worldwide|regeneration
Tardigrade|worm|Apochela|Milnesiidae|both|wetland,reef|worldwide|extremophile
Great diving beetle|insect|Coleoptera|Dytiscidae|fresh|lake,pond|europe,asia|predator,diving
Water strider|insect|Hemiptera|Gerridae|fresh|river,lake|worldwide|surface-tension
Emperor dragonfly|insect|Odonata|Aeshnidae|fresh|lake,wetland|europe,asia|predator,aerial
Mayfly|insect|Ephemeroptera|Ephemeridae|fresh|river,lake|worldwide|short-lived
Caddisfly|insect|Trichoptera|Limnephilidae|fresh|river,lake|worldwide|case-builder
Barrel sponge|sponge|Haplosclerida|Petrosiidae|marine|reef|americas,asia|filter-feeder,sessile
Venus' flower basket|sponge|Lyssacinosida|Euplectellidae|marine|deep-sea|asia,oceania|silica,glowing
Comb jelly|comb-jelly|Cydippida|Pleurobrachiidae|marine|open-sea,coastal|worldwide|bioluminescent,swimmer
Sea gooseberry|comb-jelly|Cydippida|Pleurobrachiidae|marine|coastal,open-sea|worldwide|predator,transparent
Golden jellyfish|jellyfish|Rhizostomeae|Mastigiidae|marine|lake,reef|oceania|migratory,symbiosis
Zostera marina|plant|Alismatales|Zosteraceae|marine|coastal,seabed|europe,americas|seagrass
Posidonia oceanica|plant|Alismatales|Posidoniaceae|marine|coastal,seabed|europe|seagrass,meadow-builder
Vallisneria|plant|Alismatales|Hydrocharitaceae|fresh|river,lake|asia,africa,oceania|submerged
Nymphaea alba|plant|Nymphaeales|Nymphaeaceae|fresh|lake,river|europe,asia|water-lily
Nelumbo nucifera|plant|Proteales|Nelumbonaceae|fresh|wetland,lake|asia,oceania|water-lily
Lemna|plant|Alismatales|Araceae|fresh|lake,wetland|worldwide|floating,duckweed
Pontederia crassipes|plant|Commelinales|Pontederiaceae|fresh|river,lake|americas|floating,invasive
Phragmites australis|plant|Poales|Poaceae|both|wetland,estuary|worldwide|reed
Typha|plant|Poales|Typhaceae|fresh|wetland,lake|worldwide|reed
Cyperus papyrus|plant|Poales|Cyperaceae|fresh|wetland,river|africa|reed
Rhizophora mangle|plant|Malpighiales|Rhizophoraceae|both|estuary,coastal|americas|mangrove
Avicennia marina|plant|Lamiales|Acanthaceae|marine|estuary,coastal|africa,asia,oceania|mangrove
Utricularia|plant|Lamiales|Lentibulariaceae|fresh|lake,wetland|worldwide|carnivorous
Ceratophyllum demersum|plant|Ceratophyllales|Ceratophyllaceae|fresh|lake,river|worldwide|submerged
Nasturtium officinale|plant|Brassicales|Brassicaceae|fresh|river,wetland|europe,asia|edible
Salvinia molesta|plant|Salviniales|Salviniaceae|fresh|lake,wetland|americas|floating,invasive
Azolla|plant|Salviniales|Salviniaceae|fresh|wetland,lake|worldwide|floating,nitrogen-fixing
Sagittaria sagittifolia|plant|Alismatales|Alismataceae|fresh|river,wetland|europe,asia|
Butomus umbellatus|plant|Alismatales|Butomaceae|fresh|river,wetland|europe,asia|
Lobelia dortmanna|plant|Asterales|Campanulaceae|fresh|lake|europe|
Isoetes|plant|Isoetales|Isoetaceae|fresh|lake,river|worldwide|living-fossil
Macrocystis pyrifera|alga|Laminariales|Laminariaceae|marine|coastal,seabed|americas,oceania|kelp-forest
Laminaria digitata|alga|Laminariales|Laminariaceae|marine|coastal,seabed|europe|kelp
Fucus vesiculosus|alga|Fucales|Fucaceae|marine|coastal|europe,americas|bladderwrack
Sargassum|alga|Fucales|Sargassaceae|marine|open-sea,coastal|worldwide|floating
Ulva lactuca|alga|Ulvales|Ulvaceae|marine|coastal,estuary|worldwide|sea-lettuce
Chondrus crispus|alga|Gigartinales|Gigartinaceae|marine|coastal,seabed|europe,americas|carrageenan
Caulerpa taxifolia|alga|Bryopsidales|Caulerpaceae|marine|reef,seabed|worldwide|invasive
Corallina officinalis|alga|Corallinales|Corallinaceae|marine|coastal,reef|europe,americas|calcareous
Spirogyra|alga|Zygnematales|Zygnemataceae|fresh|river,lake|worldwide|filamentous
Volvox|alga|Volvocales|Volvocaceae|fresh|lake,wetland|worldwide|colony
Diatom|plankton|Naviculales|Naviculaceae|both|open-sea,lake|worldwide|silica-shell
Dinoflagellate|plankton|Peridiniales|Peridiniaceae|marine|coastal,open-sea|worldwide|red-tide,bioluminescent
Radiolaria|plankton|Nassellaria|Nassellariidae|marine|open-sea,deep-sea|worldwide|silica-shell
Foraminifera|plankton|Rotaliida|Rotaliidae|marine|seabed,open-sea|worldwide|shell
Copepod|plankton|Calanoida|Calanidae|both|open-sea,lake|worldwide|zooplankton
Paramecium|protist|Peniculida|Parameciidae|fresh|wetland,lake|worldwide|single-celled
Amoeba|protist|Amoebida|Amoebidae|fresh|wetland|worldwide|single-celled
Euglena|protist|Euglenida|Euglenaceae|fresh|wetland,lake|worldwide|flagellate
Stentor (protozoan)|protist|Heterotrichida|Stentoridae|fresh|lake,wetland|worldwide|trumpet-shaped
Noctiluca scintillans|protist|Noctilucales|Noctilucaceae|marine|coastal,open-sea|worldwide|bioluminescent,red-tide
Cyanobacteria|microbe|Synechococcales|Synechococcaceae|both|lake,open-sea|worldwide|photosynthetic
Prochlorococcus|microbe|Synechococcales|Synechococcaceae|marine|open-sea|worldwide|photosynthetic,abundant
Trichodesmium|microbe|Oscillatoriales|Oscillatoriaceae|marine|open-sea|worldwide|nitrogen-fixing
Halobacterium|microbe|Halobacteriales|Halobacteriaceae|marine|coastal|worldwide|extremophile
Batrachochytrium dendrobatidis|fungus|Rhizophydiales|Rhizophydiaceae|fresh|wetland|worldwide|pathogen
Saprolegnia|fungus|Saprolegniales|Saprolegniaceae|fresh|wetland,river|worldwide|water-mould
Salp|tunicate|Salpida|Salpidae|marine|open-sea|worldwide|colony,filter-feeder
Sea squirt|tunicate|Stolidobranchia|Styelidae|marine|coastal,seabed|worldwide|filter-feeder
Lancelet|chordate|Amphioxiformes|Branchiostomidae|marine|coastal,seabed|worldwide|filter-feeder
Rotifer|worm|Ploima|Brachionidae|fresh|wetland,lake|worldwide|microscopic
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
        return row, None, None, summary.get("__error__", summary.get("type", "missing"))
    media = fetch("https://en.wikipedia.org/api/rest_v1/page/media-list/" + urllib.parse.quote(page))
    audio = None
    if "__error__" not in media:
        for item in media.get("items", []):
            name = item.get("title", "")
            if item.get("type") == "audio" and name.lower().endswith((".ogg", ".oga", ".wav", ".mp3", ".flac")):
                audio = name
                break
    return row, summary, audio, None


def wikidata(qids):
    status, taxon, length_seen, mass_seen = {}, {}, {}, {}
    for start in range(0, len(qids), 40):
        batch = qids[start:start + 40]
        query = """
SELECT ?item ?taxon ?statusLabel ?len ?lenUnitLabel ?mass ?massUnitLabel WHERE {
  VALUES ?item { %s }
  OPTIONAL { ?item wdt:P141 ?status }
  OPTIONAL { ?item wdt:P225 ?taxon }
  OPTIONAL { ?item p:P2043/psv:P2043 ?lv .
             ?lv wikibase:quantityAmount ?len ; wikibase:quantityUnit ?lenUnit }
  OPTIONAL { ?item p:P2067/psv:P2067 ?mv .
             ?mv wikibase:quantityAmount ?mass ; wikibase:quantityUnit ?massUnit }
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
            if "len" in binding:
                unit = binding.get("lenUnitLabel", {}).get("value", "")
                try:
                    value = float(binding["len"]["value"])
                except ValueError:
                    value = 0
                if unit.startswith("centimetre"):
                    cm = value
                elif unit.startswith("metre"):
                    cm = value * 100
                elif unit.startswith("millimetre"):
                    cm = value / 10
                else:
                    cm = 0
                if 0.05 <= cm <= 4000:
                    length_seen.setdefault(qid, []).append(round(cm, 1))
            if "mass" in binding:
                unit = binding.get("massUnitLabel", {}).get("value", "")
                try:
                    value = float(binding["mass"]["value"])
                except ValueError:
                    value = 0
                if unit.startswith("gram"):
                    grams = value
                elif unit.startswith("kilogram"):
                    grams = value * 1000
                elif unit.startswith("milligram"):
                    grams = value / 1000
                elif unit.startswith("tonne"):
                    grams = value * 1000000
                else:
                    grams = 0
                if 0.001 <= grams <= 200000000:
                    mass_seen.setdefault(qid, []).append(round(grams, 2))
    return (status, taxon,
            {q: max(v) for q, v in length_seen.items()},
            {q: max(v) for q, v in mass_seen.items()})


def audio_urls(titles):
    urls = {}
    for start in range(0, len(titles), 40):
        batch = titles[start:start + 40]
        query = urllib.parse.urlencode({
            "action": "query", "format": "json", "formatversion": "2",
            "prop": "imageinfo", "iiprop": "url", "titles": "|".join(batch),
        })
        data = fetch("https://en.wikipedia.org/w/api.php?" + query)
        found = data.get("query", {})
        for page in found.get("pages", []):
            info = page.get("imageinfo") or []
            if info and info[0].get("url"):
                url = info[0]["url"].split("?utm_source")[0]
                urls[page["title"]] = url
                urls[page["title"].replace(" ", "_")] = url
        for norm in found.get("normalized", []):
            if norm.get("to") in urls:
                urls[norm["from"]] = urls[norm["to"]]
    return urls


def spec_rows():
    rows = []
    for line in SPEC.strip().splitlines():
        bits = [b.strip() for b in line.split("|")]
        if len(bits) < 5:
            continue
        bits += [""] * (8 - len(bits))
        rows.append({
            "title": bits[0], "grp": bits[1], "order": bits[2], "family": bits[3],
            "salinity": bits[4],
            "zones": [z for z in bits[5].split(",") if z],
            "regions": [r for r in bits[6].split(",") if r],
            "traits": [t for t in bits[7].split(",") if t],
        })
    return rows


def main():
    rows = spec_rows()
    print("spec rows:", len(rows))

    resolved, failed = [], []
    with ThreadPoolExecutor(max_workers=3) as pool:
        for row, summary, audio, error in pool.map(gather, rows):
            if not summary:
                failed.append((row, error))
                print("  !", row["title"], "->", error)
                continue
            resolved.append((row, summary, audio))
            print("  +", row["title"])
            time.sleep(0.2)

    for round_ in range(3):
        if not failed:
            break
        print("retry round", round_ + 1, "for", len(failed))
        still = []
        for row, _error in failed:
            time.sleep(4)
            row2, summary, audio, error = gather(row)
            if summary:
                resolved.append((row2, summary, audio))
                print("  +", row["title"])
            else:
                still.append((row, error))
        failed = still
    print("resolved:", len(resolved), "failed:", len(failed))
    if failed:
        print("missing:", [row["title"] for row, _ in failed])

    titles = sorted({audio for _, _, audio in resolved if audio})
    urls = audio_urls(titles) if titles else {}
    print("recordings on the articles:", len(titles), "resolved:", len(urls))

    qids = [summary.get("wikibase_item") for _, summary, _ in resolved if summary.get("wikibase_item")]
    status, taxon, length, mass = wikidata(qids) if qids else ({}, {}, {}, {})
    print("wikidata: status", len(status), "binomials", len(taxon),
          "lengths", len(length), "masses", len(mass))

    orders, seen = {}, set()
    for row, summary, audio in resolved:
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
            "z": row["zones"], "r": row["regions"], "t": row["traits"],
            "w": row["salinity"],
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
        if audio and audio in urls:
            entry["a"] = urls[audio]
        if qid and qid in status:
            entry["st"] = status[qid]
        if qid and qid in length:
            entry["l"] = length[qid]
        if qid and qid in mass:
            entry["m"] = mass[qid]
        orders.setdefault(row["order"], {}).setdefault(row["family"], []).append(entry)

    os.makedirs(OUT, exist_ok=True)
    facets = {"group": {}, "salinity": {}, "zone": {}, "region": {}, "trait": {}, "status": {}}
    groups = []
    total = photos = songs = statuses = 0
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
        songs += sum(1 for b in beings if b.get("a"))
        statuses += sum(1 for b in beings if b.get("st"))
        for being in beings:
            facets["group"][being["grp"]] = facets["group"].get(being["grp"], 0) + 1
            facets["salinity"][being["w"]] = facets["salinity"].get(being["w"], 0) + 1
            for value in being["z"]:
                facets["zone"][value] = facets["zone"].get(value, 0) + 1
            for value in being["r"]:
                facets["region"][value] = facets["region"].get(value, 0) + 1
            for value in being["t"]:
                facets["trait"][value] = facets["trait"].get(value, 0) + 1
            if being.get("st"):
                facets["status"][being["st"]] = facets["status"].get(being["st"], 0) + 1
        groups.append({"key": key, "num": "%02d" % (len(groups) + 1), "title": order,
                       "beings": len(beings), "families": len(families),
                       "photos": sum(1 for b in beings if b.get("i")),
                       "songs": sum(1 for b in beings if b.get("a"))})

    index = {
        "generated": time.strftime("%Y-%m-%d"),
        "source": "en.wikipedia.org + wikidata.org",
        "beings": total,
        "families": len({b["fam"] for fam in orders.values() for f in fam.values() for b in f}),
        "orders": len(orders),
        "groups": len({b["grp"] for fam in orders.values() for f in fam.values() for b in f}),
        "photos": photos,
        "songs": songs,
        "statuses": statuses,
        "facets": facets,
        "sections": groups,
    }
    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as fh:
        json.dump(index, fh, ensure_ascii=False, indent=1)
    print(json.dumps({k: index[k] for k in ("beings", "families", "orders", "groups",
                                            "photos", "songs", "statuses")}))
    print("groups:", index["facets"]["group"])


if __name__ == "__main__":
    main()
