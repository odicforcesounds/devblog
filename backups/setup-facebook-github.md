# Ligar Facebook e GitHub ao login dos comentários

Guia de configuração, não de código. O widget em `docs/index.html` hoje só oferece
Google, e-mail e telefone (ver `comments-login-failure.md`). Para voltar a ter Facebook
ou GitHub são precisas duas coisas: **um par de credenciais no Firebase** e **uma entrada
no array `AUTH_PROVIDERS`** — uma sem a outra ou não aparece, ou falha ao clicar.

Projecto: `blog-comments-6b4f5`. Sítio: `https://blog.odicforcesounds.com`.
Callback que ambos os fornecedores usam:

```text
https://blog-comments-6b4f5.firebaseapp.com/__/auth/handler
```

O Firebase mostra este URL, já com o projecto certo, no painel de cada provider
(Authentication → Sign-in method → o provider → *Copy link*). Usa o que lá estiver em
vez de copiar o de cima à mão.

---

## 1. GitHub

### 1.1 Criar a OAuth App

1. <https://github.com/settings/developers> → **OAuth Apps** → **New OAuth App**
   (ou `https://github.com/organizations/odicforcesounds/settings/applications`, se
   quiseres a app na organização em vez de na conta pessoal).
2. **Application name:** `Monkey Blog Comments` (é o que o utilizador vê no ecrã de
   autorização).
3. **Homepage URL:** `https://blog.odicforcesounds.com/`
4. **Authorization callback URL:**
   `https://blog-comments-6b4f5.firebaseapp.com/__/auth/handler`
   — tem de ser este, **não** o do blog. É o Firebase que recebe o `code` do GitHub.
5. **Register application**.
6. **Generate a new client secret**. O secret aparece **uma vez**. Copia-o para o passo
   seguinte; não o guardes no repositório.

### 1.2 Ligar no Firebase

Firebase console → **Authentication** → **Sign-in method** → **GitHub** → *Enable*:

- **Client ID** — o `Client ID` da página da OAuth App.
- **Client secret** — o que acabaste de gerar.
- **Copy and save the callback URL** no GitHub se ainda não estiver lá igual.
- **Save**.

O GitHub está pronto quando `createAuthUri` deixa de responder
`OPERATION_NOT_ALLOWED : The identity provider configuration is not found.`

### 1.3 Detalhe que morde

- O scope que o Firebase pede é `read:user`. Não pede e-mail; contas GitHub com e-mail
  privado chegam **sem** `email`, e o widget cai no `displayName` e, sem ele, em
  `"Reader"`. Não é um erro — é uma conta sem nome público.
- Se mudares o `authDomain` no `firebaseConfig`, o callback muda e o GitHub tem de ser
  actualizado outra vez.

---

## 2. Facebook

O Facebook é mais chato do que o GitHub porque a app tem de sair do modo de
desenvolvimento para qualquer pessoa poder entrar.

### 2.1 Criar a app

1. <https://developers.facebook.com/apps/> → **Create app**.
2. Caso de uso: **Authenticate and request data from users with Facebook Login** →
   tipo **Consumer** (ou *Business*, se preferires).
3. **App name:** `Monkey Blog Comments`. **App contact email:** o teu.
4. Depois de criada, no menu: **Add product** → **Facebook Login** → **Set up** →
   plataforma **Web**.

### 2.2 Configurar o Facebook Login

Em **Facebook Login → Settings**:

- **Client OAuth Login:** ligado.
- **Web OAuth Login:** ligado.
- **Enforce HTTPS:** ligado.
- **Valid OAuth Redirect URIs:** `https://blog-comments-6b4f5.firebaseapp.com/__/auth/handler`
- **Login with the JavaScript SDK:** desligado (o Firebase faz o redirect sozinho, não
  usa o SDK do Facebook na página).
- **Save changes**.

Em **Settings → Basic**:

- **App Domains:** `blog.odicforcesounds.com`
- **Privacy Policy URL:** obrigatório para publicar — `https://blog.odicforcesounds.com/`
  ou uma página de privacidade do blog.
- **Terms of Service URL:** opcional.
- **Data Deletion / User data deletion:** o Facebook exige um; um URL que explique que os
  dados são apagados em pedido serve.
- **Save changes**, e copia o **App ID** e o **App Secret** (*App secret → Show*).

