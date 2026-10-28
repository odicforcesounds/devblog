# Google — o que mudou no site e o que fazer na Search Console

Companheiro do `CLOUDFLARE.md`. Este ficheiro descreve o que foi alterado no
repositório para os motores de busca e a ordem exacta das operações na Search Console
(sem custo). Não é publicado: o GitHub Pages só serve `docs/`.

Estado no momento destas alterações: 517 artigos + `index.html`, 4 idiomas
(`en`, `pt`, `pt-PT`, `es`), sitemap com 518 URLs, `robots.txt` a permitir motores de
busca e a excluir `/archive/`, `/obsdRouter/` e `/api/`.

---

## 1. O que mudou no repositório

### 1.1 Dados estruturados: um `@graph` por página

Antes: um `BlogPosting` plano, com `author` e `publisher` como `Organization` e a
imagem como texto solto.

Agora cada página tem um bloco único:

```json
{ "@context": "https://schema.org",
  "@graph": [ { "@type": "BlogPosting", … }, { "@type": "BreadcrumbList", … } ] }
```

Campos do `BlogPosting`:

| Campo | Valor |
| --- | --- |
| `@id` | `https://blog.odicforcesounds.com/pagina.html#article` |
| `image` | `ImageObject` com `url`, `width` e `height` reais do ficheiro |
| `author` | `Person` — `Oscar`, com `url` do site e `sameAs` do Mastodon |
| `publisher` | `Organization` — `Monkey Blog`, com `logo` (`images/three.jpg`, 1024×1024) |
| `articleSection` | a categoria em que a página está listada no `index.html` |
| `keywords` | os `h2`/`h3` da própria página, limpos, até 10 |
| `wordCount` | palavras de texto visível |
| `inLanguage`, `datePublished`, `dateModified` | mantidos como estavam (datas do git) |

Cada artigo tem também um `BreadcrumbList` de três níveis:
`Home` → categoria → artigo, com o segundo nível a apontar para um *anchor* real no
`index.html` (`/#category-programming-and-development`, por exemplo). A página
inicial não leva breadcrumb (não é um artigo).

Categorias agora com âncora: Programming & Development, Linux & Open Source,
BSD — FreeBSD & OpenBSD, Security & Hacking, Networking, Science & Engineering,
Philosophy & Spirituality, Politics Law & Justice, Psychology & the Mind,
Society Culture & Education, Music Art & Creativity, Games & Quests,
Health Food & Wellbeing, Business & Economics, Site Blog & Reading.

### 1.2 `browse.html` deixou de estar órfão

`docs/browse.html` (o browser sobre a API JSON) não tinha uma única ligação a apontar
para ele. Agora há uma na barra do `index.html` — **Browse all** — ao lado de
*Master Exam*, a reutilizar a classe `.game-link` que já existia. Nenhum CSS novo.

### 1.3 Canonical da página inicial

`canonical`, `og:url` e o `url`/`@id` do JSON-LD passaram de `/index.html` para `/`,
que é o que o `sitemap.xml` lista. Um documento, um endereço.

### 1.4 O que **não** mudou

- Nenhum texto visível foi reescrito. Só `index.html` tem corpo alterado (a ligação
  nova); nas restantes 516 páginas o corpo é byte a byte igual.
- `robots.txt` continua a permitir tudo excepto as três pastas.
- Nada foi publicado: isto só está no repositório até `./pushit.sh`.

### 1.5 Ferramentas

- `.agents/skills/blog-ops/enrich_schema.py` — reaplica o `@graph` a todas as páginas.
  É idempotente: correr duas vezes não muda nada. `--check` mostra quantas mudariam.
- `.agents/skills/blog-ops/check_site.py` — passou a validar o `@graph`, as dimensões
  da imagem, o autor `Person`, o logo do publisher, o `wordCount` e o breadcrumb.

```sh
python3 .agents/skills/blog-ops/enrich_schema.py --check
python3 .agents/skills/blog-ops/check_site.py
```

---

## 2. Ordem de operações na Search Console

### Passo 1 — Confirmar que o rastreio não está a ser bloqueado

`Configurações → Estatísticas de rastreio`.

- Em **Por que o Google não conseguiu rastrear**, vê se aparece `403`.
- Em **Resposta HTTP**, a fatia `200` deve ser a esmagadora maioria.

Se houver `403`, para aqui: é a regra de rate limiting do Cloudflare descrita no
`CLOUDFLARE.md` §2. Nenhuma alteração de dados estruturados compensa um rastreador
bloqueado.

### Passo 2 — Sitemap

`Sitemaps → sitemap.xml → Pedir reanálise` (depois do deploy).

Confirma que lê **518** URLs e que o estado é *Sucesso*. Se aparecerem avisos sobre
`/api/`, é esperado: essa pasta está em `Disallow` e serve apenas JSON.

### Passo 3 — Validar duas páginas antes de pedir indexação

`Inspecção de URL` → cola `https://blog.odicforcesounds.com/docker.html` → **Testar URL
em direto**.

O que deve aparecer:

