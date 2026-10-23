const fs = require('fs');
const path = require('path');

const PT = '../docs/jardimDas15Portas.html';
const MAP = 'en-door-mapping.json';
const OUT = '../docs/jardimDas15Portas-en.html';

const mapping = JSON.parse(fs.readFileSync(MAP, 'utf8'));
const mappingByDoor = {};
mapping.forEach(d => { mappingByDoor[d.doorId] = d.enLinks; });

const html = fs.readFileSync(PT, 'utf8');

const doorStart = html.indexOf('const DOORS = [');
const doorEnd = html.indexOf('];\n', doorStart) + 2;
const ptDoorsBlock = html.slice(doorStart, doorEnd);

const enDoorsBlock = ptDoorsBlock.replace(/links:\s*\[[^\]]*\]/g, (m) => {
  const firstIdMatch = m.match(/id:\s*"([^"]+)"/);
  const doorId = firstIdMatch ? firstIdMatch[1] : null;
  const newLinks = doorId && mappingByDoor[doorId] ? mappingByDoor[doorId] : null;
  if (!newLinks) return m;
  return 'links: [' + newLinks.map(h => JSON.stringify(h)).join(', ') + ']';
});

const libStart = html.indexOf('const LIBRARY = [');
const libEnd = html.indexOf('];\n', libStart) + 2;

let bodyHtml = html.slice(html.indexOf('<body>'), html.indexOf('</body>') + '</body>'.length);

