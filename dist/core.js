/* SMRF prototype: deterministic surface accounting, no SWMM engine. */
(function(root){
'use strict';
const catchments=[
{id:'SC-01',name:'North residential',area:2.4,roof:.72,road:.30,parking:.18,green:.06,raster:48,outlet:'J1',slope:1.5,points:'65,95 290,75 310,290 80,300'},
{id:'SC-02',name:'Market quarter',area:3.1,roof:.93,road:.43,parking:.32,green:.10,raster:54,outlet:'J2',slope:1.2,points:'290,75 510,95 525,300 310,290'},
{id:'SC-03',name:'East residential',area:2.8,roof:.70,road:.34,parking:.27,green:.09,raster:45,outlet:'J3',slope:1.7,points:'510,95 735,125 710,325 525,300'},
{id:'SC-04',name:'Garden neighbourhood',area:3.4,roof:1.05,road:.46,parking:.12,green:.14,raster:46,outlet:'J4',slope:.9,points:'80,300 310,290 325,500 110,515'},
{id:'SC-05',name:'Civic centre',area:3.0,roof:.67,road:.44,parking:.40,green:.06,raster:49,outlet:'J5',slope:1.1,points:'310,290 525,300 540,520 325,500'},
{id:'SC-06',name:'Riverside district',area:3.3,roof:.79,road:.48,parking:.16,green:.12,raster:44,outlet:'J6',slope:.8,points:'525,300 710,325 680,535 540,520'}
];
const nodes=[
{id:'J1',x:190,y:174,invert:16.2,rim:18.1},
{id:'J2',x:396,y:173,invert:15.1,rim:17.2},
{id:'J3',x:603,y:202,invert:14.6,rim:16.7},
{id:'J4',x:212,y:384,invert:14.3,rim:16.4},
{id:'J5',x:430,y:390,invert:12.0,rim:14.0},
{id:'J6',x:622,y:410,invert:12.4,rim:14.7},
{id:'J7',x:448,y:492,invert:10.7,rim:12.8},
{id:'OF1',x:522,y:565,invert:9.9,rim:null,type:'outfall'}
];
const pipes=[
{id:'P1',from:'J1',to:'J4',length:160,diameter:300},
{id:'P2',from:'J2',to:'J5',length:175,diameter:375},
{id:'P3',from:'J3',to:'J6',length:165,diameter:300},
{id:'P4',from:'J4',to:'J5',length:135,diameter:450},
{id:'P5',from:'J6',to:'J5',length:150,diameter:450},
{id:'P6',from:'J5',to:'J7',length:100,diameter:600},
{id:'P7',from:'J7',to:'OF1',length:115,diameter:750}
];
function baseline(c){return c.roof+c.road+c.green;}
function defaults(){return {source:'baseline',streets:false,width:8,parking:false,green:false,terrain:false,alignment:false,manual:Object.fromEntries(catchments.map(c=>[c.id,100*baseline(c)/c.area]))};}
function accounting(c,s){
 if(s.source==='raster')return {roof:null,road:null,parking:null,correction:0,area:c.area*c.raster/100,pct:c.raster,method:'Complete demo classification'};
 if(s.source==='manual')return {roof:null,road:null,parking:null,correction:0,area:c.area*s.manual[c.id]/100,pct:s.manual[c.id],method:'User-entered fraction'};
 const road=c.road*(s.streets?s.width/6:1);
 const parking=s.parking?c.parking:0;
 const correction=s.green?c.green:0;
 const area=c.roof+road+c.green+parking-correction;
 return {roof:c.roof,road,parking,correction,area,pct:100*area/c.area,method:'Demo polygon area accounting'};
}
function totals(s){const area=catchments.reduce((a,c)=>a+c.area,0),imp=catchments.reduce((a,c)=>a+accounting(c,s).area,0),base=catchments.reduce((a,c)=>a+baseline(c),0);return {area,imp,base,pct:100*imp/area,basePct:100*base/area,deltaArea:imp-base,deltaPct:100*(imp-base)/area};}
function stages(s){
 const surface=s.source!=='baseline'||s.streets||s.parking||s.green;
 const graph=s.terrain||s.alignment;
 const any=surface||graph;
 const pipeline=[
 {id:'prepare',title:'Prepare geospatial inputs',active:any,owner:'HydroPrep / QGIS',text:any?'Check CRS, clipping, coverage and provenance; resolve overlapping surface classes.':'Baseline inputs retained; inspect their coverage and provenance.'},
 {id:'surface',title:'Recalculate imperviousness',active:surface||graph,owner:'SMRF surface adapter',text:surface?`Aggregate ${s.source==='raster'?'complete land-cover fractions':s.source==='manual'?'entered fractions':'deduplicated surface polygons'} for each subcatchment; write a proposed %Imperv table.`:graph?'Reaggregate surface inputs after catchment boundaries are regenerated.':'Keep baseline %Imperv; no surface refinement requested.'},
 {id:'graph',title:'Regenerate geometry & network',active:graph,owner:'SWMManywhere runner',text:graph?`${s.terrain?'Use a checked local DTM and redelineate catchments. ':''}${s.alignment?'Prepare a compatible starting graph from revised streets. ':''}Rebuild the affected graph stages and review outlet assignments.`:'Keep demo geometry for this comparison. Street width alone changes surface area; it does not move pipes.'},
 {id:'write',title:'Build a separate SWMM model',active:any,owner:'Runner / model writer',text:any?'Apply proposed inputs to a new model version; preserve the baseline .inp. Engine adapter is not connected in this prototype.':'Preserve baseline .inp; no new model requested.'},
 {id:'qa',title:'Validate & compare',active:any,owner:'Model Doctor / Scenario Lab',text:any?'Check surface area balance, graph connectivity, invert levels and outlets. Run the same rainfall before comparing flow, surcharge or flooding.':'Inspect the baseline graph. No hydraulic performance comparison is available.'}
 ];
 return [pipeline[0],pipeline[2],pipeline[1],pipeline[3],pipeline[4]];
}
function validate(raw){
 if(!raw||typeof raw!=='object'||Array.isArray(raw))throw new Error('Expected a refinement settings object.');
 if(!['baseline','raster','manual'].includes(raw.source))throw new Error('Unknown impervious-area source.');
 const clean=defaults();clean.source=raw.source;
 for(const k of ['streets','parking','green','terrain','alignment']){if(typeof raw[k]!=='boolean')throw new Error(`Invalid ${k} setting.`);clean[k]=raw[k];}
 if(typeof raw.width!=='number'||!Number.isFinite(raw.width)||raw.width<4||raw.width>10)throw new Error('Street width must be between 4 and 10 m.');clean.width=raw.width;
 if(!raw.manual||typeof raw.manual!=='object')throw new Error('Missing catchment fractions.');
 for(const c of catchments){const n=raw.manual[c.id];if(typeof n!=='number'||!Number.isFinite(n)||n<0||n>100)throw new Error(`${c.id}: imperviousness must be between 0 and 100%.`);clean.manual[c.id]=n;}
 return clean;
}
function diagnostics(s){
 const rows=catchments.map(c=>accounting(c,s));
 const inRange=rows.every(r=>r.pct>=0&&r.pct<=100);
 const validLinks=pipes.every(p=>nodes.some(n=>n.id===p.from)&&nodes.some(n=>n.id===p.to));
 const reachesOutfall=nodes.filter(n=>n.type!=='outfall').every(n=>{let id=n.id,seen=new Set();while(id!=='OF1'){if(seen.has(id))return false;seen.add(id);const p=pipes.find(p=>p.from===id);if(!p)return false;id=p.to;}return true;});
 return [{name:'Surface fractions',pass:inRange,detail:'All six fractions are within 0–100%.'},{name:'Link endpoints',pass:validLinks,detail:'Seven pipes connect to valid demo nodes.'},{name:'Outfall connectivity',pass:reachesOutfall,detail:'Every demo junction drains to OF1.'},{name:'Area balance',pass:rows.every((r,i)=>r.area<=catchments[i].area),detail:'Impervious area does not exceed gross catchment area.'}];
}
function plan(s,name='Current refinement') {s=validate(s);return {schema:'smrf-explorer-plan/v1',name:String(name).slice(0,60),dataset:'Fictional demo district — not Bellinge',created_at:new Date().toISOString(),engine_executed:false,geometry_regenerated:false,settings:s,summary:totals(s),catchments:catchments.map(c=>({id:c.id,area_ha:c.area,baseline_impervious_pct:100*baseline(c)/c.area,proposed_impervious_pct:accounting(c,s).pct,outlet:c.outlet})),workflow:stages(s),assumptions:['Schematic coordinates; areas and lengths are independent demo attributes.','Baseline = roof + 6 m road area + green false-positive area.','Parking increments and road areas are preclipped, nonoverlapping demo inputs.','Green correction removes only the known false-positive area, not every green polygon.','Complete land-cover and manual sources replace totals; polygon toggles are not added.','No SWMM simulation, calibration, performance improvement or real project data is represented.']};}
const api={catchments,nodes,pipes,baseline,defaults,accounting,totals,stages,validate,diagnostics,plan};
root.SMRF=api;if(typeof module!=='undefined'&&module.exports)module.exports=api;
})(typeof window!=='undefined'?window:globalThis);
