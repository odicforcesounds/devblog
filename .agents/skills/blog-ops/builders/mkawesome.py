#!/usr/bin/env python3
"""Build docs/awesomeIndex.html from the links in docs/awesome_story.html.

The page is a catalogue: every GitHub list the story page links to, sorted by
subject, with one line saying what each list collects (English + Portuguese).
The data below is the source of truth; a hard assertion makes the build fail
if a link in awesome_story.html is missing here.
"""

import os as _os

_os.chdir(_os.path.abspath(_os.path.join(
    _os.path.dirname(_os.path.abspath(__file__)),
    "..", "..", "..", "..")))

import html
import json
import re
import sys

ROOT = "."
STORY = "docs/awesome_story.html"
OUT = "docs/awesomeIndex.html"
URL = "https://blog.odicforcesounds.com/awesomeIndex.html"
IMG = "https://blog.odicforcesounds.com/images/peace.jpg"


GROUPS = [
    ("shell", "Shell, terminal and one-liners", "Shell, terminal e one-liners",
     "The command line as a workshop: prompts, one-liners, cheat sheets and text services.",
     "A linha de comandos como oficina: prompts, one-liners, folhas de referência e serviços de texto."),
    ("lang", "Languages and frameworks", "Linguagens e frameworks",
     "One list per language or framework, and the ecology around each one.",
     "Uma lista por linguagem ou framework, e a ecologia à volta de cada uma."),
    ("systems", "Servers, containers and self-hosting", "Servidores, contentores e self-hosting",
     "Running your own machines: containers, backups, tunnels and the software that replaces a subscription.",
     "Gerir as tuas máquinas: contentores, cópias, túneis e o software que substitui uma subscrição."),
    ("data", "Data, networks and archives", "Dados, redes e arquivos",
     "Moving and keeping information: packets, crawlers, graphs, ledgers and the web itself.",
     "Mover e guardar informação: pacotes, crawlers, grafos, registos e a própria web."),
    ("security", "Security, privacy and forensics", "Segurança, privacidade e forense",
     "The largest shelf, for obvious reasons: attacks, defences, malware, privacy and the tools of the trade.",
     "A prateleira maior, por razões óbvias: ataques, defesas, malware, privacidade e as ferramentas do ofício."),
    ("ai", "AI and automation", "IA e automação",
     "Models, agents and the wiring that puts them to work.",
     "Modelos, agentes e a cablagem que os põe a trabalhar."),
    ("web", "Web, design and product", "Web, design e produto",
     "How interfaces are designed, documented and shipped.",
     "Como as interfaces são desenhadas, documentadas e publicadas."),
    ("learning", "Learning, careers and collections", "Aprendizagem, carreira e colecções",
     "Courses, interviews, newsletters and the people worth following.",
     "Cursos, entrevistas, boletins e as pessoas que vale a pena seguir."),
    ("beyond", "Beyond code", "Além do código",
     "Food, music, money, health, games. The lists that have nothing to do with work and everything to do with living.",
     "Comida, música, dinheiro, saúde, jogos. As listas que nada têm a ver com trabalho e tudo com a vida."),
]

