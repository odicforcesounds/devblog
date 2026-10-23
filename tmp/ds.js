const fs = require('fs');
const p = 'docs/jardimDas15Portas-en.html';
const html = fs.readFileSync(p, 'utf8');

// Replace the entire atlas Links section: from the "Links" list heading
// through the last link entry in that list, including the trailing </ul>.
const startMarker = '    <h2 class="atlas-legend">Ligações</h2>';
const endMarker = '          <span class="name-tag">privacy.html</span></li>\n        </ul>';

const sIdx = html.indexOf(startMarker);
const eIdx = html.indexOf(endMarker, sIdx);

if (sIdx === -1 || eIdx === -1) {
  console.error('Could not locate atlas Links section:', { startFound: sIdx !== -1, endFound: eIdx !== -1 });
  process.exit(1);
}

const endIdx = eIdx + endMarker.length;

const newSection = `    <h2 class="atlas-legend">Links</h2>
        <ul>
          <li><a href="./HowAIWorks.html">How AI Works: Technical Pipeline</a><span>The actual flow behind an AI answer: prompts, tokenization, inference, and why token IDs are not ordered numbers.</span><span class="name-tag">HowAIWorks.html</span></li>
          <li><a href="./AIForEveryone.html">AI for Everyone</a><span>If you design AI to help people, what changes — and what does not.</span><span class="name-tag">AIForEveryone.html</span></li>
          <li><a href="./StrangeNaming.html">Strange Naming</a><span>A confusion about programming conventions that is really about human creativity and language.</span><span class="name-tag">StrangeNaming.html</span></li>
          <li><a href="./HellIsFullOfGoodIdeas.html">Hell Is Full of Good Ideas</a><span>Why good ideas can create bad conditions, and why that matters when you ship something.</span><span class="name-tag">HellIsFullOfGoodIdeas.html</span></li>
        </ul>`;

const before = html.slice(0, sIdx);
const after = html.slice(endIdx);
const updated = before + newSection + after;

fs.writeFileSync(p, updated, 'utf8');
console.log('Replaced atlas Links section in', p);
console.log('File size:', updated.length, 'bytes');
