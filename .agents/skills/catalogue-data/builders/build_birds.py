#!/usr/bin/env python3
"""Build docs/birds/data/ — the bird catalogue behind docs/birdsIndex.html.

Sources, all external and cited on the page:
  * en.wikipedia.org REST summary      -> lead image, intro text, canonical URL, Wikidata id
  * en.wikipedia.org REST media-list   -> first audio file on the article (song or call)
  * en.wikipedia.org action API        -> real file URL for that audio (imageinfo)
  * query.wikidata.org SPARQL          -> IUCN status (P141), length (P2043), mass (P2067)

The species table below is the only part written by hand: title, order, family,
habitats, regions, traits. Everything else is fetched, so the page can be rebuilt.
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
import urllib.request
from concurrent.futures import ThreadPoolExecutor

UA = {"User-Agent": "devblog-birds/1.0 (https://blog.odicforcesounds.com; contact via site)"}
OUT = "docs/birds/data"
LIMIT = int(sys.argv[1]) if len(sys.argv) > 1 else 0

# title | order | family | habitats | regions | traits
SPEC = """
Golden eagle|Accipitriformes|Accipitridae|alpine,grassland,woodland|europe,asia,americas|raptor
Bald eagle|Accipitriformes|Accipitridae|coastal,wetland|americas|raptor,fish-eater
White-tailed eagle|Accipitriformes|Accipitridae|coastal,wetland|europe,asia|raptor,fish-eater
Red-tailed hawk|Accipitriformes|Accipitridae|grassland,woodland,farmland|americas|raptor
Common buzzard|Accipitriformes|Accipitridae|farmland,woodland|europe,asia|raptor
Eurasian sparrowhawk|Accipitriformes|Accipitridae|woodland,urban|europe,asia|raptor
Northern goshawk|Accipitriformes|Accipitridae|forest|europe,asia,americas|raptor
Osprey|Accipitriformes|Pandionidae|coastal,wetland,marine|worldwide|raptor,fish-eater,migratory
Harpy eagle|Accipitriformes|Accipitridae|forest|americas|raptor
Philippine eagle|Accipitriformes|Accipitridae|forest|asia|raptor
Egyptian vulture|Accipitriformes|Accipitridae|desert,grassland|africa,asia,europe|scavenger,tool-user
Bearded vulture|Accipitriformes|Accipitridae|alpine|europe,africa,asia|scavenger
Griffon vulture|Accipitriformes|Accipitridae|alpine,grassland|europe,africa,asia|scavenger,colonial
Secretarybird|Accipitriformes|Sagittariidae|grassland|africa|raptor,ground-nester
Black kite|Accipitriformes|Accipitridae|urban,wetland|europe,asia,africa,oceania|raptor,migratory
Western marsh harrier|Accipitriformes|Accipitridae|wetland|europe,asia,africa|raptor
Andean condor|Cathartiformes|Cathartidae|alpine|americas|scavenger
California condor|Cathartiformes|Cathartidae|alpine,desert|americas|scavenger
Turkey vulture|Cathartiformes|Cathartidae|woodland,farmland|americas|scavenger
King vulture|Cathartiformes|Cathartidae|forest|americas|scavenger
Peregrine falcon|Falconiformes|Falconidae|coastal,urban,alpine|worldwide|raptor
Common kestrel|Falconiformes|Falconidae|farmland,urban|europe,asia,africa|raptor
American kestrel|Falconiformes|Falconidae|grassland,farmland|americas|raptor
Merlin|Falconiformes|Falconidae|grassland,coastal|europe,asia,americas|raptor,migratory
Gyrfalcon|Falconiformes|Falconidae|alpine,coastal|europe,asia,americas|raptor
Eurasian hobby|Falconiformes|Falconidae|woodland,farmland|europe,asia,africa|raptor,migratory
Barn owl|Strigiformes|Tytonidae|farmland,grassland,urban|worldwide|owl,nocturnal
Great horned owl|Strigiformes|Strigidae|woodland,desert|americas|owl,nocturnal
Snowy owl|Strigiformes|Strigidae|alpine,grassland|europe,asia,americas|owl,day-hunter
Eurasian eagle-owl|Strigiformes|Strigidae|forest,woodland|europe,asia|owl,nocturnal
Tawny owl|Strigiformes|Strigidae|woodland,urban|europe|owl,nocturnal
Little owl|Strigiformes|Strigidae|farmland,desert|europe,asia,africa|owl
Burrowing owl|Strigiformes|Strigidae|grassland,desert|americas|owl,ground-nester
Northern saw-whet owl|Strigiformes|Strigidae|forest|americas|owl,nocturnal
Great grey owl|Strigiformes|Strigidae|forest|europe,asia,americas|owl
Long-eared owl|Strigiformes|Strigidae|woodland|europe,asia,americas|owl,nocturnal
Short-eared owl|Strigiformes|Strigidae|grassland,wetland|worldwide|owl,day-hunter
Spectacled owl|Strigiformes|Strigidae|forest|americas|owl,nocturnal
Powerful owl|Strigiformes|Strigidae|forest|oceania|owl,nocturnal
Tawny frogmouth|Podargiformes|Podargidae|woodland|oceania|nocturnal,camouflage
Kea|Psittaciformes|Strigopidae|alpine|oceania|parrot,tool-user
Kākāpō|Psittaciformes|Strigopidae|forest|oceania|parrot,flightless,nocturnal
Kākā|Psittaciformes|Strigopidae|forest|oceania|parrot
Sulphur-crested cockatoo|Psittaciformes|Cacatuidae|forest,urban|oceania|parrot
Galah|Psittaciformes|Cacatuidae|grassland,farmland|oceania|parrot
Palm cockatoo|Psittaciformes|Cacatuidae|forest|oceania|parrot,tool-user
Cockatiel|Psittaciformes|Cacatuidae|grassland|oceania|parrot
Budgerigar|Psittaciformes|Psittaculidae|grassland,desert|oceania|parrot,nomadic
Rainbow lorikeet|Psittaciformes|Psittaculidae|forest,urban|oceania|parrot,nectar
Rose-ringed parakeet|Psittaciformes|Psittaculidae|urban,woodland|africa,asia|parrot
Night parrot|Psittaciformes|Psittaculidae|desert,grassland|oceania|parrot,nocturnal
Grey parrot|Psittaciformes|Psittacidae|forest|africa|parrot,mimic
Eclectus parrot|Psittaciformes|Psittacidae|forest|oceania|parrot
Scarlet macaw|Psittaciformes|Psittacidae|forest|americas|parrot
Blue-and-yellow macaw|Psittaciformes|Psittacidae|forest|americas|parrot
Hyacinth macaw|Psittaciformes|Psittacidae|forest,grassland|americas|parrot
Great green macaw|Psittaciformes|Psittacidae|forest|americas|parrot
Monk parakeet|Psittaciformes|Psittacidae|urban,grassland|americas|parrot,colonial
Sun parakeet|Psittaciformes|Psittacidae|forest|americas|parrot
Rock dove|Columbiformes|Columbidae|urban,coastal|worldwide|colonial
Mourning dove|Columbiformes|Columbidae|woodland,urban|americas|migratory
Eurasian collared dove|Columbiformes|Columbidae|urban,farmland|europe,asia|
Common wood pigeon|Columbiformes|Columbidae|woodland,farmland|europe|
European turtle dove|Columbiformes|Columbidae|farmland,woodland|europe,africa|migratory
Passenger pigeon|Columbiformes|Columbidae|forest|americas|extinct,colonial,migratory
Dodo|Columbiformes|Columbidae|forest|africa|extinct,flightless
Nicobar pigeon|Columbiformes|Columbidae|forest,coastal|asia,oceania|colonial
Victoria crowned pigeon|Columbiformes|Columbidae|forest|oceania|
Zebra dove|Columbiformes|Columbidae|urban,grassland|asia|
Red junglefowl|Galliformes|Phasianidae|forest|asia|gamebird
Indian peafowl|Galliformes|Phasianidae|forest,farmland|asia|gamebird
Wild turkey|Galliformes|Phasianidae|forest|americas|gamebird
Western capercaillie|Galliformes|Phasianidae|forest|europe,asia|gamebird,lek
Willow ptarmigan|Galliformes|Phasianidae|alpine|europe,asia,americas|gamebird,camouflage
Helmeted guineafowl|Galliformes|Numididae|grassland,farmland|africa|gamebird,colonial
Northern bobwhite|Galliformes|Odontophoridae|grassland,farmland|americas|gamebird
Great curassow|Galliformes|Cracidae|forest|americas|gamebird
Maleo|Galliformes|Megapodiidae|forest,coastal|asia|ground-nester
Malleefowl|Galliformes|Megapodiidae|desert,woodland|oceania|ground-nester
Mallard|Anseriformes|Anatidae|wetland,urban|worldwide|waterfowl,migratory
Mandarin duck|Anseriformes|Anatidae|forest,wetland|asia|waterfowl
Wood duck|Anseriformes|Anatidae|forest,wetland|americas|waterfowl
Mute swan|Anseriformes|Anatidae|wetland|europe,asia|waterfowl
Whooper swan|Anseriformes|Anatidae|wetland|europe,asia|waterfowl,migratory
Black swan|Anseriformes|Anatidae|wetland|oceania|waterfowl
Canada goose|Anseriformes|Anatidae|wetland,grassland|americas|waterfowl,migratory
Barnacle goose|Anseriformes|Anatidae|wetland,grassland|europe|waterfowl,migratory
Snow goose|Anseriformes|Anatidae|wetland,alpine|americas|waterfowl,colonial
Greylag goose|Anseriformes|Anatidae|wetland,farmland|europe,asia|waterfowl
King eider|Anseriformes|Anatidae|coastal,marine|europe,asia,americas|waterfowl,sea-duck
Harlequin duck|Anseriformes|Anatidae|coastal,marine|europe,asia,americas|waterfowl,sea-duck
Northern shoveler|Anseriformes|Anatidae|wetland|worldwide|waterfowl,migratory
Common merganser|Anseriformes|Anatidae|wetland,forest|europe,asia,americas|waterfowl,fish-eater
Emperor penguin|Sphenisciformes|Spheniscidae|marine,antarctica|antarctica|flightless,colonial
King penguin|Sphenisciformes|Spheniscidae|marine,antarctica|antarctica|flightless,colonial
Adélie penguin|Sphenisciformes|Spheniscidae|marine,antarctica|antarctica|flightless,colonial
Gentoo penguin|Sphenisciformes|Spheniscidae|marine,antarctica|antarctica|flightless,colonial
Chinstrap penguin|Sphenisciformes|Spheniscidae|marine,antarctica|antarctica|flightless,colonial
African penguin|Sphenisciformes|Spheniscidae|coastal,marine|africa|flightless,colonial
Galápagos penguin|Sphenisciformes|Spheniscidae|coastal,marine|americas|flightless
Little penguin|Sphenisciformes|Spheniscidae|coastal,marine|oceania|flightless,nocturnal
Macaroni penguin|Sphenisciformes|Spheniscidae|marine|antarctica|flightless,colonial
Southern rockhopper penguin|Sphenisciformes|Spheniscidae|marine|antarctica|flightless,colonial
Humboldt penguin|Sphenisciformes|Spheniscidae|coastal,marine|americas|flightless
Magellanic penguin|Sphenisciformes|Spheniscidae|coastal,marine|americas|flightless,colonial,migratory
Wandering albatross|Procellariiformes|Diomedeidae|marine|antarctica,oceania|seabird,colonial
Laysan albatross|Procellariiformes|Diomedeidae|marine|oceania,americas|seabird,colonial
Northern fulmar|Procellariiformes|Procellariidae|marine,coastal|europe,americas|seabird
Manx shearwater|Procellariiformes|Procellariidae|marine|europe,americas|seabird,nocturnal
Snow petrel|Procellariiformes|Procellariidae|marine|antarctica|seabird
Wilson's storm petrel|Procellariiformes|Oceanitidae|marine|worldwide|seabird
Atlantic puffin|Charadriiformes|Alcidae|marine,coastal|europe,americas|seabird,colonial,fish-eater
Razorbill|Charadriiformes|Alcidae|marine,coastal|europe|seabird
Little auk|Charadriiformes|Alcidae|marine,alpine|europe,americas|seabird,colonial
European herring gull|Charadriiformes|Laridae|coastal,urban|europe,americas|seabird
Lesser black-backed gull|Charadriiformes|Laridae|coastal,urban|europe|migratory
Black-headed gull|Charadriiformes|Laridae|wetland,urban|europe,asia|colonial
Great black-backed gull|Charadriiformes|Laridae|coastal|europe,americas|seabird
Arctic tern|Charadriiformes|Laridae|marine,coastal|worldwide|seabird,migratory
Common tern|Charadriiformes|Laridae|wetland,coastal|europe,americas|migratory
Sooty tern|Charadriiformes|Laridae|marine|worldwide|seabird,colonial
Black skimmer|Charadriiformes|Laridae|coastal|americas|seabird
Inca tern|Charadriiformes|Laridae|coastal,marine|americas|seabird
Eurasian oystercatcher|Charadriiformes|Haematopodidae|coastal|europe,asia|wader
Northern lapwing|Charadriiformes|Charadriidae|farmland,grassland|europe,asia|wader,migratory
Killdeer|Charadriiformes|Charadriidae|grassland,urban|americas|wader
Red knot|Charadriiformes|Scolopacidae|coastal|worldwide|wader,migratory
Bar-tailed godwit|Charadriiformes|Scolopacidae|coastal,wetland|worldwide|wader,migratory
Dunlin|Charadriiformes|Scolopacidae|coastal,wetland|worldwide|wader,migratory,colonial
Sanderling|Charadriiformes|Scolopacidae|coastal|worldwide|wader,migratory
Ruff (bird)|Charadriiformes|Scolopacidae|wetland,grassland|europe,asia|wader,lek
Eurasian curlew|Charadriiformes|Scolopacidae|coastal,grassland|europe,asia|wader
Great skua|Charadriiformes|Stercorariidae|marine|europe|seabird
South polar skua|Charadriiformes|Stercorariidae|marine|antarctica|seabird
Pied avocet|Charadriiformes|Recurvirostridae|wetland|europe,asia,africa|wader
Common crane|Gruiformes|Gruidae|wetland,farmland|europe,asia|migratory,colonial
Demoiselle crane|Gruiformes|Gruidae|grassland,wetland|asia,africa|migratory
Sandhill crane|Gruiformes|Gruidae|wetland,grassland|americas|migratory
Whooping crane|Gruiformes|Gruidae|wetland|americas|
Grey crowned crane|Gruiformes|Gruidae|wetland,grassland|africa|
Sarus crane|Gruiformes|Gruidae|wetland,farmland|asia,oceania|
Water rail|Gruiformes|Rallidae|wetland|europe,asia|
Common moorhen|Gruiformes|Rallidae|wetland|worldwide|
Eurasian coot|Gruiformes|Rallidae|wetland|europe,asia,africa|
Limpkin|Gruiformes|Aramidae|wetland|americas|
Grey-winged trumpeter|Gruiformes|Psophiidae|forest|americas|
Sunbittern|Eurypygiformes|Eurypygidae|forest,wetland|americas|
Kagu|Eurypygiformes|Rhynochetidae|forest|oceania|flightless
White stork|Ciconiiformes|Ciconiidae|wetland,farmland,urban|europe,africa|migratory
Black stork|Ciconiiformes|Ciconiidae|forest,wetland|europe,asia|migratory
Marabou stork|Ciconiiformes|Ciconiidae|wetland,urban|africa|scavenger
Yellow-billed stork|Ciconiiformes|Ciconiidae|wetland|africa|
Jabiru|Ciconiiformes|Ciconiidae|wetland|americas|colonial
Painted stork|Ciconiiformes|Ciconiidae|wetland|asia|colonial
Great white pelican|Pelecaniformes|Pelecanidae|wetland|africa,asia,europe|colonial
Brown pelican|Pelecaniformes|Pelecanidae|coastal,marine|americas|seabird
Dalmatian pelican|Pelecaniformes|Pelecanidae|wetland|europe,asia|
Grey heron|Pelecaniformes|Ardeidae|wetland|europe,asia,africa|
Great blue heron|Pelecaniformes|Ardeidae|wetland|americas|
Great egret|Pelecaniformes|Ardeidae|wetland|worldwide|
Little egret|Pelecaniformes|Ardeidae|wetland,coastal|europe,asia,africa,oceania|
Western cattle egret|Pelecaniformes|Ardeidae|farmland,grassland|worldwide|migratory
Black-crowned night heron|Pelecaniformes|Ardeidae|wetland|worldwide|nocturnal
Goliath heron|Pelecaniformes|Ardeidae|wetland|africa|
Purple heron|Pelecaniformes|Ardeidae|wetland|europe,asia,africa|
Snowy egret|Pelecaniformes|Ardeidae|wetland|americas|
Green heron|Pelecaniformes|Ardeidae|wetland|americas|tool-user
Shoebill|Pelecaniformes|Balaenicipitidae|wetland|africa|
Hamerkop|Pelecaniformes|Scopidae|wetland|africa|
African sacred ibis|Pelecaniformes|Threskiornithidae|wetland|africa|
Scarlet ibis|Pelecaniformes|Threskiornithidae|wetland|americas|colonial
Northern bald ibis|Pelecaniformes|Threskiornithidae|desert,grassland|africa,asia|
Roseate spoonbill|Pelecaniformes|Threskiornithidae|wetland|americas|
Eurasian spoonbill|Pelecaniformes|Threskiornithidae|wetland|europe,asia,africa|
Blue-footed booby|Suliformes|Sulidae|marine,coastal|americas|seabird,colonial
Northern gannet|Suliformes|Sulidae|marine|europe,americas|seabird,colonial
Red-footed booby|Suliformes|Sulidae|marine|worldwide|seabird,colonial
Great cormorant|Suliformes|Phalacrocoracidae|coastal,wetland|europe,asia,africa|
Double-crested cormorant|Suliformes|Phalacrocoracidae|coastal,wetland|americas|
Flightless cormorant|Suliformes|Phalacrocoracidae|coastal,marine|americas|flightless
Anhinga|Suliformes|Anhingidae|wetland|americas|
Great frigatebird|Suliformes|Fregatidae|marine|worldwide|seabird,kleptoparasite
Magnificent frigatebird|Suliformes|Fregatidae|marine|americas|seabird,kleptoparasite
Greater flamingo|Phoenicopteriformes|Phoenicopteridae|wetland|africa,asia,europe|colonial
Lesser flamingo|Phoenicopteriformes|Phoenicopteridae|wetland|africa,asia|colonial
Chilean flamingo|Phoenicopteriformes|Phoenicopteridae|wetland|americas|colonial
James's flamingo|Phoenicopteriformes|Phoenicopteridae|alpine,wetland|americas|colonial
Great crested grebe|Podicipediformes|Podicipedidae|wetland|europe,asia,africa,oceania|
Little grebe|Podicipediformes|Podicipedidae|wetland|europe,asia,africa|
Western grebe|Podicipediformes|Podicipedidae|wetland|americas|colonial
Hooded grebe|Podicipediformes|Podicipedidae|alpine,wetland|americas|
Red-billed tropicbird|Phaethontiformes|Phaethontidae|marine|americas,africa|seabird
White-tailed tropicbird|Phaethontiformes|Phaethontidae|marine|worldwide|seabird
Common loon|Gaviiformes|Gaviidae|wetland,marine|europe,americas|fish-eater
Red-throated loon|Gaviiformes|Gaviidae|wetland,marine|europe,asia,americas|migratory
Yellow-billed loon|Gaviiformes|Gaviidae|alpine,wetland|europe,asia,americas|
Common ostrich|Struthioniformes|Struthionidae|grassland,desert|africa|flightless
Somali ostrich|Struthioniformes|Struthionidae|grassland,desert|africa|flightless
Emu|Casuariiformes|Casuariidae|grassland,woodland|oceania|flightless
Southern cassowary|Casuariiformes|Casuariidae|forest|oceania|flightless
North Island brown kiwi|Apterygiformes|Apterygidae|forest|oceania|flightless,nocturnal
Okarito kiwi|Apterygiformes|Apterygidae|forest|oceania|flightless,nocturnal
Greater rhea|Rheiformes|Rheidae|grassland|americas|flightless
Lesser rhea|Rheiformes|Rheidae|alpine,grassland|americas|flightless
Great tinamou|Tinamiformes|Tinamidae|forest|americas|
Elegant crested tinamou|Tinamiformes|Tinamidae|grassland|americas|
Great bustard|Otidiformes|Otididae|grassland,farmland|europe,asia|
Kori bustard|Otidiformes|Otididae|grassland|africa|
Little bustard|Otidiformes|Otididae|grassland|europe,asia|
Pallas's sandgrouse|Pterocliformes|Pteroclidae|desert,grassland|asia|
Namaqua sandgrouse|Pterocliformes|Pteroclidae|desert|africa|
Common cuckoo|Cuculiformes|Cuculidae|woodland,farmland|europe,asia,africa|brood-parasite,migratory
Greater roadrunner|Cuculiformes|Cuculidae|desert,woodland|americas|
Groove-billed ani|Cuculiformes|Cuculidae|forest,grassland|americas|colonial
Guira cuckoo|Cuculiformes|Cuculidae|grassland,wetland|americas|colonial
Channel-billed cuckoo|Cuculiformes|Cuculidae|forest,urban|oceania|brood-parasite,migratory
European nightjar|Caprimulgiformes|Caprimulgidae|woodland,grassland|europe,asia,africa|nocturnal,migratory
Common poorwill|Caprimulgiformes|Caprimulgidae|desert,grassland|americas|nocturnal
Eastern whip-poor-will|Caprimulgiformes|Caprimulgidae|forest,woodland|americas|nocturnal,migratory
Oilbird|Caprimulgiformes|Steatornithidae|forest|americas|nocturnal,echolocation
Southern ground hornbill|Bucerotiformes|Bucerotidae|grassland|africa|ground-nester
Rhinoceros hornbill|Bucerotiformes|Bucerotidae|forest|asia|
Great hornbill|Bucerotiformes|Bucerotidae|forest|asia|
Eurasian hoopoe|Bucerotiformes|Upupidae|farmland,grassland|europe,asia,africa|migratory
Common kingfisher|Coraciiformes|Alcedinidae|wetland|europe,asia,africa|fish-eater
Belted kingfisher|Coraciiformes|Alcedinidae|wetland,coastal|americas|fish-eater
Laughing kookaburra|Coraciiformes|Alcedinidae|woodland,urban|oceania|
European bee-eater|Coraciiformes|Meropidae|farmland,grassland|europe,asia,africa|migratory,colonial
European roller|Coraciiformes|Coraciidae|farmland,woodland|europe,asia,africa|migratory
Indian roller|Coraciiformes|Coraciidae|farmland,urban|asia|
Amazonian motmot|Coraciiformes|Momotidae|forest|americas|
Great spotted woodpecker|Piciformes|Picidae|woodland,urban|europe,asia|woodpecker
Black woodpecker|Piciformes|Picidae|forest|europe,asia|woodpecker
European green woodpecker|Piciformes|Picidae|woodland,farmland|europe|woodpecker
Pileated woodpecker|Piciformes|Picidae|forest|americas|woodpecker
Downy woodpecker|Piciformes|Picidae|woodland,urban|americas|woodpecker
Acorn woodpecker|Piciformes|Picidae|woodland|americas|colonial
Ivory-billed woodpecker|Piciformes|Picidae|forest|americas|woodpecker
Toco toucan|Piciformes|Ramphastidae|forest|americas|
Keel-billed toucan|Piciformes|Ramphastidae|forest|americas|
Greater honeyguide|Piciformes|Indicatoridae|woodland|africa|brood-parasite
Coppersmith barbet|Piciformes|Megalaimidae|urban,woodland|asia|
Common swift|Apodiformes|Apodidae|urban,woodland|europe,asia,africa|migratory,aerial
Alpine swift|Apodiformes|Apodidae|alpine,urban|europe,asia,africa|migratory,aerial
Chimney swift|Apodiformes|Apodidae|urban|americas|migratory,aerial
Ruby-throated hummingbird|Apodiformes|Trochilidae|forest,urban|americas|hummingbird,nectar,migratory
Anna's hummingbird|Apodiformes|Trochilidae|woodland,urban|americas|hummingbird,nectar
Rufous hummingbird|Apodiformes|Trochilidae|forest,alpine|americas|hummingbird,nectar,migratory
Bee hummingbird|Apodiformes|Trochilidae|forest|americas|hummingbird,nectar
Sword-billed hummingbird|Apodiformes|Trochilidae|forest,alpine|americas|hummingbird,nectar
Marvelous spatuletail|Apodiformes|Trochilidae|forest|americas|hummingbird,nectar
Giant hummingbird|Apodiformes|Trochilidae|alpine,woodland|americas|hummingbird,nectar
Resplendent quetzal|Trogoniformes|Trogonidae|forest|americas|
Elegant trogon|Trogoniformes|Trogonidae|forest,woodland|americas|
Narina trogon|Trogoniformes|Trogonidae|forest|africa|
Great blue turaco|Musophagiformes|Musophagidae|forest|africa|
Knysna turaco|Musophagiformes|Musophagidae|forest|africa|
Violet turaco|Musophagiformes|Musophagidae|woodland,urban|africa|
Speckled mousebird|Coliiformes|Coliidae|woodland,urban|africa|
Red-faced mousebird|Coliiformes|Coliidae|woodland|africa|
Cuckoo roller|Leptosomiformes|Leptosomidae|forest|africa|
Red-legged seriema|Cariamiformes|Cariamidae|grassland|americas|
Black-legged seriema|Cariamiformes|Cariamidae|desert,grassland|americas|
Hoatzin|Opisthocomiformes|Opisthocomidae|forest,wetland|americas|
Common raven|Passeriformes|Corvidae|alpine,woodland,urban|worldwide|songbird
Carrion crow|Passeriformes|Corvidae|farmland,urban|europe,asia|songbird
Rook (bird)|Passeriformes|Corvidae|farmland,grassland|europe,asia|songbird
Western jackdaw|Passeriformes|Corvidae|urban,farmland|europe,asia|songbird
Eurasian magpie|Passeriformes|Corvidae|woodland,farmland,urban|europe,asia|songbird
Azure-winged magpie|Passeriformes|Corvidae|woodland|europe,asia|songbird
Taiwan blue magpie|Passeriformes|Corvidae|forest|asia|songbird
Blue jay|Passeriformes|Corvidae|forest,urban|americas|songbird
Steller's jay|Passeriformes|Corvidae|forest|americas|songbird
Canada jay|Passeriformes|Corvidae|forest,alpine|americas|songbird
Siberian jay|Passeriformes|Corvidae|forest|europe,asia|songbird
Clark's nutcracker|Passeriformes|Corvidae|alpine,forest|americas|songbird
Australian raven|Passeriformes|Corvidae|woodland,urban|oceania|songbird
New Caledonian crow|Passeriformes|Corvidae|forest|oceania|songbird,tool-user
Hawaiian crow|Passeriformes|Corvidae|forest|oceania|songbird
Pinyon jay|Passeriformes|Corvidae|desert,woodland|americas|songbird,colonial
Great tit|Passeriformes|Paridae|woodland,urban|europe,asia|songbird
Eurasian blue tit|Passeriformes|Paridae|woodland,urban|europe|songbird
Coal tit|Passeriformes|Paridae|forest|europe,asia|songbird
European crested tit|Passeriformes|Paridae|forest|europe|songbird
Willow tit|Passeriformes|Paridae|forest,woodland|europe,asia|songbird
Tufted titmouse|Passeriformes|Paridae|woodland,urban|americas|songbird
Black-capped chickadee|Passeriformes|Paridae|woodland,urban|americas|songbird
Boreal chickadee|Passeriformes|Paridae|forest|americas|songbird
Long-tailed tit|Passeriformes|Aegithalidae|woodland,urban|europe,asia|songbird
Eurasian penduline tit|Passeriformes|Remizidae|wetland,woodland|europe,asia|songbird
Bearded reedling|Passeriformes|Panuridae|wetland|europe,asia|songbird
Eurasian nuthatch|Passeriformes|Sittidae|woodland|europe,asia|songbird
Red-breasted nuthatch|Passeriformes|Sittidae|forest|americas|songbird
White-breasted nuthatch|Passeriformes|Sittidae|woodland,urban|americas|songbird
Wallcreeper|Passeriformes|Tichodromidae|alpine|europe,asia,africa|songbird
Eurasian treecreeper|Passeriformes|Certhiidae|woodland|europe,asia|songbird
Brown creeper|Passeriformes|Certhiidae|forest|americas|songbird
Eurasian wren|Passeriformes|Troglodytidae|woodland,urban|europe,asia,africa|songbird
Northern house wren|Passeriformes|Troglodytidae|woodland,urban|americas|songbird
Cactus wren|Passeriformes|Troglodytidae|desert|americas|songbird
Marsh wren|Passeriformes|Troglodytidae|wetland|americas|songbird
Northern mockingbird|Passeriformes|Mimidae|urban,woodland|americas|songbird,mimic
Grey catbird|Passeriformes|Mimidae|woodland,urban|americas|songbird,mimic
Brown thrasher|Passeriformes|Mimidae|woodland|americas|songbird,mimic
Common starling|Passeriformes|Sturnidae|urban,farmland|europe,asia|songbird,mimic,colonial
Common myna|Passeriformes|Sturnidae|urban,farmland|asia|songbird,mimic
Bali myna|Passeriformes|Sturnidae|forest|asia|songbird
Superb starling|Passeriformes|Sturnidae|grassland,urban|africa|songbird,colonial
Violet-backed starling|Passeriformes|Sturnidae|woodland|africa|songbird
Common blackbird|Passeriformes|Turdidae|woodland,urban|europe,asia,oceania|songbird
Song thrush|Passeriformes|Turdidae|woodland,urban|europe,asia|songbird,migratory
Mistle thrush|Passeriformes|Turdidae|woodland,farmland|europe,asia|songbird
American robin|Passeriformes|Turdidae|woodland,urban|americas|songbird
Eastern bluebird|Passeriformes|Turdidae|woodland,farmland|americas|songbird
Wood thrush|Passeriformes|Turdidae|forest|americas|songbird,migratory
Ring ouzel|Passeriformes|Turdidae|alpine,woodland|europe,asia|songbird,migratory
Fieldfare|Passeriformes|Turdidae|farmland,woodland|europe,asia|songbird,migratory
Redwing|Passeriformes|Turdidae|woodland,farmland|europe,asia|songbird,migratory
European robin|Passeriformes|Muscicapidae|woodland,urban|europe,asia|songbird
Common nightingale|Passeriformes|Muscicapidae|woodland,wetland|europe,asia,africa|songbird,migratory
European pied flycatcher|Passeriformes|Muscicapidae|woodland|europe,asia,africa|songbird,migratory
Spotted flycatcher|Passeriformes|Muscicapidae|woodland,urban|europe,asia,africa|songbird,migratory
Black redstart|Passeriformes|Muscicapidae|urban,alpine|europe,asia,africa|songbird,migratory
Common redstart|Passeriformes|Muscicapidae|woodland,farmland|europe,asia,africa|songbird,migratory
Bluethroat|Passeriformes|Muscicapidae|wetland,alpine|europe,asia|songbird,migratory
European stonechat|Passeriformes|Muscicapidae|grassland,heath|europe,asia,africa|songbird
Siberian rubythroat|Passeriformes|Muscicapidae|forest,woodland|asia|songbird,migratory
Eurasian blackcap|Passeriformes|Sylviidae|woodland,urban|europe,asia,africa|songbird,migratory
Garden warbler|Passeriformes|Sylviidae|woodland|europe,africa|songbird,migratory
Common whitethroat|Passeriformes|Sylviidae|farmland,woodland|europe,asia,africa|songbird,migratory
Dartford warbler|Passeriformes|Sylviidae|grassland|europe|songbird
Willow warbler|Passeriformes|Phylloscopidae|woodland,alpine|europe,asia|songbird,migratory
Common chiffchaff|Passeriformes|Phylloscopidae|woodland,urban|europe,asia,africa|songbird,migratory
Wood warbler|Passeriformes|Phylloscopidae|forest|europe,africa|songbird,migratory
Pallas's leaf warbler|Passeriformes|Phylloscopidae|forest|asia|songbird,migratory
Great reed warbler|Passeriformes|Acrocephalidae|wetland|europe,asia,africa|songbird,migratory
Sedge warbler|Passeriformes|Acrocephalidae|wetland|europe,africa|songbird,migratory
Marsh warbler|Passeriformes|Acrocephalidae|wetland|europe,africa|songbird,migratory
Icterine warbler|Passeriformes|Acrocephalidae|woodland|europe,africa|songbird,migratory
Barn swallow|Passeriformes|Hirundinidae|farmland,urban|worldwide|songbird,migratory,colonial
Common house martin|Passeriformes|Hirundinidae|urban,farmland|europe,asia,africa|songbird,migratory,colonial
Sand martin|Passeriformes|Hirundinidae|wetland,coastal|europe,asia,africa|songbird,migratory,colonial
Purple martin|Passeriformes|Hirundinidae|urban,wetland|americas|songbird,migratory,colonial
Tree swallow|Passeriformes|Hirundinidae|wetland,farmland|americas|songbird,migratory
White wagtail|Passeriformes|Motacillidae|urban,wetland|europe,asia,africa|songbird,migratory
Grey wagtail|Passeriformes|Motacillidae|wetland,urban|europe,asia,africa|songbird
Meadow pipit|Passeriformes|Motacillidae|grassland,alpine|europe,asia|songbird,migratory
Tree pipit|Passeriformes|Motacillidae|woodland,alpine|europe,africa|songbird,migratory
Common chaffinch|Passeriformes|Fringillidae|woodland,urban|europe,asia|songbird
European goldfinch|Passeriformes|Fringillidae|farmland,urban|europe,asia,africa|songbird
European greenfinch|Passeriformes|Fringillidae|woodland,urban|europe,asia|songbird
Eurasian siskin|Passeriformes|Fringillidae|forest|europe,asia|songbird
Common linnet|Passeriformes|Fringillidae|farmland,grassland|europe,asia,africa|songbird
Eurasian bullfinch|Passeriformes|Fringillidae|woodland|europe,asia|songbird
Hawfinch|Passeriformes|Fringillidae|woodland|europe,asia|songbird
Red crossbill|Passeriformes|Fringillidae|forest|europe,asia,americas|songbird
American goldfinch|Passeriformes|Fringillidae|farmland,urban|americas|songbird
Pine grosbeak|Passeriformes|Fringillidae|forest,alpine|europe,asia,americas|songbird
Evening grosbeak|Passeriformes|Fringillidae|forest|americas|songbird
Atlantic canary|Passeriformes|Fringillidae|woodland,urban|africa|songbird
Yellowhammer|Passeriformes|Emberizidae|farmland,grassland|europe,asia|songbird
Corn bunting|Passeriformes|Emberizidae|farmland|europe,asia,africa|songbird
Reed bunting|Passeriformes|Emberizidae|wetland,farmland|europe,asia|songbird
Snow bunting|Passeriformes|Emberizidae|alpine,coastal|europe,asia,americas|songbird,migratory
Ortolan bunting|Passeriformes|Emberizidae|farmland,grassland|europe,asia,africa|songbird,migratory
Dark-eyed junco|Passeriformes|Passerellidae|forest,urban|americas|songbird,migratory
White-throated sparrow|Passeriformes|Passerellidae|forest,urban|americas|songbird,migratory
Song sparrow|Passeriformes|Passerellidae|wetland,urban|americas|songbird
Chipping sparrow|Passeriformes|Passerellidae|woodland,urban|americas|songbird,migratory
Savannah sparrow|Passeriformes|Passerellidae|grassland|americas|songbird,migratory
Rufous-collared sparrow|Passeriformes|Passerellidae|grassland,urban|americas|songbird
Harris's sparrow|Passeriformes|Passerellidae|alpine,grassland|americas|songbird,migratory
Red-winged blackbird|Passeriformes|Icteridae|wetland,farmland|americas|songbird,colonial
Baltimore oriole|Passeriformes|Icteridae|woodland,urban|americas|songbird,migratory
Common grackle|Passeriformes|Icteridae|urban,farmland|americas|songbird,colonial
Bobolink|Passeriformes|Icteridae|grassland,farmland|americas|songbird,migratory
Yellow-headed blackbird|Passeriformes|Icteridae|wetland|americas|songbird,colonial
Montezuma oropendola|Passeriformes|Icteridae|forest|americas|songbird,colonial
Brown-headed cowbird|Passeriformes|Icteridae|farmland,woodland|americas|songbird,brood-parasite
Great-tailed grackle|Passeriformes|Icteridae|urban,wetland|americas|songbird,colonial
American redstart|Passeriformes|Parulidae|forest|americas|songbird,migratory
Ovenbird|Passeriformes|Parulidae|forest|americas|songbird,migratory
Yellow warbler|Passeriformes|Parulidae|woodland,wetland|americas|songbird,migratory
Black-throated blue warbler|Passeriformes|Parulidae|forest|americas|songbird,migratory
Cerulean warbler|Passeriformes|Parulidae|forest|americas|songbird,migratory
Kirtland's warbler|Passeriformes|Parulidae|forest|americas|songbird,migratory
Prothonotary warbler|Passeriformes|Parulidae|wetland,forest|americas|songbird,migratory
Hooded warbler|Passeriformes|Parulidae|forest|americas|songbird,migratory
Northern parula|Passeriformes|Parulidae|forest|americas|songbird,migratory
Northern cardinal|Passeriformes|Cardinalidae|woodland,urban|americas|songbird
Scarlet tanager|Passeriformes|Cardinalidae|forest|americas|songbird,migratory
Indigo bunting|Passeriformes|Cardinalidae|woodland,farmland|americas|songbird,migratory
Rose-breasted grosbeak|Passeriformes|Cardinalidae|forest|americas|songbird,migratory
Painted bunting|Passeriformes|Cardinalidae|woodland|americas|songbird,migratory
Red-legged honeycreeper|Passeriformes|Thraupidae|forest|americas|songbird,nectar
Green honeycreeper|Passeriformes|Thraupidae|forest|americas|songbird,nectar
Swallow tanager|Passeriformes|Thraupidae|forest|americas|songbird
Saffron finch|Passeriformes|Thraupidae|grassland,urban|americas|songbird
Blue dacnis|Passeriformes|Thraupidae|forest|americas|songbird,nectar
Zebra finch|Passeriformes|Estrildidae|desert,grassland|oceania|songbird,colonial
Gouldian finch|Passeriformes|Estrildidae|woodland|oceania|songbird
Java sparrow|Passeriformes|Estrildidae|farmland,urban|asia|songbird
Diamond firetail|Passeriformes|Estrildidae|woodland,grassland|oceania|songbird
Red-billed firefinch|Passeriformes|Estrildidae|woodland,urban|africa|songbird
Village weaver|Passeriformes|Ploceidae|grassland,urban|africa|songbird,colonial
Southern masked weaver|Passeriformes|Ploceidae|grassland,wetland|africa|songbird,colonial
Red-billed quelea|Passeriformes|Ploceidae|grassland,farmland|africa|songbird,colonial,nomadic
Sociable weaver|Passeriformes|Ploceidae|desert,grassland|africa|songbird,colonial
Northern red bishop|Passeriformes|Ploceidae|wetland,grassland|africa|songbird
Long-tailed widowbird|Passeriformes|Ploceidae|grassland|africa|songbird,lek
Pin-tailed whydah|Passeriformes|Viduidae|grassland,urban|africa|songbird,brood-parasite
Splendid fairywren|Passeriformes|Maluridae|woodland|oceania|songbird
Superb fairywren|Passeriformes|Maluridae|woodland,urban|oceania|songbird
Variegated fairywren|Passeriformes|Maluridae|woodland|oceania|songbird
Noisy miner|Passeriformes|Meliphagidae|woodland,urban|oceania|songbird,colonial
Bell miner|Passeriformes|Meliphagidae|forest|oceania|songbird,colonial
Blue-faced honeyeater|Passeriformes|Meliphagidae|woodland,urban|oceania|songbird,nectar
Regent honeyeater|Passeriformes|Meliphagidae|woodland|oceania|songbird,nectar
Tūī|Passeriformes|Meliphagidae|forest,urban|oceania|songbird,nectar,mimic
New Holland honeyeater|Passeriformes|Meliphagidae|woodland,coastal|oceania|songbird,nectar
Brown thornbill|Passeriformes|Acanthizidae|woodland|oceania|songbird
Yellow-rumped thornbill|Passeriformes|Acanthizidae|woodland,grassland|oceania|songbird
Australian magpie|Passeriformes|Artamidae|grassland,urban|oceania|songbird
Pied butcherbird|Passeriformes|Artamidae|woodland,urban|oceania|songbird
White-breasted woodswallow|Passeriformes|Artamidae|woodland,grassland|oceania|songbird
White-winged chough|Passeriformes|Corcoracidae|woodland|oceania|songbird,colonial
Apostlebird|Passeriformes|Corcoracidae|woodland|oceania|songbird,colonial
Willie wagtail|Passeriformes|Rhipiduridae|grassland,urban|oceania|songbird
Grey fantail|Passeriformes|Rhipiduridae|forest,woodland|oceania|songbird
Magpie-lark|Passeriformes|Monarchidae|wetland,urban|oceania|songbird
Black-naped monarch|Passeriformes|Monarchidae|forest|asia|songbird
Blue vanga|Passeriformes|Vangidae|forest|africa|songbird
Helmet vanga|Passeriformes|Vangidae|forest|africa|songbird
Red-backed shrike|Passeriformes|Laniidae|farmland,woodland|europe,asia,africa|songbird,migratory
Great grey shrike|Passeriformes|Laniidae|alpine,grassland|europe,asia|songbird
Loggerhead shrike|Passeriformes|Laniidae|grassland,farmland|americas|songbird
Eurasian golden oriole|Passeriformes|Oriolidae|woodland|europe,asia,africa|songbird,migratory
Australasian figbird|Passeriformes|Oriolidae|forest,urban|oceania|songbird
Black drongo|Passeriformes|Dicruridae|farmland,urban|asia|songbird
Fork-tailed drongo|Passeriformes|Dicruridae|woodland,urban|africa|songbird
Indian pitta|Passeriformes|Pittidae|forest|asia|songbird,migratory
Noisy pitta|Passeriformes|Pittidae|forest|oceania|songbird
Superb lyrebird|Passeriformes|Menuridae|forest|oceania|songbird,mimic
Albert's lyrebird|Passeriformes|Menuridae|forest|oceania|songbird,mimic
Satin bowerbird|Passeriformes|Ptilonorhynchidae|forest|oceania|songbird,mimic
Regent bowerbird|Passeriformes|Ptilonorhynchidae|forest|oceania|songbird
Great bowerbird|Passeriformes|Ptilonorhynchidae|woodland|oceania|songbird
Vogelkop bowerbird|Passeriformes|Ptilonorhynchidae|forest|oceania|songbird
Raggiana bird-of-paradise|Passeriformes|Paradisaeidae|forest|oceania|songbird
Twelve-wired bird-of-paradise|Passeriformes|Paradisaeidae|forest|oceania|songbird
King bird-of-paradise|Passeriformes|Paradisaeidae|forest|oceania|songbird
Blue bird-of-paradise|Passeriformes|Paradisaeidae|forest|oceania|songbird
Ribbon-tailed astrapia|Passeriformes|Paradisaeidae|forest|oceania|songbird
Magnificent riflebird|Passeriformes|Paradisaeidae|forest|oceania|songbird
Rifleman|Passeriformes|Acanthisittidae|forest|oceania|songbird
Guianan cock-of-the-rock|Passeriformes|Cotingidae|forest|americas|songbird,lek
Andean cock-of-the-rock|Passeriformes|Cotingidae|forest|americas|songbird,lek
Golden-headed manakin|Passeriformes|Pipridae|forest|americas|songbird,lek
Vermilion flycatcher|Passeriformes|Tyrannidae|woodland,wetland|americas|songbird
Great kiskadee|Passeriformes|Tyrannidae|wetland,urban|americas|songbird
Eastern kingbird|Passeriformes|Tyrannidae|farmland,wetland|americas|songbird,migratory
Rufous hornero|Passeriformes|Furnariidae|grassland,urban|americas|songbird
Eurasian skylark|Passeriformes|Alaudidae|farmland,grassland|europe,asia|songbird,migratory
Woodlark|Passeriformes|Alaudidae|grassland,woodland|europe,asia|songbird
Dunnock|Passeriformes|Prunellidae|woodland,urban|europe,asia|songbird
Bohemian waxwing|Passeriformes|Bombycillidae|forest,urban|europe,asia,americas|songbird,migratory
Cedar waxwing|Passeriformes|Bombycillidae|woodland,urban|americas|songbird,migratory
White-throated dipper|Passeriformes|Cinclidae|wetland|europe,asia,africa|songbird
American dipper|Passeriformes|Cinclidae|wetland,alpine|americas|songbird
Goldcrest|Passeriformes|Regulidae|forest|europe,asia|songbird
Common firecrest|Passeriformes|Regulidae|forest|europe,africa|songbird
Japanese white-eye|Passeriformes|Zosteropidae|woodland,urban|asia|songbird
Silvereye|Passeriformes|Zosteropidae|woodland,urban|oceania|songbird
Palestine sunbird|Passeriformes|Nectariniidae|desert,urban|asia,africa|songbird,nectar
Malachite sunbird|Passeriformes|Nectariniidae|alpine,grassland|africa|songbird,nectar
Spotted pardalote|Passeriformes|Pardalotidae|woodland|oceania|songbird
Grey-crowned babbler|Passeriformes|Pomatostomidae|woodland|oceania|songbird,colonial
North Island saddleback|Passeriformes|Callaeidae|forest|oceania|songbird
Kōkako|Passeriformes|Callaeidae|forest|oceania|songbird
Stitchbird|Passeriformes|Notiomystidae|forest|oceania|songbird
Scarlet robin|Passeriformes|Petroicidae|woodland|oceania|songbird
Eastern yellow robin|Passeriformes|Petroicidae|forest|oceania|songbird
Red-whiskered bulbul|Passeriformes|Pycnonotidae|urban,woodland|asia|songbird
Common bulbul|Passeriformes|Pycnonotidae|woodland,urban|africa|songbird
Zitting cisticola|Passeriformes|Cisticolidae|grassland,wetland|europe,asia,africa|songbird
Common tailorbird|Passeriformes|Cisticolidae|urban,woodland|asia|songbird
Cetti's warbler|Passeriformes|Scotocercidae|wetland|europe,asia,africa|songbird
"""


def slug(text):
    text = text.lower().replace("ā", "a").replace("ō", "o").replace("ū", "u")
    text = text.replace("é", "e").replace("á", "a").replace("í", "i").replace("ó", "o")
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def fetch(url, tries=4):
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001 - retry any transport error
            if attempt == tries - 1:
                return {"__error__": str(exc)}
            time.sleep(1.2 * (attempt + 1))
    return {}


def clean_extract(text):
    """Drop pronunciation brackets and trim to two sentences."""
    text = re.sub(r"\s*\((?=[^)]*(?:ˈ|ˌ|ə|ʉ|ɨ|/|-[⁠\u2060]))[^)]*\)", "", text)
    text = re.sub(r"\s{2,}", " ", text).strip()
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z(])", text)
    out = " ".join(parts[:2]).strip()
    if len(out) > 330:
        out = out[:327].rsplit(" ", 1)[0] + "…"
    return out


def image_url(thumb):
    """Lead photo at a size the Wikimedia thumbnail service actually allows."""
    if not thumb:
        return None
    url = thumb.split("?utm_source")[0]
    url = url.replace("https://thumb.wikimedia.org", "https://upload.wikimedia.org")
    return re.sub(r"/\d+px-", "/500px-", url, count=1)


def file_page(img_url):
    if not img_url:
        return None
    name = img_url.split("?")[0].rsplit("/", 1)[-1]
    name = re.sub(r"^\d+px-", "", name)
    return "https://commons.wikimedia.org/wiki/File:" + name


def audio_file(title):
    return "https://commons.wikimedia.org/wiki/Special:FilePath/" + title.split(":", 1)[1]


def gather(spec):
    title = spec["title"]
    page = title.replace(" ", "_")
    summary = fetch("https://en.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(page))
    if "__error__" in summary or summary.get("type") in ("disambiguation", "no-extract"):
        return spec, None, "summary: " + summary.get("__error__", summary.get("type", "missing"))

    media = fetch("https://en.wikipedia.org/api/rest_v1/page/media-list/" + urllib.parse.quote(page))
    audio = None
    if "__error__" not in media:
        for item in media.get("items", []):
            name = item.get("title", "")
            if item.get("type") == "audio" and name.lower().endswith((".ogg", ".oga", ".wav", ".mp3", ".flac")):
                audio = name
                break

    spec["summary"] = summary
    spec["audio_title"] = audio
    return spec, summary, None


def main():
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
            "traits": [t for t in bits[5].split(",") if t],
        })
    if LIMIT:
        rows = rows[:LIMIT]
    print("spec rows:", len(rows))

    ok, gone = [], []
    with ThreadPoolExecutor(max_workers=6) as pool:
        for spec, summary, err in pool.map(gather, rows):
            if not summary:
                gone.append((spec["title"], err))
                continue
            ok.append(spec)
            print("  +", spec["title"])
    print("resolved:", len(ok), "failed:", len(gone))
    for t, e in gone:
        print("   !", t, "->", e)

    # audio file -> real URL, batched 50 titles per request
    titles = sorted({s["audio_title"] for s in ok if s["audio_title"]})
    urls = {}
    for i in range(0, len(titles), 50):
        batch = titles[i:i + 50]
        q = urllib.parse.urlencode({
            "action": "query", "format": "json", "formatversion": "2",
            "prop": "imageinfo", "iiprop": "url", "titles": "|".join(batch),
        })
        data = fetch("https://en.wikipedia.org/w/api.php?" + q)
        query = data.get("query", {})
        for p in query.get("pages", []):
            info = p.get("imageinfo") or []
            if info and info[0].get("url"):
                urls[p["title"]] = info[0]["url"]
                urls[p["title"].replace(" ", "_")] = info[0]["url"]
        for norm in query.get("normalized", []):
            if norm.get("to") in urls:
                urls[norm["from"]] = urls[norm["to"]]
    print("audio files:", len(titles), "resolved:", len(urls))

    # wikidata: status, length, mass
    qids = [s["summary"].get("wikibase_item") for s in ok if s["summary"].get("wikibase_item")]
    status, length, mass, taxon = {}, {}, {}, {}
    length_seen, mass_seen = {}, {}
    for i in range(0, len(qids), 40):
        batch = qids[i:i + 40]
        sparql = """
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
        data = fetch("https://query.wikidata.org/sparql?" + urllib.parse.urlencode({"format": "json", "query": sparql}))
        if "__error__" in data:
            print("   sparql batch failed:", data["__error__"])
            continue
        for b in data.get("results", {}).get("bindings", []):
            qid = b["item"]["value"].rsplit("/", 1)[-1]
            if "statusLabel" in b:
                status.setdefault(qid, b["statusLabel"]["value"])
            if "taxon" in b and " " in b["taxon"]["value"]:
                taxon.setdefault(qid, b["taxon"]["value"])
            if "len" in b:
                unit = b.get("lenUnitLabel", {}).get("value", "")
                try:
                    value = float(b["len"]["value"])
                except ValueError:
                    value = 0
                if unit.startswith("centimetre") or unit.startswith("cm"):
                    cm = value
                elif unit.startswith("metre") or unit == "m":
                    cm = value * 100
                elif unit.startswith("millimetre") or unit == "mm":
                    cm = value / 10
                else:
                    cm = 0
                if 3 <= cm <= 300:
                    length_seen.setdefault(qid, []).append(round(cm, 1))
            if "mass" in b:
                unit = b.get("massUnitLabel", {}).get("value", "")
                try:
                    value = float(b["mass"]["value"])
                except ValueError:
                    value = 0
                if unit.startswith("gram") or unit == "g":
                    grams = value
                elif unit.startswith("kilogram") or unit == "kg":
                    grams = value * 1000
                elif unit.startswith("milligram") or unit == "mg":
                    grams = value / 1000
                else:
                    grams = 0
                if 2 <= grams <= 200000:
                    mass_seen.setdefault(qid, []).append(round(grams, 1))
    # several statements per species (adult, female, juvenile): the largest is the adult
    length = {q: max(v) for q, v in length_seen.items()}
    mass = {q: max(v) for q, v in mass_seen.items()}
    print("wikidata: status", len(status), "length", len(length), "mass", len(mass))

    groups = {}
    for spec in ok:
        summary = spec["summary"]
        qid = summary.get("wikibase_item")
        thumb = image_url((summary.get("thumbnail") or {}).get("source"))
        audio_title = spec["audio_title"]
        url = (summary.get("content_urls", {}).get("desktop", {}).get("page")
               or "https://en.wikipedia.org/wiki/" + urllib.parse.quote(spec["title"].replace(" ", "_")))
        entry = {
            "n": summary.get("title") or spec["title"],
            "s": taxon.get(qid, "") if qid else "",
            "u": url,
            "d": clean_extract(summary.get("extract") or ""),
            "h": spec["habitats"],
            "r": spec["regions"],
            "t": spec["traits"],
            "fam": spec["family"],
            "ord": spec["order"],
        }
        if thumb:
            entry["i"] = thumb
            entry["ic"] = file_page(thumb)
        if audio_title and audio_title in urls:
            entry["a"] = urls[audio_title].split("?utm_source")[0]
            entry["an"] = "song or call"
        if not entry["s"]:
            binomial = re.search(r"\(([A-Z][a-z]+ [a-z-]+)\)", summary.get("extract") or "")
            if binomial:
                entry["s"] = binomial.group(1)
        if qid and qid in status:
            entry["st"] = status[qid]
        if qid and qid in length:
            entry["l"] = length[qid]
        if qid and qid in mass:
            entry["m"] = mass[qid]
        groups.setdefault(spec["order"], {}).setdefault(spec["family"], []).append(entry)

    os.makedirs(OUT, exist_ok=True)
    index_groups = []
    facets = {"habitat": {}, "region": {}, "trait": {}, "status": {}}
    total, photos, songs, statuses = 0, 0, 0, 0
    for order in sorted(groups, key=lambda o: (-sum(len(v) for v in groups[o].values()), o)):
        families = groups[order]
        species = [e for fam in families.values() for e in fam]
        # keep the sequence stable inside a family: alphabetical by common name
        for fam in families:
            families[fam].sort(key=lambda e: e["n"])
        slug_ = slug(order)
        payload = {
            "key": slug_,
            "title": order,
            "families": [
                {"n": fam, "c": len(families[fam]), "s": sorted(families[fam], key=lambda e: e["n"])}
                for fam in sorted(families, key=lambda f: (-len(families[f]), f))
            ],
        }
        with open(os.path.join(OUT, slug_ + ".json"), "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=1)
        total += len(species)
        photos += sum(1 for e in species if e.get("i"))
        songs += sum(1 for e in species if e.get("a"))
        statuses += sum(1 for e in species if e.get("st"))
        for entry in species:
            for value in entry.get("h", []):
                facets["habitat"][value] = facets["habitat"].get(value, 0) + 1
            for value in entry.get("r", []):
                facets["region"][value] = facets["region"].get(value, 0) + 1
            for value in entry.get("t", []):
                facets["trait"][value] = facets["trait"].get(value, 0) + 1
            if entry.get("st"):
                facets["status"][entry["st"]] = facets["status"].get(entry["st"], 0) + 1
        index_groups.append({
            "key": slug_,
            "num": "%02d" % (len(index_groups) + 1),
            "title": order,
            "species": len(species),
            "families": len(families),
            "photos": sum(1 for e in species if e.get("i")),
            "songs": sum(1 for e in species if e.get("a")),
            "statuses": sum(1 for e in species if e.get("st")),
        })

    index = {
        "generated": time.strftime("%Y-%m-%d"),
        "source": "en.wikipedia.org + wikidata.org",
        "species": total,
        "families": len({e["fam"] for g in groups.values() for f in g.values() for e in f}),
        "orders": len(groups),
        "photos": photos,
        "songs": songs,
        "statuses": statuses,
        "facets": facets,
        "groups": index_groups,
    }
    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as fh:
        json.dump(index, fh, ensure_ascii=False, indent=1)
    print(json.dumps(index, ensure_ascii=False)[:600])
    print("wrote", OUT)


if __name__ == "__main__":
    main()
