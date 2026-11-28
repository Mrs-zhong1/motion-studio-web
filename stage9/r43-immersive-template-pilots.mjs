/**
 * R43 — immersive, template-specific interaction pilots.
 * Agency = live project index / scene-linked case navigation.
 * SaaS = inline workflow simulator / stateful product demo.
 * The exported page remains the canvas; no permanent editor rail is introduced.
 */
export const R43_PILOTS = Object.freeze({
  agency: { model: 'project-index', interaction: 'hover-and-select-case', layout: 'editorial-scene' },
  saas: { model: 'workflow-demo', interaction: 'step-through-product-state', layout: 'full-width-product-stage' }
});

export const r43CSS = String.raw`
/* R43 shared contract: a single canvas, controls live inside the scene. */
html[data-r43-template] body{overflow-x:hidden}
html[data-r43-template] .r43-scene-control{position:relative;z-index:20;display:flex;align-items:center;gap:10px;flex-wrap:wrap;width:min(100% - 48px,1240px);margin:0 auto;padding:18px 0;color:inherit}
html[data-r43-template] .r43-scene-control button{appearance:none;border:1px solid currentColor;background:transparent;color:inherit;padding:10px 14px;border-radius:999px;font:600 11px/1.2 ui-monospace,monospace;letter-spacing:.08em;cursor:pointer;transition:transform .25s,background .25s,color .25s}
html[data-r43-template] .r43-scene-control button:hover{transform:translateY(-2px)}
html[data-r43-template] .r43-scene-control button[aria-pressed="true"]{background:var(--r43-accent);color:var(--r43-ink);border-color:var(--r43-accent)}
html[data-r43-template] .r43-scene-control button:focus-visible{outline:3px solid var(--r43-accent);outline-offset:4px}
html[data-r43-template] .r43-scene-status{font:600 10px/1.4 ui-monospace,monospace;letter-spacing:.12em;opacity:.72;margin-left:auto}
html[data-r43-template] .r43-scene-control button:disabled{opacity:.45;cursor:not-allowed}
@media(prefers-reduced-motion:reduce){html[data-r43-template] .r43-scene-control button{transition:none}}
/* Creative Agency: one vivid art-directed stage, project index is part of the composition. */
html[data-r43-template="agency"]{--r43-accent:#d9ff67;--r43-ink:#111719;background:#111719;color:#f4f2e9}
html[data-r43-template="agency"] .r43-agency-index{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:8px;width:min(100% - 48px,1240px);margin:0 auto 7vh;padding:0;list-style:none}
html[data-r43-template="agency"] .r43-agency-index button{width:100%;min-height:100px;text-align:left;border-radius:2px;padding:16px;background:#202a2d;color:#f4f2e9;border:1px solid #ffffff22}
html[data-r43-template="agency"] .r43-agency-index button[aria-pressed="true"]{background:#d9ff67;color:#111719;transform:translateY(-5px)}
html[data-r43-template="agency"] .r43-agency-index small{display:block;font:600 9px ui-monospace,monospace;opacity:.7;margin-bottom:14px}
html[data-r43-template="agency"] .r43-agency-index strong{display:block;font-size:clamp(12px,1.2vw,18px);line-height:1.05;text-transform:uppercase}
html[data-r43-template="agency"] .r43-agency-intro{width:min(100% - 48px,1240px);margin:5vh auto 3vh;font:900 clamp(48px,10vw,150px)/.82 system-ui,sans-serif;letter-spacing:-.085em;text-transform:uppercase;max-width:1240px}
html[data-r43-template="agency"] .r43-agency-intro em{color:#d9ff67;font-style:normal}
html[data-r43-template="agency"] .page .section{isolation:isolate}
html[data-r43-template="agency"] .page .section .designed-chapter-heading{mix-blend-mode:normal;text-wrap:balance}
@media(max-width:760px){html[data-r43-template="agency"] .r43-agency-index{grid-template-columns:repeat(2,minmax(0,1fr));gap:6px}html[data-r43-template="agency"] .r43-agency-index button{min-height:78px;padding:12px}html[data-r43-template="agency"] .r43-agency-index li:last-child{grid-column:1/-1}}
/* SaaS: the feature demonstration is an inline, full-width workflow, not a dashboard side panel. */
html[data-r43-template="saas"]{--r43-accent:#a9f278;--r43-ink:#10251c;background:#f0f5ed;color:#173428}
html[data-r43-template="saas"] .r43-saas-shell{width:min(100% - 48px,1240px);margin:4vh auto 8vh;border:1px solid #b9cbbb;background:#e4eee3;border-radius:22px;overflow:hidden;box-shadow:0 25px 80px #244b391c}
html[data-r43-template="saas"] .r43-saas-top{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:18px 22px;border-bottom:1px solid #b9cbbb;font:700 10px ui-monospace,monospace;letter-spacing:.12em}
html[data-r43-template="saas"] .r43-saas-tabs{display:flex;gap:8px;flex-wrap:wrap;padding:16px 22px 0}
html[data-r43-template="saas"] .r43-saas-tabs button{border:1px solid #a8c0ac;border-radius:999px;padding:10px 15px;background:transparent;color:#173428;font:600 11px system-ui;cursor:pointer}
html[data-r43-template="saas"] .r43-saas-tabs button[aria-pressed="true"]{background:#173428;color:#f0f5ed;border-color:#173428}
html[data-r43-template="saas"] .r43-saas-workflow{display:grid;grid-template-columns:1fr 1.15fr;gap:clamp(18px,4vw,56px);padding:clamp(22px,5vw,64px);align-items:center;min-height:340px}
html[data-r43-template="saas"] .r43-saas-copy h2{font-size:clamp(30px,5vw,66px);line-height:.96;letter-spacing:-.06em;margin:0 0 18px}
html[data-r43-template="saas"] .r43-saas-copy p{max-width:38em;line-height:1.65;color:#476252}
html[data-r43-template="saas"] .r43-saas-preview{min-height:220px;border-radius:16px;background:#14291f;color:#eaf4e7;padding:22px;display:grid;align-content:start;gap:14px}
html[data-r43-template="saas"] .r43-saas-preview-bar{display:flex;gap:6px}
html[data-r43-template="saas"] .r43-saas-preview-header{display:flex;align-items:center;justify-content:space-between;gap:12px;padding-bottom:12px;border-bottom:1px solid #ffffff28}
html[data-r43-template="saas"] .r43-saas-preview-brand{font:800 10px ui-monospace,monospace;letter-spacing:.14em;color:#e7f5e5}
html[data-r43-template="saas"] .r43-saas-preview-status{font:700 9px ui-monospace,monospace;letter-spacing:.1em;color:#b4f47d}
html[data-r43-template="saas"] .r43-saas-preview-kpis{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}
html[data-r43-template="saas"] .r43-saas-kpi{display:grid;gap:6px;padding:11px 12px;border:1px solid #ffffff25;border-radius:9px;background:#ffffff0a}
html[data-r43-template="saas"] .r43-saas-kpi span{font:600 9px ui-monospace,monospace;color:#b8cfc0}
html[data-r43-template="saas"] .r43-saas-kpi strong{font:700 clamp(18px,2vw,25px)/1 system-ui,sans-serif;color:#f2f8ef}
html[data-r43-template="saas"] .r43-saas-preview-body{display:grid;grid-template-columns:minmax(0,1.4fr) minmax(150px,.8fr);gap:10px;min-height:0}
html[data-r43-template="saas"] .r43-saas-preview-list{display:grid;gap:8px;align-content:start}
html[data-r43-template="saas"] .r43-saas-preview-item{display:grid;gap:6px;padding:11px 12px;border:1px solid #ffffff24;border-radius:9px;background:#ffffff09}
html[data-r43-template="saas"] .r43-saas-preview-item-meta{display:flex;justify-content:space-between;align-items:center;gap:8px}
html[data-r43-template="saas"] .r43-saas-preview-source,.r43-saas-preview-item-detail,.r43-saas-preview-owner{font:600 9px/1.4 ui-monospace,monospace;color:#b8cfc0}
html[data-r43-template="saas"] .r43-saas-preview-tag{padding:3px 6px;border-radius:4px;background:#b4f47d20;color:#c8f4a5;font:800 8px ui-monospace,monospace;letter-spacing:.08em}
html[data-r43-template="saas"] .r43-saas-preview-title{font:700 12px/1.3 system-ui,sans-serif;color:#f2f8ef}
html[data-r43-template="saas"] .r43-saas-preview-item-detail{margin:0;color:#b8cfc0}
html[data-r43-template="saas"] .r43-saas-preview-owner{justify-self:start;padding:3px 7px;border:1px solid #ffffff25;border-radius:20px}
html[data-r43-template="saas"] .r43-saas-preview-side{display:flex;flex-direction:column;gap:10px;padding:15px;border:1px solid #ffffff2a;border-radius:10px;background:linear-gradient(145deg,#ffffff12,#ffffff04)}
html[data-r43-template="saas"] .r43-saas-preview-side-kicker{font:700 9px ui-monospace,monospace;letter-spacing:.12em;color:#b4f47d}
html[data-r43-template="saas"] .r43-saas-preview-side h3{margin:0;font:700 17px/1.15 system-ui,sans-serif;color:#f2f8ef}
html[data-r43-template="saas"] .r43-saas-preview-side p{margin:0;font:400 11px/1.55 system-ui,sans-serif;color:#b8cfc0}
html[data-r43-template="saas"] .r43-saas-preview-side-note{margin-top:auto;font:600 9px/1.45 ui-monospace,monospace;color:#e2efd9}
html[data-r43-template="saas"] .r43-saas-preview-footer{font:700 8px ui-monospace,monospace;letter-spacing:.1em;color:#9db9a4}

html[data-r43-template="saas"] .r43-saas-preview-bar i{width:7px;height:7px;border-radius:50%;background:#9fbea5}
html[data-r43-template="saas"] .r43-saas-preview-card{border:1px solid #ffffff25;border-radius:10px;padding:16px;background:#ffffff0c}
html[data-r43-template="saas"] .r43-saas-progress{height:5px;background:#ffffff24;border-radius:5px;overflow:hidden}
html[data-r43-template="saas"] .r43-saas-progress span{display:block;height:100%;width:var(--r43-progress,25%);background:#b4f47d;transition:width .35s}
html[data-r43-template="saas"] .r43-saas-cta{display:inline-flex;align-items:center;justify-content:center;margin-top:16px;padding:11px 16px;background:#173428;color:#f0f5ed;border:0;border-radius:999px;text-decoration:none;font-weight:700;font-size:12px;cursor:pointer}html[data-r43-template="saas"] .r43-saas-cta:focus-visible{outline:3px solid #173428;outline-offset:4px}
@media(max-width:760px){html[data-r43-template="saas"] .r43-saas-shell{width:calc(100% - 24px);border-radius:14px}html[data-r43-template="saas"] .r43-saas-workflow{grid-template-columns:1fr;padding:22px;min-height:0}html[data-r43-template="saas"] .r43-saas-preview{min-height:190px}}
`;

