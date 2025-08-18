import argparse
import os
import sys
import numpy as np
import time
from app.utils.extract_text import extract_text
from app.utils.chunk_text import split_sentences
from app.utils.synthesize import (
    synthesize_kokoro_chunks,
    synthesize_cosyvoice2_chunks,
    concat_audio,
)
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


def _create_simple_srt(chunks, wavs, sr, out_srt):
    """Create SRT file with simple timing based on audio duration"""
    def fmt_srt(t):
        ms = int(round(t * 1000))
        h, ms = divmod(ms, 3600000)
        m, ms = divmod(ms, 60000)
        s, ms = divmod(ms, 1000)
        return f"{h:02}:{m:02}:{s:02},{ms:03}"
    
    os.makedirs(os.path.dirname(out_srt), exist_ok=True)
    
    with open(out_srt, "w", encoding="utf-8") as f:
        offset = 0.0
        for i, (chunk, wav) in enumerate(zip(chunks, wavs), 1):
            duration = len(wav) / sr
            start_time = offset
            end_time = offset + duration
            
            f.write(f"{i}\n")
            f.write(f"{fmt_srt(start_time)} --> {fmt_srt(end_time)}\n")
            f.write(f"{chunk.strip()}\n\n")
            
            offset += duration


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", default="out")
    ap.add_argument(
        "--engine", choices=["kokoro", "cosyvoice2"], default="kokoro")
    ap.add_argument("--lang", default="en")
    ap.add_argument("--format", default="srt,vtt")
    ap.add_argument("--voice", default="af_heart")
    ap.add_argument("--speed", type=float, default=1.0)
    ap.add_argument("--max-chars", type=int, default=240)
    ap.add_argument("--num-jobs", type=int, default=4)
    ap.add_argument("--single-speaker", action="store_true")
    ap.add_argument("--cache-dir", default=None)
    ap.add_argument("--fast-mode", action="store_true", 
                    help="Skip MFA alignment for faster processing (simple timing only)")

    # CosyVoice2 specific
    ap.add_argument("--cosy_mode", choices=["auto", "zero", "cross"], default="auto",
                    help="Zero-shot uses text+ref to generate tokens; cross is more stable on CPU.")
    ap.add_argument("--cosy_ref", default=None,
                    help="Path to 16kHz mono reference WAV for CosyVoice2.")
    ap.add_argument("--cosy_prompt", default="",
                    help="Style prompt text for CosyVoice2 (e.g., 'neutral, calm').")

    # Optional post-processing
    ap.add_argument("--post", choices=["none", "brighten"], default="none",
                    help="Optional post-processing on the synthesized audio (CosyVoice2 only).")

    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    text = extract_text(args.inp)
    chunks = split_sentences(text, max_chars=args.max_chars)
    print(f"Chunks: {len(chunks)} (max_chars={args.max_chars})")

    t0 = time.time()

    # Preload models for better performance (only if not already loaded)
    from app.services.models import preload_models, _COSYVOICE2_SINGLETON, _KOKORO
    if _COSYVOICE2_SINGLETON is None or _KOKORO is None:
        print("Preloading models...")
        preload_models()
    else:
        print("Models already loaded, skipping preload")

    if args.engine == "kokoro":
        wavs, sr = synthesize_kokoro_chunks(
            chunks,
            voice=args.voice,
            lang_code="a",
            speed=args.speed,
            cache_dir=args.cache_dir,
            post=args.post,  # accepted but ignored by kokoro synth
        )
    else:
        wavs, sr = synthesize_cosyvoice2_chunks(
            chunks,
            model_dir=None,
            ref_wav=args.cosy_ref,
            prompt_text=args.cosy_prompt,
            stream=False,
            fp16=False,
            # cosy_mode=args.cosy_mode,
            # post=args.post,
            mode=args.cosy_mode,
            speed=args.speed,
        )

    full = concat_audio(wavs)
    wav_path = os.path.join(args.out, "audio.wav")
    _save_full_wav(wav_path, full, sr)

    srt_path = os.path.join(args.out, "captions.srt")
    
    # Skip expensive MFA alignment for short text or when fast-mode is enabled
    total_chars = sum(len(chunk) for chunk in chunks)
    if args.fast_mode or total_chars < 500:  # Skip MFA for short text or fast mode
        reason = "fast-mode enabled" if args.fast_mode else f"short text ({total_chars} chars)"
        print(f"Skipping MFA alignment ({reason}). Using simple timing.")
        _create_simple_srt(chunks, wavs, sr, srt_path)
    else:
        mfa_align_chunks_to_srt(
            chunks,
            wavs,
            sr,
            srt_path,
            num_jobs=args.num_jobs,
            single_speaker=args.single_speaker,
        )

    if "vtt" in args.format.split(","):
        srt_to_vtt(srt_path, os.path.join(args.out, "captions.vtt"))
    print("Done →", args.out)

    wall = time.time() - t0
    dur_sec = len(full) / sr if sr else 0
    rtf = wall / dur_sec if dur_sec else 0
    print(f"Wall: {wall:.2f}s  Audio: {dur_sec:.2f}s  RTF: {rtf:.2f}")


if __name__ == "__main__":
    # allow `python app/main.py` and `python -m app.main`
    if __package__ is None:
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    main()
