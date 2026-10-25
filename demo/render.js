// Phase 2 of the demo video: re-render the REAL app page frame by frame from run-log.json.
// The app's clock (timers, Date, CSS animations) is virtual and advanced one frame at a time, so the
// video is smooth whatever the CPU is doing. Inputs are replayed from the real run: the Kokoro clips
// are fed to the app's own capture code, and /api/* answers are the recorded ones with their recorded
// latencies. The stage around the app adds camera, cursor, subtitles and pop-outs.
//
//   node render.js                  -> out/video.mp4 (no audio) + out/timeline.json (for the audio mix)
//   STILLS=3,12.5,40 node render.js -> out/still-<t>.jpg only (fast review)
const puppeteer = require("puppeteer-core");
const fs = require("fs");
const os = require("os");
const { spawn, spawnSync } = require("child_process");

const W = __dirname, OUT = `${W}/out`;
fs.mkdirSync(OUT, { recursive: true });
const CHROME = "C:/Program Files/Google/Chrome/Application/chrome.exe";
const APP = "http://127.0.0.1:8765";
const FPS = 30, VW = 1920, VH = 1080, AW = 1600, AH = 900;   // the app renders at 1600x900, shown at 1.2x
const RUN = JSON.parse(fs.readFileSync(process.env.RUN_LOG || `${W}/logs/take2-run-log.json`, "utf8"));
for (const e of RUN.events) if (e.clip) e.clip = `${W}/clips/${require("path").basename(e.clip)}`;   // logs hold the original paths
const POP = JSON.parse(fs.readFileSync(`${W}/popouts.json`, "utf8"));
const LINES = JSON.parse(fs.readFileSync(`${W}/script.json`, "utf8"));
const STILLS = process.env.STILLS ? process.env.STILLS.split(",").map(Number) : null;

// ---------------- data from the real run ----------------
const tlog = RUN.log.filter((l) => l.url.includes("/api/transcribe"));
const turnLat = tlog.slice(1).map((l) => (l.t1 - l.t0) / 1000);          // [0] is the warm-up call
const nlog = RUN.log.find((l) => l.url.includes("/api/notes"));
const notesLat = (nlog.t1 - nlog.t0) / 1000;
const clipSec = RUN.events.filter((e) => e.type === "speak").map((e) => e.clip_s);
const pcm16k = RUN.events.filter((e) => e.type === "speak").map((e) => {
  const r = spawnSync("ffmpeg", ["-v", "error", "-i", e.clip, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], { maxBuffer: 1 << 26 });
  return new Float32Array(r.stdout.buffer, r.stdout.byteOffset, r.stdout.length / 4);
});
const COLORS = ["#ffe27a", "#ffb3c8", "#aedcf4", "#c4e4a3", "#ffc58c", "#d8c6f3"];
const colorOf = (n) => COLORS[RUN.people.indexOf(n)] || "#e8d9bb";

// ---------------- easing ----------------
function bezier(x1, y1, x2, y2) {
  const f = (t, a, b) => 3 * a * t * (1 - t) ** 2 + 3 * b * t * t * (1 - t) + t ** 3;
  return (x) => { if (x <= 0) return 0; if (x >= 1) return 1;
    let lo = 0, hi = 1; for (let i = 0; i < 40; i++) { const m = (lo + hi) / 2; if (f(m, x1, x2) < x) lo = m; else hi = m; }
    return f((lo + hi) / 2, y1, y2); };
}
const camEase = bezier(0.65, 0, 0.35, 1), outEase = bezier(0.22, 1, 0.36, 1), popEase = bezier(0.34, 1.3, 0.64, 1);
const clamp01 = (x) => Math.max(0, Math.min(1, x));
const prog = (t, a, d) => clamp01((t - a) / d);
const lerp = (a, b, p) => a + (b - a) * p;