# url, display name, group, English line, Portuguese line
E = [
    # --- shell -------------------------------------------------------------
    ("https://github.com/awesome-lists/awesome-bash", "Bash", "shell",
     "Scripts, prompts, testing helpers and guides for Bash.",
     "Scripts, prompts, ajudas de teste e guias para Bash."),
    ("https://github.com/detailyang/awesome-cheatsheet", "Cheat Sheets", "shell",
     "One-screen reference sheets for languages, tools and sysadmin commands.",
     "Folhas de referência de um ecrã para linguagens, ferramentas e comandos de administração."),
    ("https://github.com/OlivierLaflamme/Cheatsheet-God", "Cheatsheet God", "shell",
     "Pentest and sysadmin cheat sheets gathered in a single repository.",
     "Folhas de batota de pentest e administração reunidas num só repositório."),
    ("https://github.com/agarrharr/awesome-cli-apps", "CLI Apps", "shell",
     "Terminal applications for files, git, music, chat and everything between.",
     "Aplicações de terminal para ficheiros, git, música, conversa e tudo o resto."),
    ("https://github.com/chubin/awesome-console-services", "Console Services", "shell",
     "Services reachable with curl, ssh or telnet: weather, news, chat.",
     "Serviços alcançáveis por curl, ssh ou telnet: tempo, notícias, conversa."),
    ("https://github.com/emacs-tw/awesome-emacs", "Emacs", "shell",
     "Packages, configurations and guides for the extensible editor.",
     "Pacotes, configurações e guias para o editor extensível."),
    ("https://github.com/trimstray/the-book-of-secret-knowledge", "The Book of Secret Knowledge", "shell",
     "Manuals, one-liners, hacks and tools for people who live in a terminal.",
     "Manuais, one-liners, truques e ferramentas para quem vive num terminal."),

    # --- languages ---------------------------------------------------------
    ("https://github.com/PatrickJS/awesome-angular", "Angular", "lang",
     "The Angular ecosystem: components, libraries and learning paths.",
     "O ecossistema Angular: componentes, bibliotecas e percursos de aprendizagem."),
    ("https://github.com/fffaraz/awesome-cpp", "C and C++", "lang",
     "Libraries, frameworks and software written in C and C++.",
     "Bibliotecas, frameworks e software escritos em C e C++."),
    ("https://github.com/DovAmir/awesome-design-patterns", "Design Patterns", "lang",
     "Patterns explained across languages, with code and articles.",
     "Padrões explicados em várias linguagens, com código e artigos."),
    ("https://github.com/wsvincent/awesome-django", "Django", "lang",
     "Django packages, real projects and tutorials.",
     "Pacotes, projectos reais e tutoriais de Django."),
    ("https://github.com/Solido/awesome-flutter", "Flutter", "lang",
     "Widgets, plugins, templates and articles for Flutter.",
     "Widgets, plugins, modelos e artigos para Flutter."),
    ("https://github.com/avelino/awesome-go", "Go", "lang",
     "Libraries, frameworks and tools for Go, sorted by domain.",
     "Bibliotecas, frameworks e ferramentas para Go, por domínio."),
    ("https://github.com/akullpp/awesome-java", "Java", "lang",
     "Frameworks, libraries and tooling for the JVM.",
     "Frameworks, bibliotecas e ferramentas para a JVM."),
    ("https://github.com/micromata/awesome-javascript-learning", "JavaScript Learning", "lang",
     "Blogs, books, courses and exercises to learn JavaScript properly.",
     "Blogues, livros, cursos e exercícios para aprender JavaScript a sério."),
    ("https://github.com/actions/javascript-action", "JavaScript Action", "lang",
     "The official template for writing a GitHub Action in JavaScript.",
     "O modelo oficial para escrever uma GitHub Action em JavaScript."),
    ("https://github.com/mfornos/awesome-microservices", "Microservices", "lang",
     "Platforms, gateways and practices for service-oriented systems.",
     "Plataformas, gateways e práticas para sistemas orientados a serviços."),
    ("https://github.com/sindresorhus/awesome-nodejs", "Node.js", "lang",
     "Packages and resources for Node.js, curated by Sindre Sorhus.",
     "Pacotes e recursos para Node.js, seleccionados por Sindre Sorhus."),
    ("https://github.com/vinta/awesome-python", "Python", "lang",
     "The canonical map of Python libraries, frameworks and resources.",
     "O mapa canónico de bibliotecas, frameworks e recursos de Python."),
    ("https://github.com/enaqx/awesome-react", "React", "lang",
     "Components, hooks, tutorials and tooling around React.",
     "Componentes, hooks, tutoriais e ferramentas à volta do React."),
    ("https://github.com/markets/awesome-ruby", "Ruby", "lang",
     "Gems, tools and reading material for Ruby developers.",
     "Gems, ferramentas e leitura para quem programa em Ruby."),
    ("https://github.com/rust-unofficial/awesome-rust", "Rust", "lang",
     "Crates, projects and learning material for Rust.",
     "Crates, projectos e material de aprendizagem para Rust."),
    ("https://github.com/binhnguyennus/awesome-scalability", "Scalability", "lang",
     "How large systems scale: patterns, talks and real architectures.",
     "Como os grandes sistemas escalam: padrões, palestras e arquitecturas reais."),
    ("https://github.com/aniftyco/awesome-tailwindcss", "Tailwind CSS", "lang",
     "Plugins, components, templates and tools for Tailwind CSS.",
     "Plugins, componentes, modelos e ferramentas para Tailwind CSS."),
    ("https://github.com/dzharii/awesome-typescript", "TypeScript", "lang",
     "TypeScript libraries, starters, books and videos.",
     "Bibliotecas, projectos iniciais, livros e vídeos de TypeScript."),

    # --- systems -----------------------------------------------------------
    ("https://github.com/Kikobeats/awesome-api", "API", "systems",
     "Design, documentation, testing and monitoring tools for APIs.",
     "Ferramentas de desenho, documentação, teste e monitorização de APIs."),
    ("https://github.com/yosriady/awesome-api-devtools", "API DevTools", "systems",
     "Everything between writing an endpoint and shipping it.",
     "Tudo o que existe entre escrever um endpoint e publicá-lo."),
    ("https://github.com/mgramin/awesome-db-tools", "Database Tools", "systems",
     "Clients, migration tools and utilities for SQL and NoSQL.",
     "Clientes, ferramentas de migração e utilitários para SQL e NoSQL."),
    ("https://github.com/veggiemonk/awesome-docker", "Docker", "systems",
     "Images, compose files, tools and articles about containers.",
     "Imagens, ficheiros compose, ferramentas e artigos sobre contentores."),
    ("https://github.com/zoidyzoidzoid/awesome-ebpf", "eBPF", "systems",
     "Tracing, networking and security tools built on eBPF.",
     "Ferramentas de tracing, rede e segurança construídas sobre eBPF."),
    ("https://github.com/johnjago/awesome-free-software", "Free Software", "systems",
     "Software that respects freedom, plus alternatives to proprietary tools.",
     "Software que respeita a liberdade, com alternativas às ferramentas proprietárias."),
    ("https://github.com/denji/awesome-http-benchmark", "HTTP Benchmark", "systems",
     "Load-testing tools, compared against each other.",
     "Ferramentas de teste de carga, comparadas entre si."),
    ("https://github.com/ipfs/awesome-ipfs", "IPFS", "systems",
     "The content-addressed web: apps, tools and datasets on IPFS.",
     "A web endereçada por conteúdo: aplicações, ferramentas e dados em IPFS."),
    ("https://github.com/jaywcjlove/awesome-mac", "Mac", "systems",
     "Applications and utilities for macOS.",
     "Aplicações e utilitários para macOS."),
    ("https://github.com/thibmaek/awesome-raspberry-pi", "Raspberry Pi", "systems",
     "Projects, operating systems and accessories for the Pi.",
     "Projectos, sistemas operativos e acessórios para o Pi."),
    ("https://github.com/mikeroyal/Self-Hosting-Guide", "Self-Hosting Guide", "systems",
     "A guide to building, securing and maintaining your own server.",
     "Um guia para construir, proteger e manter o teu próprio servidor."),
    ("https://github.com/awesome-selfhosted/awesome-selfhosted", "Self-Hosted", "systems",
     "Free software you can host yourself instead of renting a service.",
     "Software livre que podes alojar em vez de alugar um serviço."),
    ("https://github.com/anaibol/awesome-serverless", "Serverless", "systems",
     "Frameworks, platforms and examples for serverless architectures.",
     "Frameworks, plataformas e exemplos de arquitecturas serverless."),
    ("https://github.com/awesome-foss/awesome-sysadmin", "Sysadmin", "systems",
     "Open-source tools for running servers: monitoring, backup, config.",
     "Ferramentas open-source para gerir servidores: monitorização, cópias, configuração."),
    ("https://github.com/anderspitman/awesome-tunneling", "Tunneling", "systems",
     "Tools that expose a local service to the internet safely.",
     "Ferramentas que expõem um serviço local à internet com segurança."),

    # --- data --------------------------------------------------------------
    ("https://github.com/BruceDone/awesome-crawler", "Crawler", "data",
     "Crawler frameworks in every major language.",
     "Frameworks de crawling nas principais linguagens."),
    ("https://github.com/gjy3035/Awesome-Crowd-Counting", "Crowd Counting", "data",
     "Datasets and models for counting people in images.",
     "Conjuntos de dados e modelos para contar pessoas em imagens."),
    ("https://github.com/rguo12/awesome-causality-algorithms", "Causality Algorithms", "data",
     "Causal inference methods and their implementations.",
     "Métodos de inferência causal e as suas implementações."),
    ("https://github.com/pingcap/awesome-database-learning", "Database Learning", "data",
     "Papers and courses on how databases are actually built.",
     "Artigos e cursos sobre como as bases de dados são construídas."),
    ("https://github.com/yjjnls/awesome-blockchain", "Blockchain", "data",
     "Protocols, papers and tooling for distributed ledgers.",
     "Protocolos, artigos e ferramentas para registos distribuídos."),
    ("https://github.com/Zheaoli/awesome-coins", "Coins", "data",
     "Cryptocurrency projects, exchanges and mining resources.",
     "Projectos de criptomoeda, bolsas e recursos de mineração."),
    ("https://github.com/briatte/awesome-network-analysis", "Network Analysis", "data",
     "Graph theory, visualisation and tools for network data.",
     "Teoria de grafos, visualização e ferramentas para dados de rede."),
    ("https://github.com/caesar0301/awesome-pcaptools", "PCAP Tools", "data",
     "Capturing, dissecting and analysing packet traces.",
     "Captura, dissecação e análise de traços de pacotes."),
    ("https://github.com/iipc/awesome-web-archiving", "Web Archiving", "data",
     "Tools and standards for preserving the web.",
     "Ferramentas e normas para preservar a web."),
    ("https://github.com/lorien/awesome-web-scraping", "Web Scraping", "data",
     "Libraries and services for extracting data from websites.",
     "Bibliotecas e serviços para extrair dados de sítios web."),

    # --- security ----------------------------------------------------------
    ("https://github.com/ashishb/android-security-awesome", "Android Security", "security",
     "Android testing tools, papers and CTFs.",
     "Ferramentas de teste, artigos e CTFs de Android."),
    ("https://github.com/arainho/awesome-api-security", "API Security", "security",
     "Testing and protecting APIs against abuse.",
     "Testar e proteger APIs contra abusos."),
    ("https://github.com/fabacab/awesome-cybersecurity-blueteam", "Blue Team", "security",
     "Blue team defence: detection, response and hardening.",
     "Defesa de equipa azul: detecção, resposta e endurecimento."),
    ("https://github.com/devanshbatham/Awesome-Bugbounty-Writeups", "Bug Bounty Writeups", "security",
     "Real bug bounty disclosures, written up step by step.",
     "Divulgações reais de bug bounty, escritas passo a passo."),
    ("https://github.com/vavkamil/awesome-bugbounty-tools", "Bug Bounty Tools", "security",
     "Tools used in bug bounty programmes, by stage.",
     "Ferramentas usadas em programas de bug bounty, por fase."),
    ("https://github.com/snoopysecurity/awesome-burp-extensions", "Burp Extensions", "security",
     "Extensions for Burp Suite, by purpose.",
     "Extensões para o Burp Suite, por finalidade."),
    ("https://github.com/W00t3k/Awesome-Cellular-Hacking", "Cellular Hacking", "security",
     "Basebands, SIM cards and mobile network research.",
     "Basebands, cartões SIM e investigação de redes móveis."),
    ("https://github.com/sobolevn/awesome-cryptography", "Cryptography", "security",
     "Libraries, papers and courses on applied cryptography.",
     "Bibliotecas, artigos e cursos de criptografia aplicada."),
    ("https://github.com/apsdehal/awesome-ctf", "CTF", "security",
     "CTF platforms, write-ups and practice material.",
     "Plataformas de CTF, resoluções e material de treino."),
    ("https://github.com/cugu/awesome-forensics", "Forensics", "security",
     "Disk, memory and network forensics tools and reading.",
     "Ferramentas e leitura de forense de disco, memória e rede."),
    ("https://github.com/edoardottt/awesome-hacker-search-engines", "Hacker Search Engines", "security",
     "Search engines and databases that index exposed systems.",
     "Motores de busca e bases de dados que indexam sistemas expostos."),
    ("https://github.com/Hack-with-Github/Awesome-Hacking", "Hacking", "security",
     "The starting point: how to learn hacking legally.",
     "O ponto de partida: como aprender hacking legalmente."),
    ("https://github.com/vitalysim/Awesome-Hacking-Resources", "Hacking Resources", "security",
     "A broad library of hacking tutorials and tools.",
     "Uma biblioteca vasta de tutoriais e ferramentas de hacking."),
    ("https://github.com/onlurking/awesome-infosec", "InfoSec", "security",
     "Courses, books, blogs and tools for information security.",
     "Cursos, livros, blogues e ferramentas de segurança da informação."),
    ("https://github.com/husnainfareed/awesome-ethical-hacking-resources", "Ethical Hacking Resources", "security",
     "Learning ethical hacking: labs, courses and write-ups.",
     "Aprender hacking ético: laboratórios, cursos e relatos."),
    ("https://github.com/HynekPetrak/javascript-malware-collection", "JavaScript Malware Collection", "security",
     "A corpus of obfuscated JavaScript malware samples.",
     "Um corpus de amostras de malware JavaScript ofuscado."),
    ("https://github.com/SecWiki/linux-kernel-exploits", "Linux Kernel Exploits", "security",
     "Kernel exploits with the versions they affect.",
     "Exploits de kernel e as versões afectadas."),
    ("https://github.com/milabs/awesome-linux-rootkits", "Linux Rootkits", "security",
     "Rootkits for Linux, with source and analysis.",
     "Rootkits para Linux, com código e análise."),
    ("https://github.com/rshipp/awesome-malware-analysis", "Malware Analysis", "security",
     "Analysing malware: sandboxes, YARA, reports.",
     "Análise de malware: sandboxes, YARA e relatórios."),
    ("https://github.com/enaqx/awesome-pentest", "Pentest", "security",
     "Pentest tools and resources, by phase.",
     "Ferramentas e recursos de pentest, por fase."),
    ("https://github.com/Lissy93/awesome-privacy", "Privacy", "security",
     "Guides and tools to reduce what you expose online.",
     "Guias e ferramentas para reduzir o que expões online."),
    ("https://github.com/alphaSeclab/awesome-rat", "RAT", "security",
     "Remote access trojans and how they are analysed.",
     "Trojans de acesso remoto e como são analisados."),
    ("https://github.com/yeyintminthuhtut/Awesome-Red-Teaming", "Red Teaming", "security",
     "Adversary simulation: tooling and tradecraft.",
     "Simulação de adversário: ferramentas e técnicas."),
    ("https://github.com/alphaSeclab/awesome-reverse-engineering", "Reverse Engineering", "security",
     "Disassemblers, debuggers and guides for taking binaries apart.",
     "Desassembladores, depuradores e guias para desmontar binários."),
    ("https://github.com/PaulSec/awesome-sec-talks", "Security Talks", "security",
     "Conference talks on security, sorted by topic.",
     "Palestras de conferências de segurança, por tema."),
    ("https://github.com/decalage2/awesome-security-hardening", "Security Hardening", "security",
     "Hardening guides for servers, desktops and networks.",
     "Guias de endurecimento para servidores, postos e redes."),
    ("https://github.com/jakejarvis/awesome-shodan-queries", "Shodan Queries", "security",
     "Shodan search strings for finding exposed devices.",
     "Pesquisas Shodan para encontrar dispositivos expostos."),
    ("https://github.com/0x4D31/awesome-threat-detection", "Threat Detection", "security",
     "Detection engineering: rules, telemetry and hunting.",
     "Engenharia de detecção: regras, telemetria e caça a ameaças."),
    ("https://github.com/jaredthecoder/awesome-vehicle-security", "Vehicle Security", "security",
     "CAN bus, keyless entry and car attack research.",
     "CAN bus, abertura sem chave e investigação de ataques a automóveis."),
    ("https://github.com/0xInfection/Awesome-WAF", "WAF", "security",
     "Web application firewalls, bypasses and payloads.",
     "Firewalls de aplicação web, contornos e cargas úteis."),
    ("https://github.com/infoslack/awesome-web-hacking", "Web Hacking", "security",
     "Techniques and write-ups for attacking web applications.",
     "Técnicas e relatos de ataques a aplicações web."),
    ("https://github.com/qazbnm456/awesome-web-security", "Web Security", "security",
     "Web vulnerabilities, explained and demonstrated.",
     "Vulnerabilidades web, explicadas e demonstradas."),
    ("https://github.com/matter-labs/awesome-zero-knowledge-proofs", "Zero-Knowledge Proofs", "security",
     "ZK proofs: papers, libraries and applications.",
     "Provas de conhecimento zero: artigos, bibliotecas e aplicações."),

    # --- ai ----------------------------------------------------------------
    ("https://github.com/e2b-dev/awesome-ai-agents", "AI Agents", "ai",
     "Frameworks and products for autonomous software agents.",
     "Frameworks e produtos para agentes de software autónomos."),
    ("https://github.com/tensorchord/Awesome-LLMOps", "LLMOps", "ai",
     "Platforms for training, serving and monitoring large models.",
     "Plataformas para treinar, servir e monitorizar grandes modelos."),
    ("https://github.com/enescingoz/awesome-n8n-templates", "n8n Templates", "ai",
     "Ready-made n8n workflows for mail, files, AI and chat.",
     "Fluxos n8n prontos para correio, ficheiros, IA e conversa."),

    # --- web ---------------------------------------------------------------
    ("https://github.com/awesome-css-group/awesome-css", "CSS", "web",
     "Frameworks, preprocessors and CSS learning material.",
     "Frameworks, pré-processadores e material de aprendizagem de CSS."),
    ("https://github.com/alexpate/awesome-design-systems", "Design Systems", "web",
     "Public design systems and how they document themselves.",
     "Sistemas de design públicos e a forma como se documentam."),
    ("https://github.com/goabstract/Awesome-Design-Tools", "Design Tools", "web",
     "Tools for interface design, prototyping and handoff.",
     "Ferramentas de desenho de interface, prototipagem e entrega."),
    ("https://github.com/Kristories/awesome-guidelines", "Guidelines", "web",
     "Coding style guides from companies and communities.",
     "Guias de estilo de empresas e comunidades."),
    ("https://github.com/aviaryan/awesome-no-login-web-apps", "No-Login Web Apps", "web",
     "Web apps that work without creating an account.",
     "Aplicações web que funcionam sem criar conta."),
    ("https://github.com/sindresorhus/privacy-policy", "Privacy Policy", "web",
     "A reusable, plain-language privacy policy for apps.",
     "Uma política de privacidade reutilizável e em linguagem simples."),
    ("https://github.com/dexteryy/spellbook-of-modern-webdev", "Spellbook of Modern Webdev", "web",
     "A map of the modern web stack, from bundlers to data stores.",
     "Um mapa do stack web moderno, dos bundlers às bases de dados."),

    # --- learning ----------------------------------------------------------
    ("https://github.com/dipakkr/A-to-Z-Resources-for-Students", "A to Z Resources for Students", "learning",
     "Hackathons, internships, scholarships and learning paths.",
     "Hackathons, estágios, bolsas e percursos de aprendizagem."),
    ("https://github.com/prakhar1989/awesome-courses", "Courses", "learning",
     "University courses on computer science, free online.",
     "Cursos universitários de informática, gratuitos e online."),
    ("https://github.com/brootware/awesome-cyber-security-university", "Cyber Security University", "learning",
     "Free university courses on security, in order.",
     "Cursos universitários gratuitos de segurança, por ordem."),
    ("https://github.com/joe-shenouda/awesome-cyber-skills", "Cyber Skills", "learning",
     "Training grounds and labs to practise security.",
     "Campos de treino e laboratórios para praticar segurança."),
    ("https://github.com/bnb/awesome-developer-streams", "Developer Streams", "learning",
     "Developers worth watching live, by language.",
     "Programadores que vale a pena ver em directo, por linguagem."),
    ("https://github.com/MunGell/awesome-for-beginners", "For Beginners", "learning",
     "Projects that label issues for first contributions.",
     "Projectos que marcam tarefas para primeiras contribuições."),
    ("https://github.com/DopplerHQ/awesome-interview-questions", "Interview Questions", "learning",
     "Interview questions per language, framework and platform.",
     "Perguntas de entrevista por linguagem, framework e plataforma."),
    ("https://github.com/zudochkin/awesome-newsletters", "Newsletters", "learning",
     "Newsletters per language, framework and discipline.",
     "Boletins por linguagem, framework e disciplina."),
    ("https://github.com/NirantK/awesome-project-ideas", "Project Ideas", "learning",
     "Ideas for what to build next, with datasets and papers.",
     "Ideias para o próximo projecto, com dados e artigos."),
    ("https://github.com/lukasz-madon/awesome-remote-job", "Remote Job", "learning",
     "Remote job boards, companies and how the work is done.",
     "Quadros de emprego remoto, empresas e como se trabalha."),
    ("https://github.com/terkelg/awesome-creative-coding", "Creative Coding", "learning",
     "Generative art, shaders and tools for coding visuals.",
     "Arte generativa, shaders e ferramentas para programar imagens."),
    ("https://github.com/JoseDeFreitas/awesome-youtubers", "YouTubers", "learning",
     "Programming channels that actually teach something.",
     "Canais de programação que ensinam mesmo algo."),

    # --- beyond ------------------------------------------------------------
    ("https://github.com/Psyhackological/AAA", "AAA — Android Apps", "beyond",
     "Free and open-source Android apps for freedom and privacy.",
     "Aplicações Android livres para liberdade e privacidade."),
    ("https://github.com/Axorax/awesome-free-apps", "Free Apps", "beyond",
     "Free desktop and mobile applications, by platform.",
     "Aplicações gratuitas de desktop e móvel, por plataforma."),
    ("https://github.com/mr-karan/awesome-investing", "Investing", "beyond",
     "Books, blogs and tools for long-term investing.",
     "Livros, blogues e ferramentas para investir a longo prazo."),
    ("https://github.com/dreamingechoes/awesome-mental-health", "Mental Health", "beyond",
     "Mental-health resources and support for people in tech.",
     "Recursos de saúde mental e apoio para quem trabalha em tecnologia."),
    ("https://github.com/k4m4/movies-for-hackers", "Movies for Hackers", "beyond",
     "Films and series with a hacker plot worth watching.",
     "Filmes e séries com hackers que valem a pena."),
    ("https://github.com/noteflakes/awesome-music", "Music", "beyond",
     "Music software, labels and instruments for programmers.",
     "Software de música, editoras e instrumentos para programadores."),
    ("https://github.com/michelpereira/awesome-open-source-games", "Open Source Games", "beyond",
     "Playable open-source games and the engines behind them.",
     "Jogos open-source jogáveis e os motores por trás."),
    ("https://github.com/738/awesome-sushi", "Sushi", "beyond",
     "Types of sushi, etiquette and where to eat it.",
     "Tipos de sushi, etiqueta e onde o comer."),
]

