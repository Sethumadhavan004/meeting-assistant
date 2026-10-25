// Audio for the demo video: the Kokoro lines at the times the renderer used, plus two quiet Kenney (CC0)
// sounds, a click per cursor click and a soft tap per note landing. No music (licence unverified).
// Loudness-normalised to -16 LUFS, then muxed with out/video.mp4 -> out/brag.mp4
const fs = require("fs");
const { spawnSync } = require("child_process");
const W = __dirname, T = JSON.parse(fs.readFileSync(`${W}/out/timeline.json`, "utf8"));
// Kenney CC0 sounds (kenney.nl: "Interface Sounds", "Impact Sounds"); point SFX at your copy
const SFX = process.env.SFX || "C:/Users/nseth/.claude/plugins/cache/brag/brag/0.4.0/skills/brag/assets/sfx";
const sounds = [
  ...T.audio.map((a) => ({ file: a.file, at: a.at, vol: 1.0 })),
  ...T.sfx.filter((s) => s.kind === "click").map((s) => ({ file: `${SFX}/interface/click_002.ogg`, at: s.at, vol: 0.16 })),
  ...T.sfx.filter((s) => s.kind === "drop").map((s) => ({ file: `${SFX}/impact/impactSoft_medium_000.ogg`, at: s.at, vol: 0.22 })),
];
const args = ["-v", "error", "-y", "-i", `${W}/out/video.mp4`];
sounds.forEach((s) => args.push("-i", s.file));
const chains = sounds.map((s, i) => {
  const ms = Math.round(s.at * 1000);
  return `[${i + 1}:a]aresample=48000,aformat=channel_layouts=stereo,volume=${s.vol},adelay=${ms}|${ms}[a${i}]`;
});
const filter = chains.join(";") + ";" + sounds.map((_, i) => `[a${i}]`).join("") +
  `amix=inputs=${sounds.length}:normalize=0:dropout_transition=0,loudnorm=I=-16:TP=-1.5:LRA=11,apad,atrim=0:${T.end.toFixed(3)}[mix]`;
args.push("-filter_complex", filter, "-map", "0:v", "-map", "[mix]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
  "-t", T.end.toFixed(3), "-movflags", "+faststart", `${W}/out/brag.mp4`);
const r = spawnSync("ffmpeg", args, { stdio: "inherit" });
if (r.status) process.exit(r.status);
console.log(`brag.mp4: ${sounds.length} sounds mixed (${T.audio.length} voice lines)`);