// ---------------- the director: every cue in video seconds ----------------
const CAM = { FULL: { s: 1.2, x: 0, y: 0 }, LEFT: { s: 1.5, x: 0, y: 0 }, DESK: { s: 1.4, x: VW - AW * 1.4, y: -84 } };
const cues = { clicks: [], audio: [], sfx: [], subs: [], cam: [], pops: [] };
const hookAt = 0.5, hookClip = 2;                                   // cold open: Akhash's line
cues.audio.push({ file: RUN.events.filter((e) => e.type === "speak")[hookClip].clip, at: hookAt });
cues.subs.push({ who: LINES[hookClip][0], text: LINES[hookClip][1], from: hookAt, to: hookAt + clipSec[hookClip] + 0.2, hook: true });
const APP_IN = hookAt + clipSec[hookClip] + 0.35;
cues.cam.push({ from: APP_IN + 1.3, d: 1.2, to: CAM.LEFT });
let t = APP_IN + 1.3 + 1.2 + 0.5;                                   // short hold after the move
const speech = [];
for (let i = 0; i < LINES.length; i++) {
  const click = i === 0 ? t + 0.85 : speech[i - 1].end + 0.2;   // natural turn-taking gap
  const start = click + 0.25, end = start + clipSec[i];
  speech.push({ click, start, end });
  cues.clicks.push({ at: click, target: { speaker: LINES[i][0] } });
  cues.audio.push({ file: RUN.events.filter((e) => e.type === "speak")[i].clip, at: start });
  cues.subs.push({ who: LINES[i][0], text: LINES[i][1], from: start, to: end + 0.15 });
}
const stopAt = speech.at(-1).end + 0.3;
cues.clicks.push({ at: stopAt, target: { speaker: LINES.at(-1)[0] } });
const lastLanded = stopAt + Math.max(...turnLat.slice(-2)) + 0.2;
cues.cam.push({ from: lastLanded + 0.1, d: 1.2, to: CAM.FULL });
const extractAt = lastLanded + 0.1 + 1.2 + 0.3 + 0.85;
cues.clicks.push({ at: extractAt, target: { sel: "#extract" } });
// time compression of the model wait: ramp 1x -> 4x -> 1x (300 ms ramps), result lands 0.5 s after ramp-down
const RAMP = 0.3, FAST = 6;
const fastSpan = Math.max(0, (notesLat - 0.2 - 2 * RAMP * (1 + FAST) / 2 - 0.5) / FAST);
const ramp = { up: extractAt + 0.2, top: extractAt + 0.2 + RAMP, down: extractAt + 0.2 + RAMP + fastSpan, end: extractAt + 0.2 + 2 * RAMP + fastSpan };
const speedAt = (v) => v < ramp.up || v >= ramp.end ? 1 : v < ramp.top ? lerp(1, FAST, (v - ramp.up) / RAMP)
  : v < ramp.down ? FAST : lerp(FAST, 1, (v - ramp.down) / RAMP);
// app-time of a video time (integral of speed), and the video time the notes land
const appTime = (v) => { let a = 0; const step = 1 / 600; for (let x = 0; x < v; x += step) a += speedAt(x) * Math.min(step, v - x); return a; };
let landAt = extractAt; while (appTime(landAt) - appTime(extractAt) < notesLat) landAt += 1 / FPS;
const nNotes = RUN.result.items.length;
for (let i = 0; i < nNotes; i++) cues.sfx.push({ kind: "drop", at: landAt + i * 0.18 + 0.22 });
const dropsDone = landAt + (nNotes - 1) * 0.18 + 0.5;
cues.cam.push({ from: dropsDone + 0.5, d: 1.4, to: CAM.DESK });
t = dropsDone + 0.5 + 1.4 + 0.5;
let typeCue = null;                                                 // pop-outs and the owner typing, in order
for (const p of POP) {
  if (p.kind === "type") {
    const at = t + 0.85;
    cues.clicks.push({ at, target: { note: p.note, part: ".owner" } });
    typeCue = { note: p.note, value: p.value, at };
    t = at + 0.3 + p.value.length * 0.12 + 0.3 + 0.5;
  } else {                                                          // out 0.45, hold words*0.3+0.6, back 0.35
    const hold = p.text.split(/\s+/).length * 0.3 + 0.6;
    cues.pops.push({ ...p, notes: p.notes || [p.note], from: t, hold, to: t + 0.45 + hold + 0.35 });
    t += 0.45 + hold + 0.35 + 0.15;
  }
}
const OUTRO = t + 0.3, OUTRO_B = OUTRO + 5.6, OUTRO_C = OUTRO_B + 10.0, END = OUTRO_C + 8.6;
for (const c of cues.clicks) cues.sfx.push({ kind: "click", at: c.at });
const NFRAMES = Math.ceil(END * FPS);
if (process.env.PLAN) {                                             // PLAN=1: print the cue sheet and stop
  const f = (x) => x.toFixed(2);
  console.log({ APP_IN: f(APP_IN), firstClick: f(speech[0].click), stop: f(stopAt), extract: f(extractAt), ramp, land: f(landAt),
    pops: cues.pops.map((p) => [f(p.from), f(p.to)]), type: typeCue && f(typeCue.at), OUTRO: f(OUTRO), OUTRO_B: f(OUTRO_B), OUTRO_C: f(OUTRO_C), END: f(END),
    turnLat: turnLat.map(f), notesLat: f(notesLat) });
  process.exit(0);
}

