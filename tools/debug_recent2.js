#!/usr/bin/env node
const fs = require('fs');
const html = fs.readFileSync('docs/index.html', 'utf8');
const m = html && html.match && html.match(/<script>([\s\S]*?)<\/script>/);
if (!m) { console.error('no inline script'); process.exit(2); }
const js = m[1];

const debug = process.argv[2];

function Elem(tag){
  this.tag=tag; this.parent=null; this.children=[]; this.attrs={}; this.text=''; this.hidden=false;
}
Elem.prototype.getAttribute=function(n){ return this.attrs[n]||''; };
Elem.prototype.setAttribute=function(n,v){ this.attrs[n]=v; };
Elem.prototype.appendChild=function(n){ this.children.push(n); n.parent=this; };
Elem.prototype.querySelector=function(s){ return this._select(s); };
Elem.prototype.querySelectorAll=function(s){ const o=[]; this._collect(s,o); return o; };
Elem.prototype._select=function(s, root){ root=root||this; if(this._matches(s, root)) return root; for(let i=0;i<root.children.length;i++){ const r=root.children[i]._select(s, root.children[i]); if(r) return r; } return null; };
Elem.prototype._collect=function(sel, out, root){ root=root||this; if(this._matches(sel, root)) out.push(root); for(let i=0;i<root.children.length;i++){ root.children[i]._collect(sel, out, root.children[i]); } };
Elem.prototype._matches=function(sel, node){
  if(debug && !this.__matched){
    this.__matched = true;
    if(debug === 'verbose') console.log('MATCH candidate', node.tag, node.attrs ? Object.keys(node.attrs) : []);
    if(sel==='.recent') return node.tag==='section' && ('recent'===node.attrs.class);
    if(sel==='.recent-list') return node.tag==='ol' && ('recent-list'===node.attrs.class);
    if(sel==='.recent-list li') return node.tag==='li' && node.parent && node.parent.tag==='ol' && ('recent-list'===node.parent.attrs.class);
    if(sel.indexOf('.recent-cat')===0) return !!node.attrs.class && node.attrs.class.indexOf('recent-cat')!==-1;
    if(sel==='.links li') return node.tag==='li' && node.parent && node.parent.tag==='ul' && ('links'===node.parent.attrs.class);
    if(sel==='.cat') return node.tag==='details' && ('cat'===node.attrs.class);
    if(sel==='.cat-head') return node.tag==='summary' && ('cat-head'===node.attrs.class);
    if(sel==='.count') return node.tag==='span' && ('count'===node.attrs.class);
    if(sel==='.recent-cat') return !!node.attrs.class && node.attrs.class.indexOf('recent-cat')!==-1;
    if(sel.indexOf('.recent-cat')===0) return !!node.attrs.class && node.attrs.class.indexOf('recent-cat')!==-1;
    if(sel.indexOf('.links li')===0) return node.tag==='li' && node.parent && node.parent.tag==='ul' && ('links'===node.parent.attrs.class);
    return false;
  }
  if(!(node instanceof Elem)) return false;
  if(!node.attrs || typeof node.attrs !== 'object'){ node.attrs = {}; }
  sel=String(sel).trim();
  if(sel==='.recent') return node.tag==='section' && ('recent'===node.attrs.class);
  if(sel==='.recent-list') return node.tag==='ol' && ('recent-list'===node.attrs.class);
  if(sel==='.recent-list li') return node.tag==='li' && node.parent && node.parent.tag==='ol' && ('recent-list'===node.parent.attrs.class);
  if(sel.indexOf('.recent-cat')===0) return !!node.attrs.class && node.attrs.class.indexOf('recent-cat')!==-1;
  if(sel==='.links li') return node.tag==='li' && node.parent && node.parent.tag==='ul' && ('links'===node.parent.attrs.class);
  if(sel==='.cat') return node.tag==='details' && ('cat'===node.attrs.class);
  if(sel==='.cat-head') return node.tag==='summary' && ('cat-head'===node.attrs.class);
  if(sel==='.count') return node.tag==='span' && ('count'===node.attrs.class);
  if(sel==='.name-tag') return node.tag==='span' && ('name-tag'===node.attrs.class);
  if(sel==='.cat-head h2' || sel==='h2') return node.tag==='h2';
  if(sel==='a') return node.tag==='a';
  if(sel==='time') return node.tag==='time';
  if(sel==='span') return node.tag==='span';
  if(sel==='.status') return node.tag==='p' && ('status'===node.attrs.class);
  if(sel==='.search input' || sel==='input') return node.tag==='input' && node.parent && node.parent.tag==='label' && ('search'===node.parent.attrs.class);
  if(sel==='.toggle-all') return node.tag==='button' && ('toggle-all'===node.attrs.class);
  if(sel==='.featured') return node.tag==='div' && ('featured'===node.attrs.class);
  if(sel==='.featured .name-tag') return node.tag==='span' && ('name-tag'===node.attrs.class);
  if(sel==='.featured-link') return node.tag==='a' && ('featured-link'===node.attrs.class);
  if(sel==='.toolbar') return node.tag==='div' && ('toolbar'===node.attrs.class);
  if(sel==='.ledger') return node.tag==='p' && ('ledger'===node.attrs.class);
  if(sel.indexOf('.category')===0) return node.tag==='section' && ('category'===node.attrs.class);
  if(sel==='.sutra-lines li') return node.tag==='li' && node.parent && node.parent.tag==='ul' && ('sutra-lines'===node.parent.attrs.class);
  if(sel==='.dock-home') return node.tag==='a' && ('dock-home'===node.attrs.class);
  if(sel==='.to-top') return node.tag==='a' && ('to-top'===node.attrs.class);
  if(sel==='.dock a') return node.tag==='a' && node.parent && node.parent.tag==='nav' && ('dock'===node.parent.attrs.class);
  if(sel==='.dock-label') return node.tag==='span' && ('dock-label'===node.attrs.class);
  if(sel.indexOf('.elsewhere')===0) return node.tag==='section' && ('elsewhere'===node.attrs.class);
  if(sel==='.panels') return node.tag==='div' && ('panels'===node.attrs.class);
  if(sel==='.panel') return node.tag==='div' && ('panel'===node.attrs.class);
  if(sel==='.sutra') return node.tag==='section' && ('sutra'===node.attrs.class);
  if(sel==='.sutra-head') return node.tag==='div' && ('sutra-head'===node.attrs.class);
  if(sel==='.archive') return node.tag==='div' && ('archive'===node.attrs.class);
  if(sel==='header h3' || sel==='h3') return node.tag==='h3';
  if(sel==='header') return node.tag==='header';
  if(sel==='.sutra-head h2') return node.tag==='h2' && node.parent && node.parent.tag==='div' && ('sutra-head'===node.parent.attrs.class);
  if(sel==='.sutra-head .count') return node.tag==='span' && node.parent && node.parent.tag==='div' && ('sutra-head'===node.parent.attrs.class);
  return false;
};
function Doc(){ this.documentElement=new Elem('html'); this.head=new Elem('head'); this.body=new Elem('body'); this.documentElement.appendChild(this.head); this.documentElement.appendChild(this.body); this.head.parent=this.documentElement; this.body.parent=this.documentElement; }
function parse_fragment(html_text){
  const root=new Elem('root');
  const stack=[root];
  let idx=0;
  const n=html_text.length;
  while(idx<n){
    const gt=html_text.indexOf('<', idx);
    if(gt===-1){ const rest=html_text.slice(idx); if(rest && stack.length) stack[stack.length-1].text+=rest; break; }
    if(gt>idx && stack.length) stack[stack.length-1].text+=html_text.slice(idx, gt);
    if(gt>idx) idx=gt;
    if(html_text.indexOf('<!--', idx)===idx){ const end=html_text.indexOf('-->', idx); if(end===-1) break; idx=end+3; continue; }
    const m2=html_text.slice(idx).match(/^<(\/?)([\w-]+)((?:\s+[^>]*?)?)\s*\/?>/);
    if(!m2){ idx+=1; continue; }
    const closing=m2[1]==='/';
    const tag=m2[2].toLowerCase();
    const attr_raw=m2[3];
    idx+=m2[0].length;
    if(closing){ if(stack.length && stack[stack.length-1].tag===tag) stack.pop(); continue; }
    const el=new Elem(tag);
    el.parent=stack.length ? stack[stack.length-1] : null;
    const attr_m=attr_raw.match(/\s?([\w][\w-]*)\s*=\s*"([^"]*)"/g);
    if(attr_m){ for(let i=0;i<attr_m.length;i++){ const am=attr_m[i].match(/([\w][\w-]*)\s*=\s*"([^"]*)"/); if(am) el.attrs[am[1].toLowerCase()]=am[2]; } }
    const void_tags=new Set(['link','meta','img','br','hr','input','area','base','col','embed','source','track','wbr']);
    if(void_tags.has(tag)){ if(stack.length) stack[stack.length-1].appendChild(el); } else { if(stack.length) stack[stack.length-1].appendChild(el); stack.push(el); }
  }
  return root;
}
const body_m=html.match(/<body[^>]*>([\s\S]*?)<\/body>/);
const body_inner=body_m ? body_m[1] : html;
const doc=new Doc();
const fragment=parse_fragment(body_inner);
doc.body.children=fragment.children;
for(let i=0;i<doc.body.children.length;i++){ doc.body.children[i].parent=doc.body; }
doc.body.querySelector=doc.body.querySelector.bind(doc.body);
doc.body.querySelectorAll=doc.body.querySelectorAll.bind(doc.body);
const localStorage={ getItem:()=>null, setItem:()=>{}, removeItem:()=>{} };
const window={ document:doc, localStorage, fetch:undefined, JSON, Date, decodeURIComponent, encodeURIComponent, console };
global.window=window;
global.document=doc.body;
global.localStorage=localStorage;
global.JSON=JSON;
global.Date=Date;
global.decodeURIComponent=decodeURIComponent;
global.encodeURIComponent=encodeURIComponent;
global.console=console;
console.error=function(...a){ };
function initObservable(o){
  if(!o || typeof o.addEventListener==='function') return;
  const listeners={};
  Object.defineProperty(o,'addEventListener',{ value:function(ev,fn){ if(!listeners[ev]) listeners[ev]=[]; if(listeners[ev].indexOf(fn)===-1) listeners[ev].push(fn); }, writable:true, configurable:true });
  Object.defineProperty(o,'removeEventListener',{ value:function(ev,fn){ if(!listeners[ev]) return; const i=listeners[ev].indexOf(fn); if(i!==-1) listeners[ev].splice(i,1); }, writable:true, configurable:true });
  Object.defineProperty(o,'dispatchEvent',{ value:function(ev){ if(!listeners[ev.type]) return; listeners[ev.type].forEach(function(fn){ try{ fn.call(o,ev); }catch(e){} }); }, writable:true, configurable:true });
  Object.defineProperty(o,'open',{ value:false, writable:true, configurable:true });
  Object.defineProperty(o,'hidden',{ value:false, writable:true, configurable:true });
  Object.defineProperty(o,'value',{ value:'', writable:true, configurable:true });
}
initObservable(window);
initObservable(doc.body);
initObservable(doc.documentElement);
initObservable(doc.head);
initObservable(doc.body.querySelector('.search'));
initObservable(doc.body.querySelector('.search input'));
initObservable(doc.body.querySelector('.toggle-all'));
initObservable(doc.body.querySelector('label.search'));
initObservable(doc.body.querySelector('nav.dock'));
initObservable(doc.body.querySelector('a.to-top'));
initObservable(doc.body.querySelector('a.dock-home'));
var sections=doc.body.querySelectorAll('.category');
var sectionsWin=sections;
var itemsWin=[];
Array.from(sections).forEach(function(s){
  initObservable(s);
  var d=s.querySelector('.cat');
  if(d) initObservable(d);
  var links=s.querySelectorAll('.links li');
  sectionsWin.__items = sectionsWin.__items || [];
  sectionsWin.__items.push(...links);
});
Object.defineProperty(window,'location',{ value:{ hash:'' }, writable:true, configurable:true });
Object.defineProperty(window,'addEventListener',{ value:function(){}, writable:true, configurable:true });
Object.defineProperty(window,'removeEventListener',{ value:function(){}, writable:true, configurable:true });
Object.defineProperty(window,'dispatchEvent',{ value:function(){}, writable:true, configurable:true });
Object.defineProperty(window,'matchMedia',{ value:function(){ return { matches:false, addListener:function(){}, removeEventListener:function(){} }; }, writable:true, configurable:true });
Object.defineProperty(window,'customElements',{ value:{ define:function(){}, whenDefined:function(){ return Promise.resolve(); } }, writable:true, configurable:true });
Object.defineProperty(window,'getComputedStyle',{ value:function(){ return { getPropertyValue:function(){ return ''; } }; }, writable:true, configurable:true });
Object.defineProperty(window,'structuredClone',{ value:function(v){ return v; }, writable:true, configurable:true });
Object.defineProperty(window,'Text',{ value:String, writable:true, configurable:true });
Object.defineProperty(window,'HTMLElement',{ value:Object, writable:true, configurable:true });
Object.defineProperty(window,'Element',{ value:Object, writable:true, configurable:true });
Object.defineProperty(window,'Node',{ value:Object, writable:true, configurable:true });
Object.defineProperty(window,'Document',{ value:Object, writable:true, configurable:true });
Object.defineProperty(window,'DocumentFragment',{ value:Object, writable:true, configurable:true });
Object.defineProperty(window,'DOMTokenList',{ value:Object, writable:true, configurable:true });
Object.defineProperty(window,'DOMStringList',{ value:Object, writable:true, configurable:true });
Object.defineProperty(window,'NodeList',{ value:Object, writable:true, configurable:true });
Object.defineProperty(window,'HTMLCollection',{ value:Object, writable:true, configurable:true });
Object.defineProperty(String.prototype,'trim',{ value:String.prototype.trim, writable:true, configurable:true });
Object.defineProperty(String.prototype,'normalize',{ value:String.prototype.normalize, writable:true, configurable:true });
Object.defineProperty(String.prototype,'toLowerCase',{ value:String.prototype.toLowerCase, writable:true, configurable:true });
Object.defineProperty(String.prototype,'toUpperCase',{ value:String.prototype.toUpperCase, writable:true, configurable:true });
Object.defineProperty(String.prototype,'localeCompare',{ value:String.prototype.localeCompare, writable:true, configurable:true });
Object.defineProperty(String.prototype,'substring',{ value:String.prototype.substring, writable:true, configurable:true });
Object.defineProperty(String.prototype,'slice',{ value:String.prototype.slice, writable:true, configurable:true });
Object.defineProperty(String.prototype,'indexOf',{ value:String.prototype.indexOf, writable:true, configurable:true });
Object.defineProperty(String.prototype,'endsWith',{ value:String.prototype.endsWith, writable:true, configurable:true });
Object.defineProperty(String.prototype,'startsWith',{ value:String.prototype.startsWith, writable:true, configurable:true });
Object.defineProperty(Array.prototype,'slice',{ value:Array.prototype.slice, writable:true, configurable:true });
Object.defineProperty(Array.prototype,'forEach',{ value:Array.prototype.forEach, writable:true, configurable:true });
Object.defineProperty(Array.prototype,'indexOf',{ value:Array.prototype.indexOf, writable:true, configurable:true });
Object.defineProperty(Array.prototype,'every',{ value:Array.prototype.every, writable:true, configurable:true });
Object.defineProperty(Array.prototype,'some',{ value:Array.prototype.some, writable:true, configurable:true });
Object.defineProperty(Array.prototype,'map',{ value:Array.prototype.map, writable:true, configurable:true });
Object.defineProperty(Array.prototype,'reduce',{ value:Array.prototype.reduce, writable:true, configurable:true });
Object.defineProperty(Array.prototype,'find',{ value:Array.prototype.find, writable:true, configurable:true });
Object.defineProperty(Array.prototype,'findIndex',{ value:Array.prototype.findIndex, writable:true, configurable:true });
Object.defineProperty(Array.prototype,'includes',{ value:Array.prototype.includes, writable:true, configurable:true });
Object.defineProperty(Array.prototype,'flatMap',{ value:Array.prototype.flatMap, writable:true, configurable:true });
Object.defineProperty(Array.prototype,'filter',{ value:Array.prototype.filter, writable:true, configurable:true });
Object.defineProperty(Array.prototype,'concat',{ value:Array.prototype.concat, writable:true, configurable:true });
Object.defineProperty(Object.prototype,'hasOwnProperty',{ value:Object.prototype.hasOwnProperty, writable:true, configurable:true });
Object.defineProperty(Object.prototype,'toString',{ value:Object.prototype.toString, writable:true, configurable:true });
Object.defineProperty(Object.prototype,'toLocaleString',{ value:Object.prototype.toLocaleString, writable:true, configurable:true });
Object.defineProperty(Object.prototype,'valueOf',{ value:Object.prototype.valueOf, writable:true, configurable:true });
Object.defineProperty(Object.prototype,'isPrototypeOf',{ value:Object.prototype.isPrototypeOf, writable:true, configurable:true });
Object.defineProperty(Object.prototype,'propertyIsEnumerable',{ value:Object.prototype.propertyIsEnumerable, writable:true, configurable:true });
Object.defineProperty(Error.prototype,'toString',{ value:Error.prototype.toString, writable:true, configurable:true });
Object.defineProperty(Error.prototype,'toLocaleString',{ value:Error.prototype.toLocaleString, writable:true, configurable:true });
Object.defineProperty(Error.prototype,'valueOf',{ value:Error.prototype.valueOf, writable:true, configurable:true });
Object.defineProperty(Error.prototype,'message',{ value:'', writable:true, configurable:true });
Object.defineProperty(Error.prototype,'name',{ value:'Error', writable:true, configurable:true });
Object.defineProperty(Error,'captureStackTrace',{ value:function(){ }, writable:true, configurable:true });
Object.defineProperty(global,'setTimeout',{ value:setTimeout, writable:true, configurable:true });
Object.defineProperty(global,'clearTimeout',{ value:clearTimeout, writable:true, configurable:true });
Object.defineProperty(global,'setInterval',{ value:setInterval, writable:true, configurable:true });
Object.defineProperty(global,'clearInterval',{ value:clearInterval, writable:true, configurable:true });
Object.defineProperty(global,'queueMicrotask',{ value:queueMicrotask, writable:true, configurable:true });
function noop(){ }
function rtFrame(){ rtFrameScheduled=false; try{ cb(); }catch(e){ } }
function poll(cb){ if(rtFrameScheduled) return; rtFrameScheduled=true; global.setTimeout(rtFrame,0); }
var rtFrameScheduled=false;
Object.defineProperty(global,'requestAnimationFrame',{ value:poll, writable:true, configurable:true });
Object.defineProperty(global,'cancelAnimationFrame',{ value:noop, writable:true, configurable:true });