bodyHtml = bodyHtml
  .replace(/lang="pt-PT"/, 'lang="en"')
  .replace('<title>O Jardim das 15 Portas — Um jogo de lições</title>', '<title>The Garden of 15 Doors — A game of lessons</title>')
  .replace('<meta name="description" content="Um jogo literário e interactivo em português de Portugal: quinze portas, quinze categorias, centenas de artigos. Atravessa a biblioteca, escolhe gestos e descobre o que fica quando o mapa fica em branco.">', '<meta name="description" content="A literary interactive game in English: fifteen doors, fifteen categories, hundreds of articles. Move through the library, choose gestures, and learn what remains when the map stays blank.">')
  .replace('<a class="skip" href="#jogo">Saltar para o jogo</a>', '<a class="skip" href="#jogo">Skip to the game</a>')
  .replace('<a class="brand" href="./index.html" aria-label="Voltar ao índice do site">', '<a class="brand" href="./index.html" aria-label="Back to the site index">')
  .replace('Voltar ao índice', 'Back to index')
  .replace('<span class="brand-text">O Jardim das 15 Portas<small>um jogo de lições</small></span>', '<span class="brand-text">The Garden of 15 Doors<small>a game of lessons</small></span>')
  .replace('aria-label="Secções desta página"', 'aria-label="Sections on this page"')
  .replace('<a href="#jogo">Jogo</a>', '<a href="#jogo">Game</a>')
  .replace('<a href="#portas">Portas</a>', '<a href="#portas">Doors</a>')
  .replace('<a href="#sobre">Sobre</a>', '<a href="#sobre">About</a>')
  .replace('Biblioteca viva · 15 portas', 'Living library · 15 doors')
  .replace('<h1 id="hero-title">O Jardim<span>das quinze</span><em>portas.</em></h1>', '<h1 id="hero-title">The Garden<span>of fifteen</span><em>doors.</em></h1>')
  .replace('Entrar no jardim', 'Enter the garden')
  .replace('Abrir uma porta ao acaso', 'Open a door at random')
  .replace('Ouvir um sussurro', 'Hear a whisper')
  .replace(/<p class="hero-lead">([\s\S]*?)<\/p>/, (m, inner) => {
    const translated = inner
      .replace(/Alguém está a desenhar um mapa de tudo o que amas\./, 'Someone is drawing a map of everything you love.')
      .replace(/Cada porta que abres é uma lição sobre poder, cuidado, criação e escuta\./, 'Each door you open is a lesson about power, care, making, and listening.')
      .replace(/No fim, o mapa terá uma parte em branco — e é essa parte que vai decidir se o jardim floresce\./, 'At the end the map will have a blank part — and that blank is what decides whether the garden grows.');
    return '<p class="hero-lead">' + translated + '</p>';
  })
  .replace('Roda das quinze portas', 'Ring of fifteen doors')
  .replace('○ por abrir', '○ to open')
  .replace('● semeada', '● sown')
  .replace('<span class="section-label">O jogo</span>', '<span class="section-label">The game</span>')
  .replace('<h2 id="jogo-title">Quinze portas. Quatro fios.</h2>', '<h2 id="jogo-title">Fifteen doors. Four threads.</h2>')
  .replace(/Cada porta é uma categoria deste arquivo\. Não há ordem certa\. Escolhe um gesto em cada porta e observa o que ele faz aos quatro fios: <strong>Ver<\/strong>, <strong>Guardar<\/strong>, <strong>Criar<\/strong> e <strong>Escutar<\/strong>\. No fim, o jardim responde ao que ficou mais forte — e ao que ficou demasiado fino\./, 'Each door is a category from this archive. There is no right order. Choose one gesture at each door and notice what it does to the four threads: <strong>Seeing</strong>, <strong>Keeping</strong>, <strong>Making</strong>, and <strong>Listening</strong>. At the end the garden answers to what grew strongest — and to what grew too thin.')
  .replace(/Progresso do jogo/g, 'Game progress')
  .replace(/Reiniciar/g, 'Reset')
  .replace(/semeadas/g, 'sown')
  .replace(/<span class="hud-count"><b id="visited-count">0<\/b> \/ 15 semeadas<\/span>/, '<span class="hud-count"><b id="visited-count">0</b> / 15 sown</span>')
  .replace(/<span class="lock-count">Faltam 15 portas\.<\/b> O portão final abre quando todas forem semeadas\.<\/span>/, '<span class="lock-count">15 doors remain.</b> The final gate opens when all are sown.</span>')
  .replace(/O portão final/g, 'The final gate')
  .replace(/O que fica quando o mapa fica em branco\?/, 'What remains when the map stays blank?')
  .replace(/Ler a lição central/, 'Read the central lesson')
  .replace(/As portas<\/span>/g, 'The doors</span>')
  .replace('<h2 id="portas-title">As quinze lições</h2>', '<h2 id="portas-title">The fifteen lessons</h2>')
  .replace(/Uma visão serena de cada porta, para quem quiser ler o jardim de fora para dentro\./, 'A calm view of each door, for anyone who wants to read the garden from the outside in.')
  .replace(/Um jardim feito de portas emprestadas\./, 'A garden made of borrowed doors.')
  .replace(/Esta página é uma criatura nova feita com o corpo de uma biblioteca\. As lições são interpretações; os artigos são reais\. A ferida central vem de <em>Armas Não São Conteúdo<\/em>: o que sabemos sobre alguém nunca deve ser transformado numa arma contra essa pessoa\./, 'This page is a new creature built from the body of a library. The lessons are interpretations; the articles are real. The central wound comes from <em>Armas Não São Conteúdo</em>: what we know about someone should never be turned into a weapon against that person.')
  .replace('A regra do jardim', 'The garden rule')
  .replace('Nem tudo o que cresce deve ser colhido\.', 'Not everything that grows should be picked.')
  .replace(/Ver, guardar, criar e escutar são fios\. Nenhum é bom sozinho\. O jardim só floresce quando os quatro se corrigem\./, 'Seeing, keeping, making, and listening are threads. None is good alone. The garden only grows when the four correct one another.')
  .replace('A ferida central', 'The central wound')
  .replace('O mapa não é o território\.', 'The map is not the territory.')
  .replace(/Uma etiqueta, uma fotografia e um lugar podem construir um alvo\. A parte em branco não é ignorância: é cuidado\./, 'A label, a photograph, and a place can build a target. The blank part is not ignorance: it is care.')
  .replace('Como jogar', 'How to play')
  .replace('Escolhe um gesto, não uma resposta certa\.', 'Choose a gesture, not a right answer.')
  .replace(/Não há pontuação\. Há consequências\. Podes voltar a jogar e escolher outro fio\./, 'There is no score. There are consequences. You can play again and choose a different thread.')
  .replace('Privacidade', 'Privacy')
  .replace('O progresso fica no teu navegador\.', 'Your progress stays in your browser.')
  .replace(/O jogo guarda as portas semeadas em <span class="mono">localStorage<\/span>\. Não há contas, servidores, análises ou cookies de terceiros\./, 'The game stores the sown doors in <span class="mono">localStorage</span>. There are no accounts, servers, analytics, or third-party cookies.')
  .replace(/Se este jardim te levou a algum lado, leva também a pergunta: quem está a pagar o preço daquilo que estou a mostrar\? A resposta pode mudar a próxima porta que abres\./, 'If this garden has led you somewhere, take this question too: who is paying the price for what I am showing? The answer may change the next door you open.')
  .replace(/Voltar ao índice<\/a> · <a href="#jogo">Topo do jogo<\/a> · <a href="#portas">Portas<\/a>/, 'Back to index</a> · <a href="#jogo">Top of the game</a> · <a href="#portas">Doors</a>')
  .replace(/Um jogo literário em português de Portugal\. CSS e JavaScript nativos, sem recursos externos\. As portas são artigos reais deste arquivo; as lições são uma leitura possível\./, 'A literary game in English. Native CSS and JavaScript, no external resources. The doors are real articles from this archive; the lessons are one possible reading.')
  .replace('O Jardim das 15 Portas · 2026', 'The Garden of 15 Doors · 2026')
  .replace('Fechar porta', 'Close door')
  .replace(/JavaScript está desativado\.<\/strong> O jogo é construído por JavaScript para guardar as escolhas e revelar o poema final\. Sem JavaScript, podes continuar a navegar pelo <a href="\.\/index\.html">índice principal<\/a>\./, '<strong>JavaScript is disabled.</strong> The game is built with JavaScript to store choices and reveal the final poem. Without JavaScript, you can still browse the <a href="./index.html">main index</a>.')
  .replace('JavaScript está desativado\.', 'JavaScript is disabled.')
  .replace(/Gesto escolhido · /g, 'Chosen gesture · ')
  .replace(/Porta semeada\./g, 'Door sown.')
  .replace(/Abrir porta\./g, 'Open door.')
  .replace(/semeada/g, 'sown')
  .replace(/Portas para levar/g, 'Doors to take')
  .replace(/Abrir porta/g, 'Open door')
  .replace(/fio mais forte: /g, 'strongest thread: ')
  .replace(/fio mais fino: /g, 'thinnest thread: ')
  .replace(/Final do jogo: /g, 'End of the game: ')
  .replace(/Porta semeada: /g, 'Door sown: ')
  .replace(/Jogo reiniciado\. As quinze portas estão por abrir\./, 'Game reset. The fifteen doors are ready to open.')
  .replace(/Clica outra vez/g, 'Click again');