// ---------------- stage page (served at the app's origin, so the iframe is same-origin) ----------------
const transcribedIn = turnLat.reduce((a, b) => a + b, 0);
const speechTotal = clipSec.reduce((a, b) => a + b, 0);
const STAGE = `<!doctype html><html><head><meta charset="utf-8"><style>
@font-face { font-family: Kalam; src: url(/static/fonts/kalam-700.woff2); font-weight: 700; }
@font-face { font-family: Kalam; src: url(/static/fonts/kalam-400.woff2); font-weight: 400; }
@font-face { font-family: Quattro; src: url(/static/fonts/quattro-Regular.woff2); font-weight: 400; }
@font-face { font-family: Quattro; src: url(/static/fonts/quattro-Bold.woff2); font-weight: 700; }
:root { --grain: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='220' height='220'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='3' stitchTiles='stitch'/%3E%3CfeColorMatrix values='0 0 0 0 0.25 0 0 0 0 0.2 0 0 0 0 0.1 0 0 0 .07 0'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E"); }
* { box-sizing: border-box; }
body { margin: 0; width: ${VW}px; height: ${VH}px; overflow: hidden; background: #ece8df var(--grain); color: #2a2925; font-family: Quattro, sans-serif; }
#cam { position: absolute; left: 0; top: 0; width: ${AW}px; height: ${AH}px; transform-origin: 0 0; }
#app { width: ${AW}px; height: ${AH}px; border: 0; display: block; }
.layer { position: absolute; inset: 0; pointer-events: none; }
#hook { display: flex; flex-direction: column; justify-content: center; padding: 0 180px; background: #ece8df var(--grain); }
#hook .small { font-size: 30px; color: #6e695f; margin-bottom: 18px; }
#hook h1 { font: 700 112px/1.05 Kalam, cursive; margin: 0; letter-spacing: -.01em; }
.sub { position: absolute; max-width: 760px; background: #fffdf8 var(--grain); border-radius: 6px; padding: 18px 26px 20px;
       box-shadow: 0 1px 1px rgba(60,45,20,.12), 0 18px 34px -20px rgba(60,45,20,.55); }
.sub .who { display: flex; align-items: center; gap: 10px; font: 700 22px Quattro; color: #6e695f; margin-bottom: 4px; }
.sub .who i { width: 16px; height: 16px; transform: rotate(-6deg); box-shadow: inset 0 0 0 1px rgba(0,0,0,.18); }
.sub .said { font: 400 34px/1.35 Quattro; }
.sub .said::before { content: "“"; } .sub .said::after { content: "”"; }
.sub .tag { font: 400 15px Quattro; color: #9a9384; margin-top: 8px; }
#cursor { position: absolute; width: 34px; height: 34px; left: 0; top: 0; transform-origin: 4px 3px; }
#ring { position: absolute; width: 24px; height: 24px; border: 3px solid #2a2925; border-radius: 50%; }
#corner { position: absolute; right: 34px; bottom: 26px; font: 400 18px Quattro; color: #6e695f; background: rgba(255,253,248,.85);
          padding: 7px 14px; border-radius: 999px; }
#badge { position: absolute; font: 700 40px Kalam; color: #c0392b; transform: rotate(-4deg); }
#annot { position: absolute; font: 700 34px Kalam; color: #c0392b; transform: rotate(-3deg); white-space: nowrap; }
.pop { position: absolute; width: 520px; background: #fffdf8 var(--grain); border-radius: 6px; padding: 22px 28px 24px;
       font: 700 36px/1.25 Kalam; box-shadow: 0 1px 1px rgba(60,45,20,.12), 0 26px 44px -22px rgba(60,45,20,.6); }
.pop small { display: block; font: 400 17px Quattro; color: #8a8273; margin-top: 10px; }
.outro { display: flex; flex-direction: column; justify-content: center; padding: 0 170px; background: #ece8df var(--grain); }
.outro h2 { font: 700 84px/1.05 Kalam; margin: 0 0 30px; }
.outro p { font: 400 30px/1.5 Quattro; margin: 0 0 14px; max-width: 1500px; }
.outro .dim { color: #6e695f; font-size: 25px; }
.outro .sw { display: inline-block; width: 22px; height: 22px; margin-right: 12px; vertical-align: -2px; transform: rotate(-6deg); }
</style></head><body>
<div id="cam"><iframe id="app" src="/"></iframe></div>
<div class="layer" id="ov">
  <div id="annot">← click a name, then talk</div>
  <div class="sub" id="sub"><div class="who"><i></i><span></span></div><div class="said"></div><div class="tag">said (script)</div></div>
  <div id="badge">6× speed</div>
  <div class="pop" id="pop"><div class="t"></div><small></small></div>
  <div id="corner">Synthetic voices · real run (take 2), re-rendered frame by frame</div>
  <div id="ring"></div>
  <svg id="cursor" viewBox="0 0 34 34"><path d="M4 3 L4 27 L10.5 21 L15 31 L19 29.3 L14.6 19.6 L23.5 19.6 Z" fill="#1d1c1a" stroke="#fff" stroke-width="2" stroke-linejoin="round"/></svg>
</div>
<div class="layer" id="hook"><div class="small">Four friends plan a trip to Hyderabad.</div><h1>Who's booking the hotel?</h1></div>
<div class="layer outro" id="outroA">
  <h2>Your audio and notes stay on the laptop.</h2>
  <p>This run: ${speechTotal.toFixed(0)} s of synthetic speech transcribed in ${transcribedIn.toFixed(1)} s; notes in ${RUN.result.seconds.toFixed(0)} s (4-core laptop, CPU only).</p>
  <p class="dim">Open models: Moonshine for speech, Bonsai 4B for notes, Kokoro for the demo voices.</p>
  <p class="dim">Code and the eval behind it: link in the post.</p>
</div>
<div class="layer outro" id="outroB">
  <h2>What you just saw</h2>
  <p>A re-enactment. The app was first used live, offline, with friends planning this trip; screen-recording a live meeting wasn't feasible on this 8 GB laptop. So this is a scripted take, written to include the cases the app is built for.</p>
  <p>Voices are synthetic (Kokoro) and fed straight in as clean audio, each starting 250 ms after the mic was live. Transcript, notes and timings are real, from that run, re-rendered frame by frame.</p>
  <p class="dim">Real voices, accents and crosstalk: untested.</p>
</div>
<div class="layer outro" id="outroC">
  <h2>Take 2</h2>
  <p>Take 1 was discarded. An app bug dropped the first half-second of each turn, so “We need a hotel” became “Tell near” and the hotel went to Akhash.</p>
  <p>Fixed (one mic stream per meeting). Take 2 used the same script, model and settings, recorded once. Both logs are linked in the post.</p>
</div>
</body></html>`;