DEEP = {"shell": "awesome-01-shell.html", "lang": "awesome-02-languages.html",
        "systems": "awesome-03-systems.html", "data": "awesome-04-data.html",
        "security": "awesome-05-security.html", "ai": "awesome-06-ai.html",
        "web": "awesome-07-web.html", "learning": "awesome-08-learning.html",
        "beyond": "awesome-09-beyond.html"}


def esc(t):
    return html.escape(t, quote=False)

def build():
    story = open(STORY, encoding="utf-8").read()
    linked = set(re.findall(r'href="(https://github\.com/[^"]+)"', story))
    ours = {u for u, *_ in E}
    if len(E) != len(ours):
        sys.exit("duplicate url in data")
    if linked - ours:
        sys.exit("missing from data: %s" % sorted(linked - ours))
    if ours - linked:
        sys.exit("not linked by the story page: %s" % sorted(ours - linked))

    n = len(E)
    title = "Awesome Index — %d Curated Lists, Sorted by Subject" % n
    desc = ("Every awesome list linked from this blog — %d of them — sorted by subject, "
            "from the shell and the languages to security, AI and dinner." % n)
    if not 110 <= len(desc) <= 155:
        sys.exit("description is %d characters" % len(desc))

    order = [g[0] for g in GROUPS]
    by_group = {g: [] for g in order}
    for url, name, g, en, pt in E:
        by_group[g].append((url, name, en, pt))

    # Each list's own table of contents, harvested from its README (tmp/sections.json).
    try:
        sections = json.load(open("tmp/sections.json", encoding="utf-8"))
    except (OSError, ValueError):
        sections = {}

    def contents(repo, word_sections, word_entries, word_more):
        entry = sections.get(repo) or {}
        names = entry.get("sections") or []
        if not names:
            return ""
        shown = names[:30]
        rest = len(names) - len(shown)
        tail = (" · +%d %s" % (rest, word_more)) if rest else ""
        return ('<details class="sec"><summary>%d %s · %d %s</summary>'
                '<p>%s%s</p></details>'
                % (len(names), word_sections, entry.get("entries", 0), word_entries,
                   esc(" · ".join(shown)), esc(tail)))

    rows = []
    nav = []
    for i, (key, ten, tpt, ben, bpt) in enumerate(GROUPS, 1):
        items = sorted(by_group[key], key=lambda r: r[1].lower())
        nav.append('<a href="#section-%s">%02d %s</a>' % (key, i, esc(ten)))
        body = []
        for url, name, en, pt in items:
            repo = url.replace("https://github.com/", "")
            head = ('<td><a href="%s" target="_blank" rel="noopener">%s</a>'
                    '<span class="repo">%s</span></td>' % (url, esc(name), esc(repo)))
            body.append('<tr>%s<td class="desc">%s%s</td></tr>'
                        % (head, esc(en), contents(repo, "sections", "entries", "more")))
        rows.append((i, key, ten, ben, len(items), "\n".join(body)))

    words = len(" ".join(
        [e[3] for e in E] + [e[1] for e in E] + [g[3] for g in GROUPS] + [g[1] for g in GROUPS]
    ).split()) + 150

    keywords = ", ".join(g[1] for g in GROUPS)

    def section(r):
        i, key, ten, ben, n, body = r
        return """
    <section class="grp" id="section-%s">
      <h2><span class="num">%02d</span> %s<span class="count">%d</span></h2>
      <p class="blurb">%s</p>
      <p class="shelf"><a href="%s">Every entry on this shelf, expandable →</a></p>
      <table>
        <thead><tr><th scope="col">List</th><th scope="col">What it collects</th></tr></thead>
        <tbody>
%s
        </tbody>
      </table>
    </section>""" % (key, i, esc(ten), n, esc(ben), DEEP[key], body)

    doc = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; img-src 'self' data:; style-src 'unsafe-inline'; script-src 'unsafe-inline'">
