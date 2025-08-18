# app/utils/synthesize.py
from __future__ import annotations
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Iterator, List, Tuple, Optional
import hashlib
import os
import sys
import threading
import inspect
import torch
import numpy as np
import wave

from app.services.models import get_kokoro, get_cosyvoice2

# ---------------------------
# Common helpers
# ---------------------------

# ---- Cosy frontend feature cache (safe monkey patch) ----
_COSY_FEAT_CACHE_INSTALLED = False
_COSY_LOCK = threading.Lock()
_COSY_OBJ = None  # cached CosyVoice2 object


def _find_cosy_root() -> Path | None:
    """Find the CosyVoice repo root (if vendored), else None for site-package import."""
    env = os.getenv("COSY_ROOT")
    if env:
        p = Path(env)
        if (p / "cosyvoice" / "cli" / "cosyvoice.py").exists():
            return p

    here = Path(__file__).resolve()
    for up in [here, *here.parents]:
        cand = up / "third_party" / "CosyVoice"
        if (cand / "cosyvoice" / "cli" / "cosyvoice.py").exists():
            return cand

    # If we don't find a vendored copy, we'll import the installed package.
    return None


def _install_cosy_feat_cache(cv):
    global _COSY_FEAT_CACHE_INSTALLED
    if _COSY_FEAT_CACHE_INSTALLED:
        return
    fe = getattr(cv, "frontend", None)
    if fe is None or not hasattr(fe, "_extract_speech_feat"):
        return

    import hashlib
    import torch
    _orig = fe._extract_speech_feat
    _cache = {}

    def _key_from_tensor(t: torch.Tensor):
        t_cpu = t.detach().to("cpu", dtype=torch.float32, non_blocking=True).contiguous()
        # Hash first ~256k samples to keep it cheap, plus full length for uniqueness
        n = int(t_cpu.numel())
        head = t_cpu.view(-1)[:min(n, 262144)]
        h = hashlib.sha1(head.numpy().tobytes()).hexdigest()
        return (h, n)

    def _wrapped(t: "torch.Tensor"):
        try:
            k = _key_from_tensor(t)
        except Exception:
            # fallback: no cache
            return _orig(t)
        if k in _cache:
            return _cache[k]
        out = _orig(t)
        _cache[k] = out
        return out

    fe._extract_speech_feat = _wrapped
    setattr(fe, "_feat_cache_enabled", True)
    _COSY_FEAT_CACHE_INSTALLED = True


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


def _to_float32(x) -> np.ndarray:
    """Accepts numpy/tensor/list; returns 1D float32 numpy array in [-1, 1]."""
    if x is None:
        return np.zeros(0, dtype=np.float32)
    try:
        import torch  # noqa: F401
        if isinstance(x, torch.Tensor):
            x = x.detach().cpu().float().numpy()
    except Exception:
        pass
    x = np.asarray(x, dtype=np.float32)
    if x.ndim > 1:
        x = np.squeeze(x)
    return x


def _trim_ref(y: np.ndarray, sr: int = 16000, max_sec: float = 4.0) -> np.ndarray:
    """
    Fast silence trim + cap length to keep embedding stable & quick.
    No heavy deps; simple amp threshold.
    """
    if y is None:
        return None
    y = np.asarray(y, dtype=np.float32).flatten()
    if y.size == 0:
        return y
    thr = 0.01  # tweak if your refs are very quiet/noisy
    idx = np.where(np.abs(y) > thr)[0]
    if idx.size >= 2:
        y = y[idx[0]: idx[-1] + 1]
    # cap to first N seconds
    max_len = int(max_sec * sr)
    if y.size > max_len:
        y = y[:max_len]
    # tiny fade to avoid click
    if y.size > 32:
        y[:16] *= np.linspace(0, 1, 16, dtype=np.float32)
        y[-16:] *= np.linspace(1, 0, 16, dtype=np.float32)
    return y