// ---------------- page-side: virtual clock + replayed mic and API (runs in every frame) ----------------
function pageSetup() {
  const RealDate = Date, realSetTimeout = window.setTimeout.bind(window), base = RealDate.now();
  let vt = 0, nextId = 1; const timers = new Map(), rafs = new Map();
  window.setTimeout = (fn, ms = 0, ...a) => { const id = nextId++; timers.set(id, { fn, at: vt + Math.max(0, +ms || 0), a }); return id; };
  window.setInterval = (fn, ms = 0, ...a) => { const id = nextId++; const e = Math.max(1, +ms || 0); timers.set(id, { fn, at: vt + e, a, every: e }); return id; };
  window.clearTimeout = window.clearInterval = (id) => timers.delete(id);
  window.requestAnimationFrame = (fn) => { const id = nextId++; rafs.set(id, fn); return id; };
  window.cancelAnimationFrame = (id) => rafs.delete(id);
  performance.now = () => vt;
  class VDate extends RealDate { constructor(...a) { if (a.length) super(...a); else super(base + vt); } static now() { return base + vt; } }
  window.Date = VDate;
  const flush = () => new Promise((r) => realSetTimeout(r, 0));
  window.__advance = async (ms) => {
    const end = vt + ms;
    for (;;) {
      let next = null;
      for (const [id, tm] of timers) if (tm.at <= end && (!next || tm.at < next[1].at)) next = [id, tm];
      if (!next) break;
      const [id, tm] = next; vt = tm.at;
      if (tm.every) tm.at += tm.every; else timers.delete(id);
      try { tm.fn(...tm.a); } catch (e) { console.error(e); }
      await flush();
    }
    vt = end; await flush();
    const rs = [...rafs.values()]; rafs.clear(); rs.forEach((f) => f(vt));
    for (const an of document.getAnimations()) {            // CSS animations/transitions follow the virtual clock
      if (an.__t0 === undefined) an.__t0 = vt - ms;
      an.pause(); an.currentTime = vt - an.__t0;
    }
  };
  // the microphone and the API, replayed from the real run
  navigator.mediaDevices.getUserMedia = async () => ({ getTracks: () => [{ stop() {} }] });
  window.AudioContext = class {
    constructor() { this.sampleRate = 16000; }
    createMediaStreamSource() { return { connect() {} }; }
    createScriptProcessor() { const p = { connect() {}, disconnect() { window.__proc = null; }, onaudioprocess: null }; window.__proc = p; return p; }
    get destination() { return {}; }
    async close() {}
  };
  window.__feed = (arr) => { if (window.__proc && window.__proc.onaudioprocess) window.__proc.onaudioprocess({ inputBuffer: { getChannelData: () => Float32Array.from(arr) } }); };
  let nTranscribe = 0;
  window.fetch = (url, opts = {}) => {
    const u = String(url), R = () => window.__R;
    const reply = (body, ms) => new Promise((res) => setTimeout(() => res(new Response(JSON.stringify(body()), { status: 200, headers: { "Content-Type": "application/json" } })), ms));
    if (u.includes("/api/config")) return reply(() => R().config, 5);
    if (u.includes("/api/health")) return reply(() => R().health, 5);
    if (u.includes("/api/transcribe")) {
      const k = nTranscribe++;
      if (k === 0) return reply(() => ({ text: "", seconds: 1 }), 300);              // warm-up call at load
      return reply(() => ({ text: R().turns[k - 1].text, seconds: 0 }), R().turnLat[k - 1] * 1000);
    }
    if (u.includes("/api/notes")) return reply(() => R().result, R().notesLat * 1000);
    return reply(() => ({}), 5);
  };
}

