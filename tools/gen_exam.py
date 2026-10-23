#!/usr/bin/env python3
"""Generate docs/gameReference.html — sequential Archive Master Exam.

Reads /tmp/levels3.json (topic-based questions, shuffled answer positions)
and rebuilds the single-file game with the same step-by-step structure:
Step 1 READ (in-box link), then 3 questions, only the active level visible.
"""
import json

levels = json.load(open('/tmp/levels3.json'))
TOTAL = len(levels)

HEAD = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Archive Master Exam — Sequential Technical Path</title>
  <style>
    :root {
      --bg: #05070d;
      --panel: rgba(16, 22, 32, 0.95);
      --panel-2: rgba(20, 26, 38, 0.97);
      --border: rgba(130, 160, 200, 0.28);
      --border-glow: rgba(84, 227, 196, 0.65);
      --text: #e9f2f9;
      --text-soft: #bcc9de;
      --muted: #7f91b0;
      --accent: #54e3c4;
      --accent-warm: #ffbe6b;
      --accent-violet: #a78bfa;
    }
    * { box-sizing: border-box; }
    html, body {
      margin:0; padding:0;
      background: radial-gradient(ellipse at top, rgba(84,227,196,0.12), transparent 55%),
                  radial-gradient(ellipse at bottom, rgba(167,139,250,0.1), transparent 62%),
                  var(--bg);
      color: var(--text);
      font-family: "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
      line-height:1.8; min-height:100%;
    }
    body::before, body::after { content:""; position:fixed; inset:0; pointer-events:none; }
    body::before {
      background-image: linear-gradient(rgba(84,227,196,0.02) 1px, transparent 1px),
                        linear-gradient(90deg, rgba(84,227,196,0.02) 1px, transparent 1px);
      background-size: 60px 60px; opacity:0.32; z-index:0;
    }
    body::after {
      background: radial-gradient(circle at 15% 5%, rgba(84,227,196,0.14), transparent 48%),
                  radial-gradient(circle at 85% 0%, rgba(167,139,250,0.14), transparent 44%);
      z-index:0;
    }
    header {
      position:relative; z-index:3; text-align:center;
      padding: clamp(2rem,6vw,4.4rem) 1.5rem 1rem;
      display:flex; flex-direction:column; align-items:center; gap:1rem;
    }
    .top-nav { display:flex; flex-wrap:wrap; justify-content:center; gap:0.8rem; }
    .nav-pill {
      display:inline-flex; align-items:center; gap:0.5rem;
      padding:0.4rem 0.95rem; border-radius:999px; border:1px solid var(--border);
      background: linear-gradient(90deg, transparent, rgba(84,227,196,0.16), transparent);
      font-family:"Courier New", monospace; text-transform:uppercase; letter-spacing:0.3em; font-size:0.7rem; color:var(--muted);
    }
    .nav-pill strong { color:var(--accent); letter-spacing:0.22em; }
    .home-link {
      display:inline-flex; align-items:center; gap:0.4rem;
      padding:0.4rem 0.95rem; border-radius:999px; border:1px solid var(--border);
      color:var(--text); text-decoration:none; letter-spacing:0.14em; text-transform:uppercase; font-size:0.9rem;
      transition:border-color 160ms ease, color 160ms ease, box-shadow 160ms ease;
    }
    .home-link:hover, .home-link:focus-visible { border-color:var(--border-glow); color:var(--accent); box-shadow:0 0 0 4px rgba(84,227,196,0.08); outline:none; }
    .kicker { font-family:"Courier New", monospace; text-transform:uppercase; letter-spacing:0.64em; font-size:0.72rem; color:var(--muted); margin:0; }
    h1 { margin:0; font-size:clamp(2.8rem,12vw,6.2rem); letter-spacing:-0.05em; text-transform:uppercase; }
    .title-gradient {
      background: linear-gradient(120deg, var(--text) 0%, var(--accent) 48%, var(--accent-violet) 100%);
      -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent;
    }
    .subtitle { margin:0 auto; max-width:820px; color:var(--text-soft); font-size:clamp(1rem,2vw,1.16rem); }
    main {
      position:relative; z-index:3;
      display:flex; flex-direction:column; gap:clamp(1.6rem,6vw,3.6rem);
      width:min(1180px,100%); margin:0 auto; padding:0 clamp(1.2rem,4vw,2.8rem) clamp(4rem,10vw,7rem);
    }
    .level-container { display:flex; flex-direction:column; gap:clamp(1.2rem,4vw,2rem); }
    .level { position:relative; display:none; }
    .level.active { display:block; }
    .level-card {
      position:relative; border-radius:1rem; border:1px solid var(--border);
      background: linear-gradient(180deg, rgba(84,227,196,0.1) 0%, transparent 44%), var(--panel-2);
      overflow:hidden; box-shadow: 0 90px 150px -110px rgba(84,227,196,0.48);
    }
    .level-ornament { position:absolute; inset:0; pointer-events:none; background: radial-gradient(circle at top left, rgba(84,227,196,0.2), transparent 60%); }
    .level-content {
      position:relative; z-index:1;
      display:grid; grid-template-columns: repeat(12, 1fr);
      gap:clamp(1.2rem,4vw,2.8rem);
      padding:clamp(1.8rem,6vw,3.8rem);
    }
    .level-header { grid-column:1 / -1; display:flex; flex-wrap:wrap; align-items:flex-start; justify-content:space-between; gap:1rem; }
    .level-id-group { display:flex; flex-direction:column; gap:0.4rem; }
    .level-kicker {
      font-family:"Courier New", monospace; text-transform:uppercase; letter-spacing:0.42em; font-size:0.7rem; color:var(--muted);
      display:flex; align-items:center; gap:0.6rem;
    }
    .level-dot { width:0.4rem; height:0.4rem; border-radius:50%; background: radial-gradient(circle, var(--accent), transparent 70%); box-shadow: 0 0 0 8px rgba(84,227,196,0.12); }
    .level-title { margin:0; font-size:clamp(2rem,5vw,3.4rem); letter-spacing:-0.03em; }
    .level-status { font-family:"Courier New", monospace; text-transform:uppercase; letter-spacing:0.32em; font-size:0.7rem; color:var(--muted); }
    .level-grid { grid-column:1 / -1; display:grid; grid-template-columns: repeat(12, 1fr); gap:clamp(1.2rem,4vw,2.6rem); }
    .step-section { grid-column:1 / -1; display:flex; flex-direction:column; gap:1.2rem; }
    .step-kicker { font-family:"Courier New", monospace; text-transform:uppercase; letter-spacing:0.38em; font-size:0.68rem; color:var(--accent-warm); }
    .step-title { margin:0; font-size:clamp(1.6rem,3.6vw,2.2rem); }
    .step-text { margin:0; color:var(--text-soft); font-size:clamp(1.02rem,2vw,1.14rem); }
    .ref-block {
      border-radius:0.9rem; border:1px solid var(--border); background: rgba(10,16,26,0.86);
      padding:clamp(1rem,3vw,1.6rem); display:flex; flex-direction:column; gap:0.8rem;
    }
    .ref-kicker { font-family:"Courier New", monospace; text-transform:uppercase; letter-spacing:0.34em; font-size:0.66rem; color:var(--muted); }
    .word-link { color:var(--accent); text-decoration:none; position:relative; padding:0 0.2rem; }
    .word-link::after {
      content:""; position:absolute; left:0; bottom:-0.18rem; width:100%; height:1px;
      background: linear-gradient(90deg, transparent, var(--accent), transparent);
      transform: scaleX(0.4); transform-origin:center; transition: transform 160ms ease, opacity 160ms ease; opacity:0.6;
    }
    .word-link:hover, .word-link:focus-visible { color:var(--text); outline:none; }
    .word-link:hover::after, .word-link:focus-visible::after { transform: scaleX(1); opacity:1; }
    .exam-panel { grid-column:1 / -1; display:flex; flex-direction:column; gap:1rem; }
    .exam-card {
      border-radius:0.9rem; border:1px solid var(--border);
      background: radial-gradient(circle at top, rgba(84,227,196,0.18), transparent 74%), rgba(10,16,26,0.92);
      padding:clamp(1.2rem,3vw,1.9rem); display:flex; flex-direction:column; gap:1rem; position:relative; overflow:hidden;
    }
    .exam-card::after { content:""; position:absolute; inset:0; background: radial-gradient(circle at bottom right, rgba(255,190,107,0.12), transparent 64%); pointer-events:none; }
    .exam-card>* { position:relative; z-index:1; }
    .exam-kicker { font-family:"Courier New", monospace; text-transform:uppercase; letter-spacing:0.38em; font-size:0.68rem; color:var(--accent-warm); }
    .exam-question { margin:0; font-size:clamp(1.16rem,2.6vw,1.6rem); }
    .exam-options { display:flex; flex-direction:column; gap:0.7rem; }
    .exam-option {
      border-radius:999px; border:1px solid var(--border); background:transparent; color:var(--text-soft);
      text-align:left; padding:0.7rem 1.2rem; font-size:0.98rem;
      display:flex; align-items:flex-start; gap:0.8rem; cursor:pointer;
      transition:border-color 160ms ease, color 160ms ease, background 160ms ease, box-shadow 160ms ease;
    }
    .exam-option:hover:not(:disabled) { border-color:var(--border-glow); color:var(--text); box-shadow:0 0 0 4px rgba(84,227,196,0.06); }
    .exam-option:disabled { cursor:not-allowed; opacity:0.8; }
    .exam-option.correct { border-color:rgba(34,211,238,0.9); color:var(--text); background: radial-gradient(circle at left, rgba(34,211,238,0.18), transparent 72%); }
    .exam-option.wrong { border-color:rgba(255,107,107,0.85); color:var(--text); }
    .option-index { font-family:"Courier New", monospace; color:var(--muted); flex-shrink:0; }
    .exam-feedback { margin:0; font-family:"Courier New", monospace; font-size:0.88rem; color:var(--muted); min-height:1.4rem; }
    .advance-btn {
      align-self:flex-start; border-radius:999px; border:1px solid var(--border); background:transparent;
      color:var(--text); padding:0.6rem 1.4rem; font-size:0.95rem; letter-spacing:0.12em; text-transform:uppercase;
      cursor:pointer; display:none;
    }
    .advance-btn.visible { display:inline-flex; }
    .advance-btn:hover, .advance-btn:focus-visible { border-color:var(--border-glow); color:var(--accent); box-shadow:0 0 0 4px rgba(84,227,196,0.08); outline:none; }
    footer {
      position:relative; z-index:3; text-align:center;
      padding:0 1.5rem clamp(3rem,8vw,5rem);
      color:var(--muted); display:flex; flex-direction:column; gap:0.8rem; align-items:center;
    }
    .footer-line { width:min(560px,80%); height:1px; background:linear-gradient(90deg, transparent, var(--border), transparent); }
    .footer-text { margin:0; font-family:"Courier New", monospace; text-transform:uppercase; letter-spacing:0.42em; font-size:0.7rem; }
    .footer-home { color:var(--accent); text-decoration:none; }
    .footer-home:hover, .footer-home:focus-visible { color:var(--text); outline:none; }
  </style>
