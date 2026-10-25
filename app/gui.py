"""
gui.py - record a meeting with "who is speaking" buttons, transcribe locally, extract action items.

v1 speaker labelling without diarization: click your name, speak, click it again (or click the next
speaker). Each turn is transcribed by Moonshine (on CPU) and added as "Name: text", the same format the
eval tested. The transcript box is editable, so speech-to-text mistakes can be fixed before extraction.

Usage:  python app/gui.py            (Bonsai server on :8080, or pick phi/granite for Ollama)
"""
import datetime
import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

import numpy as np
import sounddevice as sd

from core import BACKENDS, ROOT, notes

RATE = 16_000            # Moonshine expects 16 kHz mono
MAX_CLIP_S = 30          # Moonshine accepts 0.1-64 s per call; long turns are split at a quiet point
NAMES = "Akhash, Goutham, Muhil, Priya, Eric, Darcy, Elizabeth"


def split_clip(audio):
    """Split audio into pieces <= MAX_CLIP_S, cutting at the quietest 100 ms in the last third of each."""
    pieces, step = [], RATE // 10
    while len(audio) > MAX_CLIP_S * RATE:
        lo, hi = int(MAX_CLIP_S * RATE * 2 / 3), MAX_CLIP_S * RATE
        energy = [np.abs(audio[i:i + step]).mean() for i in range(lo, hi - step, step)]
        cut = lo + int(np.argmin(energy)) * step
        pieces.append(audio[:cut])
        audio = audio[cut:]
    return pieces + [audio]


def transcribe(model, tokenizer, audio):
    texts = []
    for piece in split_clip(audio):
        if len(piece) < RATE // 5:  # under 0.2 s: a click, not speech
            continue
        tokens = model.generate(piece[None, :].astype(np.float32))
        texts.append(tokenizer.decode_batch(tokens)[0].strip())
    return " ".join(t for t in texts if t)


