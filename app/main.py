import argparse
import os
import sys
import time
import numpy as np
from app.utils.extract_text import extract_text
from app.utils.chunk_text import split_sentences
from app.utils.synthesize import synthesize_kokoro_chunks, concat_audio
from app.utils.align_subtitles import mfa_align_chunks_to_srt
from app.utils.make_captions import srt_to_vtt


def _save_full_wav(path, audio, sr=24000):
    import wave
    a16 = (np.clip(audio, -1, 1) * 32767).astype("<i2").tobytes()
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sr)
        f.writeframes(a16)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", default="out")
    ap.add_argument("--engine", choices=["kokoro"], default="kokoro")
    ap.add_argument("--lang", default="en")
    ap.add_argument("--format", default="srt,vtt")
    ap.add_argument("--voice", default="af_heart")
    ap.add_argument("--speed", type=float, default=1.0)
    ap.add_argument("--max-chars", type=int, default=240)
    ap.add_argument("--num-jobs", type=int, default=4)
    ap.add_argument("--single-speaker", action="store_true", default=True)
    ap.add_argument("--cache-dir", default=None,
                    help="Cache dir for per-chunk WAVs (default: OUT/cache)")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    cache_dir = args.cache_dir if args.cache_dir is not None else os.path.join(
        args.out, "cache")

    text = extract_text(args.inp).strip()
    if not text:
        raise SystemExit("Input text is empty after extraction.")
    chunks = split_sentences(text, max_chars=args.max_chars)
    print(f"Chunks: {len(chunks)} (max_chars={args.max_chars})")

    t0 = time.time()

    # Synthesize per-chunk (with caching)
    wavs, sr = synthesize_kokoro_chunks(
        chunks, voice=args.voice, lang_code="a", speed=args.speed,
        repo_id="hexgrad/Kokoro-82M", cache_dir=cache_dir
    )
    full = concat_audio(wavs)
    wav_path = os.path.join(args.out, "audio.wav")
    _save_full_wav(wav_path, full, sr)

    # Align via MFA, produce SRT
    srt_path = os.path.join(args.out, "captions.srt")
    mfa_align_chunks_to_srt(
        chunks, wavs, sr, srt_path,
        num_jobs=args.num_jobs, single_speaker=args.single_speaker,
        conda_env="aligner", verbose=False
    )

    formats = {f.strip().lower() for f in args.format.split(",")}
    if "vtt" in formats:
        srt_to_vtt(srt_path, os.path.join(args.out, "captions.vtt"))

    wall = time.time() - t0
    dur_sec = len(full) / sr if sr else 0.0
    rtf = (wall / dur_sec) if dur_sec else 0.0
    print(f"Done → {args.out}")
    print(f"Wall: {wall:.2f}s  Audio: {dur_sec:.2f}s  RTF: {rtf:.2f}")


if __name__ == "__main__":
    if __package__ is None:
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    main()