</head>
<body>
  <header>
    <div class="top-nav">
      <a class="home-link" href="./index.html"><span>←</span><span>Home</span></a>
      <div class="nav-pill"><span>Current Level</span><strong id="current-level">1 / __TOTAL__</strong></div>
      <div class="nav-pill"><span>Completed</span><strong id="completed">0</strong></div>
    </div>
    <p class="kicker">Sequential Master Path</p>
    <h1><span class="title-gradient">Archive Master Exam</span></h1>
    <p class="subtitle">Step by step. Only the current level is visible. READ first, then answer the three questions for this publication. Advance only after all three are correct.</p>
  </header>
  <main>
    <div class="level-container">
'''

TAIL = '''    </div>
  </main>
  <footer>
    <div class="footer-line"></div>
    <p class="footer-text">Archive Master Exam • Sequential Path</p>
    <p class="footer-text"><a class="footer-home" href="./index.html">Return To Index</a> • One Level Visible • 3 Questions Per Publication</p>
  </footer>
  <script>
    const levels = document.querySelectorAll(".level");
    const currentLevelEl = document.getElementById("current-level");
    const completedEl = document.getElementById("completed");
    let current = 0;
    let completed = 0;
    function updateHud() { currentLevelEl.textContent = Math.min(current + 1, levels.length) + " / " + levels.length; completedEl.textContent = completed; }
    updateHud();
    function setupLevel(levelEl) {
      const qcards = levelEl.querySelectorAll('.exam-card');
      const advanceBtn = levelEl.querySelector('.advance-btn');
      let correctCount = 0;
      qcards.forEach((qcard) => {
        const options = qcard.querySelectorAll('.exam-option');
        const feedback = qcard.querySelector('.exam-feedback');
        options.forEach((option) => {
          option.addEventListener('click', () => {
            if (qcard.classList.contains('answered')) return;
            options.forEach((btn) => { btn.disabled = true; });
            qcard.classList.add('answered');
            const isCorrect = option.getAttribute('data-correct') === 'true';
            if (isCorrect) {
              option.classList.add('correct');
              feedback.textContent = "CORRECT.";
              if (!qcard.classList.contains('scored')) { qcard.classList.add('scored'); correctCount++; }
            } else {
              option.classList.add('wrong');
              feedback.textContent = "INCORRECT. Review the in-box reference and try again.";
              setTimeout(() => {
                options.forEach((btn) => { btn.disabled = false; btn.classList.remove('wrong'); });
                qcard.classList.remove('answered');
                feedback.textContent = "Awaiting response.";
              }, 1200);
              return;
            }
            if (correctCount === qcards.length) { advanceBtn.classList.add('visible'); }
          });
        });
      });
      advanceBtn.addEventListener('click', () => {
        if (correctCount < qcards.length) return;
        levelEl.classList.remove('active');
        completed++;
        updateHud();
        current++;
        if (levels[current]) { levels[current].classList.add('active'); levels[current].scrollIntoView({ behavior: 'smooth', block: 'start' }); }
        else { alert('Master Exam Complete - All publications verified.'); }
        updateHud();
      });
    }
    levels.forEach((levelEl) => { setupLevel(levelEl); });
  </script>
