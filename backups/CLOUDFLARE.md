# Cloudflare — o que configurar neste domínio

Documento de operação para `blog.odicforcesounds.com`. Não é publicado: o GitHub Pages
só serve a pasta `docs/`, por isso este ficheiro vive na raiz do repositório.

Estado verificado em 28 de outubro de 2026, com o site a responder pelo Cloudflare:

| Verificação | Resultado |
| --- | --- |
| Origem | GitHub Pages (`x-github-edge-region: switzerlandnorth`, CDN Fastly, `cache-control: max-age=600`) |
| Proxy Cloudflare | activo (`server: cloudflare`, `cf-ray`, `cf-cache-status: DYNAMIC`) |
| HTTP → HTTPS | 301 para `https://` — já funciona |
| HSTS | presente, `max-age=15552000; includeSubDomains; preload` |
| `docs/CNAME` | correcto (`blog.odicforcesounds.com`) |
| **WebMCP** | **ligado** — injecta `/.webmcp/bridge.js` (75 756 bytes) em todas as páginas |
| Protecção de bots | **agressiva** — 15 pedidos seguidos do mesmo IP → 403 durante ~30 s, mesmo com User-Agent do Googlebot |
| Duplicação `/` vs `/index.html` | ambos 200, canonical dizia `/index.html`, sitemap dizia `/` (já alinhado no repositório) |

Ordem de prioridade: **1 → 2 → 3** são correcções; **4 → 7** são afinações. Cada passo
diz onde clicar, o que pôr e como confirmar. Não é preciso Worker para nenhum deles.

**Ainda não publicado:** `docs/404.html`, `docs/.nojekyll` e o canonical `/` do
`index.html` estão no repositório mas só ficam live depois de um `./pushit.sh`. Os
passos abaixo assumem que já correu (o GitHub Pages serve o `404.html` novo só a partir
desse deploy).

---

## 1. Desligar o WebMCP (ou reduzir ao pack de imagens)

**Onde:** Dashboard → **Agent Readiness** → **WebMCP** → domínio `odicforcesounds.com`.

**O que fazer:** desligar. Se quiseres manter a experiência, deixa só **Content
Credentials (C2PA)** e desliga **Site MCP Server**.

**Porquê:**

- É uma developer preview da Cloudflare (agosto de 2026). Com o toggle ligado, cada
  resposta HTML ganha uma linha injectada no edge por HTMLRewriter:
  `<script type="module" src="/.webmcp/bridge.js" data-packs="c2pa,mcp-server-client">`.
- São **75,7 KB de JavaScript em todas as páginas** — incluindo `index.html`, que é a
  primeira coisa que um visitante descarrega.
- O pack **Site MCP Server** aponta para `/mcp` na mesma origem. No GitHub Pages esse
  caminho devolve **404**: o pack não pode funcionar, só ocupa lugar.
- O pack C2PA lê metadados de proveniência das imagens no browser do visitante. É
  inofensivo, mas também não faz nada por um blog.

**Confirmar:**

```sh
curl -s https://blog.odicforcesounds.com/ | grep -c webmcp     # 0 depois de desligar
curl -s -o /dev/null -w '%{http_code}\n' https://blog.odicforcesounds.com/.webmcp/bridge.js   # 404
```

---

## 2. Protecção de bots: não bloquear o Googlebot

**Onde:** Dashboard → **Security** → **Bots**, e **Security** → **WAF** → **Rate limiting
rules** (em algumas contas: **Security** → **Security rules**).

**O que verificar:**

1. **Bot Fight Mode / Super Bot Fight Mode** — se estiver ligado, garante que
   *Verified bots* ficam em **Allow**. O modo "Definitely automated: Block" apanha
   clientes HTTP legítimos e, dependendo da regra, também rastreadores.
2. **Regras de rate limiting** — nenhuma deve aplicar-se a bots verificados. Em cada
   regra, adiciona a condição de exclusão:

   ```
   not cf.client.bot
   ```

   (equivalente a: a regra só conta pedidos que *não* são de bots verificados)
3. Se existir uma regra de WAF a bloquear por User-Agent ou por ASN, confirma o
   *expression* — `cf.client.bot` é a forma fiável de reconhecer Googlebot/Bingbot.

**Porquê:** o teste que fiz (15 pedidos em ~40 s, um IP) devolveu **403 a tudo** durante
meio minuto — com User-Agent de Chrome, de Googlebot e de Bingbot, e tanto em `GET`
como em `HEAD`. Se isto acontecer ao rastreador, o trabalho de títulos, descrições,
`h1` e `sitemap.xml` não chega a ser lido.

**Confirmar:**

