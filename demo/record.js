// Phase 1 of the demo video: ONE real run of the real app (one take, not retried).
// Each script line is a Kokoro clip played into the app as its microphone, so the app's own
// capture, resampling, Moonshine transcription, Bonsai extraction and code checks all run for real.
// Every request and its timing is logged to run-log.json; the app's own Save button keeps a copy.
const puppeteer = require("puppeteer-core");
const fs = require("fs");

const CHROME = "C:/Program Files/Google/Chrome/Application/chrome.exe";
const APP = "http://127.0.0.1:8765/";
// DRY=1: plumbing check with a voice sample that is NOT in the script; no extraction, nothing saved
const DRY = !!process.env.DRY;
const lines = DRY ? [["Akhash", "(voice sample, not the script)"]] : JSON.parse(fs.readFileSync(__dirname + "/script.json", "utf8"));
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function wavSeconds(buf) {  // PCM wav: data bytes / byte rate
  let off = 12, byteRate = 0;
  while (off < buf.length) {
    const id = buf.toString("ascii", off, off + 4), size = buf.readUInt32LE(off + 4);
    if (id === "fmt ") byteRate = buf.readUInt32LE(off + 16);
    if (id === "data") return size / byteRate;
    off += 8 + size;
  }
  throw new Error("no data chunk");
}

(async () => {
  const browser = await puppeteer.launch({
    executablePath: CHROME, headless: true,
    args: ["--autoplay-policy=no-user-gesture-required", "--use-fake-ui-for-media-stream", "--mute-audio"],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1600, height: 900 });
  page.on("console", (m) => m.type() === "error" && console.log("page error:", m.text()));
  await page.evaluateOnNewDocument(() => {
    window.__log = [];
    const realFetch = window.fetch.bind(window);
    window.fetch = async (url, opts = {}) => {   // log every API call: when, how long, what came back
      const t0 = performance.now(), r = await realFetch(url, opts);
      let res = null; try { res = await r.clone().json(); } catch {}
      window.__log.push({ url: String(url), t0, t1: performance.now(), status: r.status,
        req: typeof opts.body === "string" ? JSON.parse(opts.body) : opts.body ? { audio_bytes: opts.body.byteLength } : null, res });
      return r;
    };
    // the "microphone": one stream for the meeting; each Kokoro clip is played into it on cue
    navigator.mediaDevices.getUserMedia = async () => {
      window.__micCtx = new AudioContext(); window.__micDest = window.__micCtx.createMediaStreamDestination();
      return window.__micDest.stream;
    };
    window.__play = async () => {
      const ctx = window.__micCtx, buf = await ctx.decodeAudioData(window.__clip.slice(0));
      const src = ctx.createBufferSource(); src.buffer = buf; src.connect(window.__micDest); src.start();
    };
  });

  await page.goto(APP, { waitUntil: "networkidle0" });
  await page.waitForFunction(() => /ready/.test(document.getElementById("speechState").textContent), { timeout: 120000 });
  const people = await page.evaluate(() => state.people);
  for (const [who] of lines) if (!people.includes(who)) throw new Error(`${who} is not a speaker button (restart the server?)`);

  const t0 = Date.now(), events = [];
  const click = (name) => page.evaluate((n) => [...document.querySelectorAll(".speaker")].find((b) => b.textContent.trim() === n).click(), name);
  for (let i = 0; i < lines.length; i++) {
    const [who, text] = lines[i], file = DRY ? `${__dirname}/voice-samples/am_echo.wav` : `${__dirname}/clips/${i + 1}_${who}.wav`, wav = fs.readFileSync(file);
    await page.evaluate((b64) => {
      const s = atob(b64), a = new Uint8Array(s.length);
      for (let j = 0; j < s.length; j++) a[j] = s.charCodeAt(j);
      window.__clip = a.buffer;
    }, wav.toString("base64"));
    events.push({ type: "speak", who, script: text, clip: file, clip_s: wavSeconds(wav), at_ms: Date.now() - t0 });
    await click(who);                          // clicking the next name also ends the previous turn
    // take 2 harness (disclosed): the speaker starts talking 250 ms after capture is live, like a person
    await page.waitForFunction((n) => state.live === n && state.rec && state.rec.chunks.length > 0, { timeout: 30000 }, who);
    await sleep(250);
    await page.evaluate(() => window.__play());
    await sleep(wavSeconds(wav) * 1000 + 450);
    console.log(`turn ${i + 1} ${who} done`);
  }
  await click(lines.at(-1)[0]);                // click the last speaker again to stop
  events.push({ type: "stop", at_ms: Date.now() - t0 });
  await page.waitForFunction(() => state.turns.length && !state.turns.some((t) => t.pending), { timeout: 120000 });

  if (DRY) { console.log("DRY transcript:", await page.evaluate(() => transcriptText())); await browser.close(); return; }
  events.push({ type: "extract", at_ms: Date.now() - t0 });
  await page.click("#extract");
  await page.waitForFunction(() => state.result && !document.getElementById("extract").disabled, { timeout: 600000, polling: 500 });
  events.push({ type: "extracted", at_ms: Date.now() - t0 });
  await page.click("#save");
  await sleep(1500);

  const out = await page.evaluate(() => ({
    turns: state.turns, transcript: transcriptText(), result: state.result, people: state.people, log: window.__log,
    saved_toast: document.getElementById("toast").textContent,
  }));
  out.events = events;
  const crypto = require("crypto"), sha = (f) => crypto.createHash("sha256").update(fs.readFileSync(f)).digest("hex").slice(0, 16);
  const ROOT = __dirname + "/..";
  out.take = 2;
  out.identical_to_take1 = { "script.json": sha(__dirname + "/script.json"), "meeting-assistant.toml": sha(ROOT + "/meeting-assistant.toml"),
    "prompts/system/meeting-assistant.md": sha(ROOT + "/prompts/system/meeting-assistant.md"),
    git_head: require("child_process").execSync("git rev-parse --short HEAD", { cwd: ROOT }).toString().trim() };
  out.recorded_at = new Date().toISOString();
  out.note = "Take 2 of the frozen script (take 1 discarded: it exposed the lost-audio bug fixed in e3f2206). Kokoro voices fed into one mic stream, each 250 ms after capture is live. Recorded once.";
  fs.writeFileSync(__dirname + "/logs/new-run-log.json", JSON.stringify(out, null, 2));   // never overwrites take 1/2
  await page.screenshot({ path: __dirname + "/logs/new-run-final.png" });
  await browser.close();
  console.log("transcript:\n" + out.transcript);
  console.log("items:", JSON.stringify(out.result.items, null, 1));
  console.log("missed:", JSON.stringify(out.result.missed), "seconds:", out.result.seconds, "|", out.saved_toast);
})().catch((e) => { console.error("FAILED:", e.message); process.exit(1); });
