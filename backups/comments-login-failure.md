# Login dos comentários — o que falhava e o que ficou

Documento de diagnóstico. Não é publicado: `backups/` está fora de `docs/`, por isso o
GitHub Pages não o serve.

Data: 2026-10-29. Página afectada: `docs/index.html` (só ela tem o widget).

## O sintoma

O formulário de comentários mostrava sete botões (Google, GitHub, Microsoft, Apple,
X / Twitter, Facebook, Yahoo). Todos falhavam. O texto de erro na página era sempre o
mesmo — `Could not sign you in. Try another provider.` — que não diz nada sobre a causa
porque o código mapeava apenas cinco códigos de erro e mandava o resto para essa frase.

## A causa

Só existia **um** método de entrada configurado no projecto `blog-comments-6b4f5`:
Google. Os outros seis nunca foram ligados no Firebase, e o botão de cada um era um
botão que só podia falhar.

`accounts:createAuthUri` é a chamada que o Firebase faz para descobrir se um provider
existe. O resultado, por provider, nesta data:

| Provider | Resposta |
| --- | --- |
| `google.com` | `200` com `authUri` → configurado |
| `github.com` | `OPERATION_NOT_ALLOWED : The identity provider configuration is not found.` |
| `microsoft.com` | idem |
| `apple.com` | idem |
| `twitter.com` | idem |
| `facebook.com` | idem |
| `yahoo.com` | idem |

E o e-mail/palavra-passe também não estava ligado:

```sh
curl -s -X POST "https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=$KEY" \
  -H 'Content-Type: application/json' \
  -d '{"email":"probe@example.com","password":"x9Fk2LmQ7aa","returnSecureToken":true}'
# antes: {"error":{"message":"OPERATION_NOT_ALLOWED"}}
```

No browser, o SDK traduz estas duas respostas em `auth/operation-not-allowed`, que o
código antigo mostrava como *"This sign-in provider is not enabled in the Firebase
project yet."* — mas só se o utilizador reparasse na linha de estado, e nunca para os
providers que falham no meio do redirect.

## O que **não** era

Isto foi testado para não se estar a corrigir o sítio errado:

- **A chave de API.** É válida e não tem restrição de referrer: `publicKeys` e
  `securetoken` respondem, e `createAuthUri` aceita pedidos com qualquer `Referer`.
- **O domínio autorizado.** `createAuthUri` com `continueUri=https://blog.odicforcesounds.com/`
  devolve `authUri` — o domínio está na lista de domínios autorizados do projecto.
- **O cliente OAuth do Google.** O `redirect_uri` que o Firebase usa
  (`https://blog-comments-6b4f5.firebaseapp.com/__/auth/handler`) é aceite por
  `accounts.google.com`; o URL do próprio blog não é, como deve ser. Um
  `redirect_uri_mismatch` apareceria aqui e não apareceu.
- **O Firestore.** As regras deixam ler sem sessão (por desenho) e o `index.html`
  recebia os comentários; o problema era só entrar, não ler nem escrever.
- **O Cloudflare.** Vê a secção 2 do `CLOUDFLARE.md`: a borda devolve 403 a pedidos
  automáticos, mas isso afecta o carregamento da página, não o popup de login, que vive
  em `accounts.google.com` e `firebaseapp.com`.

## O que mudou no repositório

`docs/index.html`, só o bloco dos comentários:

1. `AUTH_PROVIDERS` passou de sete entradas para uma — Google — porque é o único
   provider OAuth ligado. Os botões dos outros seis desapareceram em vez de ficarem
   a prometer o que o projecto não tem.
2. Entraram os dois métodos que foram ligados no Firebase no mesmo dia:
   **e-mail/palavra-passe** (`signInWithEmailAndPassword`,
   `createUserWithEmailAndPassword`, `sendPasswordResetEmail`) e **telefone**
   (`RecaptchaVerifier` invisível + `signInWithPhoneNumber` → confirmação por SMS).
3. Os erros destes métodos têm mensagens próprias (`credentialMessage`), em vez de
   caírem todos em *"try another provider"*: palavra-passe errada, conta já existente,
   número mal formado, código inválido, código expirado, reCAPTCHA recusado.
