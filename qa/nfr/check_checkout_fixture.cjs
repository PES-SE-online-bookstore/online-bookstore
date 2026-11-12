/* Local synthetic server only. Exercises actual browser code, not Render. */
'use strict';
const assert = require('node:assert/strict');
const http = require('node:http');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {run,productionConfig,p90} = require('./checkout_performance.cjs');
const password = 'LOCAL_FIXTURE_PRIVATE_PASSWORD';
const address = '<strong>QA Performance Buyer</strong><br>1 QA Test Street<br>Bengaluru, Karnataka 560001<br>India<br>Phone: 0000000000';
const detail = fields => Object.entries(fields).map(([key,value]) => `<div class="detail-item"><span class="detail-label">${key}</span><span class="detail-value">${value}</span></div>`).join('');
const nav = '<span class="nav-user">Signed in as qa_perf_fixture</span>';
let mode = 'pass', orders = 0, checkoutPosts = 0, loginPosts = 0, forbiddenCalls = 0;
let summaryFile;
const server = http.createServer(async (request,response) => {
  let body = '';
  for await (const chunk of request) body += chunk;
  response.setHeader('Content-Type','text/html; charset=utf-8');
  response.setHeader('Set-Cookie','fixture_private_cookie=NEVER_PUBLISH');
  const url = request.url;
  if (request.method === 'POST' && url === '/accounts/login/') {
    loginPosts++;
    assert(body.includes('password='+password));
    response.writeHead(302,{Location:'/books/'}); response.end(); return;
  }
  if (url === '/accounts/login/') { response.end('<h1>Login</h1><form method="post"><input id="username" name="username"><input id="password" name="password" type="password"><button>Login</button></form>'); return; }
  if (url === '/books/') { response.end(nav+'<h1>Book Catalogue</h1>'); return; }
  if (url === '/cart/checkout/' && request.method === 'POST') {
    checkoutPosts++; orders++;
    if (mode === 'stop-after-post') {
      const state = JSON.parse(fs.readFileSync(summaryFile)); state.status = 'Stopped';
      fs.writeFileSync(summaryFile,JSON.stringify(state));
    }
    if (mode === '503') { response.writeHead(503); response.end('Private failure content'); return; }
    const id = mode === 'duplicate' ? 1 : orders;
    response.end(nav+`<section aria-labelledby="checkout-result-heading"><h2>Checkout Submitted</h2>
      Payment status: Pending Order total: ₹1.00 No real money was charged. Your cart has been preserved.
      <a href="/orders/${id}/">View Order Details</a></section>`); return;
  }
  if (url === '/cart/checkout/') {
    const title = mode === 'wrong-cart' ? 'Unexpected Book' : 'QA Fixture Book';
    response.end(nav+`<h1>Checkout</h1><div class="cart-item"><strong>${title}</strong><p>Quantity: 1</p><span>₹1.00</span></div>
      <p class="total">Total: ₹1.00</p><form method="post"><input type="radio" name="address_id" id="address-1" value="1"><label for="address-1">${address}</label>
      <input type="checkbox" id="use_new_address"><input type="radio" name="payment_method" value="TEST_CARD"><button>Place Order (Test Mode)</button></form>`); return;
  }
  if (/^\/orders\/\d+\/$/.test(url)) {
    const id = Number(url.split('/')[2]);
    response.end(nav+`<h1>Order #${id}</h1><section aria-labelledby="summary-heading">${detail({'Order Status':'Pending'})}</section>
      <section aria-labelledby="items-heading"><table><tbody><tr><td>QA Fixture Book</td><td>₹1.00</td><td>1</td><td>₹1.00</td></tr></tbody></table></section>
      <p class="total-row">Order Total: ₹${mode === 'wrong-total' ? '2.00' : '1.00'}</p>
      <section aria-labelledby="address-heading">${detail({Recipient:'QA Performance Buyer','Address Line 1':'1 QA Test Street',City:'Bengaluru',State:'Karnataka','Postal Code':'560001',Country:'India',Phone:'0000000000'})}</section>
      <section aria-labelledby="payment-heading">${detail({'Payment Method':'Test Card','Payment Status':'Pending','Payment Amount':'₹1.00','Transaction Reference':'TEST-LOCAL'})}</section>`); return;
  }
  forbiddenCalls++; response.writeHead(404); response.end();
});
const start = () => new Promise(resolve => server.listen(0,'127.0.0.1',resolve));
(async () => {
  assert.equal(p90([1,2,3,4,5,6,7,8,9,100]),9);
  const env = {QA_PERF_USERNAME:'qa_perf_fixture', QA_PERF_PASSWORD:password, QA_EXPECTED_BOOK:'QA Fixture Book',
    QA_EXPECTED_UNIT_PRICE:'1.00', QA_REPORTED_DEPLOYED_SHA:'a'.repeat(40), QA_LOAD_OUTPUT:'fixture',QA_PUBLIC_LOAD_WINDOW_CONFIRMED:'YES',QA_TARGET:'999'};
  const fixed = productionConfig(env);
  assert.equal(fixed.target,20); assert.equal(fixed.threshold,5000);
  assert.equal(fixed.host,'https://online-bookstore-10nn.onrender.com');
  assert.throws(()=>productionConfig({...env,QA_PERF_USERNAME:'administrator'}));
  assert.throws(()=>productionConfig({...env,QA_EXPECTED_UNIT_PRICE:'bad'}));
  await start();
  const temp = fs.mkdtempSync(path.join(os.tmpdir(),'qa-checkout-fixture-'));
  const report = {scope:'Localhost synthetic fixture only; no public-app requests or performance acceptance',checks:[]};
  try {
    for (const scenario of ['preflight','pass','wrong-cart','wrong-total','503','duplicate','inactive','stop-after-post','timing-failure']) {
      mode = scenario; orders = 0; checkoutPosts = 0; loginPosts = 0;
      const output = path.join(temp,scenario); fs.mkdirSync(output);
      summaryFile = path.join(output,'summary.json');
      fs.writeFileSync(summaryFile,JSON.stringify({status:scenario==='inactive'?'Stopped':'Running',profile_name:'checkout-normal-10',
        stages:[{users:10,current_actual_users:10,phase:'steady',steady_started_at_utc:new Date().toISOString(),steady_target_seconds:300}]}));
      const result = await run({...fixed,host:`http://127.0.0.1:${server.address().port}`,output,
        preflight:scenario==='preflight', target:scenario==='pass'?20:3,
        threshold:scenario==='timing-failure'?0:5000,firstDelay:0,interval:0,minimumRemaining:0});
      if (scenario==='preflight') { assert(result.status.startsWith('Passed')); assert.equal(checkoutPosts,0); }
      else if (scenario==='pass') { assert.equal(result.status,'Passed completed mock checkout sample',JSON.stringify(result.errors));
        assert.equal(result.samples.length,20); assert.equal(checkoutPosts,20); assert(result.samples.every(x=>x.correct)); }
      else { assert(result.status.startsWith('Stopped'),scenario); assert.equal(checkoutPosts,scenario==='timing-failure'?3:scenario==='duplicate'?2:['wrong-cart','inactive'].includes(scenario)?0:1); }
      assert.equal(loginPosts,scenario==='inactive'?0:1);
      const saved = fs.readFileSync(path.join(output,scenario==='preflight'?'checkout-preflight':'browser','results.json'),'utf8');
      assert(!saved.includes(password)); assert(!saved.includes('NEVER_PUBLISH')); assert(!saved.includes('1 QA Test Street'));
      report.checks.push({scenario,status:'Passed',synthetic_orders:checkoutPosts});
    }
    assert.equal(forbiddenCalls,0);
    // Existing output and stopped load must not permit a retry to create orders.
    report.checks.push({scenario:'fixed_host_and_count_invalid_account_sanitization_allowlist',status:'Passed'});
    console.log(JSON.stringify(report,null,2));
  } finally {
    await new Promise(resolve=>server.close(resolve));
    // Temporary fixture evidence contains synthetic data only; retain it for inspection.
    console.log('Local fixture evidence: '+temp);
  }
})().catch(error => { console.error(error.stack); server.close(); process.exitCode=1; });
