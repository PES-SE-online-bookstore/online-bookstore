/* Sequential measurement browser; requires the monitored 10-VU steady stage. */
const fs=require('node:fs');
const path=require('node:path');
const {createRequire}=require('node:module');
const r=createRequire(path.join(process.env.QA_NODE_MODULES,'qa-browser.cjs'));
const {chromium}=r('playwright');
const root=path.resolve(process.env.QA_LOAD_OUTPUT||path.join(__dirname,'../Runs/LOAD-001'));
const diagnostic=process.argv.includes('--diagnostic');
const targetSamples=diagnostic?5:20;
const out=path.join(root,diagnostic?'diagnostic-browser':'browser');
fs.mkdirSync(out,{recursive:true});
const result={started_at_utc:new Date().toISOString(),scope:'One measurement browser during 10 active anonymous Locust VUs; total up to 11 active clients',
 measurement:'Navigation start to loadEventEnd, browser assets included; warm browser cache; initial navigation excluded',
 samples:[],errors:[],status:'Running'};
const save=()=>fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(result,null,2));
const state=()=>JSON.parse(fs.readFileSync(path.join(root,'summary.json'),'utf8'));
if(diagnostic)result.scope='Low-rate single-browser diagnostic after the load generator stopped; no normal-load acceptance claim';
const active=()=>{const s=state();if(diagnostic)return s.status!=='Running';const stage=s.stages.at(-1);return s.status==='Running'&&stage?.users===10&&stage.phase==='steady'&&!stage.abort_reason;};
const percentile=values=>values.slice().sort((a,b)=>a-b)[Math.ceil(values.length*.9)-1];
(async()=>{
 if(!active())throw Error('Required measurement conditions are not active; no requests sent');
 const browser=await chromium.launch({headless:true});
 result.browser=browser.version();
 const context=await browser.newContext({viewport:{width:1366,height:768},serviceWorkers:'block'});
 await context.route('**/*',route=>['GET','HEAD'].includes(route.request().method())?route.continue():route.abort());
 const page=await context.newPage();
 try {
  for(let index=0;index<=targetSamples;index++)for(const endpoint of ['/books/','/books/?q=QA']){
   if(!active())throw Error('Load stage stopped/changed; measurement stopped');
   const record={endpoint,index,phase:index===0?'warmup':'measured',started_at_utc:new Date().toISOString()};
   try{
    const response=await page.goto('https://online-bookstore-10nn.onrender.com'+endpoint,{waitUntil:'load',timeout:30000});
    const h1=await page.locator('h1').allTextContents();
    record.status=response.status();record.correct=response.status()===200&&new URL(page.url()).pathname==='/books/'&&h1.some(h=>h==='Book Catalogue');
    const timing=await page.evaluate(()=>{const n=performance.getEntriesByType('navigation')[0];return{load_ms:n.loadEventEnd-n.startTime,ttfb_ms:n.responseStart-n.startTime,dom_ms:n.domContentLoadedEventEnd-n.startTime};});
    Object.assign(record,timing);
    if(!record.correct)throw Error('Incorrect page/status');
   }catch(e){record.correct=false;record.error=e.message;result.errors.push({endpoint,index,message:e.message});}
   result.samples.push(record);save();
   if(!record.correct)throw Error('Navigation failure; stopped');
   await page.waitForTimeout(1000);
  }
  result.summaries=['/books/','/books/?q=QA'].map(endpoint=>{
   const values=result.samples.filter(v=>v.endpoint===endpoint&&v.phase==='measured'&&v.correct).map(v=>v.load_ms);
   return{endpoint,samples:values.length,p90_load_ms:percentile(values),max_load_ms:Math.max(...values),at_or_below_3000ms:values.filter(t=>t<=3000).length,
    sample_target_met:values.length===targetSamples&&values.filter(t=>t<=3000).length>=Math.ceil(targetSamples*.9)};
  });
  result.status=diagnostic?'Diagnostic complete; no normal-load acceptance claim':(result.summaries.every(s=>s.sample_target_met)?'Passed declared normal-load browser sample':'Failed browser timing target');
 }finally{await browser.close();result.finished_at_utc=new Date().toISOString();save();}
 console.log(JSON.stringify({status:result.status,summaries:result.summaries,errors:result.errors},null,2));
})().catch(e=>{result.status='Stopped';result.errors.push({message:e.message});result.finished_at_utc=new Date().toISOString();save();console.error(e.message);process.exitCode=1;});