def _read_wav_mono_float(path: str) -> tuple[np.ndarray, int]:
    """Read a WAV file, downmix to mono float32 in [-1,1]."""
    with wave.open(path, "rb") as w:
        sr = w.getframerate()
        ch = w.getnchannels()
        samp = w.getsampwidth()
        frames = w.readframes(w.getnframes())
    if samp != 2:
        # support 16-bit only (simple, fast)
        raise ValueError(f"Expected 16-bit PCM, got {samp*8}-bit")
    audio = np.frombuffer(frames, dtype="<i2").astype(np.float32) / 32768.0
    if ch > 1:
        audio = audio.reshape(-1, ch).mean(axis=1)
    return audio, sr


def _resample_linear(x: np.ndarray, sr_in: int, sr_out: int) -> np.ndarray:
    if sr_in == sr_out:
        return x
    t_in = np.linspace(0.0, len(x) / sr_in, num=len(x), endpoint=False)
    t_out = np.linspace(0.0, len(x) / sr_in,
                        num=int(round(len(x) * sr_out / sr_in)), endpoint=False)
    return np.interp(t_out, t_in, x).astype(np.float32)


def _float_to_pcm16_bytes(x: np.ndarray) -> bytes:
    return (np.clip(x, -1.0, 1.0) * 32767.0).astype("<i2").tobytes()


def _canon_path(p: str) -> str:
    """Canonicalize a path so the cache hits even if callers pass variants."""
    try:
        return str(Path(p).resolve())
    except Exception:
        return os.path.abspath(p)


@lru_cache(maxsize=128)
def _load_ref_16k_cached_core(canon_path: str) -> np.ndarray:
    """
    Read WAV (16-bit PCM), mono-downmix, resample to 16k, quick-trim, float32.
    Return is contiguous float32 in [-1, 1]. Cached by canonical path.
    """
    ref_float, ref_sr = _read_wav_mono_float(canon_path)
    ref_16k = _resample_linear(ref_float, ref_sr, 16000)
    ref_16k = _trim_ref(ref_16k, 16000, max_sec=4.0)
    if ref_16k.size < int(1.2 * 16000):
        pad = np.zeros(int(1.2 * 16000) - ref_16k.size, dtype=np.float32)
        ref_16k = np.concatenate([ref_16k, pad], axis=0)
    return np.ascontiguousarray(ref_16k.astype(np.float32, copy=False))


def load_ref_16k_trimmed(path: str) -> np.ndarray:
    """Public entry: canonicalize then hit the LRU cache."""
    return _load_ref_16k_cached_core(_canon_path(path))


def _rms_normalize(x: np.ndarray, target_dbfs: float = -20.0) -> np.ndarray:
    x = np.asarray(x, dtype=np.float32).flatten()
    if x.size == 0:
        return x
    rms = np.sqrt(np.mean(np.square(x)) + 1e-12)
    target = 10 ** (target_dbfs / 20.0)
    gain = target / max(rms, 1e-6)
    # cap gain to avoid crazy boosts on silence
    gain = float(np.clip(gain, 0.25, 8.0))
    y = np.clip(x * gain, -1.0, 1.0)
    return y


try:
    import torchaudio  # noqa: F401
    _HAS_TORCHAUDIO = True
except Exception:
    _HAS_TORCHAUDIO = False


def _resample_hq(x: np.ndarray, sr_in: int, sr_out: int) -> np.ndarray:
    if sr_in == sr_out:
        return np.asarray(x, dtype=np.float32)
    if _HAS_TORCHAUDIO:
        import torch
        import torchaudio.functional as AF
        t = torch.from_numpy(np.asarray(x, np.float32)).unsqueeze(0)  # [1, T]
        with torch.inference_mode():
            y = AF.resample(t, sr_in, sr_out)  # CPU kernel
        return y.squeeze(0).numpy().astype(np.float32)
    # fallback to linear if torchaudio isn't available
    return _resample_linear(np.asarray(x, np.float32), sr_in, sr_out)

# ---------------------------
# Kokoro
# ---------------------------


