'use strict';
/* Sequential WCAG 2.1 A/AA automated samples; login is the only permitted POST.
 * Automated findings and incomplete rules are evidence, not full conformance.
 */
const fs=require('node:fs');
const path=require('node:path');
const {createRequire}=require('node:module');
const {createHash}=require('node:crypto');
const HOST='https://online-bookstore-10nn.onrender.com';
const TAGS=['wcag2a','wcag2aa','wcag21a','wcag21aa'];
const norm=value=>value.replace(/\s+/g,' ').trim();
function requireThat(condition,code){if(!condition)throw Error(code);}
function configFromEnv(env){
 requireThat(/^[a-f0-9]{40}$/i.test(env.QA_REPORTED_DEPLOYED_SHA||''),'FULL_DEPLOYED_SHA_REQUIRED');
 requireThat(/^QA\b/.test(env.QA_A11Y_BOOK_TITLE||''),'QA_BOOK_TITLE_REQUIRED');
 requireThat(/^[1-9]\d*$/.test(env.QA_A11Y_ORDER_ID||''),'BUYER_ORDER_ID_REQUIRED');
 requireThat(Boolean(env.QA_A11Y_OUTPUT),'OUTPUT_REQUIRED');
 requireThat(Boolean(env.QA_PERF_USERNAME)&&Boolean(env.QA_PERF_PASSWORD),'BUYER_SECRETS_REQUIRED');
 return {host:HOST,output:path.resolve(env.QA_A11Y_OUTPUT),sha:env.QA_REPORTED_DEPLOYED_SHA,
  harnessSha:env.GITHUB_SHA||null,title:env.QA_A11Y_BOOK_TITLE,orderId:Number(env.QA_A11Y_ORDER_ID),delay:1000,
  credentials:{buyer:{username:env.QA_PERF_USERNAME,password:env.QA_PERF_PASSWORD},
   seller:{username:env.QA_A11Y_SELLER_USERNAME,password:env.QA_A11Y_SELLER_PASSWORD},
   admin:{username:env.QA_A11Y_ADMIN_USERNAME,password:env.QA_A11Y_ADMIN_PASSWORD}}};
}
const readable=pathname=>/^\/(?:accounts\/(?:login|register|password-reset)\/|books\/|books\/\d+\/|books\/wishlist\/|books\/seller\/(?:listings|create)\/|books\/seller\/listings\/\d+\/edit\/|cart\/|cart\/checkout\/|orders\/|orders\/\d+\/|admin\/|admin\/login\/|admin\/jsi18n\/|admin\/books\/book\/|admin\/orders\/order\/|admin\/orders\/order\/\d+\/change\/|static\/.*|media\/.*)$/.test(pathname);
function safeTarget(target){
 const raw=JSON.stringify(target);
 const selectors=target.flat(Infinity).map(String).map(value=>value.replace(/\[[^\]]*\]/g,'[attribute-redacted]'));
 return {selector:selectors.join(' >>> ').replace(/[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}/g,'<email-redacted>').slice(0,400),
  selector_sha256:createHash('sha256').update(raw).digest('hex')};
}
function compactRules(rules){return rules.map(rule=>({id:rule.id,impact:rule.impact,tags:rule.tags,
 help:rule.help,help_url:rule.helpUrl,node_count:rule.nodes.length,
 nodes:rule.nodes.map(node=>({...safeTarget(node.target),check_ids:[...new Set([...node.any,...node.all,...node.none].map(check=>check.id))]}))}));}