// ---------------- main ----------------
(async () => {
  const cfg = await (await fetch(`${APP}/api/config`)).json();
  const browser = await puppeteer.launch({ executablePath: CHROME, headless: true,
    args: ["--hide-scrollbars", "--mute-audio", "--force-color-profile=srgb"], defaultViewport: { width: VW, height: VH } });
  const page = await browser.newPage();
  await page.emulateMediaFeatures([{ name: "prefers-color-scheme", value: "light" }, { name: "prefers-reduced-motion", value: "no-preference" }]);
  await page.evaluateOnNewDocument(pageSetup);
  await page.setRequestInterception(true);
  page.on("request", (r) => r.url().endsWith("/__stage.html")
    ? r.respond({ status: 200, contentType: "text/html", body: STAGE }) : r.continue());
  page.on("console", (m) => m.type() === "error" && console.log("page:", m.text()));
  await page.goto(`${APP}/__stage.html`, { waitUntil: "load" });
  const frame = page.frames().find((f) => f.url() === `${APP}/`);
  await frame.evaluate((R) => { window.__R = R; try { localStorage.setItem("theme", "light"); } catch {} }, {
    config: { ...cfg, participants: RUN.people }, health: Object.fromEntries(Object.keys(cfg.backends).map((k) => [k, { ok: true }])),
    turns: RUN.turns, turnLat, result: RUN.result, notesLat });
  for (let i = 0; i < 30; i++) await frame.evaluate(() => window.__advance(50));   // init(): config, health, warm-up
  await frame.evaluate(() => document.fonts.ready);
  await page.evaluate(() => document.fonts.ready);

  const cdp = await page.createCDPSession();
  let ff = null, encoded = 0;
  if (!STILLS) {
    ff = spawn("ffmpeg", ["-v", "error", "-y", "-f", "image2pipe", "-framerate", `${FPS}`, "-c:v", "mjpeg", "-i", "-",
      "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-threads", "2", "-movflags", "+faststart", `${OUT}/video.mp4`]);
    ff.stderr.on("data", (d) => process.stderr.write(d));
  }

  // per-frame state
  let cur = { x: 1500, y: 760 }, curFrom = null, curTo = null, curT0 = 0, curD = 0, lastClick = -9;
  let feedPos = 0, lastApp = 0, typed = 0, liveSpeaker = null;
  const rectOf = (q) => frame.evaluate((q) => {
    let el;
    if (q.speaker) el = [...document.querySelectorAll(".speaker")].find((b) => b.textContent.trim() === q.speaker);
    else if (q.sel) el = document.querySelector(q.sel);
    else if (q.note != null) { el = document.querySelectorAll(".note")[q.note]; if (q.part) el = el.querySelector(q.part); }
    if (!el) return null;
    const r = el.getBoundingClientRect(); return { x: r.x, y: r.y, w: r.width, h: r.height };
  }, q);
  const camAt = (v) => {
    let c = CAM.FULL;
    for (const m of cues.cam) {
      if (v >= m.from + m.d) c = m.to;
      else if (v >= m.from) { const p = camEase((v - m.from) / m.d); return { s: lerp(c.s, m.to.s, p), x: lerp(c.x, m.to.x, p), y: lerp(c.y, m.to.y, p) }; }
    }
    return c;
  };
  const toStage = (r, c) => ({ x: c.x + r.x * c.s, y: c.y + r.y * c.s, w: r.w * c.s, h: r.h * c.s });
  const t0wall = Date.now();

  for (let f = 0; f < NFRAMES; f++) {
    const v = f / FPS, vPrev = (f - 1) / FPS;
    const cam = camAt(v);

    // 1. clicks due this frame (the cursor arrives 250 ms early and rests)
    for (const c of cues.clicks) {
      if (c.at > vPrev && c.at <= v) {
        if (c.target.speaker) { liveSpeaker = liveSpeaker === c.target.speaker ? null : c.target.speaker; }
        await frame.evaluate((q) => {
          let el;
          if (q.speaker) el = [...document.querySelectorAll(".speaker")].find((b) => b.textContent.trim() === q.speaker);
          else if (q.sel) el = document.querySelector(q.sel);
          else { el = document.querySelectorAll(".note")[q.note].querySelector(q.part); el.focus(); }
          el.click();
        }, c.target);
        lastClick = v; feedPos = 0;
      }
    }
    // typing the owner onto the white card, then Enter
    if (typeCue && v > typeCue.at + 0.3) {
      const want = Math.min(typeCue.value.length, Math.floor((v - typeCue.at - 0.3) / 0.12) + 1);
      if (want > typed) {
        typed = want;
        await frame.evaluate((i, val, done) => {
          const inp = document.querySelectorAll(".note")[i].querySelector(".owner");
          inp.value = val; inp.dispatchEvent(new Event("input"));
          if (done) inp.dispatchEvent(new Event("change"));
        }, typeCue.note, typeCue.value.slice(0, typed), typed === typeCue.value.length);
      }
    }
    // 2. microphone samples for this frame: the clip while it plays, silence around it
    if (liveSpeaker) {
      const i = speech.findIndex((s, k) => v >= s.click && (k === speech.length - 1 ? v < stopAt : v < speech[k + 1].click));
      if (i >= 0) {
        const n = Math.round(v * 16000) - Math.round(vPrev * 16000), out = new Array(n).fill(0);
        for (let j = 0; j < n; j++) {
          const at = vPrev + j / 16000 - speech[i].start;
          if (at >= 0) { const idx = Math.floor(at * 16000); if (idx < pcm16k[i].length) out[j] = pcm16k[i][idx]; }
        }
        await frame.evaluate((a) => window.__feed(a), out);
      }
    }
    // 3. advance the app's clock by this frame's share of app-time (faster during the model wait)
    const app = appTime(v), dApp = (app - lastApp) * 1000; lastApp = app;
    await frame.evaluate((ms) => window.__advance(ms), Math.max(0, dApp));

    // 4. stage: camera, cursor, subtitles, badge, pop-outs, hook and outro
    let nextClick = cues.clicks.find((c) => c.at > v - 0.08);
    let target = null;
    if (nextClick && nextClick.at - v < 0.85) {
      const r = await rectOf(nextClick.target);
      if (r) { const s = toStage(r, cam); target = { x: s.x + s.w * (nextClick.target.part ? 0.25 : 0.5), y: s.y + s.h * 0.55 }; }
      if (!curTo || curTo.key !== nextClick.at) {
        curFrom = { ...cur }; curT0 = Math.max(v, nextClick.at - 0.85);
        const dist = Math.hypot(target.x - cur.x, target.y - cur.y); curD = Math.min(0.7, 0.45 + dist / 4000);
        curTo = { key: nextClick.at };
      }
      const p = outEase(prog(v, curT0, curD));
      const mx = (curFrom.x + target.x) / 2, my = (curFrom.y + target.y) / 2;
      const nx = -(target.y - curFrom.y) * 0.12, ny = (target.x - curFrom.x) * 0.12;     // gentle curve
      const q = 1 - p;
      cur = { x: q * q * curFrom.x + 2 * q * p * (mx + nx) + p * p * target.x, y: q * q * curFrom.y + 2 * q * p * (my + ny) + p * p * target.y };
    }
    const subs = cues.subs.filter((s) => v >= s.from - 0.15 && v <= s.to + 0.15);
    const popNow = cues.pops.find((p) => v >= p.from && v <= p.to);
    let popRect = null;
    if (popNow) {                                                    // union of the notes it explains
      const rs = (await Promise.all(popNow.notes.map((n) => rectOf({ note: n })))).filter(Boolean).map((r) => toStage(r, cam));
      if (rs.length) { const x = Math.min(...rs.map((r) => r.x)), y = Math.min(...rs.map((r) => r.y));
        popRect = { x, y, w: Math.max(...rs.map((r) => r.x + r.w)) - x, h: Math.max(...rs.map((r) => r.y + r.h)) - y }; }
    }
    const badgeRect = v >= ramp.up - 0.2 && v <= ramp.end + 0.2 ? toStage(await rectOf({ sel: "#extract" }), cam) : null;
    const annotRect = v < speech[0].click ? toStage(await rectOf({ speaker: RUN.people.at(-1) }), cam) : null;

    // pop-out lift on the real note element
    for (const p of cues.pops) {
      if (v >= p.from - 0.05 && v <= p.to + 0.05) {
        const k = v < p.from + 0.45 ? popEase(prog(v, p.from, 0.45)) : v > p.from + 0.45 + p.hold ? 1 - camEase(prog(v, p.from + 0.45 + p.hold, 0.35)) : 1;
        for (const i of p.notes) await frame.evaluate((i, k, lift) => {
          const n = document.querySelectorAll(".note")[i]; if (!n) return;
          const tilt = parseFloat(n.style.getPropertyValue("--tilt")) || 0;
          n.style.transform = k > 0.001 ? `translateY(${-10 * k}px) scale(${1 + lift * k}) rotate(${tilt * (1 - k)}deg)` : "";
          n.style.zIndex = k > 0.001 ? 5 : "";
          n.style.boxShadow = k > 0.001 ? `0 2px 2px rgba(60,45,20,.12), 0 ${18 + 22 * k}px ${22 + 20 * k}px -16px rgba(60,45,20,${0.5 + 0.1 * k})` : "";
        }, i, k, p.notes.length > 1 ? 0.035 : 0.1);
      }
    }

    await page.evaluate((st) => {
      const $ = (id) => document.getElementById(id);
      $("cam").style.transform = `translate(${st.cam.x}px, ${st.cam.y + st.appY}px) scale(${st.cam.s})`;
      $("cam").style.opacity = st.appO;
      $("hook").style.opacity = st.hookO; $("hook").style.transform = `translateY(${st.hookY}px)`;
      $("hook").querySelector("h1").style.clipPath = `inset(-20px ${100 - st.hookReveal}% -20px 0)`;
      $("hook").querySelector(".small").style.opacity = st.hookSmall;
      // subtitle: right side over the empty desk during the meeting, centred under the question in the hook
      const sub = $("sub");
      if (st.sub) {
        sub.style.opacity = st.sub.o; sub.querySelector(".who i").style.background = st.sub.color;
        sub.querySelector(".who span").textContent = st.sub.who; sub.querySelector(".said").textContent = st.sub.text;
        Object.assign(sub.style, st.sub.hook ? { left: "180px", top: "700px", right: "auto", zIndex: 20 } : { left: "auto", right: "60px", top: "450px", zIndex: 1 });
      } else sub.style.opacity = 0;
      $("cursor").style.opacity = st.curO; $("cursor").style.transform = `translate(${st.cur.x - 4}px, ${st.cur.y - 3}px) scale(${st.curS})`;
      $("ring").style.opacity = st.ring.o; $("ring").style.transform = `translate(${st.cur.x - 12}px, ${st.cur.y - 12}px) scale(${st.ring.s})`;
      $("badge").style.opacity = st.badge ? st.badge.o : 0;
      if (st.badge) { $("badge").style.left = st.badge.x + "px"; $("badge").style.top = st.badge.y + "px"; }
      $("annot").style.opacity = st.annot ? st.annot.o : 0;
      if (st.annot) { $("annot").style.left = st.annot.x + "px"; $("annot").style.top = st.annot.y + "px"; }
      $("corner").style.opacity = st.cornerO;
      const pop = $("pop");
      if (st.pop) {
        pop.style.opacity = st.pop.o; pop.querySelector(".t").textContent = st.pop.text; pop.querySelector("small").textContent = st.pop.small || "";
        pop.style.width = st.pop.w + "px"; pop.style.left = st.pop.x + "px"; pop.style.top = st.pop.y + "px"; pop.style.transform = `scale(${st.pop.s})`;
        pop.style.transformOrigin = { left: "100% 50%", right: "0 50%", below: "50% 0" }[st.pop.side];
      } else pop.style.opacity = 0;
      $("outroA").style.opacity = st.outA; $("outroA").style.transform = `translateY(${(1 - st.outA) * 24}px)`;
      $("outroB").style.opacity = st.outB; $("outroB").style.transform = `translateY(${(1 - st.outB) * 24}px)`;
      $("outroC").style.opacity = st.outC; $("outroC").style.transform = `translateY(${(1 - st.outC) * 24}px)`;
    }, {
      cam,
      appO: v < APP_IN ? 0 : Math.min(outEase(prog(v, APP_IN, 0.6)), 1 - prog(v, OUTRO - 0.5, 0.35)), appY: v < APP_IN ? 24 : 24 * (1 - outEase(prog(v, APP_IN, 0.6))),
      hookO: 1 - prog(v, APP_IN - 0.45, 0.35), hookY: -18 * prog(v, APP_IN - 0.45, 0.35),
      hookReveal: 100 * outEase(prog(v, 1.6, 0.8)), hookSmall: outEase(prog(v, 0.2, 0.4)),
      sub: subs.length ? (() => { const s = subs.at(-1); const o = Math.min(prog(v, s.from - 0.15, 0.15), 1 - prog(v, s.to, 0.15));
        return { o, who: s.who, text: s.text, color: colorOf(s.who), hook: !!s.hook }; })() : null,
      cur, curO: v < APP_IN + 3 || v > OUTRO - 0.3 ? 0 : Math.min(prog(v, APP_IN + 3, 0.3), 1 - prog(v, OUTRO - 0.6, 0.3),
        Math.max(clamp01((1.5 - ((cues.clicks.find((c) => c.at > v) || { at: 1e9 }).at - v)) / 0.3), clamp01((1.6 - (v - lastClick)) / 0.3))),
      curS: v - lastClick < 0.08 ? 0.9 : 1,
      ring: { o: v - lastClick < 0.3 ? 1 - (v - lastClick) / 0.3 : 0, s: 0.6 + 1.2 * clamp01((v - lastClick) / 0.3) },
      badge: badgeRect ? { o: Math.min(prog(v, ramp.up - 0.2, 0.2), 1 - prog(v, ramp.end, 0.2)), x: badgeRect.x + badgeRect.w + 26, y: badgeRect.y - 4 } : null,
      annot: annotRect ? { o: Math.min(prog(v, APP_IN + 0.8, 0.3), 1 - prog(v, speech[0].click - 0.6, 0.3)), x: annotRect.x + annotRect.w + 22, y: annotRect.y - 2 } : null,
      cornerO: v < APP_IN ? 0 : Math.min(prog(v, APP_IN + 0.3, 0.4), 1 - prog(v, OUTRO - 0.4, 0.3)),
      pop: popNow && popRect ? (() => {
        const p = popNow, k = v < p.from + 0.45 ? popEase(prog(v, p.from, 0.45)) : v > p.from + 0.45 + p.hold ? 1 - camEase(prog(v, p.from + 0.45 + p.hold, 0.35)) : 1;
        const side = p.place || (popRect.x > VW / 2 ? "left" : "right");
        const w = p.width || 520;
        const x = side === "left" ? popRect.x - w - 40 : side === "right" ? popRect.x + popRect.w + 36 : popRect.x + popRect.w / 2 - w / 2;
        const y = side === "below" ? popRect.y + popRect.h + 34 : popRect.y + popRect.h / 2 - 110;
        return { o: clamp01(k * 1.4), s: 0.86 + 0.14 * k, text: p.text, small: p.small, side, w,
          x: Math.max(30, Math.min(VW - w - 24, x)), y: Math.max(40, Math.min(VH - 290, y)) };
      })() : null,
      outA: v < OUTRO ? 0 : Math.min(outEase(prog(v, OUTRO, 0.6)), 1 - prog(v, OUTRO_B - 0.35, 0.35)),
      outB: v < OUTRO_B ? 0 : Math.min(outEase(prog(v, OUTRO_B, 0.6)), 1 - prog(v, OUTRO_C - 0.35, 0.35)),
      outC: v < OUTRO_C ? 0 : outEase(prog(v, OUTRO_C, 0.6)),
    });

    // 5. capture
    const want = STILLS ? STILLS.find((s) => Math.round(s * FPS) === f) : true;
    if (want !== undefined && want !== false) {
      const { data } = await cdp.send("Page.captureScreenshot", { format: "jpeg", quality: 93 });
      const buf = Buffer.from(data, "base64");
      if (STILLS) fs.writeFileSync(`${OUT}/still-${String(want).padStart(5, "0")}.jpg`, buf);
      else if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once("drain", r));
      encoded++;
    }
    if (f % 150 === 0) {
      const free = os.freemem() / 2 ** 20;
      console.log(`frame ${f}/${NFRAMES}  t=${v.toFixed(1)}s  free RAM ${free.toFixed(0)} MB  ${((Date.now() - t0wall) / 1000).toFixed(0)} s elapsed`);
      while (os.freemem() / 2 ** 20 < 450) { console.log("low RAM: pausing 5 s"); await new Promise((r) => setTimeout(r, 5000)); }
    }
    if (STILLS && f > Math.max(...STILLS) * FPS) break;
  }

  fs.writeFileSync(`${OUT}/timeline.json`, JSON.stringify({ fps: FPS, end: END, audio: cues.audio, sfx: cues.sfx,
    speech, extractAt, landAt, ramp, pops: cues.pops, outro: OUTRO }, null, 2));
  if (ff) { ff.stdin.end(); await new Promise((r) => ff.on("close", r)); }
  await browser.close();
  console.log(`done: ${encoded} frames, ${END.toFixed(1)} s video, ${((Date.now() - t0wall) / 1000).toFixed(0)} s to render`);
})().catch((e) => { console.error("FAILED:", e.stack || e.message); process.exit(1); });
