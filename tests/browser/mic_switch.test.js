// Browser test: switching speakers must not lose audio (bug found by the demo take, 2026-10-26).
// The old code opened a new mic + AudioContext on every click, dropping ~0.3-0.5 s at each turn start.
// Needs the app running (meeting-assistant serve) and Chrome installed. Transcription is stubbed.
//   cd tests/browser && npm install && npm test
const puppeteer = require("puppeteer-core");
const assert = require("assert");
const CHROME = process.env.CHROME || "C:/Program Files/Google/Chrome/Application/chrome.exe";
const APP = process.env.APP || "http://127.0.0.1:8765/";
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

(async () => {
  const browser = await puppeteer.launch({ executablePath: CHROME, headless: true,
    args: ["--autoplay-policy=no-user-gesture-required", "--use-fake-ui-for-media-stream", "--mute-audio"] });
  const page = await browser.newPage();
  await page.evaluateOnNewDocument(() => {
    window.__opens = 0;
    navigator.mediaDevices.getUserMedia = async () => {      // a continuous tone as the microphone
      window.__opens++;
      const ctx = new AudioContext(), osc = ctx.createOscillator(), dest = ctx.createMediaStreamDestination();
      osc.connect(dest); osc.start();
      return dest.stream;
    };
  });
  const posted = []; let clicking = false;          // only turns, not the 1 s warm-up at load
  await page.setRequestInterception(true);
  page.on("request", (r) => {
    if (r.url().endsWith("/api/transcribe") && r.method() === "POST") {
      const bytes = r.postDataBuffer ? r.postDataBuffer().length : (r.postData() || "").length;
      if (clicking) posted.push(bytes / 4 / 16000);
      return r.respond({ status: 200, contentType: "application/json", body: '{"text":"x","seconds":0}' });
    }
    r.continue();
  });
  await page.goto(APP, { waitUntil: "networkidle0" });
  const names = await page.evaluate(() => [...document.querySelectorAll(".speaker")].map((b) => b.textContent.trim()));
  const click = (n) => page.evaluate((n) => [...document.querySelectorAll(".speaker")].find((b) => b.textContent.trim() === n).click(), n);

  clicking = true;
  await click(names[0]);
  await page.waitForFunction(() => state.rec && state.rec.chunks.length > 0);    // capture is live
  const t0 = Date.now();
  await sleep(1500);
  await click(names[1]);                                                         // switch speaker
  await sleep(1500);
  await click(names[1]);                                                         // stop
  const wall = (Date.now() - t0) / 1000;
  await sleep(500);
  const opens = await page.evaluate(() => window.__opens);
  await browser.close();

  const total = posted.reduce((a, b) => a + b, 0);
  console.log(`turns: ${posted.map((s) => s.toFixed(2)).join(" + ")} = ${total.toFixed(2)} s of audio for ${wall.toFixed(2)} s of clicking`);
  assert.strictEqual(posted.length, 2, "two turns recorded");
  assert.strictEqual(opens, 1, `the mic was opened ${opens} times for one meeting`);
  assert.ok(total >= wall - 0.25, `audio lost at the switch: ${total.toFixed(2)} s captured for ${wall.toFixed(2)} s`);
  console.log("PASS: no audio lost when switching speakers");
})().catch((e) => { console.error("FAIL:", e.message); process.exit(1); });