let scriptHtml = bodyHtml.slice(bodyHtml.indexOf('<script>'), bodyHtml.length);

scriptHtml = scriptHtml
  .replace('Ver', 'Seeing')
  .replace('Guardar', 'Keeping')
  .replace('Criar', 'Making')
  .replace('Escutar', 'Listening')
  .replace('title: "A Janela"', 'title: "The Window"')
  .replace('title: "O Cofre"', 'title: "The Strongbox"')
  .replace('title: "A Chama"', 'title: "The Flame"')
  .replace('title: "A Raiz"', 'title: "The Root"')
  .replace('title: "O Jardim"', 'title: "The Garden"')
  .replace(/Não escolheste uma porta\. Escolheste aprender a abrir e a fechar\. O mapa ficou com uma parte em branco — e foi essa parte que salvou alguém\. O jardim não cresce porque alguém o vê; cresce porque alguém sabe quando não deve desenhar\./, 'You did not choose a door. You chose to learn to open and close. The map stayed with a blank part — and that blank is what saved someone. The garden does not grow because someone sees it; it grows because someone knows when not to draw.')
  .replace(/Viste tudo\. A luz entrou, mas também entraram os olhos dos outros\. Aprende agora que ver não é possuir: a próxima janela precisa de uma cortina, e a próxima verdade precisa de um rosto que a possa suportar\./, 'You saw everything. Light came in, but so did other eyes. Learn now that seeing is not possessing: the next window needs a curtain, and the next truth needs a face that can bear it.')
  .replace(/Protegeste tudo\. O mapa ficou fechado, mas também ficaram lá dentro as vozes que precisavam de sair\. A próxima chave deve abrir uma porta, não um silêncio\. Proteger sem escutar é apenas adiar a ferida\./, 'You protected everything. The map stayed closed, but the voices that needed to leave were trapped inside it too. The next key should open a door, not a silence. Protecting without listening is only postponing the wound.')
  .replace(/Criaste uma saída onde havia muro\. A chama iluminou o caminho e queimou uma parte do mapa\. Aprende a cuidar do que acendes: a beleza que não protege transforma a casa em cinza\./, 'You made an exit where there was a wall. The flame lit the path and burned part of the map. Learn to care for what you set alight: beauty that does not protect turns the house to ash.')
  .replace(/Escutaste até ao fundo\. A raiz encontrou água, mas ficou tempo demais debaixo da terra\. A próxima escuta deve terminar num gesto\. Compreender não é o mesmo que ficar parado\./, 'You listened all the way down. The root found water, but stayed too long under the earth. The next listening should end in a gesture. Understanding is not the same as standing still.');

const newHtml = html.slice(0, html.indexOf('<body>'))
  + '\nconst DOORS = [\n'
  + enDoorsBlock.slice('const DOORS = ['.length)
  + '\n\nconst LIBRARY = ['
  + html.slice(libStart + 'const LIBRARY = ['.length, libEnd)
  + '\n\n'
  + bodyHtml.slice(0, bodyHtml.indexOf('<script>'))
  + scriptHtml;

fs.writeFileSync(OUT, newHtml, 'utf8');
console.log('wrote', OUT, 'bytes', newHtml.length);

const idRegex = /"id":\s*"([^"]+)"/g;
const linksByDoor = {};
let lastDoorId = null;
let m;
while ((m = idRegex.exec(newHtml)) !== null) {
  lastDoorId = m[1];
}
const linkRegex = /"links":\s*\[([^\]]*)\]/g;
while ((m = linkRegex.exec(newHtml)) !== null) {
  const before = newHtml.slice(0, m.index);
  const idMatch = before.match(/"id":\s*"([^"]+)"/);
  if (idMatch) linksByDoor[idMatch[1]] = m[1];
}

let errors = [];
Object.keys(linksByDoor).forEach(doorId => {
  const linkList = linksByDoor[doorId];
  if (!linkList) return;
  const links = linkList.split(',').map(s => s.trim().replace(/^"(.*)"$/, '$1').replace(/^'(.*)'$/, '$1'));
  links.forEach(link => {
    if (!link) return;
    if (!link.endsWith('.html') && !/^https?:\/\//.test(link)) {
      errors.push(doorId + ' -> ' + link);
    }
  });
});

console.log('doors mapped in script:', Object.keys(linksByDoor).length);
console.log('link errors:', errors.length, JSON.stringify(errors));