- *A página está disponível para rastreio*
- **Dados estruturados: 1 item válido detectado**
- Em "Ver dados estruturados", `BlogPosting` com `author`, `publisher`, `image`,
  `datePublished` e `articleSection`, mais `BreadcrumbList` com 3 itens.

Repete para uma página em português (`habitacao.html` ou `autonomia.html`).

O teste mais rápido é o **Rich Results Test** (`search.google.com/test/rich-results`):
não gasta quota e diz imediatamente se algo no `BlogPosting` ou no breadcrumb está
inválido. Corre-o em 3 URLs: uma em inglês, uma em português, e `index.html`.

### Passo 4 — Pedir indexação do que importa

`Inspecção de URL → Pedir indexação`. A quota é pequena (ordem de uma dezena por dia).
Usa-a nas páginas que já aparecem em `Desempenho` com posição 5–20 — são as que podem
subir com um título melhor. Não vale a pena pedir as 517.

### Passo 5 — Melhorias

`Melhorias → Artigos` e `Melhorias → Navegação estrutural`.

- Os dados só aparecem depois de o Google voltar a rastrear as páginas — dias, não
  horas. O breadcrumb é a parte mais lenta a propagar.
- Se aparecer "Itens inválidos", abre um e vê o campo; o `check_site.py` já valida os
  mesmos requisitos localmente, por isso o mais provável é ser um aviso de imagem
  (dimensões ou formato) e não um erro de estrutura.

### Passo 6 — Trabalhar o CTR

`Desempenho`:

1. Filtro de período: 3 meses.
2. Separador **Consultas** → ordenar por **Impressões**.
3. Procurar posição entre **5 e 20** e CTR abaixo de **2 %**.
4. Para cada uma, `Páginas` → vê qual página ocupa essa consulta.
5. Exporta (canto superior direito → Exportar) e trata os títulos dessas páginas
   primeiro. É o maior retorno gratuito que resta.

### Passo 7 — Cobertura

`Indexação → Páginas`. As categorias que vais ver, e o que fazer com cada uma:

| Estado | Significado | Acção |
| --- | --- | --- |
| `Rastreada — não indexada` | o Google leu e decidiu que não vale a pena | ligações internas e conteúdo, não reenvio |
| `Detectada — não indexada` | conhecida por um link ou pelo sitemap, ainda não lida | esperar; melhorar o rastreio |
| `Duplicada, o Google escolheu outra canónica` | duas URLs, um conteúdo | corrigir o canonical dessa página |
| `Excluída por robots.txt` | `/archive/`, `/obsdRouter/`, `/api/` | esperado |
| `Não encontrada (404)` | — | confirmar que `docs/404.html` está a servir |

`browse.html` e `404.html` vão aparecer no relatório. O `404.html` está de propósito.
O `browse.html` agora tem ligação; deve ser rastreado na próxima passagem.

### Passo 8 — Bing, de graça

`bing.com/webmasters` → *Importar do Google Search Console*. Um clique, mesma
verificação de propriedade. O índice da Bing alimenta o Copilot e parte das respostas
de IA, e o `robots.txt` já nomeia o `Bingbot`.

---

## 3. O que esperar, e o que não prometer

- **Nada acontece no mesmo dia.** A propagação de dados estruturados novos leva de
  dias a semanas; o breadcrumb nos resultados, mais tempo.
- **O `keywords` não posiciona.** O Google ignora-o desde 2009. Está lá porque outros
  consumidores (agregadores, ferramentas internas) o usam, e porque o `articleSection`
  ao lado é lido.
- **As 51 descrições abaixo de 110 caracteres continuam assim.** São páginas com pouco
  texto; encher com frase inventada seria pior.
- **Os dois documentos concatenados continuam a falhar:**
  `ArtOfCreation.html` (3 documentos) e `JS4Children.html` (2). O Google vê o texto
  repetido dentro da mesma página. Separar é trabalho de conteúdo, não de metadados.

## 4. Problemas conhecidos, por ordem de impacto

1. **403 no rastreio** (Cloudflare, não o repositório) — `CLOUDFLARE.md` §2.
2. **Dois ficheiros com documentos concatenados** — duplicação dentro do URL.
3. **Sem `hreflang`**: as páginas multilingues trocam de idioma por JavaScript no mesmo
   URL, por isso o Google só indexa um idioma por página. Resolver exige URLs próprias
   por idioma.
4. **Poucos links externos**: o relatório `Links` vai estar magro. O `index.html` liga a
   `wiki`, `book` e `art`; falta o caminho inverso.
5. **Autor**: `Oscar` com `sameAs` do Mastodon é o que existe. Se houver página de autor
   própria, vale a pena apontar `author.url` para ela.

## 5. Reverter

Tudo isto é um bloco `<script type="application/ld+json">` por página, no `<head>`.
Reverter uma página:

```sh
git checkout -- docs/pagina.html
```

Reverter todas: `git checkout -- docs/` (perde também a ligação nova do `index.html`).
Depois, `python3 build_api.py` para o índice voltar a bater com os ficheiros.
