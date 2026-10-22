#!/usr/bin/env python3
from pathlib import Path
import subprocess, sys, tempfile, os

def main():
    cwd = Path.cwd()
    node_prog = r"""
const fs = require('fs');
const html = fs.readFileSync('docs/index.html','utf8');
const m = html && html.match && html.match(/<script>([\s\S]*?)<\/script>/);
if(!m){ console.error('no inline script'); process.exit(2); }
const js = m[1];

function Elem(tag){
  this.tag = tag;
  this.parent = null;
  this.children = [];
  this.attrs = {};
  this.text = '';
  this.hidden = false;
}
Elem.prototype.getAttribute = function(name){ return this.attrs[name] || ''; };
Elem.prototype.setAttribute = function(name,value){ this.attrs[name] = value; };
Elem.prototype.appendChild = function(node){
  this.children.push(node);
  node.parent = this;
};
Elem.prototype.querySelector = function(sel){
  return this._select(sel);
};
Elem.prototype.querySelectorAll = function(sel){
  const out = [];
  this._collect(sel, out);
  return out;
};
Elem.prototype._select = function(sel, root){
  root = root || this;
  if(this._matches(sel, root)) return root;
  for(let i=0;i<root.children.length;i++){
    const r = root.children[i]._select(sel, root.children[i]);
    if(r) return r;
  }
  return null;
};
Elem.prototype._collect = function(sel, out, root){
  root = root || this;
  if(this._matches(sel, root)) out.push(root);
  for(let i=0;i<root.children.length;i++){
    root.children[i]._collect(sel, out, root.children[i]);
  }
};
Elem.prototype._matches = function(sel, node){
  if(!(node instanceof Elem)) return false;
  sel = String(sel).trim();
  if(sel === '.recent') return node.tag === 'section' && ('recent' === node.attrs.class);
  if(sel === '.recent-list') return node.tag === 'ol' && ('recent-list' === node.attrs.class);
  if(sel === '.recent-list li'){
    return node.tag === 'li' && node.parent && node.parent.tag === 'ol' && ('recent-list' === node.parent.attrs.class);
  }
  if(sel.indexOf('.recent-cat') === 0) return !!node.attrs.class && node.attrs.class.indexOf('recent-cat') !== -1;
  if(sel === '.links li'){
    return node.tag === 'li' && node.parent && node.parent.tag === 'ul' && ('links' === node.parent.attrs.class);
  }
  if(sel === '.cat') return node.tag === 'details' && ('cat' === node.attrs.class);
  if(sel === '.cat-head') return node.tag === 'summary' && ('cat-head' === node.attrs.class);
  if(sel === '.count') return node.tag === 'span' && ('count' === node.attrs.class);
  if(sel === '.name-tag') return node.tag === 'span' && ('name-tag' === node.attrs.class);
  if(sel === '.cat-head h2' || sel === 'h2') return node.tag === 'h2';
  if(sel === 'a') return node.tag === 'a';
  if(sel === 'time') return node.tag === 'time';
  if(sel === 'span') return node.tag === 'span';
  if(sel === '.status') return node.tag === 'p' && ('status' === node.attrs.class);
  if(sel === '.search input' || sel === 'input'){
    return node.tag === 'input' && node.parent && node.parent.tag === 'label' && ('search' === node.parent.attrs.class);
  }
  if(sel === '.toggle-all') return node.tag === 'button' && ('toggle-all' === node.attrs.class);
  if(sel === '.featured') return node.tag === 'div' && ('featured' === node.attrs.class);
  if(sel === '.featured .name-tag') return node.tag === 'span' && ('name-tag' === node.attrs.class);
  if(sel === '.featured-link') return node.tag === 'a' && ('featured-link' === node.attrs.class);
  if(sel === '.toolbar') return node.tag === 'div' && ('toolbar' === node.attrs.class);
  if(sel === '.ledger') return node.tag === 'p' && ('ledger' === node.attrs.class);
  if(sel.indexOf('.category') === 0) return node.tag === 'section' && ('category' === node.attrs.class);
  if(sel === '.sutra-lines li'){
    return node.tag === 'li' && node.parent && node.parent.tag === 'ul' && ('sutra-lines' === node.parent.attrs.class);
  }
  if(sel === '.dock-home') return node.tag === 'a' && ('dock-home' === node.attrs.class);
  if(sel === '.to-top') return node.tag === 'a' && ('to-top' === node.attrs.class);
  if(sel === '.dock a') return node.tag === 'a' && node.parent && node.parent.tag === 'nav' && ('dock' === node.parent.attrs.class);
  if(sel === '.dock-label') return node.tag === 'span' && ('dock-label' === node.attrs.class);
  if(sel.indexOf('.elsewhere') === 0) return node.tag === 'section' && ('elsewhere' === node.attrs.class);
  if(sel === '.panels') return node.tag === 'div' && ('panels' === node.attrs.class);
  if(sel === '.panel') return node.tag === 'div' && ('panel' === node.attrs.class);
  if(sel === '.sutra') return node.tag === 'section' && ('sutra' === node.attrs.class);
  if(sel === '.sutra-head') return node.tag === 'div' && ('sutra-head' === node.attrs.class);
  if(sel === '.archive') return node.tag === 'div' && ('archive' === node.attrs.class);
  if(sel === 'header h3' || sel === 'h3') return node.tag === 'h3';
  if(sel === 'header') return node.tag === 'header';
  if(sel === '.sutra-head h2') return node.tag === 'h2' && node.parent && node.parent.tag === 'div' && ('sutra-head' === node.parent.attrs.class);
  if(sel === '.sutra-head .count') return node.tag === 'span' && node.parent && node.parent.tag === 'div' && ('sutra-head' === node.parent.attrs.class);
  return false;
};

function Doc(){
  this.documentElement = new Elem('html');
  this.head = new Elem('head');
  this.body = new Elem('body');
  this.documentElement.appendChild(this.head);
  this.documentElement.appendChild(this.body);
  this.head.parent = this.documentElement;
  this.body.parent = this.documentElement;
}

function parse_fragment(html_text){
  const root = new Elem('root');
  const stack = [root];
  let idx = 0;
  const n = html_text.length;
  while(idx < n){
    const gt = html_text.indexOf('<', idx);
    if(gt === -1){
      const rest = html_text.slice(idx);
      if(rest && stack.length) stack[stack.length-1].text += rest;
      break;
    }
    if(gt > idx && stack.length) stack[stack.length-1].text += html_text.slice(idx, gt);
    if(gt > idx) idx = gt;
    if(html_text.indexOf('<!--', idx) === idx){
      const end = html_text.indexOf('-->', idx);
      if(end === -1) break;
      idx = end + 3;
      continue;
    }
    const m2 = html_text.slice(idx).match(/^<(\/?)([\w-]+)((?:\s+[^>]*?)?)\s*\/?>/);
    if(!m2){ idx += 1; continue; }
    const closing = m2[1] === '/';
    const tag = m2[2].toLowerCase();
    const attr_raw = m2[3];
    idx += m2[0].length;
    if(closing){
      if(stack.length && stack[stack.length-1].tag === tag) stack.pop();
      continue;
    }
    const el = new Elem(tag);
    el.parent = stack.length ? stack[stack.length-1] : null;
    const attr_m = attr_raw.match(/\s([\w][\w-]*)\s*=\s*"([^"]*)"/g);
    if(attr_m){
      for(let i=0;i<attr_m.length;i++){
        const am = attr_m[i].match(/([\w][\w-]*)\s*=\s*"([^"]*)"/);
        if(am) el.attrs[am[1].toLowerCase()] = am[2];
      }
    }
    const void_tags = new Set(['link','meta','img','br','hr','input','area','base','col','embed','source','track','wbr']);
    if(void_tags.has(tag)){
      if(stack.length) stack[stack.length-1].appendChild(el);
    } else {
      if(stack.length) stack[stack.length-1].appendChild(el);
      stack.push(el);
    }
  }
  return root;
}

const body_m = html.match(/<body[^>]*>([\s\S]*?)<\/body>/);
const body_inner = body_m ? body_m[1] : html;

const doc = new Doc();
const fragment = parse_fragment(body_inner);
doc.body.children = fragment.children;
for(let i=0;i<doc.body.children.length;i++){
  doc.body.children[i].parent = doc.body;
}
doc.body.querySelector = doc.body.querySelector.bind(doc.body);
doc.body.querySelectorAll = doc.body.querySelectorAll.bind(doc.body);

const localStorage = { getItem:()=>null, setItem:()=>{}, removeItem:()=>{} };
function isEventTarget(o){ return !!o && typeof o.addEventListener === 'function'; }
function ensureEvents(o){
  if(isEventTarget(o)) return;
  const listeners = {};
  o.addEventListener = function(ev, fn){
    if(!listeners[ev]) listeners[ev] = [];
    if(Array.isArray(listeners[ev]) && listeners[ev].indexOf(fn) === -1) listeners[ev].push(fn);
  };
  o.removeEventListener = function(ev, fn){
    if(!listeners[ev]) return;
    const i = listeners[ev].indexOf(fn);
    if(i !== -1) listeners[ev].splice(i,1);
  };
  o.dispatchEvent = function(ev){
    if(!listeners[ev.type] || !Array.isArray(listeners[ev.type])) return;
    listeners[ev.type].forEach(function(fn){ try{ fn.call(o, ev); }catch(e){} });
  };
}
function makeEventTarget(o){
  if(o.addEventListener) return;
  const listeners = {};
  o.addEventListener = function(ev, fn){
    if(!listeners[ev]) listeners[ev] = [];
    if(listeners[ev].indexOf(fn) === -1) listeners[ev].push(fn);
  };
  o.removeEventListener = function(ev, fn){
    if(!listeners[ev]) return;
    const i = listeners[ev].indexOf(fn);
    if(i !== -1) listeners[ev].splice(i,1);
  };
  o.dispatchEvent = function(ev){
    if(!listeners[ev.type]) return;
    listeners[ev.type].forEach(function(fn){ try{ fn.call(o, ev); }catch(e){} });
  };
}  function makeEventTargetShim(o){
    if(!o || typeof o !== 'object') return;
    const listeners = {};
    const roots = new Set([
      doc.documentElement,
      doc.head,
      doc.body,
      window
    ]);
    if(roots.has(o) || typeof o.addEventListener === 'function' || o.addEventListener) return;
    Object.defineProperty(o, 'addEventListener', {
      value: function(ev, fn){
        if(!listeners[ev]) listeners[ev] = [];
        if(listeners[ev].indexOf(fn) === -1) listeners[ev].push(fn);
      },
      writable: true,
      configurable: true
    });
    Object.defineProperty(o, 'removeEventListener', {
      value: function(ev, fn){
        if(!listeners[ev]) return;
        const i = listeners[ev].indexOf(fn);
        if(i !== -1) listeners[ev].splice(i,1);
      },
      writable: true,
      configurable: true
    });
    Object.defineProperty(o, 'dispatchEvent', {
      value: function(ev){
        if(!listeners[ev.type]) return;
        listeners[ev.type].forEach(function(fn){ try{ fn.call(o, ev); }catch(e){} });
      },
      writable: true,
      configurable: true
    });
    Object.defineProperty(o, 'open', { value: false, writable: true, configurable: true });
    Object.defineProperty(o, 'hidden', { value: false, writable: true, configurable: true });
    Object.defineProperty(o, 'value', { value: '', writable: true, configurable: true });
  }

const window = { document:doc, localStorage, fetch:undefined, JSON, Date, decodeURIComponent, encodeURIComponent, console };
global.window = window;
global.document = doc.body;
global.localStorage = localStorage;
global.fetch = undefined;
global.JSON = JSON;
global.Date = Date;
global.decodeURIComponent = decodeURIComponent;
global.encodeURIComponent = encodeURIComponent;
global.console = console;

const roots = new Set([
  window,
  doc.documentElement,
  doc.head,
  doc.body
]);
function walkAndShim(node){
  if(!node || typeof node !== 'object' || node instanceof String || node instanceof Number || node instanceof Boolean) return;
  if(roots.has(node) || typeof node.addEventListener === 'function') return;
  makeEventTargetShim(node);
  if(node.children){ Array.from(node.children).forEach(walkAndShim); }
}
walkAndShim(doc);
walkAndShim(doc.body);
walkAndShim(doc.documentElement);
walkAndShim(doc.head);
walkAndShim(window);
var navs = doc.body.querySelectorAll('nav, div.toolbar, label.search, input');
Array.from(navs).forEach(walkAndShim);
var sections = doc.body.querySelectorAll('.category');
Array.from(sections).forEach(function(s){
  walkAndShim(s);
  var details = s.querySelector('.cat');
  if(details) walkAndShim(details);
  var summary = s.querySelector('.cat-head');
  if(summary) walkAndShim(summary);
  var toggleAll = doc.body.querySelector('.toggle-all');
  if(toggleAll) walkAndShim(toggleAll);
});
[
  window,
  doc.body,
  doc.documentElement,
  doc.head
].forEach(walkAndShim);


try {
  eval(js);
} catch(e){
  console.error('runtime error', e && e.message ? e.message : String(e));
  process.exit(3);
}

const recentEl = doc.body.querySelector('.recent');
const listEl = doc.body.querySelector('.recent-list');
console.log('recent hidden:', Boolean(recentEl && recentEl.hidden));
console.log('recent items:', listEl ? listEl.children.length : 'no list');
if(listEl && listEl.children.length){
  Array.from(listEl.children).forEach(function(it){
    const a = it.querySelector('a');
    const cat = it.querySelector('.recent-cat');
    const tm = it.querySelector('time');
    console.log(
      (a ? a.textContent : '?'),
      '::',
      (cat ? cat.textContent : '?'),
      '::',
      (tm ? tm.textContent : '?')
    );
  });
}
"""
    try:
        with tempfile.TemporaryDirectory(prefix="run_index_recent_") as td:
            td = Path(td)
            repo = td / "repo"
            repo.symlink_to(cwd, target_is_directory=True)
            script_file = td / "run.js"
            script_file.write_text(node_prog, encoding="utf-8")
            proc = subprocess.run(
                ["node", str(script_file)],
                cwd=str(repo),
                text=True,
                capture_output=True,
                timeout=120,
            )
            sys.stdout.write(proc.stdout)
            sys.stderr.write(proc.stderr)
            return proc.returncode
    except FileNotFoundError:
        print("node not found; cannot run JS verification", file=sys.stderr)
        return 5
    except subprocess.TimeoutExpired:
        print("node timed out", file=sys.stderr)
        return 6

if __name__ == "__main__":
    sys.exit(main())