<meta name="X-Content-Type-Options" content="nosniff">
<meta name="X-Frame-Options" content="DENY">
<meta name="Referrer-Policy" content="no-referrer">
<title>%(title)s | Monkey Blog</title>
<meta name="description" content="%(desc)s">
<link rel="canonical" href="%(url)s">
<meta property="og:title" content="%(title)s">
<meta property="og:description" content="%(desc)s">
<meta property="og:type" content="article">
<meta property="og:url" content="%(url)s">
<meta property="og:site_name" content="Monkey Blog">
<meta property="og:image" content="%(img)s">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="%(title)s">
<meta name="twitter:description" content="%(desc)s">
<meta name="twitter:image" content="%(img)s">
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "BlogPosting",
      "@id": "%(url)s#article",
      "headline": "%(title)s",
      "name": "%(title)s",
      "description": "%(desc)s",
      "url": "%(url)s",
      "mainEntityOfPage": {
        "@type": "WebPage",
        "@id": "%(url)s"
      },
      "image": {
        "@type": "ImageObject",
        "url": "%(img)s",
        "width": 1496,
        "height": 960
      },
      "inLanguage": "en",
      "author": {
        "@type": "Person",
        "name": "Oscar",
        "url": "https://blog.odicforcesounds.com/",
        "sameAs": [
          "https://mastodon.social/@TaoExpression"
        ]
      },
      "publisher": {
        "@type": "Organization",
        "name": "Monkey Blog",
        "url": "https://blog.odicforcesounds.com/",
        "logo": {
          "@type": "ImageObject",
          "url": "https://blog.odicforcesounds.com/images/three.jpg",
          "width": 1024,
          "height": 1024
        }
      },
      "isPartOf": {
        "@type": "Blog",
        "name": "Monkey Blog",
        "url": "https://blog.odicforcesounds.com/"
      },
      "articleSection": "Programming & Development",
      "keywords": "%(keywords)s",
      "wordCount": %(words)s,
      "datePublished": "2026-11-02",
      "dateModified": "2026-11-02"
    },
    {
      "@type": "BreadcrumbList",
      "itemListElement": [
        {
          "@type": "ListItem",
          "position": 1,
          "name": "Home",
          "item": "https://blog.odicforcesounds.com/"
        },
        {
          "@type": "ListItem",
          "position": 2,
          "name": "Programming & Development",
          "item": "https://blog.odicforcesounds.com/#category-programming-and-development"
        },
        {
          "@type": "ListItem",
          "position": 3,
          "name": "%(title)s",
          "item": "%(url)s"
        }
      ]
    }
  ]
}
</script>
<style>
:root{
  --bg:#070b10;--ink:#e9f0f7;--dim:#a9b7c6;--muted:#7d8d9f;
  --line:rgba(126,163,196,.15);--line-2:rgba(126,163,196,.32);
  --accent:#54e3c4;--warm:#ffbe6b;--panel:#0c131b;
  --sans:system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
  --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:80px;-webkit-text-size-adjust:100%}
