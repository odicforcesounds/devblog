# plan

Goal: remove "strange effects" that should not be present on otherwise static docs pages — especially
blanket-consent kind of animations (CSS color/movement effects and JS) that are not tied to a clear
page identity.

Targeted removals (only):
- independent "floating/flickering" ambient loops that look more decorative than page identity:
  - `animation: flicker ... infinite` anywhere it looks standalone and decorative
  - `animation: dragonFlow / tigerFlow ... infinite` in KaliLinux.html (these are the "monster flow" ones)
  - CSS marquee-style infinite scroll animations (`marquee` class with infinite `scrollX` / `marq` / `scroll`)
- remove the small JS loops / timers that are decorative only and clearly not interactive content:
  - requestAnimationFrame loops / setInterval loops that only do movement/confetti/particles and have no
    user-facing state worth keeping

Do NOT remove:
- embedded media iframes / embeds (Bandcamp, YouTube, VOD players, etc.)
- tab-switching / quiz / lesson / TOC / reading-progress / print logic that powers real page functionality
- gating / progression localStorage logic that the page describes itself as using
- legitimately-identity animations that the page seems to intend as branding (only remove if they look
  like blanket decorative bloat; if unsure, leave them)

Files currently in scope (from earlier greps):
- docs/KaliLinux.html
- docs/linuxDistroComparison.html
- docs/anarquism.html
- docs/EthicalMorals.html
- docs/communism.html
- docs/business.html
- docs/activism.html
- docs/survival.html
- docs/Security.html
- docs/SELinux.html
- docs/Chemistry.html
- docs/Voltage.html
- docs/OpenBSDServices.html
- docs/ExamePolicial.html
- docs/terroristasLegais.html
- docs/MusicQuest.html
- docs/fireJail.html
- docs/androidStudio.html
- docs/reactNative.html
- docs/Physics.html
- docs/OpenBSDTribute.html
- docs/ccna_ccnp.html
- docs/DebianSecurity.html
- docs/AndroidDevelopment.html
- docs/Military.html
- docs/rustLanguage.html
- docs/ArtOfCreation.html
- docs/index.html
- docs/gemini4You.html
- docs/howAIworks.html
- docs/improveNatoONU.html
- docs/improveMilitary.html
- docs/learnChess.html
- docs/consciencia.html
- docs/geoPolitical.html
- docs/wordGame.html
- docs/MusicAnimation.html
- docs/unhappy.html
- docs/oDragaoMacaco.html

Final scope to be confirmed by user before edits.

Verification:
- after edits, re-run the same grep for `flicker`/`dragonFlow`/`tigerFlow`/`marquee`/`animation:.*infinite`
  and for stray `<script>` that only does decorative motion.
- each touched file must still parse as HTML (tag balance check) and read cleanly.
