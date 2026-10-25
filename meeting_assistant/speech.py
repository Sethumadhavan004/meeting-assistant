"""
speech.py - local speech-to-text with Moonshine (ONNX, CPU).

Moonshine accepts 0.1-64 s per call, so long turns are split at the quietest moment before 30 s
instead of cutting a word in half. Measured: ~11x faster than real time on a 4-core laptop.
"""
import threading

import numpy as np

from . import config

RATE = 16_000            # Moonshine expects 16 kHz mono float32
MAX_CLIP_S = 30

_model = _tokenizer = None
_lock = threading.Lock()


def load():
    """Load once (first call downloads the model, ~20 s); safe to call from several threads."""
    global _model, _tokenizer
    with _lock:
        if _model is None:
            from moonshine_onnx import MoonshineOnnxModel, load_tokenizer
            _model = MoonshineOnnxModel(model_name=config.load()["speech"]["model"])
            _tokenizer = load_tokenizer()
    return _model, _tokenizer


def split_clip(audio):
    """Pieces <= MAX_CLIP_S, each cut at the quietest 100 ms in its last third."""
    pieces, step = [], RATE // 10
    while len(audio) > MAX_CLIP_S * RATE:
        lo, hi = int(MAX_CLIP_S * RATE * 2 / 3), MAX_CLIP_S * RATE
        energy = [np.abs(audio[i:i + step]).mean() for i in range(lo, hi - step, step)]
        cut = lo + int(np.argmin(energy)) * step
        pieces.append(audio[:cut])
        audio = audio[cut:]
    return pieces + [audio]


_run_lock = threading.Lock()


def transcribe(audio):
    """16 kHz mono float32 array -> text. One clip at a time: the CPU is the bottleneck anyway."""
    model, tokenizer = load()
    texts = []
    with _run_lock:
        for piece in split_clip(np.asarray(audio, dtype=np.float32)):
            if len(piece) < RATE // 5:  # under 0.2 s: a click, not speech
                continue
            texts.append(tokenizer.decode_batch(model.generate(piece[None, :]))[0].strip())
    return " ".join(t for t in texts if t)
