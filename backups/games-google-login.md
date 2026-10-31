# Contas nos jogos — Google, pontuação e mensagens por nível

Runbook. Não é publicado: `backups/` está fora de `docs/`.

Data: 2026-10-31. Ficheiros: `docs/gameAccount.js` (módulo partilhado),
`docs/oJogoDoAdvogado.html`, `docs/oJogoDoOperador.html`, `docs/gamePlayers.html`.

## O que ficou

- **Entrar com Google** nos dois jogos que têm níveis. `oJogoDoAdvogado.html`
  (cinco níveis) e `oJogoDoOperador.html` (dezanove níveis) chamam
  `window.GameAccount`; sem sessão continuam a jogar-se exactamente como antes,
  com o progresso no `localStorage`.
- **Pontuação e certificado** guardados por conta em `gamePlayers/{uid}`, no
  campo `games.<jogo>`: `points`, `max`, `levels`, `level`, `answered`, `total`,
  `certificate`, `updatedAt`.
- **Uma mensagem por nível**, escrita e lida no ecrã de fecho desse nível, em
  `gameNotes` (`game`, `level`, `points`, `max`, `text`, `uid`, `name`, `photo`,
  `createdAt`). O limite é 280 caracteres.
- **`gamePlayers.html`** lê as duas colecções por REST e mostra jogadores,
  pontos, certificado e mensagens.

Projecto: `blog-comments-6b4f5` (o mesmo dos comentários de `index.html`).
O login é só Google; não há botão para outro fornecedor.

## O passo que falta no servidor

As colecções novas não existem até alguém escrever nelas, mas **as regras têm de
ser publicadas antes**, senão a primeira gravação falha com
`permission-denied`. No Firebase Console → Firestore → Regras, manter o bloco
dos comentários que já lá está e acrescentar:

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    /* … as regras existentes de /comments ficam como estão … */

    match /gamePlayers/{uid} {
      allow read: if true;
      allow create, update: if request.auth != null
        && request.auth.uid == uid
        && request.resource.data.uid == uid
        && request.resource.data.name is string
        && request.resource.data.name.size() <= 60;
      allow delete: if false;
    }

    match /gameNotes/{note} {
      allow read: if true;
      allow create: if request.auth != null
        && request.resource.data.uid == request.auth.uid
        && request.resource.data.text is string
        && request.resource.data.text.size() > 0
        && request.resource.data.text.size() <= 280
        && request.resource.data.name is string
        && request.resource.data.name.size() <= 60;
      allow update, delete: if false;
    }
  }
}
```

`allow read: if true` é deliberado: `gamePlayers.html` é pública e a lista de
jogadores é o ponto da página. Nada de e-mail é escrito nem lido.

## Verificar

```sh
# o módulo e os scripts inline têm de continuar a passar
cp docs/gameAccount.js /tmp/ga.mjs && node --check /tmp/ga.mjs

# a lista vazia não é erro: as colecções só aparecem depois da primeira gravação
curl -s "https://firestore.googleapis.com/v1/projects/blog-comments-6b4f5/databases/(default)/documents/gamePlayers?pageSize=5&key=AIzaSyAJm-VbCE6c-0shUsvFxKgFu9jnqdMU4So"
```

No browser, com sessão terminada: o botão do HUD diz `Entrar com Google`, o
fecho de cada nível mostra a caixa de mensagem desactivada, e depois de entrar
aparece o nome e o avatar. O certificado só é marcado quando todas as perguntas
do jogo estão respondidas.

## Limites conhecidos

- Sem sessão não há gravação: os jogos não pedem conta para jogar.
- A mensagem é pública. Está escrito na página de jogadores.
- `gameNotes` é lida inteira (limite de 300) e filtrada no cliente por
  `game` + `level`; é o que evita um índice composto no Firestore. Se a
  colecção crescer para milhares, passa a valer a pena o índice e a consulta
  filtrada no servidor.
- Apagar um registo é manual, no Console: as regras não permitem `delete` a
  partir do cliente.