def synthesize_kokoro_chunks(
    chunks: List[str],
    voice: str = "af_heart",
    lang_code: str = "a",
    speed: float = 1.0,
    sr: int = 24000,
    *,
    repo_id: Optional[str] = None,
    cache_dir: Optional[str] = None,
    post: str = "none",  # Add missing parameter
) -> Tuple[List[np.ndarray], int]:
    """Return list of per-chunk mono float32 arrays and the sample rate.
    If cache_dir is provided, each chunk is cached as 16-bit PCM WAV and reused on re-runs.
    """
    # CPU optimization for better performance
    import os
    import torch
    os.environ["OMP_NUM_THREADS"] = str(min(8, os.cpu_count() or 4))
    os.environ["MKL_NUM_THREADS"] = str(min(8, os.cpu_count() or 4))
    torch.set_num_threads(min(8, os.cpu_count() or 4))
    
    pipe = get_kokoro(repo_id=repo_id, lang_code=lang_code) if repo_id else get_kokoro(
        lang_code=lang_code)

    use_cache = bool(cache_dir)
    if use_cache:
        os.makedirs(cache_dir, exist_ok=True)

    wavs: List[np.ndarray] = []
    if use_cache:
        # Check cache first, collect uncached chunks
        uncached_chunks = []
        uncached_indices = []
        
        for i, txt in enumerate(chunks):
            key = _hash_key(voice, lang_code, speed, sr, txt)
            cpath = os.path.join(cache_dir, f"{key}.wav")
            if os.path.isfile(cpath):
                audio, _ = _read_wav_mono16(cpath)
                wavs.append(audio.astype(np.float32, copy=False))
            else:
                # Placeholder for uncached chunk
                wavs.append(None)
                uncached_chunks.append(txt)
                uncached_indices.append(i)
        
        # Process all uncached chunks at once if any
        if uncached_chunks:
            print(f"Processing {len(uncached_chunks)} uncached chunks with Kokoro...")
            text = "\n".join(uncached_chunks)
            uncached_wavs = []
            for _, _, wav in pipe(text, voice=voice, speed=float(speed), split_pattern=r"\n+"):
                uncached_wavs.append(_to_float32(wav))
            
            # Cache and insert results
            for i, (idx, txt, wav_data) in enumerate(zip(uncached_indices, uncached_chunks, uncached_wavs)):
                key = _hash_key(voice, lang_code, speed, sr, txt)
                cpath = os.path.join(cache_dir, f"{key}.wav")
                _write_wav_mono16(cpath, wav_data, sr)
                wavs[idx] = wav_data
    else:
        # Batch process all chunks at once for better performance
        print(f"Processing {len(chunks)} chunks with Kokoro (batch mode)...")
        text = "\n".join(chunks)
        for _, _, wav in pipe(text, voice=voice, speed=float(speed), split_pattern=r"\n+"):
            wavs.append(_to_float32(wav))

    return wavs, sr


def stream_kokoro_chunks(
    chunks: List[str],
    *,
    voice: str = "af_heart",
    speed: float = 1.0,
    lang_code: str = "a",
) -> Iterator[bytes]:
    """Yields raw PCM16 (s16le) bytes per chunk, as soon as each chunk is ready."""
    pipe = get_kokoro(lang_code=lang_code)
    for txt in chunks:
        for _lang, _ph, wav in pipe(txt, voice=voice, speed=float(speed)):
            f32 = _to_float32(wav)
            yield (np.clip(f32, -1.0, 1.0) * 32767.0).astype("<i2").tobytes()
            break  # one audio per chunk

# ---------------------------
# CosyVoice2 (cross-lingual streaming)
# ---------------------------


