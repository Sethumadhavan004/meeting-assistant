# 01 · Setup

## Hardware

| item | value | why it matters |
|---|---|---|
| machine | HP L14 | |
| CPU | AMD Ryzen 4000-series (Zen 2) | |
| SIMD | AVX2 yes, AVX-512 / VNNI no | decides which optimized kernels llama.cpp can use |
| RAM | 8 GB DDR4-2667, **single channel** (1 of 2 slots) | caps memory bandwidth |
| visible RAM | 7.4 GB (650 MB reserved for integrated Radeon graphics) | |
| available RAM | ~2.7 GB with a browser open, more with it closed | browser closed for all runs |
| GPU | integrated AMD Radeon, not used | **all runs are CPU-only** |
| OS / shell | Windows 11, PowerShell | |

### Memory bandwidth ceiling

Generating one token reads (roughly) every weight once, so on a memory-bound CPU:

```
max tokens/s ≈ memory bandwidth ÷ model file size
bandwidth    = 2667 MT/s × 8 bytes × 1 channel = 21.3 GB/s
```

`eval_runner.py` logs this ceiling and the % of it each run reaches (`bw_ceiling_tps`, `pct_of_ceiling`).

## Runtimes

| runtime | version | endpoint | used for |
|---|---|---|---|
| Ollama | 0.40.10 | `http://localhost:11434/api/chat` (native, exact token counts and durations) | granite, phi |
| PrismML llama.cpp fork (Bonsai demo repo) | _fill in_ | `http://localhost:8080/v1/chat/completions` (with `timings` block) | bonsai |
| Python | 3.13.5, deps in `requirements.txt` | | `eval_runner.py` |

## Models under test

| key | model | runtime | quant | file size | thinking? |
|---|---|---|---|---|---|
| granite | `granite4.2:3b` | Ollama | Q4_K_M | ~2.2 GB _(verify)_ | yes (on/off) |
| phi | `phi4-mini` | Ollama | Q4_K_M | ~2.5 GB _(verify)_ | no |
| bonsai | Ternary-Bonsai-2-4B (`Ternary-Bonsai-2-4B-PQ2_0.gguf`) | llama-server (PrismML fork) | PQ2_0, 2.13 bpw, group 128 | _measured in Stage 2_ | yes (on/off) |

Bonsai's model lives in `models/Bonsai-demo/models/bonsai2-gguf/4B/` (not committed).
The server also auto-loads a multimodal projector (`...mmproj-Q8_0.gguf`), which adds RAM
that the text task doesn't need. See [07-limitations.md](07-limitations.md).

## Starting the Bonsai server

It must run in **its own terminal, left open** (the server exits when its terminal closes):

```powershell
cd D:\projects\meeting-assistant\models\Bonsai-demo
$env:BONSAI_MODEL = "4B"     # without this it defaults to the 27B model
$env:BONSAI_NGL   = "0"      # force CPU (otherwise it auto-picks GPU, -ngl 99)
$env:BONSAI_CTX   = "4096"   # match Ollama's context (default was 8192)
.\scripts\start_llama_server.ps1
```