### 2.3 Ligar no Firebase

Firebase console → **Authentication** → **Sign-in method** → **Facebook** → *Enable*:

- **App ID** e **App secret** do passo anterior.
- Copia o **OAuth redirect URI** mostrado ali e confirma que é exactamente o mesmo que
  puseste em *Valid OAuth Redirect URIs*.
- **Save**.

### 2.4 Pôr a app em Live

Enquanto a app estiver em **Development**, só entra quem tiver um papel na app (admin,
developer, tester). Para todos os outros o popup fecha e o Firebase devolve
`auth/operation-not-allowed` ou `auth/popup-closed-by-user` sem explicação.

**App Mode: Development → Live** (interruptor no topo do painel). O Facebook pede
revisão de permissões apenas para `email` e `public_profile`? Não: essas duas são as
básicas e passam sem revisão, mas a app tem de estar em Live e com política de
privacidade preenchida.

### 2.5 Detalhe que morde

- Facebook não entrega e-mail a quem tenha a app autenticada sem permissão aprovada, e
  contas sem e-mail verificado chegam com `email` vazio → mesmo fallback do GitHub.
- O avatar vem de `platform-lookaside.fbsbx.com`, que já está na lista `AVATAR_HOSTS`.

---

## 3. O código: voltar a mostrar os botões

Só depois de o provider estar ligado no Firebase. Em `docs/index.html`, no módulo dos
comentários, duas alterações:

```js
// imports
import {
  ...
  FacebookAuthProvider,
  GithubAuthProvider,
  ...
} from "https://www.gstatic.com/firebasejs/10.12.5/firebase-auth.js";

// providers
const AUTH_PROVIDERS = [
  { id: "google.com", label: "Continue with Google", primary: true, make: function () { return new GoogleAuthProvider(); } },
  { id: "github.com", label: "Continue with GitHub", primary: false, make: function () { return new GithubAuthProvider(); } },
  { id: "facebook.com", label: "Continue with Facebook", primary: false, make: function () { return new FacebookAuthProvider(); } }
];
```

Nada mais é preciso: `renderProviders()` constrói os botões a partir do array,
`startSignIn()` já trata de `signInWithPopup` com queda para `signInWithRedirect`, e
`PROVIDER_LABELS` deriva os nomes do próprio array. O botão de telefone e o de e-mail
ficam como estão, abaixo dos providers.

Depois de editar:

```sh
python3 .agents/skills/blog-ops/check_site.py
node tmp/authtest/test_comments_auth.mjs      # a asserção "um só botão" passa a falhar
```

O teste verifica que existe **um** botão de provider; ao acrescentares outros, ajusta
essa asserção (é uma linha) — não a apagues, senão deixa de provar o que interessa.

---

## 4. Confirmar que ficou igual ao Firebase

```sh
KEY=AIzaSyAJm-VbCE6c-0shUsvFxKgFu9jnqdMU4So
for p in google.com github.com facebook.com; do
  printf '%-14s ' "$p"
  curl -s -X POST "https://identitytoolkit.googleapis.com/v1/accounts:createAuthUri?key=$KEY" \
    -H 'Content-Type: application/json' \
    -d "{\"identifier\":\"a@b.com\",\"continueUri\":\"https://blog.odicforcesounds.com/\",\"providerId\":\"$p\"}" \
    | tr -d '\n' | head -c 110; echo
done
```

- `"authUri": "https://github.com/login/oauth/authorize?..."` → o provider está ligado
  e o pedido até chega ao GitHub.
- `OPERATION_NOT_ALLOWED : The identity provider configuration is not found.` → o
  Firebase ainda não tem credenciais para esse provider, ou ficou por gravar.

Um `authUri` gerado **não** prova que o login termina: o `redirect_uri_mismatch` do
GitHub e o "app em Development" do Facebook só aparecem depois de escolheres a conta. O
teste final é sempre um login a sério numa janela privada, com a conta de outra pessoa se
possível.

## 5. O que nunca vai para o repositório

O **client secret** do GitHub e o **App secret** do Facebook ficam só no Firebase. O
`apiKey` no `firebaseConfig` do `index.html` é público por desenho (identifica o
projecto, não autoriza nada); os secrets não. Se um deles alguma vez entrar num commit,
roda-os no fornecedor — o histórico do git não é sítio para os apagar.