window.__probe = {
  itemsWinWithinStep: function(stepIdx){
    return sectionsWin.__items ? sectionsWin.__items.slice(0,80).map(function(item){ return { tag:item.tag, text: item.text ? String(item.text).slice(0,80) : '', href: (item.getAttribute&&item.getAttribute('href')) || '', firstChildTag: (item.children && item.children.length && item.children[0].tag) || '' }; }) : [];
  }
};

if(debug === 'verbose'){
  console.log('querying .recent directly');
  const recentRoot = doc.body.querySelector('.recent');
  console.log('querying .recent-list directly');
  const recentList = doc.body.querySelector('.recent-list');
  console.log('querying .recent-list li directly');
  const recentItems = doc.body.querySelectorAll('.recent-list li');
  console.log('.recent found', recentRoot && recentRoot.tag, recentRoot && recentRoot.attrs && recentRoot.attrs.class);
  console.log('.recent-list found', recentList && recentList.tag, recentList && recentList.attrs && recentList.attrs.class);
  console.log('.recent-list li count', recentItems.length);
  const names = doc.body.querySelectorAll('.recent-list li a');
  console.log('.recent-list li a count', names.length);
  const tbl = doc.body.querySelectorAll('.recent-list li');
  for(let i=0;i<tbl.length;i++){
    console.log('table', i, tbl[i] && tbl[i].tag, tbl[i] && tbl[i].attrs && Object.keys(tbl[i].attrs).join(','));
  }
  process.exit(0);
}

try {
  eval.call({}, js);
} catch(e){
  console.error('runtime error', e && e.message ? e.message : String(e));
  if(e && e.stack){ console.error(e.stack.split('\n').slice(0,10).join('\n')); }
  process.exit(3);
}
console.log(JSON.stringify({ ok:true }, null, 2));
