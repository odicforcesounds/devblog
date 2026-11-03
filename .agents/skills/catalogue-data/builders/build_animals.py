#!/usr/bin/env python3
"""Build docs/animals/data/ — the animal catalogue behind docs/animalsIndex.html.

Hand-written: class, order, family, habitats, regions, traits, for each species.
Fetched and cited: photograph, introduction, binomial, IUCN status, mass, length,
and a recording of the animal where the article has one.

Humans are not in this catalogue. Every other class is.
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

UA = {"User-Agent": "devblog-animals/1.0 (https://blog.odicforcesounds.com; contact via site)"}
OUT = "docs/animals/data"

# title | class | order | family | habitats | regions | traits
SPEC = """
Lion|mammal|Carnivora|Felidae|grassland,woodland|africa|predator,social
Tiger|mammal|Carnivora|Felidae|forest,grassland|asia|predator
Leopard|mammal|Carnivora|Felidae|forest,grassland|africa,asia|predator,arboreal
Jaguar|mammal|Carnivora|Felidae|forest,wetland|americas|predator
Snow leopard|mammal|Carnivora|Felidae|alpine|asia|predator
Cougar|mammal|Carnivora|Felidae|forest,alpine|americas|predator
Cheetah|mammal|Carnivora|Felidae|grassland|africa|predator
Eurasian lynx|mammal|Carnivora|Felidae|forest|europe,asia|predator
Bobcat|mammal|Carnivora|Felidae|woodland,desert|americas|predator
Serval|mammal|Carnivora|Felidae|grassland,wetland|africa|predator
Caracal|mammal|Carnivora|Felidae|desert,grassland|africa,asia|predator
European wildcat|mammal|Carnivora|Felidae|forest|europe|predator
Grey wolf|mammal|Carnivora|Canidae|forest,alpine|europe,asia,americas|predator,social
Coyote|mammal|Carnivora|Canidae|grassland,urban|americas|predator
Red fox|mammal|Carnivora|Canidae|woodland,urban|worldwide|predator
Arctic fox|mammal|Carnivora|Canidae|alpine|europe,asia,americas|predator
Fennec fox|mammal|Carnivora|Canidae|desert|africa|predator,nocturnal
Dingo|mammal|Carnivora|Canidae|woodland,desert|oceania|predator
Brown bear|mammal|Carnivora|Ursidae|forest,alpine|europe,asia,americas|omnivore
Polar bear|mammal|Carnivora|Ursidae|marine,alpine|americas,europe,asia|predator
American black bear|mammal|Carnivora|Ursidae|forest|americas|omnivore
Giant panda|mammal|Carnivora|Ursidae|forest,alpine|asia|herbivore
Sun bear|mammal|Carnivora|Ursidae|forest|asia|omnivore
Sloth bear|mammal|Carnivora|Ursidae|forest,grassland|asia|omnivore
Wolverine|mammal|Carnivora|Mustelidae|alpine,forest|europe,asia,americas|predator
Sea otter|mammal|Carnivora|Mustelidae|marine|americas|predator,social
Eurasian otter|mammal|Carnivora|Mustelidae|wetland|europe,asia,africa|predator
Honey badger|mammal|Carnivora|Mustelidae|grassland,desert|africa,asia|predator
Meerkat|mammal|Carnivora|Herpestidae|desert,grassland|africa|social
Spotted hyena|mammal|Carnivora|Hyaenidae|grassland|africa|predator,social
Striped hyena|mammal|Carnivora|Hyaenidae|desert,grassland|africa,asia|scavenger,nocturnal
Raccoon|mammal|Carnivora|Procyonidae|woodland,urban|americas|omnivore,nocturnal
Red panda|mammal|Carnivora|Ailuridae|forest,alpine|asia|herbivore,arboreal
Chimpanzee|mammal|Primates|Hominidae|forest|africa|social,tool-user
Bonobo|mammal|Primates|Hominidae|forest|africa|social
Western gorilla|mammal|Primates|Hominidae|forest|africa|social,herbivore
Bornean orangutan|mammal|Primates|Hominidae|forest|asia|arboreal
Lar gibbon|mammal|Primates|Hylobatidae|forest|asia|arboreal,social
Mandrill|mammal|Primates|Cercopithecidae|forest|africa|social
Olive baboon|mammal|Primates|Cercopithecidae|grassland,woodland|africa|social
Ring-tailed lemur|mammal|Primates|Lemuridae|forest|africa|social,arboreal
Aye-aye|mammal|Primates|Daubentoniidae|forest|africa|nocturnal
Philippine tarsier|mammal|Primates|Tarsiidae|forest|asia|nocturnal,arboreal
Pygmy marmoset|mammal|Primates|Callitrichidae|forest|americas|arboreal,social
Geoffroy's spider monkey|mammal|Primates|Atelidae|forest|americas|arboreal,social
Colombian red howler|mammal|Primates|Atelidae|forest|americas|arboreal,social
Tufted capuchin|mammal|Primates|Cebidae|forest|americas|arboreal,tool-user
Japanese macaque|mammal|Primates|Cercopithecidae|forest,alpine|asia|social
Rhesus macaque|mammal|Primates|Cercopithecidae|forest,urban|asia|social
Blue whale|mammal|Cetacea|Balaenopteridae|marine|worldwide|migratory
Humpback whale|mammal|Cetacea|Balaenopteridae|marine|worldwide|migratory
Sperm whale|mammal|Cetacea|Physeteridae|marine|worldwide|predator
Orca|mammal|Cetacea|Delphinidae|marine|worldwide|predator,social
Common bottlenose dolphin|mammal|Cetacea|Delphinidae|marine,coastal|worldwide|social
Narwhal|mammal|Cetacea|Monodontidae|marine|europe,asia,americas|social
Beluga whale|mammal|Cetacea|Monodontidae|marine|europe,asia,americas|social
Amazon river dolphin|mammal|Cetacea|Iniidae|wetland|americas|
Harbour porpoise|mammal|Cetacea|Phocoenidae|marine|europe,americas|
African bush elephant|mammal|Proboscidea|Elephantidae|grassland|africa|herbivore,social
Asian elephant|mammal|Proboscidea|Elephantidae|forest|asia|herbivore,social
West Indian manatee|mammal|Sirenia|Trichechidae|marine,wetland|americas|herbivore
Dugong|mammal|Sirenia|Dugongidae|marine|oceania,asia,africa|herbivore
Giraffe|mammal|Artiodactyla|Giraffidae|grassland|africa|herbivore,social
Okapi|mammal|Artiodactyla|Giraffidae|forest|africa|herbivore
Hippopotamus|mammal|Artiodactyla|Hippopotamidae|wetland|africa|herbivore,social
Pygmy hippopotamus|mammal|Artiodactyla|Hippopotamidae|forest,wetland|africa|herbivore
Dromedary|mammal|Artiodactyla|Camelidae|desert|africa,asia|herbivore
Bactrian camel|mammal|Artiodactyla|Camelidae|desert|asia|herbivore
Llama|mammal|Artiodactyla|Camelidae|alpine|americas|herbivore,social
Alpaca|mammal|Artiodactyla|Camelidae|alpine|americas|herbivore,social
Wild boar|mammal|Artiodactyla|Suidae|forest,farmland|worldwide|omnivore,social
Warthog|mammal|Artiodactyla|Suidae|grassland|africa|herbivore
Red deer|mammal|Artiodactyla|Cervidae|forest,alpine|europe,asia|herbivore,social
Reindeer|mammal|Artiodactyla|Cervidae|alpine,forest|europe,asia,americas|herbivore,migratory
Moose|mammal|Artiodactyla|Cervidae|forest,alpine|europe,asia,americas|herbivore
White-tailed deer|mammal|Artiodactyla|Cervidae|woodland,farmland|americas|herbivore
Pronghorn|mammal|Artiodactyla|Antilocapridae|grassland|americas|herbivore,migratory
American bison|mammal|Artiodactyla|Bovidae|grassland|americas|herbivore,social
Wisent|mammal|Artiodactyla|Bovidae|forest|europe|herbivore,social
Water buffalo|mammal|Artiodactyla|Bovidae|wetland,farmland|asia|herbivore,social
Yak|mammal|Artiodactyla|Bovidae|alpine|asia|herbivore,social
Muskox|mammal|Artiodactyla|Bovidae|alpine|americas|herbivore,social
Impala|mammal|Artiodactyla|Bovidae|grassland,woodland|africa|herbivore,social
Blue wildebeest|mammal|Artiodactyla|Bovidae|grassland|africa|herbivore,migratory
Thomson's gazelle|mammal|Artiodactyla|Bovidae|grassland|africa|herbivore,social
Springbok|mammal|Artiodactyla|Bovidae|desert,grassland|africa|herbivore,migratory
Gemsbok|mammal|Artiodactyla|Bovidae|desert|africa|herbivore
Greater kudu|mammal|Artiodactyla|Bovidae|woodland|africa|herbivore
Saiga antelope|mammal|Artiodactyla|Bovidae|grassland|asia|herbivore,migratory
Alpine ibex|mammal|Artiodactyla|Bovidae|alpine|europe|herbivore
Bighorn sheep|mammal|Artiodactyla|Bovidae|alpine,desert|americas|herbivore,social
Chamois|mammal|Artiodactyla|Bovidae|alpine,forest|europe|herbivore
Plains zebra|mammal|Perissodactyla|Equidae|grassland|africa|herbivore,social
Grévy's zebra|mammal|Perissodactyla|Equidae|grassland|africa|herbivore
Przewalski's horse|mammal|Perissodactyla|Equidae|grassland|asia|herbivore,social
White rhinoceros|mammal|Perissodactyla|Rhinocerotidae|grassland|africa|herbivore
Black rhinoceros|mammal|Perissodactyla|Rhinocerotidae|woodland,grassland|africa|herbivore
Indian rhinoceros|mammal|Perissodactyla|Rhinocerotidae|wetland,grassland|asia|herbivore
Malayan tapir|mammal|Perissodactyla|Tapiridae|forest|asia|herbivore,nocturnal
South American tapir|mammal|Perissodactyla|Tapiridae|forest,wetland|americas|herbivore
Red squirrel|mammal|Rodentia|Sciuridae|forest|europe,asia|arboreal
Eastern grey squirrel|mammal|Rodentia|Sciuridae|woodland,urban|americas|arboreal
Alpine marmot|mammal|Rodentia|Sciuridae|alpine|europe|social
Black-tailed prairie dog|mammal|Rodentia|Sciuridae|grassland|americas|social,burrower
North American beaver|mammal|Rodentia|Castoridae|wetland|americas|builder,nocturnal
Eurasian beaver|mammal|Rodentia|Castoridae|wetland|europe,asia|builder,nocturnal
Crested porcupine|mammal|Rodentia|Hystricidae|desert,grassland|africa,asia|nocturnal
Capybara|mammal|Rodentia|Caviidae|wetland|americas|social
Guinea pig|mammal|Rodentia|Caviidae|grassland|americas|social
Golden hamster|mammal|Rodentia|Cricetidae|desert,farmland|asia|burrower,nocturnal
House mouse|mammal|Rodentia|Muridae|urban,farmland|worldwide|
Brown rat|mammal|Rodentia|Muridae|urban,farmland|worldwide|social
Bank vole|mammal|Rodentia|Cricetidae|woodland|europe|
Norway lemming|mammal|Rodentia|Cricetidae|alpine|europe,asia|migratory
Naked mole-rat|mammal|Rodentia|Heterocephalidae|desert|africa|social,burrower
European hare|mammal|Lagomorpha|Leporidae|farmland,grassland|europe,asia|
European rabbit|mammal|Lagomorpha|Leporidae|woodland,farmland|europe|burrower,social
American pika|mammal|Lagomorpha|Ochotonidae|alpine|americas|
European hedgehog|mammal|Eulipotyphla|Erinaceidae|woodland,urban|europe,asia|nocturnal
Common shrew|mammal|Eulipotyphla|Soricidae|woodland,grassland|europe,asia|
European mole|mammal|Eulipotyphla|Talpidae|farmland,woodland|europe|burrower
Large flying fox|mammal|Chiroptera|Pteropodidae|forest,coastal|asia,oceania|social,nocturnal
Common vampire bat|mammal|Chiroptera|Phyllostomidae|forest,farmland|americas|nocturnal
Greater horseshoe bat|mammal|Chiroptera|Rhinolophidae|woodland|europe,asia,africa|nocturnal
Giant anteater|mammal|Pilosa|Myrmecophagidae|grassland,forest|americas|
Linnaeus's two-toed sloth|mammal|Pilosa|Bradypodidae|forest|americas|arboreal
Nine-banded armadillo|mammal|Cingulata|Dasypodidae|woodland,grassland|americas|burrower
Ground pangolin|mammal|Pholidota|Manidae|grassland|africa|nocturnal
Aardvark|mammal|Tubulidentata|Orycteropodidae|grassland,desert|africa|nocturnal,burrower
Red kangaroo|mammal|Diprotodontia|Macropodidae|desert,grassland|oceania|herbivore,social
Eastern grey kangaroo|mammal|Diprotodontia|Macropodidae|woodland,grassland|oceania|herbivore,social
Red-necked wallaby|mammal|Diprotodontia|Macropodidae|woodland|oceania|herbivore
Koala|mammal|Diprotodontia|Phascolarctidae|forest|oceania|arboreal,herbivore
Common wombat|mammal|Diprotodontia|Vombatidae|forest|oceania|burrower
Tasmanian devil|mammal|Dasyuromorphia|Dasyuridae|forest|oceania|predator,scavenger
Thylacine|mammal|Dasyuromorphia|Thylacinidae|forest,grassland|oceania|extinct
Numbat|mammal|Dasyuromorphia|Myrmecobiidae|woodland|oceania|
Platypus|mammal|Monotremata|Ornithorhynchidae|wetland|oceania|venomous,nocturnal
Short-beaked echidna|mammal|Monotremata|Tachyglossidae|woodland,desert|oceania|
Rock hyrax|mammal|Hyracoidea|Procaviidae|alpine,grassland|africa,asia|social
Common ostrich|bird|Struthioniformes|Struthionidae|grassland,desert|africa|flightless,social
Emu|bird|Casuariiformes|Casuariidae|grassland,woodland|oceania|flightless
Southern cassowary|bird|Casuariiformes|Casuariidae|forest|oceania|flightless
Emperor penguin|bird|Sphenisciformes|Spheniscidae|marine,antarctica|antarctica|flightless,social
Little penguin|bird|Sphenisciformes|Spheniscidae|marine,coastal|oceania|flightless,nocturnal
Wandering albatross|bird|Procellariiformes|Diomedeidae|marine|antarctica,oceania|migratory
Atlantic puffin|bird|Charadriiformes|Alcidae|marine,coastal|europe,americas|migratory,social
Arctic tern|bird|Charadriiformes|Laridae|marine,coastal|worldwide|migratory
Andean condor|bird|Cathartiformes|Cathartidae|alpine|americas|scavenger
Golden eagle|bird|Accipitriformes|Accipitridae|alpine,grassland|europe,asia,americas|predator
Bald eagle|bird|Accipitriformes|Accipitridae|coastal,wetland|americas|predator
Peregrine falcon|bird|Falconiformes|Falconidae|coastal,urban|worldwide|predator
Secretarybird|bird|Accipitriformes|Sagittariidae|grassland|africa|predator
Snowy owl|bird|Strigiformes|Strigidae|alpine,grassland|europe,asia,americas|predator,nocturnal
Barn owl|bird|Strigiformes|Tytonidae|farmland,grassland|worldwide|predator,nocturnal
Kea|bird|Psittaciformes|Strigopidae|alpine|oceania|tool-user
Kākāpō|bird|Psittaciformes|Strigopidae|forest|oceania|flightless,nocturnal
Scarlet macaw|bird|Psittaciformes|Psittacidae|forest|americas|social
Greater flamingo|bird|Phoenicopteriformes|Phoenicopteridae|wetland|africa,asia,europe|social
Great white pelican|bird|Pelecaniformes|Pelecanidae|wetland|africa,asia,europe|social
Shoebill|bird|Pelecaniformes|Balaenicipitidae|wetland|africa|
Marabou stork|bird|Ciconiiformes|Ciconiidae|wetland,urban|africa|scavenger
Common kingfisher|bird|Coraciiformes|Alcedinidae|wetland|europe,asia,africa|
Laughing kookaburra|bird|Coraciiformes|Alcedinidae|woodland,urban|oceania|
Toco toucan|bird|Piciformes|Ramphastidae|forest|americas|
Ruby-throated hummingbird|bird|Apodiformes|Trochilidae|forest,urban|americas|migratory
Common raven|bird|Passeriformes|Corvidae|alpine,woodland|worldwide|tool-user
New Caledonian crow|bird|Passeriformes|Corvidae|forest|oceania|tool-user
Superb lyrebird|bird|Passeriformes|Menuridae|forest|oceania|mimic
Raggiana bird-of-paradise|bird|Passeriformes|Paradisaeidae|forest|oceania|
Northern cardinal|bird|Passeriformes|Cardinalidae|woodland,urban|americas|
Rock dove|bird|Columbiformes|Columbidae|urban,coastal|worldwide|social
Great bustard|bird|Otidiformes|Otididae|grassland,farmland|europe,asia|
Common crane|bird|Gruiformes|Gruidae|wetland,farmland|europe,asia|migratory,social
Red junglefowl|bird|Galliformes|Phasianidae|forest|asia|
Mallard|bird|Anseriformes|Anatidae|wetland,urban|worldwide|migratory
European nightjar|bird|Caprimulgiformes|Caprimulgidae|woodland,grassland|europe,asia,africa|nocturnal
Southern ground hornbill|bird|Bucerotiformes|Bucerotidae|grassland|africa|social
Great crested grebe|bird|Podicipediformes|Podicipedidae|wetland|europe,asia,africa|
Northern gannet|bird|Suliformes|Sulidae|marine|europe,americas|social
Common loon|bird|Gaviiformes|Gaviidae|wetland,marine|europe,americas|
Hoatzin|bird|Opisthocomiformes|Opisthocomidae|forest,wetland|americas|
Kagu|bird|Eurypygiformes|Rhynochetidae|forest|oceania|flightless
Komodo dragon|reptile|Squamata|Varanidae|grassland,forest|asia|predator
Saltwater crocodile|reptile|Crocodilia|Crocodylidae|coastal,wetland|asia,oceania|predator
Nile crocodile|reptile|Crocodilia|Crocodylidae|wetland|africa|predator
American alligator|reptile|Crocodilia|Alligatoridae|wetland|americas|predator
Green sea turtle|reptile|Testudines|Cheloniidae|marine,coastal|worldwide|migratory
Leatherback sea turtle|reptile|Testudines|Dermochelyidae|marine|worldwide|migratory
Galápagos tortoise|reptile|Testudines|Testudinidae|alpine,grassland|americas|herbivore
Aldabra giant tortoise|reptile|Testudines|Testudinidae|coastal|africa|herbivore
King cobra|reptile|Squamata|Elapidae|forest|asia|venomous
Black mamba|reptile|Squamata|Elapidae|grassland,woodland|africa|venomous
Reticulated python|reptile|Squamata|Pythonidae|forest|asia|predator
Green anaconda|reptile|Squamata|Boidae|wetland|americas|predator
Veiled chameleon|reptile|Squamata|Chamaeleonidae|desert,woodland|asia|arboreal
Common leopard gecko|reptile|Squamata|Eublepharidae|desert|asia|nocturnal
Green iguana|reptile|Squamata|Iguanidae|forest,coastal|americas|herbivore,arboreal
Gila monster|reptile|Squamata|Helodermatidae|desert|americas|venomous
Tuatara|reptile|Rhynchocephalia|Sphenodontidae|forest|oceania|nocturnal
Common basilisk|reptile|Squamata|Corytophanidae|forest,wetland|americas|
Frill-necked lizard|reptile|Squamata|Agamidae|woodland|oceania|arboreal
Marine iguana|reptile|Squamata|Iguanidae|coastal,marine|americas|herbivore
Axolotl|amphibian|Caudata|Ambystomatidae|wetland|americas|
Chinese giant salamander|amphibian|Caudata|Cryptobranchidae|wetland,forest|asia|
Fire salamander|amphibian|Caudata|Salamandridae|forest|europe|
Golden poison frog|amphibian|Anura|Dendrobatidae|forest|americas|venomous
Red-eyed tree frog|amphibian|Anura|Hylidae|forest|americas|arboreal,nocturnal
Poison dart frog|amphibian|Anura|Dendrobatidae|forest|americas|venomous
American bullfrog|amphibian|Anura|Ranidae|wetland|americas|
Common toad|amphibian|Anura|Bufonidae|woodland,urban|europe,asia|
Darwin's frog|amphibian|Anura|Rhinodermatidae|forest|americas|
Great white shark|fish|Lamniformes|Lamnidae|marine,coastal|worldwide|predator
Whale shark|fish|Orectolobiformes|Rhincodontidae|marine|worldwide|
Tiger shark|fish|Carcharhiniformes|Carcharhinidae|marine,coastal|worldwide|predator
Great hammerhead|fish|Carcharhiniformes|Sphyrnidae|marine,coastal|worldwide|predator
Manta ray|fish|Myliobatiformes|Myliobatidae|marine|worldwide|
Atlantic bluefin tuna|fish|Scombriformes|Scombridae|marine|worldwide|migratory,predator
Atlantic salmon|fish|Salmoniformes|Salmonidae|marine,wetland|europe,americas|migratory
Red-bellied piranha|fish|Characiformes|Serrasalmidae|wetland|americas|predator,social
Seahorse|fish|Syngnathiformes|Syngnathidae|marine,coastal|worldwide|
Clownfish|fish|Perciformes|Pomacentridae|marine|oceania,asia|social
European eel|fish|Anguilliformes|Anguillidae|wetland,marine|europe,americas|migratory
Ocean sunfish|fish|Tetraodontiformes|Molidae|marine|worldwide|
Pufferfish|fish|Tetraodontiformes|Tetraodontidae|marine|worldwide|venomous
Anglerfish|fish|Lophiiformes|Lophiidae|marine|worldwide|predator
Coelacanth|fish|Coelacanthiformes|Latimeriidae|marine|africa|nocturnal
Queensland lungfish|fish|Ceratodontiformes|Ceratodontidae|wetland|oceania|
Electric eel|fish|Gymnotiformes|Gymnotidae|wetland|americas|venomous
Goldfish|fish|Cypriniformes|Cyprinidae|wetland|asia|
Common carp|fish|Cypriniformes|Cyprinidae|wetland,farmland|europe,asia|
Wels catfish|fish|Siluriformes|Siluridae|wetland|europe,asia|predator
Common octopus|invertebrate|Octopoda|Octopodidae|marine,coastal|worldwide|predator,camouflage
Giant Pacific octopus|invertebrate|Octopoda|Enteroctopodidae|marine|oceania,asia,americas|predator
Blue-ringed octopus|invertebrate|Octopoda|Octopodidae|marine,coastal|oceania|venomous
Common cuttlefish|invertebrate|Sepiida|Sepiidae|marine|europe,asia,africa|camouflage
Giant squid|invertebrate|Oegopsida|Architeuthidae|marine|worldwide|predator
Chambered nautilus|invertebrate|Nautilida|Nautilidae|marine|oceania,asia|nocturnal
Goliath birdeater|invertebrate|Araneae|Theraphosidae|forest|americas|venomous
Emperor scorpion|invertebrate|Scorpiones|Scorpionidae|forest,desert|africa|venomous,burrower
Western honey bee|invertebrate|Hymenoptera|Apidae|farmland,urban|worldwide|social
Leafcutter ant|invertebrate|Hymenoptera|Formicidae|forest|americas|social
Monarch butterfly|invertebrate|Lepidoptera|Nymphalidae|farmland,urban|americas|migratory
Atlas moth|invertebrate|Lepidoptera|Saturniidae|forest|asia|
Silkworm|invertebrate|Lepidoptera|Bombycidae|farmland|asia|
Emperor dragonfly|invertebrate|Odonata|Aeshnidae|wetland|europe,asia|predator
Praying mantis|invertebrate|Mantodea|Mantidae|grassland,urban|worldwide|predator,camouflage
Migratory locust|invertebrate|Orthoptera|Acrididae|grassland,farmland|africa,asia|migratory
Periodical cicada|invertebrate|Hemiptera|Cicadidae|woodland|americas|
Mosquito|invertebrate|Diptera|Culicidae|wetland,urban|worldwide|
Housefly|invertebrate|Diptera|Muscidae|urban,farmland|worldwide|
Flea|invertebrate|Siphonaptera|Pulicidae|urban|worldwide|
European lobster|invertebrate|Decapoda|Nephropidae|marine|europe|
Coconut crab|invertebrate|Decapoda|Coenobitidae|coastal,forest|oceania,asia|predator
Japanese spider crab|invertebrate|Decapoda|Majidae|marine|asia|
Mantis shrimp|invertebrate|Stomatopoda|Squillidae|marine,coastal|worldwide|predator
Common starfish|invertebrate|Asteroidea|Asteriidae|marine,coastal|europe,americas|predator
Sea urchin|invertebrate|Echinoidea|Echinidae|marine|worldwide|
Box jellyfish|invertebrate|Cubozoa|Chirodropidae|marine,coastal|oceania,asia|venomous
Moon jellyfish|invertebrate|Scyphozoa|Ulmaridae|marine|worldwide|
Brain coral|invertebrate|Anthozoa|Mussidae|marine|americas|social
Earthworm|invertebrate|Clitellata|Lumbricidae|farmland,woodland|worldwide|burrower
Medicinal leech|invertebrate|Hirudinea|Hirudinidae|wetland|europe|
Garden snail|invertebrate|Stylommatophora|Helicidae|woodland,urban|europe|
Blue mussel|invertebrate|Mytilida|Mytilidae|marine,coastal|europe,americas|social
Pacific oyster|invertebrate|Ostreida|Ostreidae|marine,coastal|asia,oceania|social
Atlantic horseshoe crab|invertebrate|Xiphosura|Limulidae|coastal|americas|
Tardigrade|invertebrate|Tardigrada|Macrobiotidae|forest,wetland|worldwide|
Giant centipede|invertebrate|Scolopendromorpha|Scolopendridae|forest|americas|venomous
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
                if 0.3 <= cm <= 3500:
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
                if 0.01 <= grams <= 200000000:
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
        if len(bits) < 4:
            continue
        bits += [""] * (7 - len(bits))
        rows.append({
            "title": bits[0], "cls": bits[1], "order": bits[2], "family": bits[3],
            "habitats": [h for h in bits[4].split(",") if h],
            "regions": [r for r in bits[5].split(",") if r],
            "traits": [t for t in bits[6].split(",") if t],
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
            "h": row["habitats"], "r": row["regions"], "t": row["traits"],
            "fam": row["family"], "ord": row["order"], "cls": row["cls"],
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
    facets = {"class": {}, "habitat": {}, "region": {}, "trait": {}, "status": {}}
    groups = []
    total = photos = songs = statuses = 0
    for order in sorted(orders, key=lambda o: (-sum(len(v) for v in orders[o].values()), o)):
        families = orders[order]
        animals = [a for fam in families.values() for a in fam]
        key = slug(order)
        with open(os.path.join(OUT, key + ".json"), "w", encoding="utf-8") as fh:
            json.dump({"key": key, "title": order, "families": [
                {"n": fam, "c": len(families[fam]), "s": sorted(families[fam], key=lambda a: a["n"])}
                for fam in sorted(families, key=lambda f: (-len(families[f]), f))
            ]}, fh, ensure_ascii=False, indent=1)
        total += len(animals)
        photos += sum(1 for a in animals if a.get("i"))
        songs += sum(1 for a in animals if a.get("a"))
        statuses += sum(1 for a in animals if a.get("st"))
        for animal in animals:
            facets["class"][animal["cls"]] = facets["class"].get(animal["cls"], 0) + 1
            for value in animal["h"]:
                facets["habitat"][value] = facets["habitat"].get(value, 0) + 1
            for value in animal["r"]:
                facets["region"][value] = facets["region"].get(value, 0) + 1
            for value in animal["t"]:
                facets["trait"][value] = facets["trait"].get(value, 0) + 1
            if animal.get("st"):
                facets["status"][animal["st"]] = facets["status"].get(animal["st"], 0) + 1
        groups.append({"key": key, "num": "%02d" % (len(groups) + 1), "title": order,
                       "animals": len(animals), "families": len(families),
                       "photos": sum(1 for a in animals if a.get("i")),
                       "songs": sum(1 for a in animals if a.get("a"))})

    index = {
        "generated": time.strftime("%Y-%m-%d"),
        "source": "en.wikipedia.org + wikidata.org",
        "animals": total,
        "families": len({a["fam"] for fam in orders.values() for f in fam.values() for a in f}),
        "orders": len(orders),
        "classes": len({a["cls"] for fam in orders.values() for f in fam.values() for a in f}),
        "photos": photos,
        "songs": songs,
        "statuses": statuses,
        "facets": facets,
        "groups": groups,
    }
    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as fh:
        json.dump(index, fh, ensure_ascii=False, indent=1)
    print(json.dumps({k: index[k] for k in ("animals", "families", "orders", "classes", "photos", "songs", "statuses")}))
    print("classes:", index["facets"]["class"])


if __name__ == "__main__":
    main()
