"""
eval_runner.py - one runner for every model, every prompt, thinking on/off.

Why this exists (instead of typing into terminals):
  1. Every call is a FRESH single-turn request -> no chat history leaking between prompts
     (this was the multi-turn confound in the Ollama runs).
  2. The SAME prompt file goes to every model -> no wording differences.
  3. Speed, tokens, RAM and CPU are logged automatically to runs.csv -> no screenshots.
  4. Full thinking + answer text is saved per run in outputs/ -> raw evidence for scoring.

Setup (once):
  pip install requests psutil
  mkdir prompts      -> put one meeting per .txt file in here (e.g. m01_pricing.txt)

Usage:
  python eval_runner.py baseline                         # model NOT loaded, browser closed
  python eval_runner.py run --model granite --think on
  python eval_runner.py run --model granite --think off
  python eval_runner.py run --model phi     --think off   # phi4-mini has no thinking mode
  python eval_runner.py run --model bonsai  --think on    # needs llama-server running on :8080
  python eval_runner.py run --model bonsai  --think off
"""
import argparse
import csv
import datetime
import json
import pathlib
import re
import threading
import time

import psutil
import requests

# ---------------- config: edit here, nowhere else ----------------
OLLAMA = "http://localhost:11434"
LLAMA = "http://localhost:8080"
CTX = 4096              # same context size for every model (fairness)
MAX_TOKENS = 3000       # cap so a rambling thinking run can't go forever
BANDWIDTH_GBPS = 21.3   # DDR4-2667 single channel = 2667 MT/s x 8 bytes
TIMEOUT_S = 1800

# file_gb: check the real .gguf / ollama size and correct it - it drives the % of bandwidth ceiling
MODELS = {
    # sizes measured 2026-10-24 (decimal GB, to match BANDWIDTH_GBPS): Ollama /api/tags, Bonsai .gguf on disk
    "granite": {"backend": "ollama", "name": "granite4.2:3b", "quant": "Q4_K_M", "file_gb": 2.244, "can_think": True},
    "phi":     {"backend": "ollama", "name": "phi4-mini",     "quant": "Q4_K_M", "file_gb": 2.492, "can_think": False},
    "bonsai":  {"backend": "llama",  "name": "bonsai-4b",     "quant": "PQ2_0",  "file_gb": 1.146, "can_think": True},
}

ROOT = pathlib.Path(__file__).parent
PROMPTS = ROOT / "prompts"
OUTPUTS = ROOT / "outputs"
CSV_PATH = ROOT / "runs.csv"
BASELINE = ROOT / "baseline.json"
GB = 1024 ** 3

FIELDS = [
    "run_id", "timestamp", "model", "backend", "quant", "thinking", "prompt_id", "rep", "ctx", "temperature",
    "prompt_tok", "prompt_tps", "out_tok", "gen_tps", "thinking_chars", "answer_chars",
    "wall_s", "load_s", "finish", "ram_peak_used_gb", "ram_min_avail_gb", "ram_delta_gb",
    "cpu_avg_pct", "bw_ceiling_tps", "pct_of_ceiling",
]


# ---------------- system sampler: polls RAM/CPU in the background while the model works ----------------
class Sampler(threading.Thread):
    def __init__(self, every_s=0.25):
        super().__init__(daemon=True)
        self.every_s = every_s
        self._stop = threading.Event()
        self.peak_used = 0
        self.min_avail = float("inf")
        self.cpu = []

    def run(self):
        psutil.cpu_percent(None)  # first call primes the counter
        while not self._stop.is_set():
            vm = psutil.virtual_memory()
            self.peak_used = max(self.peak_used, vm.used)
            self.min_avail = min(self.min_avail, vm.available)
            self.cpu.append(psutil.cpu_percent(None))
            time.sleep(self.every_s)

    def stop(self):
        self._stop.set()
        self.join()


def split_think(text):
    """Fallback: if the server didn't separate reasoning, pull out a <think>...</think> block ourselves."""
    m = re.search(r"<think>(.*?)</think>", text, re.DOTALL)
    if not m:
        return "", text.strip()
    return m.group(1).strip(), text[m.end():].strip()


# ---------------- backends: both return the same dict shape ----------------
def call_ollama(cfg, prompt, think, temp):
    # Native /api/chat (not /v1) because it returns exact token counts and durations.
    body = {
        "model": cfg["name"],
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {"temperature": temp, "num_ctx": CTX, "num_predict": MAX_TOKENS},
    }
    if cfg["can_think"]:
        body["think"] = think
    r = requests.post(f"{OLLAMA}/api/chat", json=body, timeout=TIMEOUT_S).json()
    if "error" in r:
        raise RuntimeError(r["error"])
    ns = 1e9
    msg = r.get("message", {})
    thinking, answer = msg.get("thinking") or "", msg.get("content") or ""
    if not thinking:
        thinking, answer = split_think(answer)
    p_n, p_d = r.get("prompt_eval_count", 0), r.get("prompt_eval_duration", 0)
    e_n, e_d = r.get("eval_count", 0), r.get("eval_duration", 0)
    return {
        "thinking": thinking, "answer": answer,
        "prompt_tok": p_n, "prompt_tps": p_n / (p_d / ns) if p_d else 0,
        "out_tok": e_n, "gen_tps": e_n / (e_d / ns) if e_d else 0,
        "load_s": r.get("load_duration", 0) / ns, "finish": r.get("done_reason", ""),
    }