body{
  margin:0;color:var(--ink);font-family:var(--sans);font-size:16px;line-height:1.62;
  background:
    radial-gradient(60rem 38rem at 50% -14%,rgba(84,227,196,.07),transparent 62%),
    radial-gradient(46rem 30rem at 104% 30%,rgba(255,190,107,.05),transparent 60%),
    var(--bg);
}
.lang-switch{position:sticky;top:0;z-index:30;display:flex;justify-content:center;gap:4px;
  padding:9px;background:rgba(8,13,19,.92);border-bottom:1px solid var(--line);
  backdrop-filter:blur(8px)}
.lang-switch a{padding:6px 18px;border-radius:999px;font-family:var(--mono);font-size:11.5px;
  letter-spacing:.12em;text-transform:uppercase;color:var(--dim);text-decoration:none}
.lang-switch a:hover{color:var(--ink)}
.lang-switch a[aria-current="true"]{background:rgba(84,227,196,.14);color:var(--accent);
  box-shadow:inset 0 0 0 1px rgba(84,227,196,.42)}
.topbar{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:12px;
  max-width:1120px;margin:0 auto;padding:18px 20px 14px;border-bottom:1px solid var(--line)}
.brand{font-family:var(--mono);font-size:13px;color:var(--accent);text-decoration:none}
.brand:hover{text-decoration:underline}
.topbar-note{font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}
.wrap{max-width:1120px;margin:0 auto;padding:32px 20px 90px}
.kicker{font-family:var(--mono);font-size:10.5px;letter-spacing:.22em;text-transform:uppercase;color:var(--accent);margin:0 0 10px}
h1,.seo-h2{margin:0 0 12px;font-size:clamp(2rem,5.4vw,3.1rem);line-height:1.06;letter-spacing:-.02em}
h1 .dim{color:var(--muted)}
.lede{margin:0 0 14px;max-width:72ch;color:var(--dim);font-size:1.06rem}
.stats{margin:0;font-family:var(--mono);font-size:12px;color:var(--muted)}
.stats b{color:var(--ink);font-weight:600}
.contents{display:flex;flex-wrap:wrap;gap:7px;margin:28px 0 6px;padding:0}
.contents a{font-family:var(--mono);font-size:11.5px;letter-spacing:.04em;padding:6px 11px;
  border:1px solid var(--line-2);border-radius:999px;color:var(--dim);text-decoration:none}
