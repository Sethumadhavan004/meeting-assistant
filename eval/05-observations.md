# 05 · Observations

_Qualitative notes from runs, dated. Append, don't rewrite._

## 2026-10-24 · Stage 2 setup and smoke test

Evidence: `raw/smoke-2026-10-24/` (one-line trivial prompt; **not** part of the results).

- **The demo start script didn't match the eval settings for the 4B model.** It used the Vulkan
  binary (prompt ops could go to the iGPU), presence penalty 1.0, auto server slots, and always
  loaded the vision projector; `--no-mmproj` couldn't override it (`/props` still showed
  `vision: true`). Replaced with `scripts/start_bonsai.ps1`, where every flag is explicit. Details in `01-setup.md`.
  Lesson: **check `/props` after starting a server**. A flag on the command line isn't proof it was applied.
- **The earlier manual Bonsai runs probably had these confounds too** (Vulkan op-offload, presence
  penalty 1.0, mmproj RAM). The manual numbers stay historical; see `07-limitations.md`.
- **The thinking toggle works both ways** on Bonsai and Granite: think off → `thinking_chars = 0`;
  think on → thinking separated from the answer. Even on a one-line meeting, thinking took
  ~14× the output tokens (24 → 333) and ~7× the time.
- **RAM pressure is real.** Granite running while the Bonsai server was still loaded left
  `ram_min_avail_gb = 0.12`, at the edge of swapping. Confirms the run order: stop the Bonsai server
  before the Ollama runs, browser closed.
- **First-prompt load time.** Ollama's `wall_s` for the first prompt of a batch includes model
  load (`load_s` 5.9–8.1 s); the Bonsai server is preloaded (`load_s = 0`). Compare
  time-to-answer as `wall_s − load_s`.
- Tooling: `Tee-Object` in Windows PowerShell 5.1 writes UTF-16 and locks the file, so the
  first server log (`raw/server-logs/bonsai-20261024-185627.log`) mixes encodings. The launcher
  now uses llama-server's own `--log-file`. That log is kept as captured.
