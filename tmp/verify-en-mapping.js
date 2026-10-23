const fs = require('fs');
const path = require('path');

// Mapping: Door id -> English HTML files in docs/
const mapping = {
  "golem": ["howAIworks.html", "aiCanHelpIf.html", "strangeNaming.html", "hell.html"],
  "casa": ["creativeLinux.html", "debianForever.html", "fireJail.html", "the_beauty_of_the_ugly.html"],
  "fortaleza": ["FreeBSD.html", "brutalBSD.html", "jailVSvms.html", "bsdResources.html"],
  "espelho": ["EthicalLawsOnIT.html", "Security.html", "privacy.html", "because_we_care.html"],
  "fios": ["dnsProtocol.html", "httpProtocol.html", "tcpudp.html", "networking.html"],
  "forja": ["Chemistry.html", "Physics.html", "Mechanics.html", "Voltage.html"],
  "silencio": ["semCulpa.html", "bondade.html", "taoExpression.html", "whatGodLikes.html"],
  "mapa": ["ArmedViolence.html", "criancasNaoSaoConteudo.html", "manifestations.html", "activism.html", "tryingToFixJustice.html"],
  "sonho": ["dreamer.html", "shadowCat.html", "outrasPsicopatias.html", "3wiseMonkeys.html"],
  "cidade": ["culture.html", "myCountry.html", "theObviousDiscrimination.html", "CommonCultures.html"],
  "chama": ["notaDJ.html", "ifPoem.html", "loveStories.html", "theGardener.html", "ArtOfCreation.html"],
  "jogo": ["learnChess.html", "wordGame.html", "MusicQuest.html", "osmAndGD.html"],
  "corpo": ["tea.html", "frutasVegetais.html", "survival.html", "drugsEffect.html"],
  "mercado": ["capitalism.html", "communism.html", "chinaGarden.html", "WorldWideBusiness.html"],
  "biblioteca": ["about_me.html", "books.html", "readingBooks.html", "postsReview.html", "umaSurpresa.html"]
};

const docsDir = 'docs';
const errors = [];

for (const [doorId, links] of Object.entries(mapping)) {
  for (const filename of links) {
    const filePath = path.join(docsDir, filename);
    if (!fs.existsSync(filePath)) {
      errors.push(`[${doorId}] Missing: ${filename}`);
    }
  }
}

if (errors.length === 0) {
  console.log('All 15 DOOR link mappings resolve to files that exist in docs/');
} else {
  errors.forEach(e => console.error(e));
  process.exit(1);
}

// Also print a quick summary
const total = Object.values(mapping).reduce((a, b) => a + b.length, 0);
console.log(`Total linked files: ${total} across ${Object.keys(mapping).length} doors`);
