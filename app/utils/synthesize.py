from typing import List, Tuple, Optional
import hashlib
import os
import numpy as np
import wave


def _hash_key(voice: str, lang_code: str, speed: float, sr: int, text: str) -> str:
    h = hashlib.sha1(
        f"{voice}|{lang_code}|{speed}|{sr}|{text}".encode("utf-8")).hexdigest()
    return h[:16]


def _read_wav_mono16(path: str) -> Tuple[np.ndarray, int]:
    with wave.open(path, "rb") as w:
        sr = w.getframerate()
        frames = w.readframes(w.getnframes())
        audio = np.frombuffer(frames, dtype="<i2").astype(np.float32) / 32767.0
        return audio, sr


def _write_wav_mono16(path: str, audio: np.ndarray, sr: int):
    a16 = (np.clip(audio, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(a16.tobytes())


def synthesize_kokoro_chunks(
    chunks: List[str],
    voice: str = "af_heart",
    lang_code: str = "a",
    speed: float = 1.0,
    sr: int = 24000,
    *,
    repo_id: Optional[str] = None,
    cache_dir: Optional[str] = None,
) -> Tuple[List[np.ndarray], int]:
    """
    Return list of per-chunk mono float32 arrays and the sample rate.
    If cache_dir is provided, each chunk is cached as 16-bit PCM WAV and reused on re-runs.
    """
    from kokoro import KPipeline
    pipe = KPipeline(lang_code=lang_code, **
                     ({"repo_id": repo_id} if repo_id else {}))

    use_cache = bool(cache_dir)
    if use_cache:
        os.makedirs(cache_dir, exist_ok=True)

    wavs: List[np.ndarray] = []
    if use_cache:
        # Generate per chunk (enables cache)
        for txt in chunks:
            key = _hash_key(voice, lang_code, speed, sr, txt)
            cpath = os.path.join(cache_dir, f"{key}.wav")
            if os.path.isfile(cpath):
                audio, read_sr = _read_wav_mono16(cpath)
                if read_sr != sr:
                    # rare; re-synthesize to desired sr
                    pass
                wavs.append(audio.astype(np.float32, copy=False))
                continue
            # synthesize single chunk
            for _, _, wav in pipe(txt, voice=voice, speed=float(speed)):
                arr = np.asarray(wav, dtype=np.float32)
                wavs.append(arr)
                _write_wav_mono16(cpath, arr, sr)
                break
    else:
        # Faster batch synth when not caching
        text = "\n".join(chunks)
        for _, _, wav in pipe(text, voice=voice, speed=float(speed), split_pattern=r"\n+"):
            wavs.append(np.asarray(wav, dtype=np.float32))

    return wavs, sr


def concat_audio(wavs: List[np.ndarray]) -> np.ndarray:
    return np.concatenate(wavs) if wavs else np.zeros(0, dtype=np.float32)
