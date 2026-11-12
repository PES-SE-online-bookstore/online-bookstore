/* Completed mock checkout timing. CLI host, sample count and gates are fixed.
 * Never saves credentials, cookies, address text, screenshots or raw pages.
 */
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const {createRequire} = require('node:module');
const {performance: clock} = require('node:perf_hooks');
const HOST = 'https://online-bookstore-10nn.onrender.com';
const p90 = values => [...values].sort((a,b) => a-b)[Math.ceil(values.length*.9)-1];
const norm = value => value.replace(/\s+/g, ' ').trim();
function requireThat(condition, code) { if (!condition) throw new Error(code); }
function money(value) {
  const match = value.match(/^(?:₹\s*)?(\d+)\.(\d{2})$/);
  requireThat(match, 'INVALID_MONEY_FORMAT');
  const cents = Number(match[1])*100 + Number(match[2]);
  requireThat(Number.isSafeInteger(cents), 'INVALID_MONEY_RANGE');
  return cents;
}
function productionConfig(env) {
  requireThat(/^qa_perf_[a-z0-9_]+$/.test(env.QA_PERF_USERNAME || ''), 'DEDICATED_QA_PERF_BUYER_REQUIRED');
  requireThat(Boolean(env.QA_PERF_PASSWORD), 'PASSWORD_SECRET_MISSING');
  requireThat(/^QA\b/.test(env.QA_EXPECTED_BOOK || ''), 'QA_BOOK_TITLE_REQUIRED');
  requireThat(money(env.QA_EXPECTED_UNIT_PRICE || '') > 0, 'POSITIVE_UNIT_PRICE_REQUIRED');
  requireThat(/^[a-f0-9]{40}$/i.test(env.QA_REPORTED_DEPLOYED_SHA || ''), 'FULL_DEPLOYED_SHA_REQUIRED');
  requireThat(env.QA_PUBLIC_LOAD_WINDOW_CONFIRMED === 'YES', 'TEST_WINDOW_REQUIRED');
  requireThat(Boolean(env.QA_LOAD_OUTPUT), 'OUTPUT_DIRECTORY_REQUIRED');
  return {host:HOST, username:env.QA_PERF_USERNAME, password:env.QA_PERF_PASSWORD,
    title:env.QA_EXPECTED_BOOK, price:env.QA_EXPECTED_UNIT_PRICE,
    deployedSha:env.QA_REPORTED_DEPLOYED_SHA, harnessSha:env.GITHUB_SHA || null,
    output:path.resolve(env.QA_LOAD_OUTPUT), preflight:process.argv.includes('--preflight'),
    target:20, threshold:5000, firstDelay:10_000, interval:12_000, minimumRemaining:25_000};
}
function activeState(config) {
  const file = path.join(config.output, 'summary.json');
  requireThat(!fs.existsSync(path.join(config.output, 'STOP')), 'OPERATOR_STOP');
  const state = JSON.parse(fs.readFileSync(file, 'utf8'));
  const stage = state.stages.at(-1);
  requireThat(state.status === 'Running' && state.profile_name === 'checkout-normal-10'
    && stage?.users === 10 && stage.current_actual_users === 10
    && stage.phase === 'steady' && !stage.abort_reason, 'NORMAL_LOAD_NOT_ACTIVE');
  return stage;
}
async function readAddress(page) {
  const radios = page.locator('input[name="address_id"]');
  requireThat(await radios.count() === 1, 'EXACTLY_ONE_SAVED_ADDRESS_REQUIRED');
  const id = await radios.getAttribute('id');
  requireThat(/^address-\d+$/.test(id || ''), 'INVALID_ADDRESS_SELECTOR');
  // Text is only held in memory for exact field comparison; never serialized.
  const lines = (await page.locator(`label[for="${id}"]`).innerText()).split('\n')
    .map(norm).filter(Boolean).filter(x => x !== 'Default address');
  requireThat(lines.length === 5 && lines[0] === 'QA Performance Buyer'
    && lines[1] === '1 QA Test Street' && lines[2] === 'Bengaluru, Karnataka 560001'
    && lines[3] === 'India' && lines[4] === 'Phone: 0000000000', 'SYNTHETIC_ADDRESS_MISMATCH');
  return {selector:`#${id}`, fields:{Recipient:lines[0], 'Address Line 1':lines[1],
    City:'Bengaluru', State:'Karnataka', 'Postal Code':'560001', Country:lines[3], Phone:'0000000000'}};
}
async function checkoutForm(page, config) {
  requireThat(norm(await page.locator('h1').innerText()) === 'Checkout', 'NOT_CHECKOUT_PAGE');
  requireThat(norm(await page.locator('.nav-user').innerText()) === `Signed in as ${config.username}`, 'ACCOUNT_MISMATCH');
  const items = page.locator('.cart-item');
  requireThat(await items.count() === 1, 'EXACTLY_ONE_CART_ITEM_REQUIRED');
  requireThat(norm(await items.locator('strong').innerText()) === config.title, 'BOOK_TITLE_MISMATCH');
  requireThat(norm(await items.locator('p').innerText()) === 'Quantity: 1', 'QUANTITY_MISMATCH');
  requireThat(money(norm(await items.locator('span').innerText())) === money(config.price), 'ITEM_PRICE_MISMATCH');
  requireThat(money(norm(await page.locator('.total').innerText()).replace(/^Total:\s*/, '')) === money(config.price), 'CART_TOTAL_MISMATCH');
  requireThat(await page.locator('input[name="payment_method"][value="TEST_CARD"]').count() === 1, 'MOCK_CARD_MISSING');
  requireThat(await page.getByRole('button', {name:'Place Order (Test Mode)', exact:true}).count() === 1, 'MOCK_SUBMIT_MISSING');
  requireThat(await page.locator('input[type="password"],input[autocomplete^="cc-"]').count() === 0, 'UNEXPECTED_SENSITIVE_INPUT');
  const address = await readAddress(page);
  await page.locator(address.selector).check();
  await page.locator('input[name="payment_method"][value="TEST_CARD"]').check();
  requireThat(!await page.locator('#use_new_address').isChecked(), 'NEW_ADDRESS_NOT_ALLOWED');
  return address;
}
async function detailFields(section) {
  return section.locator('.detail-item').evaluateAll(nodes => Object.fromEntries(nodes.map(node => [
    node.querySelector('.detail-label')?.textContent.trim(),
    node.querySelector('.detail-value,.status')?.textContent.trim()])));
}
async function verifyOrder(page, config, sample, address) {
  requireThat(norm(await page.locator('h1').innerText()) === `Order #${sample.order_id}`, 'ORDER_HEADING_MISMATCH');
  requireThat(norm(await page.locator('.nav-user').innerText()) === `Signed in as ${config.username}`, 'ORDER_ACCOUNT_MISMATCH');
  const rows = page.locator('section[aria-labelledby="items-heading"] tbody tr');
  requireThat(await rows.count() === 1, 'ORDER_ITEM_COUNT_MISMATCH');
  const cells = await rows.locator('td').allTextContents();
  requireThat(cells.length === 4 && norm(cells[0]) === config.title && norm(cells[2]) === '1'
    && money(norm(cells[1])) === money(config.price) && money(norm(cells[3])) === money(config.price), 'ORDER_LINE_MISMATCH');
  requireThat(money(norm(await page.locator('.total-row').innerText()).replace(/^Order Total:\s*/, '')) === money(config.price), 'ORDER_TOTAL_MISMATCH');
  const order = await detailFields(page.locator('section[aria-labelledby="summary-heading"]'));
  const payment = await detailFields(page.locator('section[aria-labelledby="payment-heading"]'));
  requireThat(order['Order Status'] === 'Pending' && payment['Payment Status'] === 'Pending'
    && payment['Payment Method'] === 'Test Card' && /^TEST-[A-Z0-9]+$/.test(payment['Transaction Reference'] || '')
    && money(payment['Payment Amount']) === money(config.price), 'PENDING_MOCK_PAYMENT_MISMATCH');
  const actualAddress = await detailFields(page.locator('section[aria-labelledby="address-heading"]'));
  requireThat(Object.keys(actualAddress).length === Object.keys(address.fields).length
    && Object.entries(address.fields).every(([key,value]) => actualAddress[key] === value), 'ORDER_ADDRESS_MISMATCH');
  sample.checks = {item:true, quantity:true, unit_price:true, total:true, shipping_snapshot:true,
    buyer_identity:true, order_pending:true, payment_pending:true, mock_payment:true};
}
async function run(config) {
  const modules = process.env.QA_NODE_MODULES;
  const r = modules ? createRequire(path.join(path.resolve(modules), 'qa-checkout.cjs')) : require;
  const {chromium} = r('playwright');
  const folder = path.join(config.output, config.preflight ? 'checkout-preflight' : 'browser');
  fs.mkdirSync(folder, {recursive:true});
  const resultFile = path.join(folder, 'results.json');
  requireThat(!fs.existsSync(resultFile), 'OUTPUT_EXISTS_PRESERVE_PRIOR_RESULTS');
  const result = {status:'Running', started_at_utc:new Date().toISOString(),
    reported_deployed_sha:config.deployedSha, harness_sha:config.harnessSha,
    deployment_attribution:'Operator-supplied SHA; application has no runtime build identifier',
    scope:config.preflight ? 'Read-only fixture preparation (login POST only); zero checkout submissions'
      : '20 sequential authenticated mock checkouts during 10 anonymous browsing VUs; up to 11 clients',
    measurement:'POST navigation start through loadEventEnd of correct Checkout Submitted page, browser assets included; order-detail verification outside timed interval',
    target_samples:config.target, threshold_ms:config.threshold,
    fixture:{book_title:config.title,quantity:1,unit_price:config.price,synthetic_address:true},
    limitations:['Mock payment only; no charge or paid/confirmed order acceptance',
      'One browser and one QA buyer; not concurrent checkout or 500-user capacity',
      'Warm authenticated browser; setup/login and checkout-form GET excluded from checkout timing',
      'Same-origin application assets included; third-party assets blocked',
      'No automatic POST retries or deletion; incomplete submission may have created an order'],
    submitted_attempts:0, samples:[], errors:[]};
  const save = () => {
    const temp = resultFile + '.tmp';
    fs.writeFileSync(temp, JSON.stringify(result,null,2)+'\n'); fs.renameSync(temp,resultFile);
  };
  let browser;
  let current;
  try {
    save();
    if (!config.preflight) activeState(config);
    browser = await chromium.launch({headless:true}); result.browser = browser.version();
    const context = await browser.newContext({viewport:{width:1366,height:768}, serviceWorkers:'block'});
    context.on('response', response => {
      if (new URL(response.url()).origin === config.host && response.status() >= 400) {
        result.errors.push({code:'APPLICATION_HTTP_ERROR',status:response.status()}); save();
      }
    });
    let allowedPost = null;
    await context.route('**/*', async route => {
      const request = route.request(); const url = new URL(request.url());
      const sameHost = url.origin === config.host;
      const readonly = ['GET','HEAD'].includes(request.method());
      const allowedRead = sameHost && (/^\/(?:accounts\/login\/|books\/|cart\/checkout\/|orders\/\d+\/|static\/.*|media\/.*)$/.test(url.pathname));
      if (readonly && allowedRead) return route.continue();
      if (sameHost && request.method() === 'POST' && url.pathname === allowedPost && request.isNavigationRequest()) {
        allowedPost = null; // One-use permit; redirects may only use GET.
        if (url.pathname === '/cart/checkout/') {
          try {
            requireThat(!config.preflight, 'PREFLIGHT_SUBMISSION_BLOCKED');
            activeState(config); // Recheck at network dispatch, not just before clicking.
            requireThat(current && result.submitted_attempts <= config.target, 'SUBMISSION_CAP_REACHED');
            current.request_dispatched = true; save();
          } catch (_) {
            result.errors.push({code:'CHECKOUT_DISPATCH_BLOCKED_LOAD_OR_CAP'}); save();
            return route.abort();
          }
        }
        return route.continue();
      }
      if (request.isNavigationRequest() || !readonly) {
        result.errors.push({code:'REQUEST_BLOCKED_BY_ALLOWLIST'}); save();
      }
      return route.abort(); // External assets are outside this app-only measurement.
    });
    const page = await context.newPage();
    page.setDefaultTimeout(15_000);
    const go = async pathname => {
      const response = await page.goto(config.host+pathname,{waitUntil:'load',timeout:20_000});
      requireThat(response?.status() === 200 && new URL(page.url()).pathname === pathname, 'GET_STATUS_OR_DESTINATION_MISMATCH');
    };
    await go('/accounts/login/');
    await page.locator('#username').fill(config.username);
    await page.locator('#password').fill(config.password);
    allowedPost = '/accounts/login/';
    await Promise.all([page.waitForNavigation({waitUntil:'load',timeout:20_000}), page.getByRole('button',{name:'Login',exact:true}).click()]);
    requireThat(new URL(page.url()).pathname === '/books/' && await page.locator('.nav-user').count() === 1, 'LOGIN_FAILED_NO_RETRY');
    await go('/cart/checkout/');
    await checkoutForm(page, config);
    requireThat(result.errors.length === 0, 'PREFLIGHT_HTTP_OR_ALLOWLIST_ERROR');
    result.fixture_preflight_passed = true; save();
    if (config.preflight) { result.status = 'Passed checkout fixture preflight; no orders created'; return result; }
    const stage = activeState(config);
    const age = Date.now()-Date.parse(stage.steady_started_at_utc);
    const start = clock.now()-age;
    for (let index=0; index<config.target; index++) {
      const due = start + config.firstDelay + index*config.interval;
      while (clock.now() < due) { activeState(config); await page.waitForTimeout(Math.min(250,due-clock.now())); }
      const running = activeState(config);
      const remaining = running.steady_target_seconds*1000 - (Date.now()-Date.parse(running.steady_started_at_utc));
      requireThat(remaining >= config.minimumRemaining, 'INSUFFICIENT_NORMAL_LOAD_TIME_NO_FURTHER_SUBMISSION');
      await go('/cart/checkout/');
      const address = await checkoutForm(page, config);
      activeState(config);
      current = {index:index+1, started_at_utc:new Date().toISOString(), normal_load_active_at_start:true, correct:false};
      result.samples.push(current);
      result.submitted_attempts++;
      current.submission_state = 'About to click once; if interrupted, inspect account orders before retry';
      save();
      allowedPost = '/cart/checkout/';
      const [response] = await Promise.all([
        page.waitForNavigation({waitUntil:'load',timeout:20_000}),
        page.getByRole('button',{name:'Place Order (Test Mode)',exact:true}).click()
      ]);
      const timing = await page.evaluate(() => { const n=performance.getEntriesByType('navigation')[0]; return {
        load_ms:n.loadEventEnd-n.startTime, ttfb_ms:n.responseStart-n.startTime,
        dom_ms:n.domContentLoadedEventEnd-n.startTime}; });
      Object.assign(current,timing);
      requireThat(response?.status() === 200 && new URL(page.url()).pathname === '/cart/checkout/', 'CHECKOUT_STATUS_OR_DESTINATION_MISMATCH');
      const panel = page.locator('section[aria-labelledby="checkout-result-heading"]');
      requireThat(await panel.locator('h2').innerText() === 'Checkout Submitted', 'NO_COMPLETED_CHECKOUT_CONFIRMATION');
      const href = await panel.getByRole('link',{name:'View Order Details',exact:true}).getAttribute('href');
      requireThat(/^\/orders\/[1-9]\d*\/$/.test(href || ''), 'INVALID_ORDER_LINK');
      current.order_id = Number(href.split('/')[2]);
      current.submission_state = 'Order ID captured'; save();
      requireThat(result.samples.filter(x => x.order_id === current.order_id).length === 1, 'DUPLICATE_ORDER_ID');
      const panelText = norm(await panel.innerText());
      requireThat(panelText.includes('Payment status: Pending') && panelText.includes('No real money was charged')
        && panelText.includes('Your cart has been preserved.') && panelText.includes(`Order total: ₹${config.price}`), 'CONFIRMATION_CONTENT_MISMATCH');
      activeState(config); current.normal_load_active_at_end = true;
      const detailStart = clock.now();
      await go(href); await verifyOrder(page,config,current,address);
      current.detail_verification_ms = Math.round((clock.now()-detailStart)*1000)/1000;
      activeState(config);
      current.correct = true; current.finished_at_utc = new Date().toISOString(); save();
      requireThat(result.errors.length === 0, 'REQUEST_ALLOWLIST_ERROR');
      requireThat(result.samples.filter(x => x.load_ms > config.threshold).length <= 2, 'MORE_THAN_TWO_CHECKOUT_TIMING_EXCEEDANCES');
    }
    const values = result.samples.map(x => x.load_ms);
    result.summary = {completed:result.samples.filter(x=>x.correct).length,p90_load_ms:p90(values),
      max_load_ms:Math.max(...values),at_or_below_5000ms:values.filter(x=>x<=config.threshold).length};
    requireThat(result.summary.completed === config.target && result.summary.p90_load_ms <= config.threshold, 'CHECKOUT_TIMING_GATE_FAILED');
    result.status = 'Passed completed mock checkout sample';
  } catch (error) {
    // Use our own codes only. Playwright exceptions can include rendered form data.
    const code = /^[A-Z][A-Z0-9_]+$/.test(error.message) ? error.message : 'BROWSER_OPERATION_FAILED';
    result.errors.push({code, sample:current?.index || null}); result.status = 'Stopped / checkout target not demonstrated';
  } finally {
    if (browser) await browser.close();
    result.finished_at_utc = new Date().toISOString(); save();
  }
  return result;
}
module.exports = {run,productionConfig,p90,money};
if (require.main === module) {
  Promise.resolve().then(() => run(productionConfig(process.env))).then(result => {
    console.log(JSON.stringify({status:result.status,summary:result.summary,submitted_attempts:result.submitted_attempts,errors:result.errors}));
    process.exitCode = result.status.startsWith('Passed') ? 0 : 1;
  }).catch(() => { console.error('Checkout configuration/startup failed; check required inputs and preserve prior output. No error details containing secrets are published.'); process.exitCode=1; });
}