```sh
curl -s -o /dev/null -w '%{http_code}\n' -A 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)' \
  https://blog.odicforcesounds.com/docker.html     # 200
```

Depois: **Search Console → Definições → Estatísticas de rastreio** e
**Páginas → Indexação**. Se aparecerem respostas `403` ou "acesso negado", é esta regra.

---

## 3. Um só endereço para a página inicial

**Onde:** Dashboard → **Rules** → **Redirect Rules** → *Create rule*.

- **Nome:** `index.html → raiz`
- **When incoming requests match:**

  ```
  (http.request.uri.path eq "/index.html")
  ```

- **Then:** *Static redirect*
  - **URL:** `https://blog.odicforcesounds.com/`
  - **Status code:** `301`
  - **Preserve query string:** ligado

**Porquê:** `/` e `/index.html` são o mesmo documento servido em dois endereços. O
`sitemap.xml` lista `/` e o `index.html` já foi alinhado para `/` (canonical, `og:url`,
JSON-LD). Falta o servidor dizer o mesmo com um 301, para o histórico de links antigos
não ficar dividido entre dois URLs.

**Confirmar:**

```sh
curl -sI https://blog.odicforcesounds.com/index.html | head -2      # 301, location: /
curl -sI https://blog.odicforcesounds.com/        | head -2         # 200
```

---

## 4. Cache: 10 minutos é o tecto para o JSON da API

**Onde:** Dashboard → **Caching** → **Cache Rules** → *Create rule*.

O GitHub Pages já manda `cache-control: max-age=600` para tudo — HTML, JSON e imagens.
Isso é bom para as páginas e aceitável para `docs/api/index.json` (306 KB), mas deixa
as imagens a expirar a cada 10 minutos, o que é desperdício.

**Regra A — imagens**

- **When:** `(http.request.uri.path matches "^/images/.*")`
- **Then:** *Edge TTL* → **Override origin** → **1 month**; *Browser TTL* → **Override
  origin** → **1 year**

**Regra B — API (opcional)**

- **When:** `(http.request.uri.path matches "^/api/.*")`
- **Then:** *Edge TTL* → **Override origin** → **10 minutes**

**Cuidado:** o `docs/api/` é regenerado por `build_api.py` a cada artigo novo. Com TTL
de edge, o JSON antigo pode ficar até 10 minutos depois do deploy. Se um dia aumentares
esse TTL, purga o cache (`Caching` → **Configuration** → *Purge Everything*) a seguir a
cada `pushit.sh`. Não uses **Cache Everything** em HTML: serviria a página inicial
antiga durante horas.

**Confirmar:**

```sh
curl -sI https://blog.odicforcesounds.com/images/peace.jpg | grep -i -E 'cf-cache-status|age|cache-control'
```

---

## 5. Cabeçalhos que o GitHub Pages não deixa definir

**Onde:** Dashboard → **Rules** → **Transform Rules** → **Modify response header** →
*Create rule*.

**Regra — cabeçalhos de segurança**

- **When:** `true` (todas as respostas do domínio)
- **Then (Set static):**
  - `Permissions-Policy` = `camera=(), microphone=(), geolocation=(), payment=()`
  - `Cross-Origin-Opener-Policy` = `same-origin-allow-popups`
  - `X-Content-Type-Options` = `nosniff` (já vem do GitHub, repetir não faz mal)

`Cross-Origin-Opener-Policy` tem de ser `same-origin-allow-popups`, **não**
`same-origin`: o formulário de comentários do `index.html` abre o login Google/GitHub
num popup, e `same-origin` corta a comunicação com essa janela.

**CSP — só depois de tudo o resto.** As páginas do blog são auto-contidas, com CSS e
JavaScript inline. Uma CSP restritiva parte-as a todas. Se quiseres, começa em modo de
relatório, sem bloquear nada:

- `Content-Security-Policy-Report-Only` =
  `default-src 'self'; img-src 'self' data: https://lh3.googleusercontent.com https://avatars.githubusercontent.com https://pbs.twimg.com https://platform-lookaside.fbsbx.com https://s.yimg.com; script-src 'self' 'unsafe-inline' https://www.gstatic.com https://apis.google.com; frame-src https://blog-comments-6b4f5.firebaseapp.com https://accounts.google.com https://github.com; connect-src 'self' https://*.googleapis.com https://*.firebaseio.com wss://*.firebaseio.com; style-src 'self' 'unsafe-inline'; base-uri 'self'; frame-ancestors 'self'`

Com `'unsafe-inline'` em `script-src` a protecção é parcial — serve para impedir
script de outra origem, não para travar injecção inline. Vale pelo `frame-ancestors`,
`base-uri` e `connect-src`, que hoje não existem.

