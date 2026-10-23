const fs = require('fs');
const p = 'docs/jardimDas15Portas-en.html';
const html = fs.readFileSync(p, 'utf8');

const before = '<h2 class="atlas-legend">Ligações</h2>';
const after = '<li><a href="./Security.html">How Hacking Actually Happens</a><span>A dark-theme field guide to how real intrusions work: reconnaissance, stolen credentials, social engineering</span><span class="name-tag">Security.html</span></li>';
const boundary = '</ul>\n\n    <section';

const bIdx = html.indexOf(before);
const aIdx = html.indexOf(after, bIdx);
const brIdx = html.indexOf(boundary, aIdx);

if (bIdx === -1 || aIdx === -1 || brIdx === -1) {
  console.error('Markers not found:', { beforeFound: bIdx !== -1, afterFound: aIdx !== -1, boundaryFound: brIdx !== -1 });
  process.exit(1);
}

const endOfList = aIdx + after.length;

const newSnippet =
`<h2 class="atlas-legend">Links</h2>
        <ul>
          <li><a href="./HowAIWorks.html">How AI Works: Technical Pipeline</a><span>The actual flow behind an AI answer: prompts, tokenization, inference, and why token IDs are not ordered numbers.</span><span class="name-tag">HowAIWorks.html</span></li>
          <li><a href="./AIForEveryone.html">AI for Everyone</a><span>If you design AI to help people, what changes — and what does not.</span><span class="name-tag">AIForEveryone.html</span></li>
          <li><a href="./StrangeNaming.html">Strange Naming</a><span>A confusion about programming conventions that is really about human creativity and language.</span><span class="name-tag">StrangeNaming.html</span></li>
          <li><a href="./HellIsFullOfGoodIdeas.html">Hell Is Full of Good Ideas</a><span>Why good ideas can create bad conditions, and why that matters when you ship something.</span><span class="name-tag">HellIsFullOfGoodIdeas.html</span></li>
          <li><a href="./AfterLearningPersonalizeIt.html">After Learning, Personalize It</a><span>Thank you for sharing to code, so others can change them.</span><span class="name-tag">AfterLearningPersonalizeIt.html</span></li>
          <li><a href="./DebianForever.html">Debian Forever</a><span>The best Distro of all times.</span><span class="name-tag">DebianForever.html</span></li>
          <li><a href="./FirejailManual.html">Firejail Technical Manual</a><span>A paranoid, interactive technical manual for Firejail — from zero to paranoid hero.</span><span class="name-tag">FirejailManual.html</span></li>
          <li><a href="./TheBeautyOfTheUgly.html">The Source Has Good Documentation</a><span>Based on an Arch Linux review, this one needs to be told.</span><span class="name-tag">TheBeautyOfTheUgly.html</span></li>
          <li><a href="./FreeBSD.html">BSD Is Awesome</a><span>Where complexity finds simplicity.</span><span class="name-tag">FreeBSD.html</span></li>
          <li><a href="./BrutalBSD.html">Maybe Just Another OpenBSD Tribute</a><span>The documentation is brutal, but some tips are needed if you are new.</span><span class="name-tag">BrutalBSD.html</span></li>
          <li><a href="./JailVSvms.html">FreeBSD Jails vs OpenBSD VMs</a><span>Which one is best?</span><span class="name-tag">JailVSvms.html</span></li>
          <li><a href="./BSDSourcesOfInformation.html">BSD: Sources of Information</a><span>Some people can teach, while I can learn.</span><span class="name-tag">BSDSourcesOfInformation.html</span></li>
          <li><a href="./EthicalHacking.html">Ethical Hacking</a><span>Let us question hacking.</span><span class="name-tag">EthicalHacking.html</span></li>
          <li><a href="./HowHackingActuallyHappens.html">How Hacking Actually Happens</a><span>A dark-theme field guide to how real intrusions work: reconnaissance, stolen credentials, social engineering.</span><span class="name-tag">HowHackingActuallyHappens.html</span></li>
          <li><a href="./PrivacyConcerns.html">Privacy Concerns</a><span>A good example of privacy.</span><span class="name-tag">PrivacyConcerns.html</span></li>
          <li><a href="./BecauseWeCare.html">Because We Care</a><span>A good example of privacy concerns in practice.</span><span class="name-tag">BecauseWeCare.html</span></li>
          <li><a href="./DNSProtocol.html">DNS Protocol</a><span>How names are resolved on the internet, step by step.</span><span class="name-tag">DNSProtocol.html</span></li>
          <li><a href="./HTTPProtocol.html">HTTP Protocol</a><span>How browsers ask for pages and servers answer them.</span><span class="name-tag">HTTPProtocol.html</span></li>
          <li><a href="./TCPUDP.html">TCP and UDP</a><span>Two ways of moving data, and when each one makes sense.</span><span class="name-tag">TCPUDP.html</span></li>
          <li><a href="./Networking.html">Networking</a><span>A practical guide to the basics of computer networks.</span><span class="name-tag">Networking.html</span></li>
          <li><a href="./Chemistry.html">Chemistry</a><span>A short technical field guide to matter, reactions, and measurement.</span><span class="name-tag">Chemistry.html</span></li>
          <li><a href="./Physics.html">Physics</a><span>A short technical field guide to motion, force, and energy.</span><span class="name-tag">Physics.html</span></li>
          <li><a href="./Mechanics.html">Mechanics</a><span>A short technical field guide to machines, levers, and simple systems.</span><span class="name-tag">Mechanics.html</span></li>
          <li><a href="./Voltage.html">Voltage</a><span>A short technical field guide to electrical potential and circuits.</span><span class="name-tag">Voltage.html</span></li>
          <li><a href="./GodWithoutFaults.html">God Without Faults</a><span>A spiritual text without blame.</span><span class="name-tag">GodWithoutFaults.html</span></li>
          <li><a href="./Kindness.html">Kindness</a><span>A short reflection on goodness and attention.</span><span class="name-tag">Kindness.html</span></li>
          <li><a href="./TaoExpression.html">Tao Expression</a><span>A way of living and writing the Tao.</span><span class="name-tag">TaoExpression.html</span></li>
          <li><a href="./WhatGodLikes.html">What God Likes</a><span>What pleases the divine in ordinary life.</span><span class="name-tag">WhatGodLikes.html</span></li>
          <li><a href="./ArmedViolence.html">Armed Violence</a><span>The technical and social anatomy of armed violence.</span><span class="name-tag">ArmedViolence.html</span></li>
          <li><a href="./ChildrenAreNotContent.html">Children Are Not Content</a><span>Why children should never be treated as content.</span><span class="name-tag">ChildrenAreNotContent.html</span></li>
          <li><a href="./Manifestations.html">Manifestations</a><span>When people take to the street and why it matters.</span><span class="name-tag">Manifestations.html</span></li>
          <li><a href="./Activism.html">Activism</a><span>A practical look at activism, its tools, and its limits.</span><span class="name-tag">Activism.html</span></li>
          <li><a href="./TryingToFixJustice.html">Trying to Fix Justice</a><span>Honest attempts to mend a broken system.</span><span class="name-tag">TryingToFixJustice.html</span></li>
          <li><a href="./TheDreamer.html">The Dreamer</a><span>All possibilities are just dreams.</span><span class="name-tag">TheDreamer.html</span></li>
          <li><a href="./CatsInTheShadow.html">Cats in the Shadow</a><span>A different kind of friend is what cats are.</span><span class="name-tag">CatsInTheShadow.html</span></li>
          <li><a href="./OtherPsychopathies.html">Other Psychopathies</a><span>Maybe it is just a logical question.</span><span class="name-tag">OtherPsychopathies.html</span></li>
          <li><a href="./ThreeWiseMonkeys.html">Three Wise Monkeys</a><span>Why refusing to see, hear, or speak evil can be positive.</span><span class="name-tag">ThreeWiseMonkeys.html</span></li>
          <li><a href="./Culture.html">Culture</a><span>The way most people remember the past.</span><span class="name-tag">Culture.html</span></li>
          <li><a href="./MyCountry.html">My Country</a><span>My country is a piece of land on planet Earth.</span><span class="name-tag">MyCountry.html</span></li>
          <li><a href="./ObviousDiscrimination.html">Obvious Discrimination</a><span>By nature of languages, they all create discrimination of information.</span><span class="name-tag">ObviousDiscrimination.html</span></li>
          <li><a href="./CommonCultures.html">Common Cultures</a><span>A celebration of world cultures: sayings, colors, music, artists, and peaceful activism.</span><span class="name-tag">CommonCultures.html</span></li>
          <li><a href="./DJNote.html">DJ Note</a><span>Bringing profound archetypal storytelling and transformational frequencies to live festival stages.</span><span class="name-tag">DJNote.html</span></li>
          <li><a href="./IfPoem.html">If Poem</a><span>While if you answer too quickly, you close a door that was trying to become a window.</span><span class="name-tag">IfPoem.html</span></li>
          <li><a href="./LoveStories.html">Love Stories</a><span>That was when he caught her reflection in the glasspane — Elena.</span><span class="name-tag">LoveStories.html</span></li>
          <li><a href="./TheGardener.html">The Gardener</a><span>A perfect garden, where every flower is in perfect condition, treated with care.</span><span class="name-tag">TheGardener.html</span></li>
          <li><a href="./ArtOfCreation.html">Art of Creation</a><span>A celebration of world cultures: sayings, colors, music genres, constructive artists, and peaceful activism.</span><span class="name-tag">ArtOfCreation.html</span></li>
          <li><a href="./LearnChess.html">ChessQuest: Master the Royal Game</a><span>You have mastered the principles of this chapter and earned +100 XP!</span><span class="name-tag">LearnChess.html</span></li>
          <li><a href="./WordGame.html">The Game of Words</a><span>Select the correct keystone word and lock it into the chamber to solve the puzzle.</span><span class="name-tag">WordGame.html</span></li>
          <li><a href="./MusicQuest.html">Music Quest</a><span>A gamified journey through music styles: Classical, Rock, Psychedelic, Metal, Techno, Psytrance, and more.</span><span class="name-tag">MusicQuest.html</span></li>
          <li><a href="./OSMandGD.html">Open Streets Heroes — OSM + Android Game Design</a><span>Zero to hero game-course: OpenStreetMap + game design for Android.</span><span class="name-tag">OSMandGD.html</span></li>
          <li><a href="./Tea.html">I Am a Tea Fan</a><span>Wine is for special moments, coffee for every morning, and tea before going to sleep.</span><span class="name-tag">Tea.html</span></li>
          <li><a href="./FruitsAndVegetables.html">Fruits and Vegetables</a><span>Pass all ingredients through a juice extractor, or blend well in a blender with a little water.</span><span class="name-tag">FruitsAndVegetables.html</span></li>
          <li><a href="./Survival.html">Survival</a><span>A dark-theme, self-contained survival guide: wilderness survival, urban survival during conflict.</span><span class="name-tag">Survival.html</span></li>
          <li><a href="./DrugsEffect.html">Drugs Effect</a><span>Is what drugs create for each one's perception of reality.</span><span class="name-tag">DrugsEffect.html</span></li>
          <li><a href="./Capitalism.html">Capitalism</a><span>A short look at markets, profit, and power.</span><span class="name-tag">Capitalism.html</span></li>
          <li><a href="./Communism.html">Communism</a><span>A short look at collective ownership and its limits.</span><span class="name-tag">Communism.html</span></li>
          <li><a href="./ChinaGarden.html">The Garden of Amazonas</a><span>Here is a cool initiative from China.</span><span class="name-tag">ChinaGarden.html</span></li>
          <li><a href="./WorldWideBusiness.html">World Wide Business</a><span>Military business for AI and robots.</span><span class="name-tag">WorldWideBusiness.html</span></li>
          <li><a href="./AboutMe.html">About the Monkey in Me</a><span>Popularity says: monkeys are the symbol of children.</span><span class="name-tag">AboutMe.html</span></li>
          <li><a href="./Books.html">Books</a><span>Just another idea for a new website.</span><span class="name-tag">Books.html</span></li>
          <li><a href="./ReadingBooks.html">Always Something New</a><span>Is what books can give you.</span><span class="name-tag">ReadingBooks.html</span></li>
          <li><a href="./PostsReview.html">From Markdown to HTML</a><span>The core language of the web.</span><span class="name-tag">PostsReview.html</span></li>
          <li><a href="./PostsReview.html">Posts Review</a><span>The core language of the web.</span><span class="name-tag">PostsReview.html</span></li>
          <li><a href="./UmaSurpresa.html">Uma Surpresa</a><span>A tribute to my most cherished master of life, without believing, I part with a biographical tribute.</span><span class="name-tag">UmaSurpresa.html</span></li>
        </ul>
`;

const replaced = html.slice(0, bIdx) + newSnippet + html.slice(endOfList);
fs.writeFileSync(p, replaced, 'utf8');
console.log('Patched rendered atlas Links list in', p);
console.log('Size:', replaced.length, 'bytes');