</body>
</html>'''

import html as H
def esc(t):
    return H.escape(t, quote=False)

out = [HEAD.replace('__TOTAL__', str(TOTAL))]
for idx, lvl in enumerate(levels):
    active = ' active' if idx == 0 else ''
    cards = []
    for qn, key in ((1, 'q1'), (2, 'q2'), (3, 'q3')):
        q = lvl[key]
        opts = []
        for i, (letter, text) in enumerate(q['opts']):
            correct = 'true' if i == q['correct'] else 'false'
            opts.append(
                f'<button class="exam-option" data-correct="{correct}">'
                f'<span class="option-index">{letter}.</span><span>{esc(text)}</span></button>'
            )
        cards.append(f'''                <div class="exam-card" data-q="{qn}">
                  <span class="exam-kicker">STEP {qn + 1} — QUESTION {qn} / 3</span>
                  <h3 class="exam-question">{esc(q['q'])}</h3>
                  <div class="exam-options">
                    {chr(10).join('                    ' + o for o in opts)}
                  </div>
                  <p class="exam-feedback">Awaiting response.</p>
                </div>''')
    out.append(f'''      <section class="level{active}" data-level="{idx}">
        <article class="level-card">
          <div class="level-ornament"></div>
          <div class="level-content">
            <header class="level-header">
              <div class="level-id-group">
                <div class="level-kicker"><span class="level-dot"></span><span>Level {idx + 1} of {TOTAL} • Step By Step</span></div>
                <h2 class="level-title">{esc(lvl['title'])}</h2>
              </div>
              <span class="level-status">STATUS: IN PROGRESS</span>
            </header>
            <div class="level-grid">
              <section class="step-section">
                <span class="step-kicker">STEP 1 — READ</span>
                <h3 class="step-title">Read The Publication</h3>
                <p class="step-text">Open and read the linked article carefully. The link is contained inside this game box.</p>
                <div class="ref-block">
                  <span class="ref-kicker">In-Box Reference</span>
                  <a class="word-link" href="./{esc(lvl['file'])}">{esc(lvl['file'])}</a>
                </div>
              </section>
              <aside class="exam-panel">
{chr(10).join(cards)}
                <button class="advance-btn">Complete Level &amp; Advance To Next</button>
              </aside>
            </div>
          </div>
        </article>
      </section>
''')
out.append(TAIL)

with open('/home/om/devblog/docs/gameReference.html', 'w') as f:
    f.write(''.join(out))
print('wrote', TOTAL, 'levels')