4. O painel de login tem três secções separadas por "or with an email" e
   "or with a phone number"; o code do SMS aparece só depois de o SMS ser pedido, e
   "Use another number" limpa o estado e a verificação do reCAPTCHA.
5. `PROVIDER_LABELS` passou a traduzir `password` → "email and password" e `phone` →
   "phone number", para a linha "via …" debaixo do nome não dizer "signed in".

A regra do Firestore não mudou: continua a exigir `request.auth != null`, o mesmo
conjunto de campos e `createdAt == request.time`. Um comentário de telefone grava
`provider: "phone"`, um de e-mail grava `provider: "password"`, e o `name` vem do
`displayName` ou da parte local do e-mail (para telefone, "Reader").

## O que ainda falta do teu lado

1. **SMS por país.** O telefone está ligado, mas o envio responde
   `SMS unable to be sent until this region enabled by the app developer` — Portugal
   não está na lista de regiões com SMS permitido. Firebase → Authentication →
   Settings → **SMS region policy** → *Allow* + adicionar `Portugal`. Sem isso, o botão
   do telefone responde com a mensagem de região que ficou no código.
2. **Domínio do reCAPTCHA.** O `RecaptchaVerifier` corre em
   `blog.odicforcesounds.com`; se o domínio não estiver em Authentication → Settings →
   Authorized domains, o `render()` falha com `auth/invalid-app-credential` e o widget
   di-lo ("reCAPTCHA refused this domain"). Já estava autorizado à data deste
   diagnóstico.
3. **Cloudflare.** A borda ainda devolve 403 a pedidos que não parecem um browser
   (ver `CLOUDFLARE.md`, secção 2). Um leitor atrás de uma regra demasiado apertada não
   chega a ver o formulário.

## Como verificar

```sh
# 1. sintaxe do módulo
python3 - <<'EOF'
import re
src = open('docs/index.html', encoding='utf-8').read()
open('/tmp/idx.mjs','w').write(re.findall(r'<script type="module">(.*?)</script>', src, re.S)[-1])
EOF
node --check /tmp/idx.mjs

# 2. comportamento do widget (jsdom + Firebase falso, 21 asserções)
node tmp/authtest/test_comments_auth.mjs

# 3. estado real dos providers
KEY=AIzaSyAJm-VbCE6c-0shUsvFxKgFu9jnqdMU4So
for p in google.com github.com; do
  curl -s -X POST "https://identitytoolkit.googleapis.com/v1/accounts:createAuthUri?key=$KEY" \
    -H 'Content-Type: application/json' \
    -d "{\"identifier\":\"a@b.com\",\"continueUri\":\"https://blog.odicforcesounds.com/\",\"providerId\":\"$p\"}" | head -c 120; echo
done
```

O teste de jsdom cobre: um só botão de provider, formulário trancado no arranque,
entrada por e-mail, saída, palavra-passe errada, conta já existente, pedido de SMS,
código inválido, código válido, "use another number", popup do Google e pedido de
reposição de palavra-passe.

**Nota sobre o diagnóstico:** para saber se o e-mail/palavra-passe estava ligado criei
uma conta descartável (`probe-does-not-exist-9931@example.com`) através da API e
apaguei-a logo a seguir com `accounts:delete` (HTTP 200, e o login seguinte responde
`INVALID_LOGIN_CREDENTIALS`). Não ficou nenhum utilizador no projecto por causa disto.

## Ficheiros tocados

- `docs/index.html` — imports, `AUTH_PROVIDERS`, `PROVIDER_LABELS`, markup do painel de
  login, CSS (`.comments-or`, `.comments-credentials`, `.comments-recaptcha`), funções
  `credentialMessage`, `busy`, `submitEmail`, `ensureVerifier`, `resetPhone`,
  `sendPhoneCode`, `confirmPhoneCode`, e o registo dos eventos em `wireAuth`.
- `tmp/authtest/test_comments_auth.mjs` — o teste (não versionado, `tmp/` é ignorado).
- `backups/setup-facebook-github.md` — como voltar a ligar Facebook e GitHub.
- `README.md`, `.agents/skills/blog-ops/SKILL.md` — passaram a descrever três métodos
  em vez de sete.