.contents a:hover{color:var(--accent);border-color:rgba(84,227,196,.5)}
.deep{display:flex;flex-wrap:wrap;gap:7px;margin:16px 0 0}
.deep a{font-family:var(--mono);font-size:11.5px;padding:6px 11px;border:1px solid rgba(84,227,196,.35);
  border-radius:999px;color:var(--ink);text-decoration:none;background:rgba(84,227,196,.06)}
.deep a span{color:var(--accent);margin-left:6px}
.deep a:hover{background:rgba(84,227,196,.14)}
.grp{margin:46px 0 0;padding-top:20px;border-top:1px solid var(--line)}
.grp h2{display:flex;align-items:baseline;gap:10px;margin:0 0 8px;font-size:clamp(1.15rem,2.6vw,1.5rem);letter-spacing:-.01em}
.grp h2 .num{font-family:var(--mono);font-size:.66em;color:var(--accent)}
.grp h2 .count{margin-left:auto;font-family:var(--mono);font-size:.6em;color:var(--muted)}
.blurb{margin:0 0 10px;max-width:78ch;color:var(--dim);font-size:.96rem}
.shelf{margin:0 0 18px}
.shelf a{font-family:var(--mono);font-size:11.5px;letter-spacing:.04em;color:var(--accent);text-decoration:none}
.shelf a:hover{text-decoration:underline}
table{width:100%;border-collapse:collapse}
thead th{text-align:left;padding:8px 10px;font-family:var(--mono);font-size:10.5px;
  letter-spacing:.16em;text-transform:uppercase;color:var(--muted);border-bottom:1px solid var(--line-2)}
