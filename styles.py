"""Marginalia look and feel: colours, type, and the hero section."""
from __future__ import annotations

import textwrap

# Palette
#   paper      #F1F3FF  page background, a cool blue-white
#   ink        #14163A  text
#   ultramarine#3B36F5  brand colour, hero, primary buttons
#   lemon      #FFE14D  highlighter (used on cited text)
#   marker     #FF5C93  margin notes and page tags

CSS = """
<style>
:root {
  --paper: #F1F3FF; --ink: #14163A; --muted: #5B5F86; --line: #D9DCF2;
  --ultra: #3B36F5; --lemon: #FFE14D; --marker: #FF5C93;
  --display: 'Segoe UI', system-ui, sans-serif;
  --body: 'Segoe UI', system-ui, sans-serif;
}

.stApp { background: var(--paper); color: var(--ink); }
.stApp, .stMarkdown, p, label, input, textarea, button, li { font-family: var(--body); }
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
[data-testid="stAppDeployButton"] { display: none; }
.block-container { max-width: 1200px; padding-top: 1.4rem; padding-bottom: 3rem; }
[class*="st-key-chip"], .st-key-ask { width: 100% !important; }
[class*="st-key-chip"] button, .st-key-ask button { width: 100%; }

/* ---------- Hero ---------- */
.hero {
  display: grid; grid-template-columns: 1.08fr .92fr; gap: 2.6rem; align-items: center;
  background: var(--ultra); color: #fff; border-radius: 28px;
  padding: 3.4rem 3.4rem 3.2rem; margin-bottom: 2.4rem; overflow: hidden;
}
.hero-status {
  display: inline-flex; align-items: center; gap: .55rem; padding: .35rem .9rem .35rem .7rem;
  border: 1.5px solid rgba(255,255,255,.45); border-radius: 999px; font-size: .88rem; font-weight: 500;
}
.hero-status i { width: .6rem; height: .6rem; border-radius: 50%; background: var(--lemon); display: block; }
.hero-status.off i { background: var(--marker); }
.hero-title {
  font-family: var(--display); font-weight: 800; color: #fff;
  font-size: clamp(2.2rem, 4vw, 3.5rem); line-height: 1.02; letter-spacing: -0.03em; margin: 1.3rem 0 1.2rem;
}
.hero-sub { font-size: 1.12rem; line-height: 1.6; max-width: 34rem; color: rgba(255,255,255,.88); margin: 0 0 1.6rem; }
.hero-facts { display: flex; flex-wrap: wrap; gap: .6rem 1.6rem; font-size: .95rem; font-weight: 500; }
.hero-facts span::before {
  content: ""; display: inline-block; width: .55rem; height: .55rem; background: var(--lemon);
  margin-right: .55rem; transform: rotate(45deg);
}

/* The annotated page */
.sheet-wrap { position: relative; padding: 1rem 1.6rem 1.6rem 0; }
.sheet {
  background: #fff; color: var(--ink); border-radius: 4px; padding: 1.5rem 1.6rem 1.7rem;
  transform: rotate(2.2deg); box-shadow: 12px 12px 0 rgba(20,22,58,.38);
}
.sheet-head {
  display: flex; justify-content: space-between; font-family: var(--display); font-weight: 700;
  font-size: .95rem; padding-bottom: .7rem; margin-bottom: 1rem; border-bottom: 2px solid var(--ink);
}
.sheet-head span:last-child { color: var(--muted); font-weight: 500; }
.bars { margin: .3rem 0 .9rem; }
.bars i { display: block; height: .5rem; background: #E4E6F5; border-radius: 3px; margin-bottom: .55rem; }
.bars i:nth-child(1) { width: 96%; } .bars i:nth-child(2) { width: 88%; } .bars i:nth-child(3) { width: 93%; }
.sheet-text { font-size: 1.02rem; line-height: 1.75; margin: 0 0 .9rem; color: var(--ink); }
.hl {
  background: linear-gradient(var(--lemon), var(--lemon)) no-repeat left center;
  background-size: 0% 100%; animation: sweep 1.1s .5s ease-out forwards; padding: .05em 0;
}
.note {
  position: absolute; font-size: .86rem; line-height: 1.35; padding: .55rem .8rem; max-width: 12.5rem;
  border-radius: 3px; box-shadow: 4px 4px 0 rgba(20,22,58,.35); opacity: 0;
  animation: pop .45s ease-out forwards;
}
.note b { display: block; font-family: var(--display); font-size: .98rem; }
.note-a { right: -.2rem; bottom: 1.3rem; background: var(--marker); color: var(--ink); transform: rotate(3deg); animation-delay: 1.5s; }
.note-b { left: -1.4rem; bottom: 0; background: var(--paper); color: var(--ink); transform: rotate(-3deg); animation-delay: 2s; }
@keyframes sweep { to { background-size: 100% 100%; } }
@keyframes pop { from { opacity: 0; translate: 0 8px; } to { opacity: 1; translate: 0 0; } }
@media (prefers-reduced-motion: reduce) {
  .hl { animation: none; background-size: 100% 100%; }
  .note { animation: none; opacity: 1; }
}
@media (max-width: 860px) {
  .hero { grid-template-columns: 1fr; padding: 2rem 1.4rem 2.4rem; gap: 2rem; }
  .sheet-wrap { padding: .5rem .8rem 1.8rem .4rem; }
  .note-a { right: -.2rem; bottom: 3.2rem; } .note-b { left: -.2rem; }
}

/* ---------- Sections ---------- */
.sec { font-family: var(--display); font-weight: 700; font-size: 1.6rem; letter-spacing: -0.02em; margin: 0 0 .9rem; color: var(--ink); }
.side-title { font-family: var(--display); font-weight: 700; font-size: 1.25rem; margin-bottom: .4rem; }
.empty {
  border: 2px dashed var(--line); border-radius: 14px; padding: 2rem 1.6rem; color: var(--muted);
  font-size: 1.05rem; line-height: 1.6; background: rgba(255,255,255,.55);
}
.empty b { color: var(--ink); font-family: var(--display); font-size: 1.2rem; display: block; margin-bottom: .3rem; }

.stats { display: flex; margin: 1rem 0 0; background: #fff; border: 1.5px solid var(--line); border-radius: 12px; }
.stats div { flex: 1; padding: .8rem 1rem; }
.stats div + div { border-left: 1.5px solid var(--line); }
.stats b { display: block; font-family: var(--display); font-size: 1.7rem; line-height: 1.1; color: var(--ultra); }
.stats span { font-size: .85rem; color: var(--muted); }

/* ---------- Inputs ---------- */
[data-testid="stFileUploader"] section, [data-testid="stFileUploaderDropzone"] {
  border: 2px dashed var(--ultra); background: #fff; border-radius: 14px;
}
[data-testid="stTextArea"] textarea { background: #fff; border-radius: 10px; font-size: 1.05rem; line-height: 1.5; }
[data-testid="stBaseButton-secondary"], .stButton > button[kind="secondary"] {
  border-radius: 999px; border: 1.5px solid var(--line); background: #fff; color: var(--ink);
  font-size: .9rem; padding: .35rem .9rem; min-height: 0; white-space: normal;
}
[data-testid="stBaseButton-secondary"]:hover, .stButton > button[kind="secondary"]:hover {
  border-color: var(--ultra); color: var(--ultra);
}
[data-testid="stBaseButton-primary"], .stButton > button[kind="primary"] {
  border-radius: 10px; font-family: var(--display); font-weight: 700; font-size: 1.05rem; padding: .6rem 1.2rem;
}

/* ---------- Answers ---------- */
.asked { font-family: var(--display); font-weight: 700; font-size: 1.25rem; line-height: 1.3; margin-bottom: .6rem; }
.asked span {
  display: inline-block; background: var(--marker); color: var(--ink); font-family: var(--body); font-weight: 600;
  font-size: .78rem; padding: .12rem .5rem; border-radius: 3px; margin-right: .6rem; vertical-align: .15rem;
}
.margin-note { display: flex; gap: .8rem; padding: .7rem 0; border-top: 1px solid var(--line); font-size: .93rem; line-height: 1.55; }
.margin-note:first-child { border-top: 0; }
.margin-note .pg {
  flex: none; height: fit-content; background: var(--marker); color: var(--ink); font-weight: 600;
  font-size: .8rem; padding: .1rem .5rem; border-radius: 3px;
}
.margin-note .txt { color: var(--muted); }
mark { background: var(--lemon); color: var(--ink); padding: 0 .15em; border-radius: 2px; }
.hint { color: var(--muted); font-size: .88rem; margin: .2rem 0 .8rem; }
</style>
"""