export const r43Runtime = String.raw`
(function(){
 const root=document.documentElement,kind=root.dataset.r43Template;
 if(!['agency','saas'].includes(kind)||root.dataset.r43PilotReady==='yes')return;
 root.dataset.r43PilotReady='yes';
 const page=document.querySelector('.page')||document.body;
 const sections=[...document.querySelectorAll('.page .section')];
 const text=(el,selector)=>el?.querySelector(selector)?.textContent?.trim()||'';
 const make=(tag,cls,content)=>{const el=document.createElement(tag);if(cls)el.className=cls;if(content!==undefined)el.textContent=content;return el};
 if(kind==='agency'){
   // Reuse the source template's own hero. R43 must not stack a second headline or duplicate nav/status copy.
   const index=make('ol','r43-agency-index');
   const labels=sections.map((s,i)=>text(s,'.designed-chapter-heading')||('Selected project '+String(i+1).padStart(2,'0')));
   const setActive=activeIndex=>index.querySelectorAll('button').forEach((b,i)=>b.setAttribute('aria-pressed',String(i===activeIndex)));
   sections.forEach((section,i)=>{
     const li=make('li'),button=make('button');button.type='button';button.setAttribute('aria-pressed',String(i===0));
     const small=make('small',null,'CASE / '+String(i+1).padStart(2,'0'));
     const strong=make('strong',null,labels[i]);button.append(small,strong);
     button.addEventListener('mouseenter',()=>setActive(i));
     button.addEventListener('focus',()=>setActive(i));
     button.addEventListener('click',()=>{setActive(i);section.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'})});
     li.append(button);index.append(li);
   });
   if(sections[0]) sections[0].after(index); else page.prepend(index);
   // Keep the project index truthful while users scroll, not only after a button click.
   if('IntersectionObserver' in window){
     const observer=new IntersectionObserver(entries=>{
       const current=entries.filter(entry=>entry.isIntersecting).sort((a,b)=>b.intersectionRatio-a.intersectionRatio)[0];
       if(current){const activeIndex=sections.indexOf(current.target);if(activeIndex>=0)setActive(activeIndex)}
     },{rootMargin:'-15% 0px -55% 0px',threshold:[0.1,0.25,0.5,0.75]});
     sections.forEach(section=>observer.observe(section));
   }
 } else {
   const shell=make('section','r43-saas-shell');shell.setAttribute('aria-label','Interactive product workflow demo');shell.dataset.r43SaasDemo='true';
   const top=make('div','r43-saas-top'),topBrand=make('span',null,'NORTHSTAR / PRODUCT WORKSPACE'),topStatus=make('span',null,'ILLUSTRATIVE DEMO DATA');top.append(topBrand,topStatus);
   const tabs=make('div','r43-saas-tabs');tabs.setAttribute('role','tablist');tabs.setAttribute('aria-label','Product workflow steps');
   const workflow=make('div','r43-saas-workflow'),copy=make('div','r43-saas-copy'),preview=make('div','r43-saas-preview');
   preview.id='r43-saas-preview';preview.setAttribute('aria-label','Illustrative product workspace; not connected to a live account');
   const title=make('h2'),desc=make('p'),cta=make('button','r43-saas-cta','CONTINUE TO SHAPE');cta.type='button';
   copy.append(title,desc,cta);
   const previewHeader=make('div','r43-saas-preview-header');
   previewHeader.append(make('strong','r43-saas-preview-brand','SIGNAL WORKSPACE'),make('span','r43-saas-preview-status','DEMO DATA'));
   const metrics=make('div','r43-saas-preview-kpis');
   const body=make('div','r43-saas-preview-body'),list=make('div','r43-saas-preview-list'),side=make('aside','r43-saas-preview-side');
   const progress=make('div','r43-saas-progress');progress.setAttribute('role','progressbar');progress.setAttribute('aria-label','Workflow progress');progress.setAttribute('aria-valuemin','0');progress.setAttribute('aria-valuemax','100');
   const fill=make('span');progress.append(fill);
   body.append(list,side);
   const footer=make('div','r43-saas-preview-footer','ILLUSTRATIVE WORKSPACE · SAMPLE DATA');
   preview.append(previewHeader,metrics,body,footer);workflow.append(copy,preview);
   const steps=[
    {name:'Capture',title:'Bring every signal into one place.',desc:'Collect customer requests, support themes and sales feedback while keeping every item connected to its source.',progress:33,
     metrics:[['Signals','24'],['Sources','06'],['High priority','03']],
     items:[
      {source:'CUSTOMER VOICE',tag:'HIGH',title:'Checkout friction on mobile',detail:'14 mentions · Last 7 days',owner:'PRODUCT'},
      {source:'SUPPORT INBOX',tag:'MEDIUM',title:'Saved views are hard to find',detail:'8 mentions · Last 7 days',owner:'DESIGN'},
      {source:'SALES CALLS',tag:'HIGH',title:'Need a shared approval trail',detail:'5 mentions · Last 14 days',owner:'OPERATIONS'}
     ],
     sideKicker:'SIGNAL SOURCES',sideTitle:'Keep the context.',sideCopy:'Customer voice, support and sales notes stay connected to the original request instead of becoming disconnected tasks.',sideNote:'24 signals grouped from 6 sample sources.'},
    {name:'Shape',title:'Turn raw input into clear work.',desc:'Group related signals, assign an owner and make priority, scope and the next action visible to the whole team.',progress:66,
     metrics:[['Work groups','08'],['Owners','04'],['Ready','06']],
     items:[
      {source:'PRIORITY / 01',tag:'P1',title:'Reduce checkout friction',detail:'Owner: Maya · Due: 12 Dec',owner:'MAYA'},
      {source:'PRIORITY / 02',tag:'P2',title:'Surface saved views',detail:'Owner: Leo · Due: 15 Dec',owner:'LEO'},
      {source:'PRIORITY / 03',tag:'P2',title:'Add approval activity log',detail:'Owner: Ana · Due: 18 Dec',owner:'ANA'}
     ],
     sideKicker:'DECISION QUEUE',sideTitle:'Make ownership clear.',sideCopy:'A small, ranked queue turns repeated feedback into work with an owner, a due date and a visible reason to act.',sideNote:'3 sample priorities have named owners.'},
    {name:'Deliver',title:'Move from decision to delivery.',desc:'Review the finished work, confirm release readiness and share a clear outcome with the people who raised the need.',progress:100,
     metrics:[['Released','05'],['Ready to share','02'],['Next up','01']],
     items:[
      {source:'RELEASE / 01',tag:'SHIPPED',title:'Checkout flow improvements',detail:'QA complete · 4 of 4 checks',owner:'LIVE'},
      {source:'RELEASE / 02',tag:'READY',title:'Saved views navigation',detail:'Release notes ready · 3 of 3 checks',owner:'LIVE'},
      {source:'NEXT / 03',tag:'NEXT',title:'Approval activity log',detail:'Queued for the next cycle · 2 checks',owner:'TEAM'}
     ],
     sideKicker:'RELEASE HEALTH',sideTitle:'Close the loop.',sideCopy:'The team can see what shipped, what is ready to share and which request is moving into the next cycle.',sideNote:'2 sample updates are ready to share.'}
   ];
   let active=0;
   function setStep(n){
     active=n;const step=steps[n];title.textContent=step.title;desc.textContent=step.desc;
     preview.dataset.step=step.name.toLowerCase();topStatus.textContent='DEMO DATA / '+String(n+1).padStart(2,'0')+' OF 03';
     metrics.replaceChildren(...step.metrics.map(([label,value])=>{const metric=make('div','r43-saas-kpi');metric.append(make('span',null,label),make('strong',null,value));return metric}));
     list.replaceChildren(...step.items.map(item=>{
       const row=make('article','r43-saas-preview-item');row.setAttribute('data-demo-item','true');
       const meta=make('div','r43-saas-preview-item-meta');meta.append(make('span','r43-saas-preview-source',item.source),make('span','r43-saas-preview-tag',item.tag));
       row.append(meta,make('strong','r43-saas-preview-title',item.title),make('p','r43-saas-preview-item-detail',item.detail),make('span','r43-saas-preview-owner',item.owner));
       return row;
     }));
     side.replaceChildren(make('span','r43-saas-preview-side-kicker',step.sideKicker),make('h3',null,step.sideTitle),make('p',null,step.sideCopy),progress,make('span','r43-saas-preview-side-note',step.sideNote));
     progress.setAttribute('aria-valuenow',String(step.progress));fill.style.width=step.progress+'%';
     footer.textContent='ILLUSTRATIVE WORKSPACE · SAMPLE DATA · NOT A LIVE ACCOUNT';
     tabs.querySelectorAll('button').forEach((button,i)=>{button.setAttribute('aria-pressed',String(i===n));button.setAttribute('aria-selected',String(i===n))});
     cta.textContent=n===2?'RESTART WORKFLOW':'CONTINUE TO '+steps[n+1].name.toUpperCase();cta.setAttribute('aria-label',cta.textContent);
   }
   steps.forEach((step,i)=>{const button=make('button',null,step.name);button.type='button';button.setAttribute('role','tab');button.setAttribute('aria-controls',preview.id);button.addEventListener('click',()=>setStep(i));tabs.append(button)});
   cta.addEventListener('click',()=>setStep(active===2?0:active+1));
   shell.append(top,tabs,workflow);const anchor=sections[0]||page.firstChild;if(anchor)anchor.before(shell);else page.append(shell);setStep(0);
 }
})();
`;

