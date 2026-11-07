/* The games' account strip, score sync and level notes, with no backend yet.
 *
 * The two level games call window.GameAccount from their own scripts and fall
 * back to nothing when this file has not run. The five entry points are kept so
 * those calls stay harmless: an empty strip, no note form, a save that keeps
 * nothing, and a click that is never handled.
 *
 * Public API
 *   hud(lang)        account strip (empty)
 *   level(opts)      note form + notes, for a level closing screen (empty)
 *   save(info)       points/certificate sync (keeps nothing)
 *   afterRender()    fill the notes list after the game repaints (no-op)
 *   click(event)     delegated clicks; never handled
 */
function hud() { return ""; }

function level() { return ""; }

function save() {}

function afterRender() {}

function click() { return false; }

window.GameAccount = { hud: hud, level: level, save: save, afterRender: afterRender, click: click };