_HERO = """
<div class="hero">
  <div>
    <div class="hero-status {status_class}"><i></i>{status_text}</div>
    <div class="hero-title">Ask your PDF. Get the page it came from.</div>
    <p class="hero-sub">Marginalia reads your document on your own computer, answers with a local Ollama model,
    and highlights the passages behind every answer.</p>
    <div class="hero-facts"><span>No cloud key</span><span>Your PDF stays here</span><span>Every answer cites a page</span></div>
  </div>
  <div class="sheet-wrap">
    <div class="sheet">
      <div class="sheet-head"><span>Facilities report 2019</span><span>Page 4</span></div>
      <div class="bars"><i></i><i></i><i></i></div>
      <p class="sheet-text">The east wing renovation <span class="hl">finished in March 2019, six weeks ahead of
      schedule</span>, and the final cost landed four percent under the approved budget.</p>
      <div class="bars"><i></i><i></i></div>
    </div>
    <div class="note note-a"><b>Page 4</b>Cited in the answer</div>
    <div class="note note-b">You asked: when did the renovation finish?</div>
  </div>
</div>
"""


def hero_html(ollama_online: bool) -> str:
    """Return the hero as one line of HTML so Markdown never treats it as a code block."""
    html = _HERO.format(
        status_class="" if ollama_online else "off",
        status_text="Ollama is running on this computer" if ollama_online
        else "Ollama is not running. Start it with: ollama serve",
    )
    return "".join(line.strip() + " " for line in textwrap.dedent(html).splitlines())