export function applyR43TemplatePilots(html){
 if(typeof html!=='string'||!html.includes('</head>')||!html.includes('</body>'))throw Error('R43 requires a complete exported HTML document');
 if(html.includes('id="r43-template-pilot-css"'))throw Error('R43 duplicate injection');
 if(!html.includes('function exportDocument('))throw Error('R43 exportDocument hook missing');
 const hook=`;(function(){const previous=exportDocument;exportDocument=function(){const result=previous();const id=project&&project.templateId;if(!['agency','saas'].includes(id))return result;const css=document.getElementById('r43-template-pilot-css').textContent;const runtime=document.getElementById('r43-template-pilot-runtime').textContent;const marked=result.replace('<html','<html data-r43-template="'+id+'"');return marked.replace('</head>','<style id="r43-export-css">'+css+'</style></head>').replace('</body>','<script id="r43-export-runtime">'+runtime+'<'+'/script></body>')}})();`;
 const apiAnchor='window.MotionStudioUnified={undo:';
 if(!html.includes(apiAnchor))throw Error('R43 public API insertion anchor missing');
 let source=html.replace(apiAnchor,hook+apiAnchor);
 const bodyClose=source.lastIndexOf('</body>');
 const headClose=source.indexOf('</head>');
 if(bodyClose<0||headClose<0)throw Error('R43 actual document closing tags missing');
 source=source.slice(0,bodyClose)+'<script type="text/plain" id="r43-template-pilot-runtime">'+r43Runtime+'</script>'+source.slice(bodyClose);
 return source.slice(0,headClose)+'<style id="r43-template-pilot-css">'+r43CSS+'</style>'+source.slice(headClose);
}