def stream_cosyvoice2_cross(
    text: str,
    *,
    ref_path: Optional[str] = None,
    ref_wav: Optional[np.ndarray] = None,
    speed: float = 1.0,
) -> Tuple[int, Iterator[bytes]]:
    """
    Returns (sr, chunk_bytes_iter). Chunks are PCM16 bytes at sr=24000.
    Robust to Cosy returning dicts, tuples, tensors, or numpy arrays.
    """
    import torch

    from app.services.models import get_cosyvoice2
    cv = get_cosyvoice2()
    if isinstance(cv, tuple):
        cv = cv[0]

    _install_cosy_feat_cache(cv)

    # --- build 16k mono numpy prompt in [-1,1] ---
    if ref_wav is not None:
        ref_16k = _to_float32(ref_wav)
        ref_16k = _trim_ref(ref_16k, 16000, max_sec=3.2)
    elif ref_path:
        ref_float, ref_sr = _read_wav_mono_float(ref_path)
        ref_16k = _resample_linear(ref_float, ref_sr, 16000)
        ref_16k = _trim_ref(ref_16k, 16000, max_sec=3.2)
    else:
        ref_16k = np.zeros(16000, dtype=np.float32)

    # normalize loudness & ensure CPU torch tensor [1, T]
    ref_16k = _rms_normalize(ref_16k, target_dbfs=-18.0)
    ref_t = torch.from_numpy(ref_16k).to(
        dtype=torch.float32, device="cpu").unsqueeze(0).contiguous()

    # ensure minimum length for frontend windowing
    if ref_t.shape[1] < 16000:  # ~1s minimum
        pad = torch.zeros(1, 16000 - ref_t.shape[1], dtype=torch.float32)
        ref_t = torch.cat([ref_t, pad], dim=1)

    print(f"[Cosy] start text='{text[:60]}' ref={'mem' if ref_wav is not None else ref_path} "
          f"ref_sh={tuple(ref_t.shape)} dtype={ref_t.dtype} dev={ref_t.device} speed={speed}")

    # --- call Cosy (prefer positional; fall back to named) ---
    try:
        raw = cv.inference_cross_lingual(text, ref_t, stream=True)
    except TypeError:
        raw = cv.inference_cross_lingual(
            text=text, prompt_speech_16k=ref_t, stream=True)

    target_sr = 24000
    frame = max(1, target_sr // 33)  # ~30 ms

    def _iter_bytes() -> Iterator[bytes]:
        frame = max(1, target_sr // 33)  # ~30ms worth of samples
        for seg in raw:
            arr = None
            sr = target_sr

            if isinstance(seg, dict):
                for k in ("tts_speech", "tts_speech_24k", "audio", "wav"):
                    if k in seg:
                        arr = seg[k]
                        break
                if "sr" in seg:
                    try:
                        sr = int(seg["sr"])
                    except Exception:
                        pass

            elif isinstance(seg, tuple) and len(seg) == 2:
                arr, sr = seg
                try:
                    sr = int(sr)
                except Exception:
                    sr = target_sr

            elif isinstance(seg, (bytes, bytearray, memoryview)):
                # --- FIX: enforce even-length PCM16 and slice on even boundaries
                b = bytes(seg)
                if not b:
                    continue
                if len(b) & 1:
                    b += b"\x00"  # pad final orphan byte
                step = 2 * frame  # bytes per ~30ms chunk (mono s16)
                for i in range(0, len(b), step):
                    chunk = b[i:i + step]
                    # defensive: guarantee even length
                    if len(chunk) & 1:
                        chunk += b"\x00"
                    yield chunk
                continue

            else:
                arr = seg

            # numeric path
            arr = _to_float32(arr)
            if arr.size == 0:
                continue
            if arr.ndim > 1:
                arr = arr.mean(axis=1)

            if sr != target_sr and sr > 0:
                arr = _resample_hq(arr, sr, target_sr)

            if speed and abs(float(speed) - 1.0) > 0.01:
                tmp_sr = int(round(target_sr * float(speed)))
                tmp_sr = max(8000, min(96000, tmp_sr))
                arr = _resample_hq(arr, target_sr, tmp_sr)
                arr = _resample_hq(arr, tmp_sr, target_sr)

            n = arr.size
            i = 0
            while i < n:
                j = min(n, i + frame)
                yield _float_to_pcm16_bytes(arr[i:j])
                i = j

    return target_sr, _iter_bytes()


def synthesize_cosyvoice2_chunks(
    chunks: List[str],
    *,
    model_dir: Optional[str] = None,
    ref_wav: Optional[str] = None,
    prompt_text: str = "",
    stream: bool = False,
    fp16: bool = False,
    mode: str = "cross",
    speed: float = 1.0,
) -> Tuple[List[np.ndarray], int]:
    """
    Synthesize chunks using CosyVoice2.
    Returns (list_of_audio_arrays, sample_rate).
    """
    from app.services.models import get_cosyvoice2
    cv = get_cosyvoice2()
    if isinstance(cv, tuple):
        cv = cv[0]

    _install_cosy_feat_cache(cv)

    # Load reference if provided
    ref_16k = None
    if ref_wav:
        try:
            ref_float, ref_sr = _read_wav_mono_float(ref_wav)
            ref_16k = _resample_linear(ref_float, ref_sr, 16000)
            ref_16k = _trim_ref(ref_16k, 16000, max_sec=3.2)
            ref_16k = _rms_normalize(ref_16k, target_dbfs=-18.0)
        except Exception:
            ref_16k = None

    if ref_16k is None:
        ref_16k = np.zeros(16000, dtype=np.float32)

    import torch
    ref_t = torch.from_numpy(ref_16k).to(dtype=torch.float32, device="cpu").unsqueeze(0).contiguous()
    
    # Ensure minimum length
    if ref_t.shape[1] < 16000:
        pad = torch.zeros(1, 16000 - ref_t.shape[1], dtype=torch.float32)
        ref_t = torch.cat([ref_t, pad], dim=1)

    wavs = []
    target_sr = 24000

    # Process chunks more efficiently
    print(f"[CosyVoice2] Processing {len(chunks)} chunks on CPU...")
    
    # Set CPU optimization flags
    import os
    os.environ["OMP_NUM_THREADS"] = str(min(8, os.cpu_count() or 4))
    os.environ["MKL_NUM_THREADS"] = str(min(8, os.cpu_count() or 4))
    
    for chunk_text in chunks:
        try:
            # Use cross-lingual mode
            raw = cv.inference_cross_lingual(chunk_text, ref_t, stream=False)
            
            # Handle generator case
            import torch
            if hasattr(raw, '__iter__') and not isinstance(raw, (str, bytes, dict, tuple, list, torch.Tensor, np.ndarray)):
                # It's a generator, collect all chunks
                chunks_data = list(raw)
                if chunks_data:
                    # Take the last complete result
                    raw = chunks_data[-1]
                else:
                    raw = None
            
            # Handle different return formats
            if isinstance(raw, dict):
                for k in ("tts_speech", "tts_speech_24k", "audio", "wav"):
                    if k in raw:
                        arr = raw[k]
                        break
                else:
                    arr = None
                    
                sr = raw.get("sr", target_sr)
            elif isinstance(raw, tuple) and len(raw) == 2:
                arr, sr = raw
            else:
                arr = raw
                sr = target_sr

            if arr is not None:
                arr = _to_float32(arr)
                if arr.ndim > 1:
                    arr = arr.mean(axis=1)
                
                # Resample if needed
                if sr != target_sr and sr > 0:
                    arr = _resample_hq(arr, sr, target_sr)
                
                # Apply speed change
                if speed and abs(float(speed) - 1.0) > 0.01:
                    tmp_sr = int(round(target_sr * float(speed)))
                    tmp_sr = max(8000, min(96000, tmp_sr))
                    arr = _resample_hq(arr, target_sr, tmp_sr)
                    arr = _resample_hq(arr, tmp_sr, target_sr)
                
                wavs.append(arr)
            else:
                # Fallback: silence
                wavs.append(np.zeros(int(target_sr * 0.5), dtype=np.float32))
                
        except Exception as e:
            import traceback
            print(f"[CosyVoice2] Error processing chunk: {e}")
            print(f"[CosyVoice2] Full traceback: {traceback.format_exc()}")
            # Fallback: silence
            wavs.append(np.zeros(int(target_sr * 0.5), dtype=np.float32))

    return wavs, target_sr


def concat_audio(wavs: List[np.ndarray]) -> np.ndarray:
    """Concatenate list of audio arrays."""
    if not wavs:
        return np.zeros(0, dtype=np.float32)
    return np.concatenate([_to_float32(w) for w in wavs], axis=0)