tbody td{padding:11px 10px;border-bottom:1px solid var(--line);vertical-align:top}
tbody tr:hover{background:rgba(255,255,255,.022)}
tbody td:first-child{width:31%}
td a{color:var(--ink);text-decoration:none;font-weight:600;border-bottom:1px solid rgba(84,227,196,.32)}
td a:hover{color:var(--accent);border-bottom-color:var(--accent)}
.repo{display:block;margin-top:3px;font-family:var(--mono);font-size:11px;color:var(--muted);word-break:break-word}
td.desc{color:var(--dim)}
.sec{margin:9px 0 0;padding-top:7px;border-top:1px dashed var(--line)}
.sec summary{cursor:pointer;font-family:var(--mono);font-size:10.5px;letter-spacing:.07em;
  text-transform:uppercase;color:var(--muted)}
.sec summary:hover{color:var(--accent)}
.sec p{margin:7px 0 0;font-size:12.5px;line-height:1.55;color:var(--muted)}
.page-foot{margin-top:58px;padding-top:18px;border-top:1px solid var(--line);color:var(--muted);font-size:14px}
.page-foot a{color:var(--accent)}
.page-foot p{margin:0 0 8px}
@media (max-width:640px){
  table,tbody,tr,td{display:block}
  thead{display:none}
  tbody tr{margin:0 0 12px;padding:8px 4px;border:1px solid var(--line);border-radius:9px}
  tbody td{border:0;padding:4px 9px}
  tbody td:first-child{width:auto;padding-bottom:0}
  td.desc{padding-top:6px}
}
@media print{
  .lang-switch,.topbar{display:none}
  body{background:#fff;color:#111}
  td a{color:#111}
}
</style>
</head>
<body>

<header class="topbar">
  <a class="brand" href="index.html">◀ Monkey Blog</a>
  <span class="topbar-note">Curated index · %(n)s lists</span>
</header>
<main class="wrap">
  <p class="kicker">Awesome · index</p>
  <h1>Awesome<br><span class="dim">index</span></h1>
  <p class="lede">The story page keeps the plot; this one keeps the map. Every GitHub list linked from <a href="awesome_story.html">Because People are Awesome</a> is here, filed by what it actually collects — and under each one, the list's own sections, so you know what is inside before you open it.</p>
  <p class="stats"><b>%(n)s</b> lists · <b>%(ng)s</b> sections · every link checked against the story page</p>
  <nav class="contents" aria-label="Sections">
    %(nav)s
  </nav>
%(sections_en)s
  <footer class="page-foot">
    <p>The narrative version, with the people and the reasons, is the link in the lede above. Every entry opens its list on GitHub in a new tab; nothing is fetched at load time and this page carries no script.</p>
  </footer>
</main>
</body>
</html>
"""

    mapping = {
        "title": esc(title),
        "desc": esc(desc),
        "url": URL,
        "img": IMG,
        "keywords": keywords.replace('"', "'"),
        "words": str(words),
        "n": str(n),
        "ng": str(len(GROUPS)),
        "nav": "\n    ".join(nav),
        "sections_en": "".join(section(r) for r in rows),
    }
    for key, value in mapping.items():
        doc = doc.replace("%%(%s)s" % key, value)

    open(OUT, "w", encoding="utf-8").write(doc)
    print("wrote %s: %d entries, %d sections, %d words" % (OUT, len(E), len(GROUPS), words))
    print("description: %d characters | title: %d characters" % (len(desc), len(title)))


if __name__ == "__main__":
    build()