class App:
    def __init__(self, root):
        self.root = root
        root.title("Meeting assistant (local)")
        self.model = self.tokenizer = None
        self.speaker, self.chunks, self.stream = None, [], None
        self.jobs = queue.Queue()  # (speaker, audio) turns waiting for transcription, in order
        self.ui = queue.Queue()    # UI updates from worker threads; only the main thread touches tkinter

        top = ttk.Frame(root, padding=8)
        top.pack(fill="x")
        ttk.Label(top, text="Participants:").pack(side="left")
        self.names = tk.StringVar(value=NAMES)
        ttk.Entry(top, textvariable=self.names, width=60).pack(side="left", padx=4)
        ttk.Button(top, text="Set", command=self.make_buttons).pack(side="left")
        self.backend = tk.StringVar(value="bonsai")
        ttk.OptionMenu(top, self.backend, "bonsai", *BACKENDS).pack(side="right")
        ttk.Label(top, text="Model:").pack(side="right")

        self.buttons_frame = ttk.Frame(root, padding=(8, 0))
        self.buttons_frame.pack(fill="x")
        self.buttons = {}

        self.status = tk.StringVar(value="Loading speech model...")
        ttk.Label(root, textvariable=self.status, padding=(8, 4)).pack(fill="x")

        panes = ttk.PanedWindow(root, orient="horizontal")
        panes.pack(fill="both", expand=True, padx=8, pady=4)
        self.transcript = tk.Text(panes, wrap="word", width=60, height=24, font=("Segoe UI", 10))
        self.output = tk.Text(panes, wrap="none", width=70, height=24, font=("Consolas", 9))
        panes.add(self.transcript, weight=1)
        panes.add(self.output, weight=1)

        bottom = ttk.Frame(root, padding=8)
        bottom.pack(fill="x")
        ttk.Button(bottom, text="Open transcript...", command=self.open_file).pack(side="left")
        ttk.Button(bottom, text="Extract action items", command=self.extract).pack(side="left", padx=6)
        ttk.Button(bottom, text="Save", command=self.save).pack(side="left")

        self.make_buttons()
        self.poll()
        threading.Thread(target=self.load_model, daemon=True).start()
        threading.Thread(target=self.worker, daemon=True).start()

    # ---- speech model ----
    def load_model(self):
        from moonshine_onnx import MoonshineOnnxModel, load_tokenizer
        self.model, self.tokenizer = MoonshineOnnxModel(model_name="moonshine/base"), load_tokenizer()
        self.set_status("Ready. Click a name to start their turn; click again to stop.")

    def worker(self):
        """Transcribe finished turns one at a time, in the order they were spoken."""
        while True:
            speaker, audio = self.jobs.get()
            while self.model is None:
                threading.Event().wait(0.5)
            self.set_status(f"Transcribing {speaker}'s turn ({len(audio) / RATE:.0f} s)...")
            text = transcribe(self.model, self.tokenizer, audio)
            if text:
                self.ui.put((self.append_line, f"{speaker}: {text}"))
            self.set_status("Ready." if self.speaker is None else f"Recording {self.speaker}...")

    # ---- recording ----
    def make_buttons(self):
        for b in self.buttons.values():
            b.destroy()
        self.buttons = {}
        for name in [n.strip() for n in self.names.get().split(",") if n.strip()]:
            b = tk.Button(self.buttons_frame, text=name, width=11, command=lambda n=name: self.toggle(n))
            b.pack(side="left", padx=2, pady=4)
            self.buttons[name] = b

    def toggle(self, name):
        previous = self.speaker
        self.stop_turn()
        if previous != name:
            self.start_turn(name)

    def start_turn(self, name):
        self.speaker, self.chunks = name, []
        self.stream = sd.InputStream(samplerate=RATE, channels=1, dtype="float32",
                                     callback=lambda data, *_: self.chunks.append(data[:, 0].copy()))
        self.stream.start()
        self.buttons[name].configure(bg="#e34948", fg="white", text=f"● {name}")
        self.set_status(f"Recording {name}...")

    def stop_turn(self):
        if self.stream is None:
            return
        self.stream.stop()
        self.stream.close()
        name, audio = self.speaker, np.concatenate(self.chunks) if self.chunks else np.zeros(0, np.float32)
        self.buttons[name].configure(bg="SystemButtonFace", fg="black", text=name)
        self.stream, self.speaker = None, None
        if len(audio) > RATE // 5:
            self.jobs.put((name, audio))

    # ---- transcript and notes ----
    def append_line(self, line):
        if self.transcript.get("1.0", "end").strip():
            self.transcript.insert("end", "\n")
        self.transcript.insert("end", line)
        self.transcript.see("end")

    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text", "*.txt")])
        if path:
            self.transcript.delete("1.0", "end")
            self.transcript.insert("1.0", Path(path).read_text(encoding="utf-8"))

    def extract(self):
        text, backend = self.transcript.get("1.0", "end").strip(), self.backend.get()
        if not text:
            return self.set_status("Transcript is empty.")
        self.set_status(f"Extracting with {backend}... (thinking off; ~10-60 s)")

        def run():
            try:
                md, _ = notes(text, backend)
            except Exception as e:  # server not running, timeout, ...
                md = f"Extraction failed: {e}\nIs the {backend} server running? See app/README.md."
            self.ui.put((self.show_notes, md))
        threading.Thread(target=run, daemon=True).start()

    def show_notes(self, md):
        self.output.delete("1.0", "end")
        self.output.insert("1.0", md)
        self.set_status("Done. Check the 'check' column before sharing.")

    def save(self):
        folder = ROOT / "meetings" / datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "transcript.txt").write_text(self.transcript.get("1.0", "end").strip() + "\n", encoding="utf-8")
        (folder / "notes.md").write_text(self.output.get("1.0", "end").strip() + "\n", encoding="utf-8")
        self.set_status(f"Saved to {folder}")

    def set_status(self, msg):
        self.ui.put((self.status.set, msg))

    def poll(self):
        while not self.ui.empty():
            fn, arg = self.ui.get()
            fn(arg)
        self.root.after(100, self.poll)


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
