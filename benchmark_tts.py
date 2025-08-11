#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Benchmark Kokoro and (optionally) CosyVoice 2 on the same text.
Measures: wall time, Real-Time Factor (RTF), and RSS memory.
Optionally runs aeneas or MFA alignment if installed and requested.

Usage:
  python benchmark_tts.py --engine kokoro
  python benchmark_tts.py --engine cosyvoice
  python benchmark_tts.py --engine all
"""
import argparse
import time
import os
import sys
import gc
import wave
import contextlib
import subprocess
import numpy as np
import psutil

SAMPLE_TEXT = (
    "This is a short passage used to benchmark text to speech. "
    "We are measuring speed, stability, and alignment quality. "
    "The tool should generate natural prosody and crisp audio. "
    "Finally, we will compare engines on Real-Time Factor."
)


def write_wav(path, audio, sr=24000):
    audio16 = np.int16(np.clip(audio, -1, 1) * 32767)
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sr)
        f.writeframes(audio16.tobytes())


def audio_duration_sec(path):
    with contextlib.closing(wave.open(path, 'rb')) as wf:
        frames = wf.getnframes()
        return frames / float(wf.getframerate())


def rss_mb():
    return psutil.Process().memory_info().rss / (1024*1024)


def run_kokoro(text, out_wav, voice="af_heart", lang_code="a"):
    t0 = time.perf_counter()
    import soundfile as sf
    from kokoro import KPipeline  # pip install kokoro>=0.9.4  (Apache-2.0)
    pipe = KPipeline(lang_code=lang_code)
    # Generate in one go; Kokoro yields chunks; we concatenate
    audio_all = []
    for _, _, audio in pipe(text, voice=voice, speed=1.0, split_pattern=r"\n+"):
        audio_all.append(audio)
    audio = np.concatenate(audio_all)
    write_wav(out_wav, audio, sr=24000)
    dt = time.perf_counter() - t0
    dur = audio.shape[0] / 24000.0
    return dt, dur


def run_cosyvoice(text, out_wav, lang="en"):
    """
    CosyVoice 2 wrapper.
    Install: pip install -U cosyvoice   (per repo README)
    This code path is best-effort; check upstream if the API changes.
    """
    t0 = time.perf_counter()
    try:
        # The actual API may vary by version; try a common pattern:
        from cosyvoice import CosyVoice
    except Exception as e:
        print("CosyVoice not installed or import failed:", e)
        return None, None
    # Load a recommended checkpoint (default weights will be downloaded on first use)
    try:
        model = CosyVoice("cosyvoice2-0.5B")  # adjust if needed per README
        wav = model.tts(text, lang=lang)      # returns numpy float32 PCM mono
    except Exception as e:
        print("CosyVoice runtime error:", e)
        return None, None
    write_wav(out_wav, wav, sr=24000)
    dt = time.perf_counter() - t0
    dur = len(wav) / 24000.0
    return dt, dur


def maybe_align_with_aeneas(audio_path, text, out_srt):
    """Optional lightweight alignment if aeneas is installed.
       NOTE: aeneas is AGPL-3. Use only if that license is acceptable."""
    try:
        import tempfile
        import json
        import subprocess
        import shutil
        tmpdir = tempfile.mkdtemp()
        text_path = os.path.join(tmpdir, "text.txt")
        with open(text_path, "w", encoding="utf-8") as f:
            # one sentence per line gives line-level SRTs
            from nltk import sent_tokenize, download
            try:
                download("punkt", quiet=True)
            except:
                pass
            for s in [s.strip() for s in __import__("nltk").sent_tokenize(text) if s.strip()]:
                f.write(s + "\n")
        map_json = os.path.join(tmpdir, "map.json")
        cfg = "task_language=en|is_text_type=plain|os_task_file_format=json"
        subprocess.check_call([
            sys.executable, "-m", "aeneas.tools.execute_task",
            audio_path, text_path, cfg, map_json
        ])
        # Convert minimal JSON to SRT
        data = __import__("json").loads(
            open(map_json, "r", encoding="utf-8").read())
        entries = data["fragments"]

        def fmt(t):
            ms = int(round(t*1000))
            h, ms = divmod(ms, 3600000)
            m, ms = divmod(ms, 60000)
            s, ms = divmod(ms, 1000)
            return f"{h:02}:{m:02}:{s:02},{ms:03}"
        with open(out_srt, "w", encoding="utf-8") as srt:
            for i, fr in enumerate(entries, 1):
                srt.write(
                    f"{i}\n{fmt(float(fr['begin']))} --> {fmt(float(fr['end']))}\n{fr['lines'][0]}\n\n")
        return True
    except Exception as e:
        print("aeneas alignment skipped:", e)
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--engine", choices=["kokoro", "cosyvoice", "all"], default="kokoro")
    ap.add_argument("--text", default=SAMPLE_TEXT)
    ap.add_argument("--align", action="store_true",
                    help="Try aeneas if installed (AGPL).")
    args = ap.parse_args()

    engines = [args.engine] if args.engine != "all" else [
        "kokoro", "cosyvoice"]
    os.makedirs("bench_out", exist_ok=True)

    for eng in engines:
        print(f"\n== Benchmark: {eng} ==")
        before_mem = rss_mb()
        if eng == "kokoro":
            dt, dur = run_kokoro(args.text, "bench_out/kokoro.wav")
        else:
            dt, dur = run_cosyvoice(args.text, "bench_out/cosyvoice.wav")
        after_mem = rss_mb()
        if dt is None:
            print("Skipped (engine not available).")
            continue
        rtf = dt / max(dur, 1e-6)
        print(
            f"Time: {dt:.2f}s | Audio: {dur:.2f}s | RTF: {rtf:.2f} | ΔRSS: {after_mem-before_mem:.1f} MB")

        if args.align:
            wav = "bench_out/kokoro.wav" if eng == "kokoro" else "bench_out/cosyvoice.wav"
            ok = maybe_align_with_aeneas(
                wav, args.text, wav.replace(".wav", ".srt"))
            print("Alignment:", "aeneas OK" if ok else "skipped/failed")

        gc.collect()


if __name__ == "__main__":
    main()