async function run(config){
 const r=process.env.QA_NODE_MODULES?createRequire(path.join(path.resolve(process.env.QA_NODE_MODULES),'qa-accessibility.cjs')):require;
 const {chromium}=r('playwright'); const AxeBuilder=r('@axe-core/playwright').default;
 const result={status:'Running',started_at_utc:new Date().toISOString(),reported_deployed_sha:config.sha,harness_sha:config.harnessSha,
  deployment_attribution:'Operator supplied; no runtime build identifier',
  scope:'Sequential public, buyer, seller and admin sampled states; desktop 1366x768 and mobile 390x844',
  rules:{tags:TAGS,standard:'WCAG 2.1 A/AA automatically detectable checks'},
  limitations:['Automated samples do not establish full WCAG conformance; manual criteria and incomplete rules need review',
   'No server-side form error state is generated; no changes, checkout, emails or admin save actions',
   'Third-party assets blocked; site CSP is not bypassed; narrow viewport is not a browser-zoom test',
   'No screenshots, raw DOM, cookies, credentials or storage-state artifacts'],
  pages:[],role_results:[],errors:[],blocked_mutations:0};
 const outfile=path.join(config.output,'accessibility-results.json');
 fs.mkdirSync(config.output,{recursive:true});requireThat(!fs.existsSync(outfile),'OUTPUT_EXISTS_PRESERVE_RESULTS');
 const save=()=>{
  const serialized=JSON.stringify(result,null,2);
  for(const credentials of Object.values(config.credentials))if(credentials?.password&&serialized.includes(credentials.password))throw Error('SECRET_LEAK_GUARD');
  fs.writeFileSync(outfile+'.tmp',serialized+'\n');fs.renameSync(outfile+'.tmp',outfile);
 };
 const browser=await chromium.launch({headless:true});result.browser=browser.version();
 let stop=false;
 try{
  for(const role of ['public','buyer','seller','admin']){
   const credentials=config.credentials[role];
   if(role!=='public'&&(!credentials?.username||!credentials?.password)){
    result.role_results.push({role,status:'Not run',reason:'Required role secrets absent'});save();continue;
   }
   const context=await browser.newContext({viewport:{width:1366,height:768},serviceWorkers:'block'});
   context.on('response',response=>{
    if(new URL(response.url()).origin===config.host&&response.status()>=400){
     result.errors.push({role,code:'APPLICATION_HTTP_ERROR',status:response.status()});save();
    }
   });
   let loginPermit=null;
   await context.route('**/*',async route=>{
    const request=route.request(),url=new URL(request.url());
    if(['GET','HEAD'].includes(request.method())&&url.origin===config.host&&readable(url.pathname))return route.continue();
    if(request.method()==='POST'&&url.origin===config.host&&url.pathname===loginPermit&&request.isNavigationRequest()){
     loginPermit=null;return route.continue();
    }
    if(!['GET','HEAD'].includes(request.method())){result.blocked_mutations++;stop=true;}
    else if(request.isNavigationRequest()&&url.origin===config.host){stop=true;result.errors.push({role,code:'UNEXPECTED_NAVIGATION_BLOCKED'});}
    return route.abort();
   });
   const page=await context.newPage();page.setDefaultTimeout(15000);
   const go=async pathname=>{
    requireThat(!stop,'PREVIOUS_GUARD_FAILURE');
    const response=await page.goto(config.host+pathname,{waitUntil:'load',timeout:30000});
    requireThat(response?.status()===200&&new URL(page.url()).pathname===pathname.split('?')[0],'UNEXPECTED_HTTP_OR_REDIRECT');
   };
   let roleRow={role,status:'Running'};result.role_results.push(roleRow);
   try{
    if(role!=='public'){
     const admin=role==='admin';await go(admin?'/admin/login/?next=/admin/':'/accounts/login/');
     await page.locator(admin?'#id_username':'#username').fill(credentials.username);
     await page.locator(admin?'#id_password':'#password').fill(credentials.password);
     loginPermit=admin?'/admin/login/':'/accounts/login/';
     await Promise.all([page.waitForNavigation({waitUntil:'load',timeout:30000}),page.locator(admin?'input[type="submit"]':'button[type="submit"]').filter({visible:true}).first().click()]);
     if(admin){requireThat(new URL(page.url()).pathname==='/admin/'&&await page.locator('#logout-form').count()===1,'ADMIN_LOGIN_FAILED_NO_RETRY');}
     else requireThat(new URL(page.url()).pathname==='/books/'&&norm(await page.locator('.nav-user').innerText())===`Signed in as ${credentials.username}`,'LOGIN_FAILED_NO_RETRY');
    }
    let pages=[];
    if(role==='public')pages=[['login','/accounts/login/'],['registration','/accounts/register/'],['reset-request','/accounts/password-reset/'],['catalogue','/books/']];
    if(role==='buyer')pages=[['cart','/cart/'],['checkout','/cart/checkout/'],['order-history','/orders/'],['order-detail',`/orders/${config.orderId}/`],['wishlist','/books/wishlist/']];
    if(role==='seller')pages=[['seller-listings','/books/seller/listings/'],['seller-create','/books/seller/create/']];
    if(role==='admin')pages=[['admin-index','/admin/'],['admin-books','/admin/books/book/'],['admin-orders','/admin/orders/order/'],['admin-order-detail',`/admin/orders/order/${config.orderId}/change/`]];
    if(role==='public'){
     await go('/books/');
     const links=page.getByRole('link',{name:config.title,exact:true});
     requireThat(await links.count()>=1,'QA_BOOK_NOT_VISIBLE');
     const href=await links.first().getAttribute('href');requireThat(/^\/books\/[1-9]\d*\/$/.test(href||''),'INVALID_BOOK_DETAIL_LINK');
     pages.push(['book-detail',href]);
    }
    if(role==='seller'){
     await go('/books/seller/listings/');
     requireThat(await page.getByRole('heading',{name:'My Book Listings',exact:true}).count()===1,'SELLER_ROLE_OR_PAGE_MISMATCH');
     const edit=page.getByRole('link',{name:'Edit Listing',exact:true});
     if(await edit.count()){
      const href=await edit.first().getAttribute('href');requireThat(/^\/books\/seller\/listings\/[1-9]\d*\/edit\/$/.test(href||''),'INVALID_SELLER_EDIT_LINK');
      pages.push(['seller-edit',href]);
     }else result.errors.push({role,code:'SELLER_EDIT_NOT_RUN_NO_OWNED_LISTING'});
    }
    for(const [name,pathname]of pages){
     for(const viewport of [{width:1366,height:768},{width:390,height:844}]){
      const record={role,name,path:pathname,viewport,started_at_utc:new Date().toISOString(),status:'Running'};
      result.pages.push(record);save();
      try{
       await page.setViewportSize(viewport);await go(pathname);
       if(role==='buyer'){
        requireThat(norm(await page.locator('.nav-user').innerText())===`Signed in as ${credentials.username}`,'BUYER_IDENTITY_MISMATCH');
        if(name==='checkout')requireThat(await page.getByRole('button',{name:'Place Order (Test Mode)',exact:true}).count()===1,'NONEMPTY_MOCK_CHECKOUT_REQUIRED');
       }
       await page.evaluate(()=>document.fonts.ready);
       const axe=await new AxeBuilder({page}).withTags(TAGS).analyze();
       result.axe_version=axe.testEngine.version;
       record.violations=compactRules(axe.violations);record.incomplete=compactRules(axe.incomplete);
       record.passed_rule_count=axe.passes.length;record.inapplicable_rule_count=axe.inapplicable.length;
       record.layout=await page.evaluate(()=>({viewport_width:innerWidth,document_width:document.documentElement.scrollWidth,
        horizontal_overflow:document.documentElement.scrollWidth>innerWidth+1}));
       record.status=record.violations.length?'Violations found':'No automatically detected tagged violations';
      }catch(error){record.status='Not completed';record.error_code=/^[A-Z0-9_]+$/.test(error.message)?error.message:'SCAN_OR_NAVIGATION_FAILED';}
      record.finished_at_utc=new Date().toISOString();save();await page.waitForTimeout(config.delay);
     }
    }
    roleRow.status=result.pages.some(p=>p.role===role&&p.status==='Not completed')?'Incomplete scans':'Scanned';
   }catch(error){roleRow.status='Not completed';roleRow.error_code=/^[A-Z0-9_]+$/.test(error.message)?error.message:'ROLE_PREPARATION_FAILED';}
   finally{await context.close();save();}
   if(stop)break;
  }
  const violationCount=result.pages.reduce((n,p)=>n+(p.violations?.length||0),0);
  const incompleteCount=result.pages.reduce((n,p)=>n+(p.incomplete?.length||0),0);
  const missing=result.role_results.filter(row=>row.status!=='Scanned').length;
  result.summary={page_states_scanned:result.pages.filter(p=>p.status!=='Not completed').length,
   expected_page_states:34,violation_rule_occurrences:violationCount,incomplete_rule_occurrences:incompleteCount,
   roles_missing_or_incomplete:missing,scan_failures:result.pages.filter(p=>p.status==='Not completed').length,
   horizontal_overflow_samples:result.pages.filter(p=>p.layout?.horizontal_overflow).length};
  result.status=result.errors.length||missing||result.blocked_mutations||result.summary.scan_failures||result.pages.length!==34
   ?'Incomplete automated coverage':violationCount?'Automated accessibility violations found':'Automated samples complete; manual review still required';
 }finally{
  await browser.close();result.finished_at_utc=new Date().toISOString();
  const serialized=JSON.stringify(result);
  for(const credentials of Object.values(config.credentials))if(credentials?.password&&serialized.includes(credentials.password))throw Error('SECRET_LEAK_GUARD');
  save();
 }
 return result;
}
module.exports={run,configFromEnv,readable,safeTarget};
if(require.main===module)Promise.resolve().then(()=>run(configFromEnv(process.env))).then(result=>{
 console.log(JSON.stringify({status:result.status,summary:result.summary,role_results:result.role_results}));
 process.exitCode=result.status==='Automated samples complete; manual review still required'?0:1;
}).catch(()=>{console.error('Accessibility startup failed; check inputs/tooling and preserve existing evidence. No sensitive diagnostic text published.');process.exitCode=1;});
