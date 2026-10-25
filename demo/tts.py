"""Kokoro (open-weight TTS, CPU) for the demo video only. Not part of the app.
usage: tts.py samples            -> voice-samples/<voice>.wav, one line per candidate voice
       tts.py script <map.json>  -> clips/<n>_<speaker>.wav for the frozen script"""
import json, sys, time
from pathlib import Path
import soundfile as sf
from kokoro_onnx import Kokoro

HERE = Path(__file__).parent
k = Kokoro(str(HERE / "kokoro/kokoro-v1.0.int8.onnx"), str(HERE / "kokoro/voices-v1.0.bin"))
LINE = "I'll book the train tickets for all four of us by tomorrow."

if sys.argv[1] == "samples":
    for v in ["hm_omega", "hm_psi", "hf_alpha", "hf_beta", "am_michael", "am_adam", "am_echo", "bm_george", "bm_lewis", "am_puck"]:
        t0 = time.time()
        audio, sr = k.create(LINE, voice=v, speed=1.0, lang="en-us")
        sf.write(HERE / f"voice-samples/{v}.wav", audio, sr)
        print(f"{v}: {len(audio)/sr:.1f} s audio in {time.time()-t0:.1f} s")

if sys.argv[1] == "script":
    # the frozen script (brag-plan.md) and the voices the author chose by ear, 2026-10-26
    VOICE = {"Sethu": "am_michael", "Goutham": "bm_lewis", "Akhash": "am_echo", "Ram": "am_adam"}
    lines = json.loads((HERE / "script.json").read_text(encoding="utf-8"))
    (HERE / "clips").mkdir(exist_ok=True)
    for i, (who, text) in enumerate(lines, 1):
        audio, sr = k.create(text, voice=VOICE[who], speed=1.0, lang="en-us")
        sf.write(HERE / f"clips/{i}_{who}.wav", audio, sr)
        print(f"{i} {who}: {len(audio)/sr:.2f} s")