def call_llama(cfg, prompt, think, temp):
    # OpenAI-style endpoint; llama-server adds a 'timings' block with exact speeds.
    body = {
        "model": cfg["name"],
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temp,
        "max_tokens": MAX_TOKENS,
        "cache_prompt": False,                                 # measure real prompt processing every time
        "chat_template_kwargs": {"enable_thinking": think},    # thinking on/off per request
    }
    r = requests.post(f"{LLAMA}/v1/chat/completions", json=body, timeout=TIMEOUT_S).json()
    if "error" in r:
        raise RuntimeError(r["error"])
    choice = r["choices"][0]
    msg = choice["message"]
    thinking, answer = msg.get("reasoning_content") or "", msg.get("content") or ""
    if not thinking:
        thinking, answer = split_think(answer)
    t = r.get("timings", {})
    return {
        "thinking": thinking, "answer": answer,
        "prompt_tok": t.get("prompt_n", 0), "prompt_tps": t.get("prompt_per_second", 0),
        "out_tok": t.get("predicted_n", 0), "gen_tps": t.get("predicted_per_second", 0),
        "load_s": 0, "finish": choice.get("finish_reason", ""),
    }


def unload_ollama(cfg):
    # keep_alive=0 frees the RAM so the next model starts clean
    try:
        requests.post(f"{OLLAMA}/api/generate", json={"model": cfg["name"], "keep_alive": 0}, timeout=60)
    except requests.RequestException:
        pass


# ---------------- commands ----------------
def cmd_baseline(_args):
    print("Sampling idle RAM for 5 s (no model loaded, browser closed)...")
    s = Sampler()
    s.start()
    time.sleep(5)
    s.stop()
    data = {"idle_used_gb": round(s.peak_used / GB, 3), "taken": datetime.datetime.now().isoformat(timespec="seconds")}
    BASELINE.write_text(json.dumps(data, indent=2))
    print(data)


def cmd_run(args):
    cfg = MODELS[args.model]
    think = args.think == "on"
    if think and not cfg["can_think"]:
        raise SystemExit(f"{args.model} has no thinking mode - use --think off")

    prompts = sorted(PROMPTS.glob("*.txt"))
    if not prompts:
        raise SystemExit("No prompts found - put .txt files in ./prompts")

    idle = json.loads(BASELINE.read_text())["idle_used_gb"] if BASELINE.exists() else None
    if idle is None:
        print("WARNING: no baseline.json - ram_delta_gb will be blank. Run `baseline` first.")

    OUTPUTS.mkdir(exist_ok=True)
    new_file = not CSV_PATH.exists()
    call = call_ollama if cfg["backend"] == "ollama" else call_llama
    ceiling = BANDWIDTH_GBPS / cfg["file_gb"]

    with CSV_PATH.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new_file:
            w.writeheader()

        for p in prompts:
            text = p.read_text(encoding="utf-8")
            for rep in range(1, args.reps + 1):
                run_id = f"{args.model}_{args.think}_{p.stem}_r{rep}_{datetime.datetime.now():%H%M%S}"
                print(f"-> {run_id} ...", end=" ", flush=True)

                s = Sampler()
                s.start()
                t0 = time.perf_counter()
                try:
                    res = call(cfg, text, think, args.temp)
                except Exception as e:  # keep the batch going; log the failure
                    s.stop()
                    print(f"FAILED: {e}")
                    continue
                wall = time.perf_counter() - t0
                s.stop()

                peak = s.peak_used / GB
                row = {
                    "run_id": run_id, "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
                    "model": args.model, "backend": cfg["backend"], "quant": cfg["quant"],
                    "thinking": args.think, "prompt_id": p.stem, "rep": rep, "ctx": CTX, "temperature": args.temp,
                    "prompt_tok": res["prompt_tok"], "prompt_tps": round(res["prompt_tps"], 2),
                    "out_tok": res["out_tok"], "gen_tps": round(res["gen_tps"], 2),
                    "thinking_chars": len(res["thinking"]), "answer_chars": len(res["answer"]),
                    "wall_s": round(wall, 1), "load_s": round(res["load_s"], 2), "finish": res["finish"],
                    "ram_peak_used_gb": round(peak, 2), "ram_min_avail_gb": round(s.min_avail / GB, 2),
                    "ram_delta_gb": round(peak - idle, 2) if idle is not None else "",
                    "cpu_avg_pct": round(sum(s.cpu) / len(s.cpu), 1) if s.cpu else 0,
                    "bw_ceiling_tps": round(ceiling, 1),
                    "pct_of_ceiling": round(100 * res["gen_tps"] / ceiling, 1) if ceiling else 0,
                }
                w.writerow(row)
                f.flush()  # write each row immediately, so a crash never loses finished runs

                (OUTPUTS / f"{run_id}.md").write_text(
                    f"# {run_id}\n\n## Prompt\n```\n{text}\n```\n\n"
                    f"## Thinking\n```\n{res['thinking'] or '(none)'}\n```\n\n## Answer\n{res['answer']}\n",
                    encoding="utf-8",
                )
                print(f"{row['gen_tps']} t/s, {row['out_tok']} tok, {row['wall_s']} s, peak {row['ram_peak_used_gb']} GB")

    if cfg["backend"] == "ollama":
        unload_ollama(cfg)
    print(f"Done. Rows appended to {CSV_PATH.name}, full texts in outputs/.")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("baseline")
    r = sub.add_parser("run")
    r.add_argument("--model", required=True, choices=MODELS)
    r.add_argument("--think", required=True, choices=["on", "off"])
    r.add_argument("--reps", type=int, default=1)
    r.add_argument("--temp", type=float, default=0.0)
    args = ap.parse_args()
    {"baseline": cmd_baseline, "run": cmd_run}[args.cmd](args)


if __name__ == "__main__":
    main()
