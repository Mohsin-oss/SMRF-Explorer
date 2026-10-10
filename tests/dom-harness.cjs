'use strict';
const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path'),C=require('../dist/core.js'),P=require('../dist/project.js');
const root=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(root,'dist/index.html'),'utf8');
function harness(storageSeed={},custom=false,initialHash=''){
 const byId=new Map(),elements=[],downloads=[],blobs=[],timers=[],storage=new Map(Object.entries(storageSeed));
 class Element{
  constructor(tag='div',attrs={}){this.tagName=tag.toUpperCase();this.attrs={...attrs};this.id=attrs.id||'';this.dataset={};for(const [k,v]of Object.entries(attrs))if(k.startsWith('data-'))this.dataset[k.slice(5).replace(/-([a-z])/g,(_,x)=>x.toUpperCase())]=v;this.value=attrs.value||'';this.checked='checked'in attrs;this.disabled='disabled'in attrs;this.hidden='hidden'in attrs;this.style={};this.textContent='';this.handlers={};this.classes=new Set((attrs.class||'').split(/\s+/).filter(Boolean));this.classList={toggle:(c,on)=>{if(on===undefined)on=!this.classes.has(c);on?this.classes.add(c):this.classes.delete(c);},contains:c=>this.classes.has(c)};this._html='';elements.push(this);if(this.id)byId.set(this.id,this);}
  set innerHTML(v){this._html=v;parse(v);}get innerHTML(){return this._html;}
  setAttribute(k,v){this.attrs[k]=String(v);}removeAttribute(k){delete this.attrs[k];}
  addEventListener(k,fn){(this.handlers[k]??=[]).push(fn);}async fire(k,extra={}){const e={target:this,preventDefault(){this.prevented=true;},...extra};for(const fn of this.handlers[k]||[])await fn(e);}
  closest(q){const attr=q.match(/^\[([^\]]+)\]$/)?.[1];return attr&&attr in this.attrs?this:null;}
  appendChild(){}remove(){}click(){if(this.download)downloads.push(this);return this.fire('click');}focus(){this.focused=true;}showModal(){this.open=true;}close(){this.open=false;}
 }
 function parse(src){const re=/<([a-zA-Z][\w:-]*)\b([^>]*)>/g;let m;const found=[];while((m=re.exec(src))){const attrs={};const ar=/([\w:-]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+)))?/g;let a;while((a=ar.exec(m[2])))attrs[a[1]]=a[2]??a[3]??a[4]??'';found.push(new Element(m[1],attrs));}return found;}
 const staticElements=parse(html),roads=[];const streetFragment=html.match(/<g id="street-layer">([\s\S]*?)<\/g>/)[1];for(const m of streetFragment.matchAll(/<path\b([^>]*)>/g))roads.push(new Element('path'));
 const doc={getElementById:id=>byId.get(id)||null,querySelectorAll:q=>q==='#street-layer path'?roads:staticElements.filter(el=>q.match(/^\[([^\]]+)\]$/)?.[1]in el.attrs),createElement:t=>new Element(t),body:new Element('body')};
 const win={SMRF:C,SMRFProject:P,crypto:{randomUUID:()=>String(savedIds++),subtle:require('node:crypto').webcrypto.subtle},addEventListener(){}};let savedIds=1;
 const ctx={window:win,document:doc,localStorage:{getItem:k=>storage.get(k)||null,setItem:(k,v)=>storage.set(k,v)},history:{replaceState(){}},location:{hash:initialHash},Blob,URL:{createObjectURL:blob=>{blobs.push(blob);return 'blob:test-'+(blobs.length-1)},revokeObjectURL(){}},setTimeout:fn=>{timers.push(fn);return timers.length;},clearTimeout(){},TextEncoder,console,Date,Math,JSON,Set};
 vm.runInNewContext(fs.readFileSync(path.join(root,'dist/app.js'),'utf8'),ctx,{filename:'app.js'});
 if(custom)vm.runInNewContext(fs.readFileSync(path.join(root,'dist/project-ui.js'),'utf8'),ctx,{filename:'project-ui.js'});
 return {get:id=>byId.get(id),select:(key,val)=>{const el=byId.get(key);el.value=val;return el.fire('change');},toggle:async(key,on)=>{const el=byId.get(key);el.checked=on;await el.fire('change');},click:id=>byId.get(id).fire('click'),nav:key=>staticElements.find(el=>el.dataset.view===key),storage,downloads,blobs,Element};
}

module.exports={harness};