**Confirmar:**

```sh
curl -sI https://blog.odicforcesounds.com/ | grep -i -E 'permissions-policy|cross-origin-opener|content-security'
```

---

## 6. HSTS: 180 dias não é "preload"

**Onde:** Dashboard → **SSL/TLS** → **Edge Certificates** → **HTTP Strict Transport
Security (HSTS)**.

O cabeçalho actual diz `max-age=15552000; includeSubDomains; preload`, mas:

- `15552000` = **180 dias**. A lista de preload exige **1 ano** (`31536000`) e o
  domínio `odicforcesounds.com` **não está na lista** (consulta a
  `hstspreload.org/api/v2/status?domain=odicforcesounds.com` → `"status": "unknown"`).

Duas opções, escolhe uma:

- **Simples:** tira o `preload` do cabeçalho e mantém 180 dias.
- **A sério:** põe `max-age=31536000`, mantém `includeSubDomains` **só se todos os
  subdomínios servirem HTTPS** (inclui `art.odicforcesounds.com` e o apex), e só depois
  submetes em `hstspreload.org`. Preload é praticamente irreversível: um subdomínio
  esquecido em HTTP fica inacessível.

`includeSubDomains` já está activo: confirma que nenhum subdomínio serve só HTTP.

---

## 7. TLS: Full (strict), nunca Flexible

**Onde:** Dashboard → **SSL/TLS** → **Overview** → *Encryption mode*.

- Tem de estar **Full (strict)**.
- **Flexible** com GitHub Pages provoca ciclo de redireccionamento: o Cloudflare fala
  HTTP com a origem, o Pages responde 301 para HTTPS, o Cloudflare repete — `ERR_TOO_MANY_REDIRECTS`.
- **Edge Certificates** → *Always Use HTTPS*: ligado (o 301 já está a acontecer).
- **Speed** → **Optimization** → *Brotli*: ligado. *Rocket Loader*: **desligado** — o
  blog usa ES modules e scripts inline; o Rocket Loader não traz nada e mexe no que não
  precisa.

---

## 8. Resumo para copiar

| # | Onde | Acção |
| --- | --- | --- |
| 1 | Agent Readiness → WebMCP | Desligar (ou só pack C2PA) |
| 2 | Security → Bots / WAF | Bots verificados em Allow; rate limit com `not cf.client.bot` |
| 3 | Rules → Redirect Rules | `301 /index.html` → `/` |
| 4 | Caching → Cache Rules | `/images/*` 1 mês; `/api/*` 10 min (opcional) |
| 5 | Rules → Transform Rules | `Permissions-Policy`, `Cross-Origin-Opener-Policy: same-origin-allow-popups`; CSP em Report-Only |
| 6 | SSL/TLS → Edge Certificates | HSTS: 1 ano, ou remover `preload` |
| 7 | SSL/TLS → Overview | Full (strict); Brotli on; Rocket Loader off |

## 9. Verificação final, de uma vez

```sh
base=https://blog.odicforcesounds.com
curl -s "$base/" | grep -c webmcp                                   # 0 — WebMCP desligado
curl -sI "$base/index.html" | head -1                               # 301
curl -sI "$base/" | grep -i strict-transport-security               # max-age=...
curl -s -o /dev/null -w '%{http_code}\n' "$base/nao-existe.html"    # 404 (serve docs/404.html)
curl -s -o /dev/null -w '%{http_code}\n' "$base/api/index.json"     # 200, application/json
curl -sI -A 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)' \
  "$base/docker.html" | head -1                                     # 200
```

Se algum destes falhar, é a regra correspondente acima — não é o repositório.

## 10. Porque não um Worker

Tudo o que está neste documento é configuração nativa: Redirect Rules, Cache Rules,
Transform Rules, WAF e SSL/TLS. Um Worker no caminho de `blog.odicforcesounds.com/*`
acrescentaria código a manter, um ponto de falha à frente de um site estático e um
deploy a mais por cada mudança de cabeçalho.

Faria sentido em dois casos apenas:

1. **Configuração em git** em vez de cliques no painel — um `worker.js` de ~70 linhas que
   aplica os cabeçalhos, o 301 e os TTL. Custo: cada visita passa por código teu.
2. **Endpoint `/api/search?q=`** para terceiros, em vez de o cliente descarregar os
   2,8 MB de `docs/api/text/*.json`. Custo: o corpus tem de sair do repositório para
   KV/R2 e passa a haver dois lugares onde a verdade vive.

Nenhum dos dois é preciso hoje. Se o (1) passar a interessar, o Worker substitui as
regras 3, 4 e 5 — as regras 1, 2, 6 e 7 continuam a ser do painel.
