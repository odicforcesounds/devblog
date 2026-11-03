#!/usr/bin/env python3
"""Categories 02-09, expanded the same way as 01.

Category -> Awesome list -> theme drawer -> tool card (number, summary from the
list's own words, a real example where one can be given honestly, source link).
One page per category, English only. Links are deduplicated inside a page.
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
ORIGIN = "https://blog.odicforcesounds.com"
IMG = ORIGIN + "/images/peace.jpg"

CATS = {
    "lang": dict(
        num="02", slug="languages", flat="awesome-tools-lang-1.html",
        title="Awesome 02 — Languages and Frameworks, Expanded",
        h1="Languages and frameworks",
        desc=("Category 02 opened up: every language and framework list, each tool in its own "
              "collapsible card with a summary and a real example where one exists."),
        lede=("Every link the language lists point at, opened one level further: category, "
              "then list, then the tool's own card. One card per tool — a library listed by two "
              "lists keeps a single card and says where else it appears."),
        small=("Read it as a shelf of shelves: open a language, then a drawer, then a tool. Cards "
               "that are documentation rather than a program say so instead of inventing a command."),
        keywords="programming languages, frameworks, libraries, rust, go, python, javascript, typescript",
    ),
    "systems": dict(
        num="03", slug="systems", flat="awesome-tools-systems-1.html",
        title="Awesome 03 — Servers, Containers and Self-Hosting, Expanded",
        h1="Servers, containers and self-hosting",
        desc=("Category 03 opened up: every server and self-hosting list, each tool in its own "
              "collapsible card with a summary and a real example where one exists."),
        lede=("The machines you run yourself, from the container upwards: the lists that collect "
              "them, and under each list the tools themselves in their own cards."),
        small=("Everything here is something you install on a machine you own, or on one you rent "
               "and pretend to own. Where a card is a guide instead of a program, it says so."),
        keywords="self-hosting, docker, kubernetes, containers, backups, vpn, homelab, linux servers",
    ),
    "data": dict(
        num="04", slug="data", flat="awesome-tools-data.html",
        title="Awesome 04 — Data, Networks and Archives, Expanded",
        h1="Data, networks and archives",
        desc=("Category 04 opened up: the data, network and archive lists, each tool in its own "
              "collapsible card with a summary and a real example where one exists."),
        lede=("Information on the move and information at rest: databases, pipelines, packets, "
              "crawlers and the people who archive the web before it forgets itself."),
        small=("Open a list, then a drawer, then a tool. A database is not a command line in the "
               "same way a crawler is, and the cards keep that difference visible."),
        keywords="data, databases, networks, archives, kafka, postgres, crawling, analytics",
    ),
    "security": dict(
        num="05", slug="security", flat="awesome-tools-security-1.html",
        title="Awesome 05 — Security, Privacy and Forensics, Expanded",
        h1="Security, privacy and forensics",
        desc=("Category 05 opened up: the security, privacy and forensics lists, each tool in its "
              "own collapsible card with a summary and a real example where one exists."),
        lede=("The largest shelf in the collection, and the one that needs the most care: recon, "
              "web testing, exploitation, forensics, defence and the privacy tools in between."),
        small=("Examples are written for machines you own or are authorised to test. Where a card "
               "is a writeup, a lab or a book rather than a program, it says so plainly."),
        keywords="security, penetration testing, forensics, privacy, malware analysis, blue team",
    ),
    "ai": dict(
        num="06", slug="ai", flat="awesome-tools-ai.html",
        title="Awesome 06 — AI and Automation, Expanded",
        h1="AI and automation",
        desc=("Category 06 opened up: the AI and automation lists, each tool in its own collapsible "
              "card with a summary and a real example where one exists."),
        lede=("Models, agents and the wiring that puts them to work — two lists, and under them "
              "the tools people actually run when they say they are running a model."),
        small=("Small shelf, fast shelf. Open a list, then a drawer, then a card; the examples show "
               "the command you need before the first token appears."),
        keywords="artificial intelligence, llm, agents, automation, machine learning, models",
    ),
    "web": dict(
        num="07", slug="web", flat="awesome-tools-web.html",
        title="Awesome 07 — Web, Design and Product, Expanded",
        h1="Web, design and product",
        desc=("Category 07 opened up: the web, design and product lists, each tool in its own "
              "collapsible card with a summary and a real example where one exists."),
        lede=("How interfaces get designed, documented and shipped: design systems, CSS, testing, "
              "audits, docs and the product work around them."),
        small=("Open a list, then a drawer, then a card. The examples run in a terminal even when "
               "the tool itself lives in a browser tab."),
        keywords="web design, css, accessibility, performance, documentation, product",
    ),
    "learning": dict(
        num="08", slug="learning", flat="awesome-tools-learning-1.html",
        title="Awesome 08 — Learning, Careers and Collections, Expanded",
        h1="Learning, careers and collections",
        desc=("Category 08 opened up: the learning and career lists, each resource in its own "
              "collapsible card with a summary and a note on what it actually is."),
        lede=("Curricula, books, interviews and the people worth following — a category where most "
              "cards are not software, and pretending otherwise would be the only lie here."),
        small=("Read it as a reading list with drawers. Cards say what kind of thing they are: a "
               "course, a repo of questions, a newsletter, a book."),
        keywords="learning, roadmaps, computer science, interviews, careers, newsletters",
    ),
    "beyond": dict(
        num="09", slug="beyond", flat="awesome-tools-beyond.html",
        title="Awesome 09 — Beyond Code, Expanded",
        h1="Beyond code",
        desc=("Category 09 opened up: the lists about life outside the terminal — food, music, "
              "money, health, games — each entry in its own collapsible card."),
        lede=("Food, music, money, health, games: the lists that have nothing to do with work and "
              "everything to do with living. Same shape as the rest, different content."),
        small=("Almost nothing here is a command, and the cards say so. Open a list, then a drawer, "
               "then the one entry you came for."),
        keywords="food, music, books, health, finance, games, travel, life",
    ),
}

# --------------------------------------------------------------- themes
EVERYTHING_ELSE = "Everything else"

THEMES = {
    "lang": [
        ("Learning, guides and examples", ["tutorial", "course", "book", "learn", "guide", "handbook",
                                           "cheat sheet", "cheatsheet", "playground", "interview",
                                           "roadmap", "exercise", "curriculum", "awesome", "example",
                                           "blog", "video", "podcast", "newsletter"]),
        ("Package managers and dependencies", ["package manager", "dependency", "dependencies", "pip",
                                               " npm", "cargo", "registry", "lockfile", "module",
                                               "vendor", "monorepo", "workspace", "version manag"]),
        ("Build tools and bundlers", ["bundler", "build tool", "build system", "webpack", "vite",
                                      "rollup", "esbuild", "cmake", "bazel", "makefile", "transpil",
                                      "babel", "swc", "parcel", "compil", "toolchain", "build"]),
        ("Testing, mocking and benchmarks", ["test", "spec", "assert", "mock", "fuzz", "benchmark",
                                             "coverage", "fixture", "property-based", "snapshot"]),
        ("Linters, formatters and types", ["lint", "format", "type check", "static analysis",
                                           "code style", "code quality", "parser", "syntax tree",
                                           "prettier", "eslint", "ruff", "mypy", "pylint", "clippy"]),
        ("Web frameworks and APIs", ["web framework", "http framework", "rest", "graphql", "api",
                                     "router", "middleware", "microservice", "rpc", "grpc",
                                     "websocket", "server", "endpoint", "backend", "back-end"]),
        ("Front-end and UI", ["frontend", "front-end", "ui component", "component", "react", "vue",
                              "svelte", "css", "dom", "template", "design system", "tailwind",
                              "state management", "browser", "html"]),
        ("Databases, ORMs and storage", ["database", "orm", "sql", "query builder", "migration",
                                         "storage", "cache", "redis", "postgres", "mongo", "sqlite",
                                         "key-value", "persistence", "index", "schema"]),
        ("Async, concurrency and networking", ["async", "concurren", "thread", "coroutine",
                                               "event loop", "channel", "actor", "socket", "tcp",
                                               "http client", "networking", "reactive", "stream"]),
        ("CLI, TUI and developer tools", ["cli", "command line", "command-line", "terminal", "tui",
                                          "argument parser", "flag", "shell", "generator", "boilerplate",
                                          "scaffold", "starter", "template engine"]),
        ("Serialization and data formats", ["json", "yaml", "toml", "serializ", "encoding", "protobuf",
                                           "csv", "xml", "msgpack", "parsing"]),
        ("Logging, metrics and configuration", ["log", "metric", "trace", "monitor", "telemetry",
                                                "config", "environment", "dotenv", "debug"]),
        ("Security, auth and crypto", ["auth", "security", "encrypt", "crypto", "jwt", "oauth",
                                       "sanitiz", "permission", "secret", "tls", "vulnerab"]),
        ("Games, graphics and media", ["game", "graphic", "image", "video", "audio", "render",
                                       "canvas", "chart", "plot", "visuali", "animation", "3d",
                                       "draw", "font"]),
        ("Machine learning and AI", ["machine learning", "deep learning", "neural", "llm", "tensor",
                                     "nlp", "embedding", "model", "inference", "dataset"]),
        ("Deploy, containers and cloud", ["docker", "kubernetes", "deploy", "container", "ci/cd",
                                          "devops", "cloud", "serverless", "infrastructure",
                                          "terraform", "aws", "azure"]),
        ("Mobile and desktop apps", ["android", "ios", "mobile", "desktop", "electron", "tauri",
                                     "flutter", "react native", "cross-platform", "swiftui"]),
        ("Documentation and site generators", ["documentation", "docs", "site generator", "readme",
                                              "markdown", "comment", "docstring", "changelog"]),
        ("Editors, IDEs and language servers", ["editor", "ide", "vim", "emacs", "vscode", "plugin",
                                               "extension", "syntax highlight", "language server",
                                               "lsp", "sublime"]),
        ("Runtime and standard library", ["interpreter", "compiler", "runtime", "virtual machine",
                                          "standard library", "repl", "garbage collect", "memory"]),
    ],
    "systems": [
        ("Containers and orchestration", ["docker", "podman", "kubernetes", "k8s", "container", "helm",
                                          "nomad", "swarm", "compose", "rancher", "k3s", "image"]),
        ("Self-hosted apps and services", ["self-host", "self host", "alternative to", "server for",
                                           "host your own", "home server", "dashboard", "notes",
                                           "photos", "calendar", "media server", "front-end for"]),
        ("Backup, sync and archives", ["backup", "restic", "borg", "rsync", "sync", "snapshot",
                                       "archive", "duplicati", "rclone", "replicat"]),
        ("Storage, filesystems and NAS", ["filesystem", "zfs", "btrfs", "nfs", "smb", "samba",
                                          "storage", "disk", "raid", "nas", "drive", "object storage"]),
        ("Networking, VPN, DNS and proxies", ["vpn", "wireguard", "tailscale", "dns", "proxy",
                                              "reverse proxy", "tunnel", "firewall", "router",
                                              "load balanc", "mesh", "zerotier", "traefik", "caddy",
                                              "nginx", "network"]),
        ("Virtualisation and homelab", ["virtual machine", "hypervisor", "proxmox", "qemu", "kvm",
                                        "homelab", "lab", "lxc", "vm", "emulat"]),
        ("Infrastructure as code", ["terraform", "ansible", "pulumi", "iac", "configuration management",
                                    "nix", "declarative", "provision", "puppet", "chef", "saltstack"]),
        ("Operating systems and distros", ["distro", "linux", "freebsd", "openbsd", "bsd",
                                           "operating system", "kernel", "alpine", "debian", "arch"]),
        ("Monitoring and dashboards", ["monitor", "metric", "dashboard", "grafana", "prometheus",
                                       "uptime", "alert", "status page", "log", "observab"]),
        ("Access, secrets and certificates", ["security", "auth", "sso", "password", "secret", "vault",
                                             "certificate", "tls", "ssh", "2fa", "ldap"]),
        ("Media and entertainment servers", ["media", "music", "video", "stream", "plex", "jellyfin",
                                             "photo", "podcast", "book", "audiobook"]),
        ("Productivity and collaboration", ["collaborat", "wiki", "chat", "team", "project management",
                                           "kanban", "office", "docs", "rss", "bookmark", "email",
                                           "task", "note"]),
        ("Deploy, CI/CD and git hosting", ["deploy", "ci", "cd", "pipeline", "gitops", "build server",
                                           "release", "jenkins", "gitlab", "gitea", "git server"]),
        ("Cloud and hosting platforms", ["cloud", "aws", "s3", "serverless", "hosting", "vps",
                                         "minio", "s3-compatible", "domain"]),
        ("Home automation and IoT", ["home assistant", "home automation", "iot", "mqtt", "zigbee",
                                     "sensor", "smart home", "esp32", "esp8266"]),
        ("Databases and data services", ["database", "postgres", "mysql", "redis", "mongo", "sql",
                                        "search engine"]),
        ("Guides, lists and directories", ["awesome", "list of", "curated", "guide", "resource",
                                           "example", "tutorial", "book", "collection"]),
    ],
    "data": [
        ("Databases and query engines", ["database", "sql", "postgres", "mysql", "sqlite", "mongo",
                                         "clickhouse", "duckdb", "oracle", "db2", "cassandra",
                                         "neo4j", "graph database", "query engine", "olap"]),
        ("Streaming, queues and events", ["kafka", "queue", "stream", "rabbitmq", "nats", "pubsub",
                                          "event", "pulsar", "message broker", "consumer"]),
        ("Analytics and dashboards", ["analytics", "business intelligence", "dashboard", "report",
                                      "superset", "metabase", "chart", "visuali", "bi"]),
        ("Pipelines and orchestration", ["pipeline", "etl", "elt", "airflow", "dag", "orchestrat",
                                         "prefect", "dagster", "scheduler", "workflow", "dbt",
                                         "transform", "ingest"]),
        ("Dataframes, notebooks and science", ["dataframe", "pandas", "polars", "numpy", "notebook",
                                               "jupyter", "science", "statistic", "analysis", "plot"]),
        ("Search and indexing", ["search", "index", "elasticsearch", "solr", "meilisearch",
                                 "typesense", "full text", "opensearch", "ranking"]),
        ("Crawlers, scraping and archives", ["crawl", "scrap", "spider", "archive", "wayback",
                                             "harvest", "extract", "parse html", "wget", "mirror"]),
        ("Networks, packets and protocols", ["graph", "network", "packet", "protocol", "tcp", "dns",
                                             "p2p", "mesh", "topology", "sniff", "pcap"]),
        ("Formats, parsing and conversion", ["format", "pars", "csv", "json", "yaml", "parquet",
                                             "arrow", "avro", "serializ", "convert", "encode",
                                             "text", "markdown"]),
        ("Time series, logs and ledgers", ["ledger", "time series", "timeseries", "log", "event",
                                           "metric", "influx", "prometheus", "tsdb", "account"]),
        ("Storage, filesystems and object stores", ["storage", "filesystem", "key-value", "kv store",
                                                    "s3", "object storage", "block", "lsm",
                                                    "deduplicat", "compression"]),
        ("Teaching, reference and research", ["book", "tutorial", "course", "paper", "guide", "learn",
                                              "example", "cheat", "awesome", "reference", "blog",
                                              "list of"]),
        ("Privacy and encryption for data", ["security", "encrypt", "privacy", "anonym", "hash",
                                             "scrub", "redact", "pii"]),
        ("Geo, maps and space", ["geo", "map", "gis", "spatial", "satellite", "openstreetmap",
                                 "coordinate", "astronom", "osm"]),
    ],
    "security": [
        ("Reconnaissance and OSINT", ["recon", "osint", "subdomain", "enumeration", "footprint",
                                      "shodan", "whois", "google dork", "social", "dns", "harvest",
                                      "username", "email"]),
        ("Web application testing", ["web", "xss", "sqli", "injection", "fuzz", "burp", "crawler",
                                     "wordpress", "api testing", "scanner", "cms", "jwt", "oauth"]),
        ("Network scanning and exploitation", ["scan", "nmap", "masscan", "exploit", "metasploit",
                                               "pivot", "sniff", "packet", "mitm", "spoof", "smb",
                                               "network"]),
        ("Password and credential attacks", ["password", "hash", "crack", "brute", "wordlist",
                                             "credential", "kerberos", "ntlm", "rainbow", "hashcat",
                                             "john"]),
        ("Malware, reversing and forensics", ["malware", "reverse", "reversing", "ghidra", "ida",
                                              "disassembl", "forensic", "memory", "disk", "artifact",
                                              "yara", "sandbox", "dump", "sample", "binary"]),
        ("Wireless, radio and hardware", ["wifi", "wireless", "bluetooth", "rfid", "sdr", "hardware",
                                          "usb", "badusb", "radio", "wardriving", "antenna"]),
        ("Active Directory and Windows", ["active directory", "windows", "domain controller",
                                          "lateral", "powershell", "bloodhound", "kerberoast",
                                          "privesc", "privilege escalation"]),
        ("Defence, detection and hardening", ["defen", "detect", "hardening", "blue team", "edr",
                                              "siem", "ids", "ips", "soc", "audit", "compliance",
                                              "baseline", "incident", "threat hunt"]),
        ("Privacy, anonymity and encryption", ["privacy", "anonym", "tor", "vpn", "encrypt", "gpg",
                                               "messenger", "tracking", "blocker", "metadata",
                                               "fingerprint", "secure messaging"]),
        ("Threat intelligence and research", ["threat", "intel", "feed", "cve", "vulnerability",
                                              "advisory", "research", "report", "writeup",
                                              "bug bounty", "blog"]),
        ("Exploit collections and payloads", ["payload", "shellcode", "exploit", "poc", "c2",
                                              "command and control", "backdoor", "rootkit", "rat",
                                              "webshell", "cheatsheet"]),
        ("Training, labs and CTFs", ["ctf", "lab", "training", "practice", "challenge", "vulnerable",
                                     "exercise", "book", "course", "tutorial", "awesome", "learn",
                                     "handbook"]),
        ("Cloud and container security", ["cloud", "aws", "azure", "gcp", "kubernetes", "container",
                                          "docker", "iam", "serverless", "s3 bucket", "k8s"]),
        ("Mobile and application security", ["android", "ios", "mobile", "apk", "frida", "jailbreak",
                                             "app security", "desktop"]),
    ],
    "ai": [
        ("Models and inference", ["model", "weights", "inference", "llama", "transformers", "runtime",
                                  "quantiz", "gpt", "diffusion", "embedding model"]),
        ("Agents and automation", ["agent", "automation", "tool use", "workflow", "autonomous",
                                   "chain", "orchestrat", "assistant", "copilot", "bot"]),
        ("Prompts, evaluation and data", ["prompt", "evaluation", "benchmark", "dataset", "fine-tun",
                                          "training", "tokeniz", "test"]),
        ("RAG, vectors and search", ["rag", "vector", "embedding", "retrieval", "search", "index",
                                     "semantic", "knowledge base"]),
        ("Image, audio and video generation", ["image", "diffusion", "audio", "speech", "video",
                                               "vision", "generat", "voice", "music"]),
        ("Apps, interfaces and tooling", ["ui", "app", "chat", "interface", "frontend", "desktop",
                                          "web", "cli", "extension", "tool"]),
        ("Learning and reference", ["course", "book", "tutorial", "paper", "list", "guide",
                                    "awesome", "learn", "blog"]),
    ],
    "web": [
        ("Design systems and UI kits", ["design system", "ui kit", "component", "pattern", "style guide",
                                        "design token", "figma", "sketch", "library"]),
        ("CSS, fonts and animation", ["css", "sass", "tailwind", "styling", "postcss", "animation",
                                      "font", "color", "icon", "layout"]),
        ("Accessibility", ["accessib", "a11y", "wcag", "screen reader", "contrast", "aria"]),
        ("Performance, audits and testing", ["performance", "lighthouse", "audit", "bundle size",
                                             "speed", "optimiz", "core web vitals", "test", "e2e",
                                             "cypress", "playwright", "qa"]),
        ("Documentation, APIs and specs", ["documentation", "api", "openapi", "swagger", "redoc",
                                           "spec", "markdown", "readme", "changelog", "docs"]),
        ("Prototyping, research and product", ["prototyp", "wireframe", "product", "roadmap",
                                              "user research", "usability", "mvp", "survey",
                                              "analytics", "growth"]),
        ("Images, media and assets", ["image", "illustration", "photo", "svg", "gif", "video",
                                      "stock", "placeholder", "avatar"]),
        ("Hosting, deployment and CMS", ["host", "deploy", "cms", "static site", "jamstack",
                                         "netlify", "vercel", "wordpress", "cdn", "domain"]),
        ("Learning and reference", ["book", "course", "guide", "tutorial", "list", "awesome",
                                    "resource", "reference", "blog", "newsletter"]),
    ],
    "learning": [
        ("Curricula and roadmaps", ["curriculum", "roadmap", "learning path", "syllabus", "bootcamp",
                                    "degree", "university", "self-taught"]),
        ("Courses and video", ["course", "video", "lecture", "mooc", "youtube", "class", "lesson",
                               "talk", "conference"]),
        ("Books and reading", ["book", "reading", "library", "paper", "essay", "manual", "notes"]),
        ("Interview preparation", ["interview", "leetcode", "system design", "coding challenge",
                                   "question", "algorithm", "data structure", "puzzle"]),
        ("Career and work", ["career", "job", "resume", "salary", "remote", "freelance", "hiring",
                             "manager", "productivity", "cv"]),
        ("Computer science fundamentals", ["computer science", "algorithm", "operating system",
                                           "compiler", "math", "theory", "distributed", "database",
                                           "network", "architecture"]),
        ("Practice and projects", ["project", "exercise", "practice", "kata", "challenge", "build",
                                   "example", "tutorial", "workshop"]),
        ("People, blogs and communities", ["newsletter", "blog", "podcast", "community", "people",
                                           "follow", "forum", "twitter", "awesome"]),
        ("Free resources and collections", ["free", "resource", "collection", "list", "awesome",
                                            "curated", "open source", "repository"]),
    ],
    "beyond": [
        ("Food and drink", ["food", "recipe", "cook", "restaurant", "coffee", "tea", "wine", "beer",
                            "sushi", "kitchen", "bak", "cheese", "bread"]),
        ("Music and sound", ["music", "album", "song", "band", "audio", "guitar", "piano", "synth",
                             "playlist", "sound", "dj", "instrument"]),
        ("Books, film and art", ["book", "film", "movie", "art", "comic", "reading", "poetry",
                                 "theatre", "anime", "manga", "cinema", "photograph"]),
        ("Money and markets", ["money", "finance", "invest", "crypto", "bitcoin", "stock", "budget",
                               "econom", "bank", "tax", "salary", "frugal"]),
        ("Health, mind and body", ["health", "fitness", "mental", "sleep", "meditation", "exercise",
                                   "nutrition", "therapy", "yoga", "habit", "mindful"]),
        ("Games and play", ["game", "gaming", "puzzle", "board game", "rpg", "chess", "emulator",
                            "retro", "speedrun", "mod"]),
        ("Travel and places", ["travel", "city", "country", "map", "hotel", "flight", "place",
                               "tourism", "hiking", "nomad"]),
        ("Learning and language", ["language", "learn", "course", "book", "tutorial", "study",
                                   "education", "dictionary", "translat"]),
        ("Science, nature and space", ["science", "nature", "space", "astronom", "biology", "physics",
                                       "climate", "animal", "plant", "ocean", "rocket"]),
        ("Society, law and politics", ["law", "politics", "society", "history", "philosoph",
                                       "justice", "policy", "government", "rights", "ethic"]),
        ("Tools for living", ["tool", "app", "productivity", "home", "garden", "diy", "kitchen",
                              "life", "organiz", "minimal"]),
    ],
}

# Links that are a list's own navigation, or the "related links" column of an entry
# (a project's Website, Repo, Paper, Founder's X ...), not the tool itself. Only
# dropped when the entry has no description at all, and only on a word boundary, so
# a real tool called "DemoGPT" or "Paperless" survives.
JUNK_RE = re.compile(
    r"^(?:"
    r"web|x|tweet|twitter|reddit|facebook|linkedin|discord|slack|youtube|medium|substack"
    r"|repo|paper|demo|guide|docs|documentation|website|home|homepage|github"
    r"|blog|video|site|source|code|link|repository|forum|wiki|rss|newsletter"
    r"|launch|article|playground|templates|use cases|ai features"
    r"|step-by-step|getting started|interview|underlying paper|arxiv|colab|hackernews"
    r"|ycombinator|product hunt|hacker news|app store|play store|chrome web store"
    r"|docker image|extension|figma|npm|pypi|read more|creators|creator|author"
    r"|founder|co-founder|hit us up|chat|demo video|twitter thread"
    r"|profile|license|subreddit|meme|waitlist|announcement|the tweet"
    r"|javascript version|project page|project demo|local demo|game data"
    r")\b", re.I)


# The tail of a compound name, when it names a link or a person's role rather than
# the entry itself: "Kaveen Kumarasinghe - founder of GPT Discord - website".
TAIL_RE = re.compile(
    r"(?i)^(website|site|homepage|linkedin|x|twitter|x\s*\(twitter\)|founder.*|co-?founder.*"
    r"|ceo.*|cto.*|docs?|documentation|guide|demo|paper|repo|github.*|blog.*|video"
    r"|youtube.*|instagram.*|discord.*|playground|pricing|app)$")
GENERIC = {"installation", "install", "ceo", "cto", "about", "team", "contact",
           "features", "pricing", "changelog", "faq", "roadmap", "usage", "examples",
           "license", "support", "community", "download"}


def junk(tool):
    if (tool["desc"] or "").strip():
        return False
    name = tool["name"].strip()
    if JUNK_RE.match(name):
        return True
    if re.search(r"\s[-–]\s", name) and TAIL_RE.match(re.split(r"\s[-–]\s", name)[-1]):
        return True
    return name.lower() in GENERIC


# ---------------------------------------------------------------- examples
# Only commands that are correct as written. A tool without an entry gets an
# honest note about what kind of thing it is instead.
EXAMPLES = {
    # language toolchains and frameworks
    "typescript": "npx tsc --noEmit",
    "python": "python3 -m venv .venv && . .venv/bin/activate",
    "go": "go mod tidy",
    "rust": "cargo new app && cargo run",
    "node.js": "node --watch server.js",
    "nodejs": "node --watch server.js",
    "react": "npm create vite@latest app -- --template react",
    "vue.js": "npm create vue@latest",
    "angular": "ng new app --standalone",
    "django": "django-admin startproject site",
    "flask": "flask --app app run --debug",
    "fastapi": "uvicorn main:app --reload",
    "ruby": "ruby -v",
    "ruby on rails": "rails new blog",
    "php": "php -S localhost:8000",
    "laravel": "composer create-project laravel/laravel blog",
    "java": "javac Main.java && java Main",
    "kotlin": "kotlinc main.kt -include-runtime -d main.jar",
    "swift": "swift run",
    "flutter": "flutter create app && flutter run",
    "tailwind css": "npx tailwindcss -i in.css -o out.css --watch",
    "svelte": "npm create svelte@latest app",
    "next.js": "npx create-next-app@latest",
    "deno": "deno run --allow-net app.ts",
    "bun": "bun init",
    "elixir": "mix new app",
    "haskell": "stack new app",
    "scala": "scala-cli run main.scala",
    "clojure": "clj -M -e '(println \"hi\")'",
    "elm": "elm reactor",
    "lua": "lua main.lua",
    "perl": "perl -e 'print \"hi\\n\"'",
    "r": "Rscript analysis.R",
    "julia": "julia -e 'println(1 + 1)'",
    "c": "cc -Wall -Wextra -o app main.c",
    "c++": "c++ -std=c++20 -O2 -o app main.cpp",
    "c#": "dotnet new console && dotnet run",
    "f#": "dotnet fsi script.fsx",
    "ocaml": "dune build",
    "zig": "zig build-exe main.zig",
    "nim": "nim c -r main.nim",
    "crystal": "crystal run main.cr",
    "dart": "dart run",
    "solidity": "solc --bin contract.sol",
    "webpack": "npx webpack --mode production",
    "vite": "npm create vite@latest",
    "jest": "npx jest --coverage",
    "vitest": "npx vitest run",
    "pytest": "pytest -q",
    "ruff": "ruff check . --fix",
    "eslint": "npx eslint . --fix",
    "prettier": "npx prettier --write .",
    "black": "black .",
    "mypy": "mypy src",
    "poetry": "poetry add requests",
    "uv": "uv run python script.py",
    "pipenv": "pipenv install requests",
    "pandas": "python3 -c \"import pandas as pd; print(pd.read_csv('f.csv').head())\"",
    "polars": "python3 -c \"import polars as pl; print(pl.read_csv('f.csv').head())\"",
    # servers, containers, self-hosting
    "docker": "docker run --rm -it alpine sh",
    "docker compose": "docker compose up -d",
    "kubernetes": "kubectl get pods -A",
    "helm": "helm install app ./chart",
    "terraform": "terraform plan",
    "ansible": "ansible-playbook -i hosts site.yml",
    "traefik": "traefik --configFile=traefik.yml",
    "nginx": "nginx -t && systemctl reload nginx",
    "caddy": "caddy run --config Caddyfile",
    "wireguard": "wg show",
    "tailscale": "tailscale up",
    "portainer": "docker run -d -p 9000:9000 portainer/portainer-ce",
    "restic": "restic -r /srv/backup backup ~/docs",
    "borg": "borg create ::backup ~/docs",
    "borgbackup": "borg create ::backup ~/docs",
    "syncthing": "syncthing serve",
    "minio": "minio server ~/data",
    "k3s": "curl -sfL https://get.k3s.io | sh -",
    "podman": "podman run --rm alpine echo hi",
    "nix": "nix-shell -p ripgrep",
    "systemd": "systemctl status sshd",
    "zfs": "zfs list",
    "jellyfin": "docker run -d -p 8096:8096 jellyfin/jellyfin",
    "gitea": "docker run -d -p 3000:3000 -p 222:22 gitea/gitea",
    "uptime kuma": "docker run -d -p 3001:3001 louislam/uptime-kuma",
    "home assistant": "docker run -d -p 8123:8123 ghcr.io/home-assistant/home-assistant:stable",
    "pi-hole": "docker run -d -p 53:53/tcp -p 53:53/udp -p 8053:80 pihole/pihole",
    "vault": "vault server -dev",
    "prometheus": "promtool check config prometheus.yml",
    "grafana": "docker run -d -p 3000:3000 grafana/grafana",
    # data
    "postgresql": "psql -h localhost -U postgres",
    "postgres": "psql -h localhost -U postgres",
    "mysql": "mysql -h 127.0.0.1 -u root -p",
    "sqlite": "sqlite3 app.db '.schema'",
    "redis": "redis-cli --scan --pattern 'user:*'",
    "apache kafka": "kafka-topics.sh --bootstrap-server localhost:9092 --list",
    "kafka": "kafka-topics.sh --bootstrap-server localhost:9092 --list",
    "elasticsearch": "curl -s localhost:9200/_cat/indices?v",
    "mongodb": "mongosh",
    "clickhouse": "clickhouse-client -q 'select 1'",
    "duckdb": "duckdb -c 'select * from read_csv_auto(\"f.csv\") limit 5'",
    "neo4j": "cypher-shell 'MATCH (n) RETURN count(n)'",
    "dbt": "dbt run",
    "apache airflow": "airflow dags list",
    "pandas ": "python3 -c \"import pandas as pd\"",
    "pyarrow": "python3 -c \"import pyarrow.parquet as pq; print(pq.read_table('f.parquet').schema)\"",
    "nmap": "nmap -sV -T4 10.0.0.0/24",
    # security
    "metasploit": "msfconsole -q",
    "wireshark": "tshark -i eth0 -f 'tcp port 443'",
    "tcpdump": "tcpdump -i eth0 -nn 'port 53'",
    "john the ripper": "john --wordlist=rockyou.txt hashes.txt",
    "hashcat": "hashcat -m 0 -a 0 hashes.txt rockyou.txt",
    "hydra": "hydra -l admin -P rockyou.txt ssh://10.0.0.5",
    "sqlmap": "sqlmap -u 'http://target/item?id=1' --batch",
    "nikto": "nikto -h https://target",
    "gobuster": "gobuster dir -u https://target -w wordlist.txt",
    "ffuf": "ffuf -u https://target/FUZZ -w wordlist.txt",
    "nuclei": "nuclei -u https://target -severity high,critical",
    "amass": "amass enum -d example.com",
    "subfinder": "subfinder -d example.com -silent",
    "httpx": "httpx -l hosts.txt -status-code",
    "masscan": "masscan 10.0.0.0/8 -p443 --rate 10000",
    "aircrack-ng": "aircrack-ng -w rockyou.txt capture.cap",
    "bettercap": "bettercap -iface wlan0",
    "mitmproxy": "mitmproxy -p 8080",
    "responder": "responder -I eth0 -wv",
    "impacket": "impacket-smbserver share . -smb2support",
    "bloodhound": "bloodhound-python -d corp.local -u user -p pass -c All",
    "volatility": "vol.py -f dump.raw imageinfo",
    "sleuth kit": "fls -r image.dd",
    "binwalk": "binwalk -e firmware.bin",
    "radare2": "r2 -A ./binary",
    "gdb": "gdb -q ./binary",
    "yara": "yara rules.yar sample.bin",
    "clamav": "clamscan -r ~/Downloads",
    "age": "age -p -o secret.age secret.txt",
    "gpg": "gpg --symmetric secret.txt",
    "tor": "curl --socks5-hostname 127.0.0.1:9050 https://check.torproject.org",
    "proxychains": "proxychains4 curl https://ifconfig.me",
    "wpscan": "wpscan --url https://target --enumerate vp",
    "theharvester": "theHarvester -d example.com -b duckduckgo",
    "sherlock": "sherlock username",
    "exiftool": "exiftool photo.jpg",
    "ssh-audit": "ssh-audit host",
    "lynis": "lynis audit system",
    "rkhunter": "rkhunter --check",
    "fail2ban": "fail2ban-client status sshd",
    "suricata": "suricata -i eth0 -c suricata.yaml",
    "zeek": "zeek -i eth0",
    "osquery": "osqueryi 'select pid, name from processes limit 5;'",
    "miranda": "miranda",
    # ai
    "ollama": "ollama run llama3.2",
    "transformers": "python3 -c \"from transformers import pipeline; print(pipeline('sentiment-analysis')('good'))\"",
    "whisper": "whisper audio.mp3 --model small",
    "vllm": "vllm serve meta-llama/Llama-3.2-1B",
    "langchain": "python3 -c \"from langchain_openai import ChatOpenAI; print(ChatOpenAI().invoke('hi'))\"",
    # web
    "storybook": "npx storybook@latest init",
    "lighthouse": "npx lighthouse https://example.com --view",
    "playwright": "npx playwright test",
    "cypress": "npx cypress open",
    "sass": "npx sass in.scss out.css",
    "stylelint": "npx stylelint '**/*.css'",
    "redoc": "npx @redocly/cli lint openapi.yaml",
    "netlify cli": "netlify deploy --prod",
    "vercel": "vercel --prod",
    "axe": "npx @axe-core/cli https://example.com",
    "npm": "npm install --save-dev typescript",
    "yarn": "yarn add react",
    "pnpm": "pnpm add zod",
    "nvm": "nvm install --lts",
    "pyenv": "pyenv install 3.12.7",
    "conda": "conda create -n app python=3.12",
    "jupyter": "jupyter notebook",
    "flake8": "flake8 src",
    "isort": "isort .",
    "pylint": "pylint src",
    "pipx": "pipx install ruff",
    "bandit": "bandit -r src",
    "requests": "python3 -c \"import requests; print(requests.get('https://example.com').status_code)\"",
    "cargo": "cargo build --release",
    "clippy": "cargo clippy -- -D warnings",
    "rustup": "rustup update stable",
    "cmake": "cmake -S . -B build && cmake --build build",
    "gcc": "gcc -Wall -Wextra -o app main.c",
    "clang": "clang -Wall -o app main.c",
    "make": "make -j4",
    "meson": "meson setup build && meson compile -C build",
    "ninja": "ninja -C build",
    "bazel": "bazel build //...",
    "esbuild": "npx esbuild app.js --bundle --minify --outfile=out.js",
    "babel": "npx babel src -d dist",
    "nodemon": "npx nodemon server.js",
    "pm2": "pm2 start server.js",
    "ts-node": "npx ts-node script.ts",
    "mocha": "npx mocha 'test/**/*.js'",
    "ava": "npx ava",
    "golangci-lint": "golangci-lint run ./...",
    "goreleaser": "goreleaser release --snapshot --clean",
    "wasm-pack": "wasm-pack build",
    "tauri": "npm create tauri-app@latest",
    "git": "git log --oneline -10",
    "vim": "vim -u NONE -c 'set number' README.md",
    "tmux": "tmux new -s work",
    "htop": "htop",
    "rsync": "rsync -av --delete ~/src/ backup:/srv/src/",
    "ffmpeg": "ffmpeg -i in.mp4 -c:v libx264 -crf 23 -c:a aac out.mp4",
    "pandoc": "pandoc notes.md -o notes.pdf",
    "jq": "jq '.items[] | .name' data.json",
    "dig": "dig +short example.com",
    "mtr": "mtr -rw example.com",
    "traceroute": "traceroute example.com",
    "iperf3": "iperf3 -c 10.0.0.5 -t 10",
    "netdata": "docker run -d -p 19999:19999 netdata/netdata",
    "vaultwarden": "docker run -d -p 8080:80 vaultwarden/server",
    "nextcloud": "docker run -d -p 8080:80 nextcloud",
    "filebrowser": "filebrowser -r /srv -p 8081",
    "unbound": "unbound-checkconf",
    "dnsmasq": "dnsmasq --test",
    "dokku": "dokku apps:list",
    "loki": "logcli query '{app=\"web\"}'",
    "pgcli": "pgcli postgres://localhost/app",
    "mycli": "mycli -h 127.0.0.1 -u root app",
    "sqlite-utils": "sqlite-utils tables app.db",
    "metabase": "docker run -d -p 3000:3000 metabase/metabase",
    "vector": "vector --config vector.toml",
    "telegraf": "telegraf --config telegraf.conf --test",
    "strace": "strace -f -e trace=openat ./app",
    "readelf": "readelf -h ./binary",
    "objdump": "objdump -d ./binary | head -40",
    "strings": "strings -n 8 sample.bin | head",
    "xxd": "xxd -l 64 sample.bin",
    "openssl": "openssl req -x509 -newkey rsa:4096 -nodes -keyout key.pem -out cert.pem -days 365 -subj '/CN=example.com'",
    "netcat": "nc -lvnp 4444",
    "ncat": "ncat -lvnp 4444",
    "socat": "socat TCP-LISTEN:4444,reuseaddr,fork -",
    "openvpn": "openvpn --config client.ovpn",
    "chisel": "chisel server -p 8080 --reverse",
    "msfvenom": "msfvenom -p linux/x64/shell_reverse_tcp LHOST=10.0.0.2 LPORT=4444 -f elf -o shell.elf",
    "feroxbuster": "feroxbuster -u https://target -w wordlist.txt",
    "katana": "katana -u https://target -d 2",
    "whatweb": "whatweb -a 3 https://target",
    "wafw00f": "wafw00f https://target",
    "sslscan": "sslscan example.com",
    "testssl.sh": "testssl.sh example.com",
    "dnsrecon": "dnsrecon -d example.com",
    "whois": "whois example.com",
    "shodan": "shodan host 1.1.1.1",
    "holehe": "holehe user@example.com",
    "trufflehog": "trufflehog git https://github.com/org/repo",
    "gitleaks": "gitleaks detect --source .",
    "semgrep": "semgrep --config auto .",
    "trivy": "trivy fs .",
    "checkov": "checkov -d .",
    "prowler": "prowler aws",
    "enum4linux": "enum4linux -a 10.0.0.5",
    "smbclient": "smbclient -L //10.0.0.5 -N",
    "ldapsearch": "ldapsearch -x -H ldap://10.0.0.5 -b 'dc=corp,dc=local'",
    "evil-winrm": "evil-winrm -i 10.0.0.5 -u admin -p pass",
    "netexec": "nxc smb 10.0.0.0/24 -u user -p pass",
    "crackmapexec": "cme smb 10.0.0.0/24 -u user -p pass",
    "rizin": "rizin -A ./binary",
    "foremost": "foremost -i image.dd -o out",
    "steghide": "steghide extract -sf photo.jpg",
    "chkrootkit": "chkrootkit",
    "aide": "aide --init",
    "auditctl": "auditctl -l",
    "snort": "snort -T -c snort.conf",
    "llama.cpp": "./llama-cli -m model.gguf -p 'hello'",
    "open webui": "docker run -d -p 3000:8080 openwebui/open-webui",
    "litellm": "litellm --model gpt-4o-mini",
    "n8n": "npx n8n",
    "postcss": "npx postcss in.css -o out.css",
    "pa11y": "npx pa11y https://example.com",
    "svgo": "npx svgo -f icons/",
    "html-validate": "npx html-validate '*.html'",
    "bootstrap": "npm install bootstrap",
    "surge": "npx surge dist",
    "gh-pages": "npx gh-pages -d dist",
    "beancount": "bean-check books.beancount",
}


# ------------------------------------------------------- security, by hand
# Second pass over the security shelf. Same rule as above: a command is here
# only if it is the tool's real invocation, spelled as its README spells it.
EXAMPLES.update({
    # discovery and enumeration
    "sublist3r": "sublist3r -d example.com -o subs.txt",
    "rustscan": "rustscan -a 10.0.0.5 -- -sV",
    "naabu": "naabu -host example.com -top-ports 1000",
    "massdns": "massdns -r resolvers.txt -t A -o S domains.txt",
    "findomain": "findomain -t example.com",
    "chaos-client": "chaos-client -d example.com",
    "shuffledns": "shuffledns -d example.com -w words.txt -r resolvers.txt",
    "puredns": "puredns bruteforce words.txt example.com",
    "dnsx": "dnsx -l subs.txt -a -resp",
    "assetfinder": "assetfinder --subs-only example.com",
    "dnstwist": "dnstwist --registered example.com",
    "dnsenum": "dnsenum example.com",
    "dnsmap": "dnsmap example.com",
    "fierce": "fierce --domain example.com",
    "subbrute": "python3 subbrute.py example.com",
    "dnsgen": "cat subs.txt | dnsgen -",
    "gotator": "gotator -sub subs.txt -perm permutations.txt -depth 1",
    "goaltdns": "echo example.com | goaltdns -w words.txt -o out.txt",
    "alterx": "alterx -l subs.txt -o out.txt",
    "subdominator": "subdominator -d example.com",
    "bbot": "bbot -t example.com -f subdomain-enum",
    "netdiscover": "netdiscover -r 10.0.0.0/24",
    "smbmap": "smbmap -H 10.0.0.5 -u guest -p ''",
    "asnmap": "asnmap -d example.com",
    "mapcidr": "echo 10.0.0.0/24 | mapcidr -cidr",
    "cdncheck": "cdncheck -i 1.1.1.1",
    "tlsx": "tlsx -u example.com -san -cn",
    "fingerprintx": "cat hosts.txt | fingerprintx",
    "graphw00f": "python3 main.py -d -f -t https://example.com/graphql",
    "vhostscan": "VHostScan -t 10.0.0.5",
    "certgraph": "certgraph example.com",

    # screenshot and inventory
    "gowitness": "gowitness scan single --url https://example.com",
    "eyewitness": "eyewitness --web -f urls.txt -d out",
    "aquatone": "cat urls.txt | aquatone",
    "webanalyze": "webanalyze -host example.com",
    "screenshoteer": "screenshoteer --url https://example.com",

    # crawling and URLs
    "hakrawler": "echo https://example.com | hakrawler -d 2",
    "gospider": "gospider -s https://example.com -d 2",
    "gau": "gau example.com",
    "waybackurls": "echo example.com | waybackurls",
    "waymore": "waymore -i example.com -mode U",
    "unfurl": "cat urls.txt | unfurl domains",
    "anew": "cat new.txt | anew old.txt",
    "gf": "cat urls.txt | gf ssrf",
    "uro": "cat urls.txt | uro",
    "qsreplace": "cat urls.txt | qsreplace 'FUZZ'",
    "linkfinder": "python3 linkfinder.py -i https://example.com -o cli",
    "jsleak": "echo https://example.com | jsleak -l",
    "arjun": "arjun -u https://example.com",
    "x8": "x8 -u https://example.com -w wordlist.txt",
    "paramspider": "paramspider -d example.com",
    "kiterunner": "kr scan https://example.com -w routes.kite",
    "uncover": "uncover -q 'title:\"index of\"'",
    "interactsh": "interactsh-client",
    "notify": "notify -bulk -data urls.txt",

    # content discovery
    "dirsearch": "dirsearch -u https://example.com -e php,html",
    "wfuzz": "wfuzz -c -w wordlist.txt https://example.com/FUZZ",
    "recursebuster": "recursebuster -u https://example.com -w words.txt",
    "filebuster": "filebuster -u https://example.com -w words.txt",
    "dirhunt": "dirhunt https://example.com",
    "snallygaster": "snallygaster https://example.com",
    "joomscan": "joomscan -u https://example.com",
    "cmsmap": "cmsmap https://example.com",

    # injection and web exploitation
    "dalfox": "dalfox url 'https://example.com/?q=1'",
    "xsstrike": "python3 xsstrike.py -u 'https://example.com/?q=1'",
    "xsser": "xsser -u 'https://example.com/search?q=XSS'",
    "commix": "commix --url='https://example.com/?cmd=1' --batch",
    "ghauri": "ghauri -u 'https://example.com/item?id=1' --batch",
    "tplmap": "python3 tplmap.py -u 'https://example.com/?name=*'",
    "sstimap": "python3 sstimap.py -u 'https://example.com/?name=*'",
    "ysoserial": "java -jar ysoserial.jar CommonsCollections5 'id'",
    "ysoserial.net": "ysoserial.exe -g TypeConfuseDelegate -f BinaryFormatter -c calc -o base64",
    "phpggc": "./phpggc Monolog/RCE1 system id",
    "smuggler": "python3 smuggler.py -u https://example.com",
    "h2csmuggler": "python3 h2csmuggler.py -x https://example.com --test",
    "ssrfmap": "python3 ssrfmap.py -r request.txt -p url -m readfiles",
    "gopherus": "python3 gopherus.py --exploit fastcgi",
    "crlfuzz": "crlfuzz -u https://example.com",
    "dotdotpwn": "./dotdotpwn.pl -m http -h example.com -M GET",
    "corsy": "python3 Corsy.py -i urls.txt",
    "jwt-hack": "jwt-hack crack -w wordlist.txt TOKEN",
    "c-jwt-cracker": "./jwtcrack TOKEN",
    "jwttool": "python3 jwt_tool.py TOKEN -T",
    "mitmproxy2swagger": "mitmproxy2swagger -i flows -o spec.yml -p https://example.com",
    "proxify": "proxify -http-addr :8080 -output out.txt",
    "whatwaf": "whatwaf -u https://example.com",
    "identywaf": "python3 identYwaf.py https://example.com",
    "subjack": "subjack -w subs.txt -t 100 -o out.txt",
    "subzy": "subzy run --targets subs.txt",

    # secrets in git and cloud
    "gitrob": "gitrob -github-access-token TOKEN org",
    "git-dumper": "python3 git_dumper.py https://example.com/.git out",
    "git-secrets": "git secrets --scan",
    "shhgit": "shhgit --local .",
    "detect-secrets": "detect-secrets scan .",
    "noseyparker": "noseyparker scan --datastore ds .",
    "zizmor": "zizmor .github/workflows",
    "s3scanner": "s3scanner scan --bucket my-bucket",
    "slurp": "./slurp domain -t example.com",
    "awsbucketdump": "python3 AWSBucketDump.py -l buckets.txt",
    "cloudbrute": "cloudbrute -d example.com -k wordlist -m storage",
    "cloudgoat": "cloudgoat create iam_privesc_by_attachment",

    # exploit frameworks and C2
    "empire": "./empire",
    "covenant": "dotnet run --project Covenant.csproj",
    "merlin": "./merlin-server",
    "dnscat2": "ruby dnscat2.rb example.com",
    "pwnat": "./pwnat -s",
    "trevorc2": "python3 trevorc2_server.py",
    "sharpshooter": "python3 SharpShooter.py --payload js --output out --stageless",
    "cobaltstrikescan": "python3 CobaltStrikeScan.py --scan-file beacon.exe",

    # Windows and AD
    "rubeus": "Rubeus.exe kerberoast /outfile:hashes.txt",
    "powersploit": "Import-Module .\\PowerSploit.psd1",
    "winpwn": "Import-Module .\\WinPwn.ps1; WinPwn -g",
    "domainpasswordspray": "Invoke-DomainPasswordSpray -Password 'Summer2026!' -Domain corp.local",
    "lazagne": "python3 laZagne.py all",
    "creddump": "pwdump.py SYSTEM SAM",
    "deepbluecli": ".\\DeepBlue.ps1 -log security.evtx",
    "shellbags": "python3 shellbags.py NTUSER.DAT",
    "hollowshunter": "hollows_hunter.exe /loop",

    # credential attacks
    "medusa": "medusa -h 10.0.0.5 -u admin -P rockyou.txt -M ssh",
    "patator": "patator ssh_login host=10.0.0.5 user=admin password=FILE0 0=rockyou.txt",
    "cowpatty": "cowpatty -r capture.cap -f rockyou.txt -s SSID",
    "wifite": "wifite --kill",
    "airgeddon": "airgeddon",
    "wifiphisher": "wifiphisher --essid 'Free WiFi'",
    "phishery": "phishery -u https://10.0.0.2/logo.png -i template.docx",

    # pivoting and traffic
    "hping3": "hping3 -S -p 80 -c 3 example.com",
    "scapy": "python3 -c \"from scapy.all import *; send(IP(dst='1.1.1.1')/ICMP())\"",
    "netsniff-ng": "netsniff-ng --in eth0 --out dump.pcap",
    "sniffglue": "sniffglue eth0",
    "ngrep": "ngrep -q -d eth0 'GET /'",
    "dnschef": "dnschef --fakeip 10.0.0.1 --interface 0.0.0.0",
    "mitmf": "python3 mitmf.py --spoof --arp --gateway 10.0.0.1 --interface eth0",
    "evilginx2": "evilginx2 -p phishlets",
    "modlishka": "./modlishka -config config.json",
    "beef": "./beef",
    "scanless": "scanless -t example.com -s nmap",
    "netcap": "net capture -iface eth0 -out out",
    "ntopng": "ntopng -i eth0",

    # blue team, detection and hardening
    "codeql": "codeql database create db --language=javascript",
    "sops": "sops -e -i secrets.yaml",
    "helm-secrets": "helm secrets decrypt secrets.yaml",
    "blackbox": "blackbox_edit_start secrets.yaml",
    "git-crypt": "git-crypt init",
    "endlessh": "endlessh -p 22",
    "bubblewrap": "bwrap --ro-bind /usr /usr --dev /dev --unshare-all sh",
    "mailspoof": "mailspoof -d example.com",
    "santa": "santactl status",
    "sysdig": "sysdig -c topprocs_cpu",
    "sigma": "sigma check rules/",
    "elastalert": "elastalert --verbose --config config.yaml",
    "wazuh": "wazuh-control status",
    "go-audit": "go-audit -config go-audit.yaml",
    "jarm": "python3 jarm.py example.com",
    "hfinger": "hfinger -f sample.pcap",
    "attackrange": "python3 attack_range.py build",
    "cryptolyzer": "cryptolyze example.com",
    "sslyze": "sslyze --regular example.com",
    "chipsec-check": "chipsec_main -m common.bios_wp",
    "certbot": "certbot certonly --standalone -d example.com",
    "rage": "rage -p -o secret.age secret.txt",
    "rhash": "rhash --sha256 file.bin",
    "xxhash": "xxhsum file.bin",
    "blake3": "b3sum file.bin",
    "nettle": "nettle-hash --sha256 file.bin",

    # forensics and memory
    "hayabusa": "hayabusa csv-timeline -d ./logs -o timeline.csv",
    "bulkextractor": "bulk_extractor -o out image.dd",
    "scalpel": "scalpel -c scalpel.conf image.dd -o out",
    "libewf": "ewfinfo image.E01",
    "bstrings": "bstrings -f sample.exe --ls url",
    "mat2": "mat2 photo.jpg",
    "oletools": "olevba suspicious.docm",
    "zsteg": "zsteg image.png",
    "stegextract": "python3 stegextract.py image.png",
    "regripper": "rip.pl -r NTUSER.DAT -f ntuser",
    "hindsight": "hindsight.py -i 'C:\\Users\\user\\AppData' -o out",
    "aleapp": "aleapp.py -t tar -i android.tar -o out",
    "ileapp": "ileapp.py -t itunes -i backup -o out",
    "mobsf": "docker run -p 8000:8000 opensecurity/mobile-security-framework-mobsf",
    "kismet": "kismet -c wlan0",
    "evtxtract": "EVTXtract -o out Security.evtx",
    "usbrip": "usbrip events history -q",
    "memprocfs": "memprocfs -device memory.raw -mount /mnt/mem",

    # malware and reverse engineering
    "capa": "capa suspicious.exe",
    "floss": "floss sample.exe",
    "manalyze": "manalyze sample.exe",
    "peframe": "peframe sample.exe",
    "angr": "python3 -c \"import angr; print(angr.Project('./bin').arch)\"",
    "ghidra": "./support/analyzeHeadless /tmp/ghidra proj -import sample.exe",
    "de4dot": "de4dot sample.exe",
    "uncompyle6": "uncompyle6 -o out app.pyc",
    "hachoir3": "hachoir-metadata sample.mp4",
    "xortool": "xortool -l 4 cipher.bin",
    "rsactftool": "python3 RsaCtfTool.py --publickey key.pub --private",
    "pwntools": "python3 -c \"from pwn import *; print(cyclic(20))\"",
    "frida": "frida -U -f com.example.app -l hook.js",
    "objection": "objection -g com.example.app explore",
    "jadx": "jadx -d out app.apk",
    "androguard": "androguard analyze app.apk",
    "apk2gold": "apk2gold app.apk -o out",
    "z3": "python3 -c \"import z3; print(z3.solve(z3.Bool('a')))\"",
    "qira": "qira ./binary",
    "onegadget": "one_gadget /lib/x86_64-linux-gnu/libc.so.6",
    "rsatool": "python3 rsatool.py -p 61 -q 53 -o key.pem",

    # CTF platforms
    "ctfd": "docker run -d -p 8000:8000 ctfd/ctfd",
    "yersinia": "yersinia -G",
    "linenum": "./LinEnum.sh -t",
    "postenum": "./postenum.sh -a",
    "pspy": "./pspy64 -pf -i 1000",
    "unix-privesc-check": "./unix-privesc-check standard",

    # honeypots
    "cowrie": "docker run -d -p 2222:2222 cowrie/cowrie",
    "conpot": "conpot --template default",
    "dionaea": "dionaea -c dionaea.cfg",
    "glastopf": "glastopf-runner",
    "thug": "thug -u https://example.com",

    # web hardening and sanitising
    "retire.js": "retire --path ./static/js",
    "dompurify": "npm install dompurify",
    "js-xss": "npm install xss",
    "cyberchef": "docker run -d -p 8080:80 ghcr.io/gchq/cyberchef:latest",
    "weevely": "weevely generate secretpass shell.php",
    "weevely3": "weevely generate secretpass shell.php",

    # crypto libraries: the example is the import that proves it is installed
    "libsodium": "python3 -c \"import nacl\"",
    "pycryptodome": "python3 -c \"from Crypto.Cipher import AES\"",
    "bcrypt": "python3 -c \"import bcrypt; print(bcrypt.hashpw(b'x', bcrypt.gensalt()))\"",
    "pynacl": "python3 -c \"import nacl.secret; print(nacl.secret.SecretBox.generate_key().hex())\"",
    "ecdsa": "python3 -c \"import ecdsa; print(ecdsa.SigningKey.generate().to_string().hex())\"",
    "hashids": "python3 -c \"from hashids import Hashids; print(Hashids('salt').encode(42))\"",
    "django-cryptography": "pip install django-cryptography",
    "crypto-js": "npm install crypto-js",
    "forge": "npm install node-forge",
    "jsrsasign": "npm install jsrsasign",
    "openpgp.js": "npm install openpgp",
    "libsodium.js": "npm install libsodium-wrappers",
    "noble-curves": "npm install @noble/curves",
    "noble-hashes": "npm install @noble/hashes",
    "noble-ciphers": "npm install @noble/ciphers",
    "noble-post-quantum": "npm install @noble/post-quantum",
    "keycloak": "docker run -p 8080:8080 -e KEYCLOAK_ADMIN=admin -e KEYCLOAK_ADMIN_PASSWORD=admin quay.io/keycloak/keycloak start-dev",
    "bcrypt-ruby": "gem install bcrypt",
    "rbnacl": "gem install rbnacl",

    # vehicle and CAN
    "python-can": "python3 -c \"import can; bus=can.Bus(interface='socketcan', channel='can0'); print(bus.recv())\"",
    "python-obd": "python3 -c \"import obd; print(obd.OBD().query(obd.commands.RPM))\"",
    "cantools": "cantools dump vehicle.dbc",
    "canmatrix": "canconvert vehicle.dbc vehicle.arxml",
    "cancat": "cancat -i can0",
})


def esc(t):
    return html.escape(t or "", quote=False)


def compile_themes(cat):
    out = []
    for title, keys in THEMES[cat]:
        pats = []
        for k in keys:
            k = k.strip()
            if not k:
                continue
            body = re.escape(k).replace(r"\ ", r"\s+")
            pats.append(re.compile(r"(?<![a-z0-9])" + body, re.I))
        out.append((title, pats))
    return out


def bucket_of(compiled, text):
    for title, pats in compiled:
        for p in pats:
            if p.search(text):
                return title
    return EVERYTHING_ELSE


def noex(url):
    """Honest one-liner for the cards that are not a runnable command."""
    host = urlparse(url).netloc.lower()
    low = url.lower()
    if low.endswith(".pdf"):
        return "A PDF, not a command: download it and keep it with your notes."
    if "arxiv.org" in host:
        return "A paper — read the abstract first, the method second."
    if "web.archive.org" in host:
        return "An archived page: the original wording, not a command."
    if "wikipedia.org" in host:
        return "Background reading, not a binary."
    if host in ("stackoverflow.com", "superuser.com", "news.ycombinator.com") or "reddit.com" in host:
        return "A thread of answers — the examples are inside, in other people's words."
    if "youtube.com" in host or "youtu.be" in host:
        return "A talk or a screencast: watch it, then read the docs it mentions."
    if host in ("man7.org", "gnu.org", "www.gnu.org", "tldp.org", "docs.python.org"):
        return "Documentation: the offline `man` page usually says the same thing."
    if host in ("npmjs.com", "pypi.org", "crates.io", "rubygems.org", "packagist.org", "hub.docker.com"):
        return "A package page: install it with your ecosystem's package manager."
    if "github.com" in host or "gitlab.com" in host or "codeberg.org" in host:
        return "A repository: its README is the example."
    if "amazon." in host or "goodreads.com" in host:
        return "A book: buy it, borrow it, or find the author's own page."
    if "medium.com" in host or "substack.com" in host or "dev.to" in host:
        return "An article — the code, if any, lives in the text."
    return "A project site: install it from there and read its own docs; no command is quoted here."


PAGE = """<!DOCTYPE html>
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
      "keywords": "__KEYS__",
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
.page-foot nav{display:flex;flex-wrap:wrap;gap:14px;margin-bottom:10px}
@media print{.topbar{display:none}body{background:#fff;color:#111}details{display:block}}
</style>
</head>
<body>
<header class="topbar">
  <a class="brand" href="awesomeIndex.html">◀ Awesome Index</a>
  <span class="note">__NUM__ · __SLUG__ · __TOTAL__ links</span>
</header>
<main>
  <p class="kicker">Category __NUM__ · expanded</p>
  <h1>__H1__</h1>
  <p class="lede">__LEDE__</p>
  <p class="lede small">__SMALL__</p>
  <p class="stats">__NF__ lists · __TOTAL__ unique links · __WITHEX__ with a runnable example · duplicated links collapsed</p>
__BODY__
  <footer class="page-foot">
    <nav>__PAGER__</nav>
    <p>Built from the public README of each list. Summaries are the list's own words; examples are written by hand and kept to commands that run as shown. Cards that are not a program say what they are instead.</p>
    <p><a href="__FLAT__">flat list for this category</a> · <a href="awesome_story.html">the story</a></p>
  </footer>
</main>
</body>
</html>
"""

ORDER = ["lang", "systems", "data", "security", "ai", "web", "learning", "beyond"]
SHELL_PAGE = ("awesome-01-shell.html", "Shell")
NAMES = {"lang": "Languages", "systems": "Systems", "data": "Data", "security": "Security",
         "ai": "AI", "web": "Web", "learning": "Learning", "beyond": "Beyond"}


def build(cat, data):
    meta = CATS[cat]
    out = "docs/awesome-%s-%s.html" % (meta["num"], meta["slug"])
    url = ORIGIN + "/" + out.split("/")[-1]
    compiled = compile_themes(cat)
    lists_in = data[cat]

    repo_of = {lst["list"]: lst["repo"] for lst in lists_in}
    seen, order, dupes = {}, [], {}
    for lst in lists_in:
        for tool in lst["tools"]:
            if junk(tool):
                continue
            key = tool["url"].rstrip("/")
            if key in seen:
                dupes.setdefault(key, []).append(lst["list"])
                continue
            seen[key] = True
            order.append((lst["list"], tool))

    by_list = {}
    for list_name, tool in order:
        by_list.setdefault(list_name, []).append(tool)

    body, total, with_ex = [], 0, 0
    for list_name, tools in by_list.items():
        buckets = {}
        for tool in tools:
            text = (tool["name"] + " " + tool["desc"]).strip()
            buckets.setdefault(bucket_of(compiled, text), []).append(tool)
        # biggest drawer first, "Everything else" last
        keys = sorted(buckets, key=lambda k: (k == EVERYTHING_ELSE, -len(buckets[k])))
        parts = []
        for title in keys:
            items = buckets[title]
            num_of = {id(t): i + 1 for i, t in enumerate(tools)}
            cards = []
            for tool in items:
                total += 1
                host = urlparse(tool["url"]).netloc.replace("www.", "")
                example = EXAMPLES.get(tool["name"].strip().lower())
                if example:
                    with_ex += 1
                extra = ""
                key = tool["url"].rstrip("/")
                if key in dupes:
                    extra = ('<p class="also">also listed in %s</p>'
                             % esc(", ".join(sorted(set(dupes[key])))))
                cards.append(
                    '<details class="tool">'
                    '<summary><span class="num">%02d</span> <span class="tn">%s</span>'
                    '<span class="host">%s</span></summary>'
                    '<div class="card">%s%s%s'
                    '<p class="src"><a href="%s" target="_blank" rel="noopener noreferrer">open the source →</a></p>'
                    '</div></details>' % (
                        num_of[id(tool)], esc(tool["name"]), esc(host),
                        ('<p class="what">%s</p>' % esc(tool["desc"])) if tool["desc"]
                        else '<p class="what muted">The list gives no description — the link is the description.</p>',
                        ('<pre><code><span class="p">$</span> %s</code></pre>' % esc(example)) if example
                        else '<p class="noex">%s</p>' % esc(noex(tool["url"])),
                        extra, esc(tool["url"])))
            parts.append('<details class="bucket"><summary>%s<span class="cnt">%d</span></summary>%s</details>'
                         % (esc(title), len(items), "".join(cards)))
        # One href per destination: when the list links to itself, the card below
        # already points at that repository, so the source line is left out.
        repo_url = "https://github.com/" + repo_of[list_name]
        src_line = ""
        if repo_url not in seen:
            src_line = ('<p class="about">Source: <a href="%s" target="_blank" '
                        'rel="noopener noreferrer">%s</a></p>'
                        % (esc(repo_url), esc("github.com/" + repo_of[list_name])))
        body.append(
            '<details class="list"><summary><span class="lid">%s</span><span class="cnt">%d tools</span></summary>'
            '%s%s</details>' % (esc(list_name), len(tools), src_line, "".join(parts)))

    if total != len(seen):
        sys.exit("%s: %d cards for %d links" % (cat, total, len(seen)))
    if not 110 <= len(meta["desc"]) <= 155:
        sys.exit("%s: description is %d chars" % (cat, len(meta["desc"])))

    idx = ORDER.index(cat)
    if idx == 0:
        prev = SHELL_PAGE[0]; prevl = "01 Shell"
    else:
        p = ORDER[idx - 1]
        prev = "awesome-%s-%s.html" % (CATS[p]["num"], CATS[p]["slug"]); prevl = "%s %s" % (CATS[p]["num"], NAMES[p])
    if idx == len(ORDER) - 1:
        nxt = "awesomeIndex.html"; nxtl = "Awesome Index"
    else:
        n = ORDER[idx + 1]
        nxt = "awesome-%s-%s.html" % (CATS[n]["num"], CATS[n]["slug"]); nxtl = "%s %s" % (CATS[n]["num"], NAMES[n])

    # The brand at the top already points at the index, so the last page's
    # "next" is dropped rather than printing that link a second time.
    pager = ['<a href="%s">◀ %s</a>' % (prev, esc(prevl))]
    if nxt != "awesomeIndex.html":
        pager.append('<a href="%s">%s ▶</a>' % (nxt, esc(nxtl)))
    html_body = "".join(body)
    words = len(re.sub(r"<[^>]+>", " ", html_body).split()) + 120
    doc = PAGE
    for k, v in (("TITLE", esc(meta["title"])), ("DESC", esc(meta["desc"])), ("URL", url),
                 ("IMG", IMG), ("NUM", meta["num"]), ("SLUG", meta["slug"].upper()),
                 ("TOTAL", str(total)), ("WITHEX", str(with_ex)), ("NF", str(len(by_list))),
                 ("H1", esc(meta["h1"])), ("LEDE", esc(meta["lede"])), ("SMALL", esc(meta["small"])),
                 ("KEYS", esc(meta["keywords"])), ("WORDS", str(words)), ("BODY", html_body),
                 ("PAGER", " ".join(pager)), ("NEXT", nxt), ("NEXTL", nxtl),
                 ("FLAT", meta["flat"])):
        doc = doc.replace("__" + k + "__", v)
    open(out, "w", encoding="utf-8").write(doc)
    print("%s: %d lists, %d unique links, %d examples, %d KB" %
          (out, len(by_list), total, with_ex, len(doc) // 1024))


def main():
    data = json.load(open(SRC, encoding="utf-8"))
    want = sys.argv[1:] or ORDER
    for cat in want:
        build(cat, data)


if __name__ == "__main__":
    main()
