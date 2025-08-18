# app/api.py - OPTIMIZED VERSION with caching and async processing
from __future__ import annotations

import io
import os
import ssl
import tempfile
import threading
import time
import wave
import zipfile
import asyncio
import hashlib
from pathlib import Path
from typing import Dict, Optional, Iterable, Iterator
from urllib.parse import unquote
from urllib.request import Request, urlopen
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from fastapi import FastAPI, File, Form, Query, Request, UploadFile, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from starlette.responses import StreamingResponse

from app.utils.chunk_text import split_sentences
from app.utils.extract_text import extract_text
from app.utils.synthesize import synthesize_kokoro_chunks, synthesize_cosyvoice2_chunks, concat_audio, stream_cosyvoice2_cross, stream_kokoro_chunks, load_ref_16k_trimmed
from app.utils.align_subtitles import mfa_align_chunks_to_srt
from app.utils.make_captions import srt_to_vtt
from app.utils.streaming import wav_stream_from_chunks, pcm16_stream_from_chunks
from app.services.models import get_cosyvoice2, get_kokoro, preload_models

# Thread pool for CPU-bound operations
executor = ThreadPoolExecutor(max_workers=4)

# Cache for synthesis results
SYNTHESIS_CACHE = {}
CACHE_LOCK = threading.Lock()
MAX_CACHE_SIZE = 50
CACHE_TTL = 3600  # 1 hour

app = FastAPI(title="TTS Starter - Optimized")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- Cache Management ----------------


def get_cache_key(text: str, engine: str, voice: str, speed: float, align: bool) -> str:
    """Generate a cache key for synthesis parameters"""
    # Use first 500 chars of text for key to avoid huge keys
    text_key = text[:500] if len(text) > 500 else text
    key_str = f"{engine}:{voice}:{speed}:{align}:{text_key}"
    return hashlib.md5(key_str.encode()).hexdigest()


def cache_result(key: str, data: bytes):
    """Store result in cache with TTL"""
    with CACHE_LOCK:
        # Remove oldest entries if cache is full
        if len(SYNTHESIS_CACHE) >= MAX_CACHE_SIZE:
            oldest = min(SYNTHESIS_CACHE.items(),
                         key=lambda x: x[1]['timestamp'])
            del SYNTHESIS_CACHE[oldest[0]]

        SYNTHESIS_CACHE[key] = {
            'data': data,
            'timestamp': time.time()
        }


def get_cached_result(key: str) -> Optional[bytes]:
    """Get cached result if available and not expired"""
    with CACHE_LOCK:
        if key in SYNTHESIS_CACHE:
            entry = SYNTHESIS_CACHE[key]
            # Check if expired
            if time.time() - entry['timestamp'] < CACHE_TTL:
                # Update timestamp for LRU
                entry['timestamp'] = time.time()
                return entry['data']
            else:
                # Remove expired entry
                del SYNTHESIS_CACHE[key]
    return None


def clear_old_cache():
    """Background task to clear expired cache entries"""
    with CACHE_LOCK:
        current_time = time.time()
        expired_keys = [
            k for k, v in SYNTHESIS_CACHE.items()
            if current_time - v['timestamp'] > CACHE_TTL
        ]
        for key in expired_keys:
            del SYNTHESIS_CACHE[key]

# ---------------- Async Wrappers ----------------


async def async_synthesize_kokoro(chunks, voice, lang_code, speed):
    """Async wrapper for Kokoro synthesis"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        executor,
        synthesize_kokoro_chunks,
        chunks,
        voice,
        lang_code,
        speed
    )


async def async_synthesize_cosyvoice2(chunks, model_dir, ref_wav, prompt_text, stream, fp16, mode, speed):
    """Async wrapper for CosyVoice2 synthesis"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        executor,
        synthesize_cosyvoice2_chunks,
        chunks,
        model_dir,
        ref_wav,
        prompt_text,
        stream,
        fp16,
        mode,
        speed
    )


async def async_align_chunks(chunks, wavs, sr, srt_path, num_jobs, single_speaker):
    """Async wrapper for MFA alignment"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        executor,
        mfa_align_chunks_to_srt,
        chunks,
        wavs,
        sr,
        srt_path,
        num_jobs,
        single_speaker
    )

# ---------------- Helper functions ----------------


def _save_full_wav(path: str, audio: np.ndarray, sr: int = 24000):
    """Save audio array as WAV file."""
    a16 = (np.clip(audio, -1, 1) * 32767).astype("<i2").tobytes()
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sr)
        f.writeframes(a16)


def _primer_silence(sr: int, ms: int = 120) -> bytes:
    """A tiny PCM16 block so ffplay/browsers begin playback immediately."""
    n = int(sr * ms / 1000.0)
    return np.zeros(n, dtype="<i2").tobytes()


def _cosyvoice_root() -> Optional[Path]:
    env = os.environ.get("COSYVOICE_DIR")
    if env:
        p = Path(env)
        if p.exists():
            return p
    for cand in (Path("third_party") / "CosyVoice", Path("CosyVoice")):
        if cand.exists():
            return cand.resolve()
    return None


def _preset_dirs() -> list[Path]:
    """Likely places that hold data/refs/*.wav."""
    here = Path(__file__).resolve()
    return [
        Path("data/refs"),
        here.parent.parent / "data" / "refs",
        here.parent / "data" / "refs",
        *([_cosyvoice_root() / "asset"] if _cosyvoice_root() else []),
    ]


def _build_ref_presets() -> Dict[str, Path]:
    presets: Dict[str, Path] = {}
    for folder in _preset_dirs():
        if folder and folder.exists():
            for wav in folder.glob("*.wav"):
                presets[wav.stem] = wav.resolve()
    return presets


def _resolve_cosy_ref(cosy_ref_id: str | None, cosy_ref_url: str | None) -> str | None:
    """Returns a local file path for a Cosy reference"""
    if cosy_ref_id:
        presets = _build_ref_presets()
        p = presets.get(cosy_ref_id)
        if p and p.exists():
            return str(p)

    if not cosy_ref_url:
        return None
    url = unquote(cosy_ref_url).strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        return None

    ua = "tts-starter/1.0"
    ctx = ssl.create_default_context()

    try:
        req = Request(url, method="HEAD", headers={"User-Agent": ua})
        with urlopen(req, timeout=8, context=ctx) as resp:
            pass
    except Exception:
        pass

    try:
        RANGE = "bytes=0-1048575"
        req = Request(url, method="GET", headers={
                      "User-Agent": ua, "Range": "bytes=0-1048575"})
        with urlopen(req, timeout=15, context=ctx) as resp:
            data = resp.read()

        if not data or len(data) < 8192:
            req = Request(url, method="GET", headers={
                          "User-Agent": ua, "Range": "bytes=0-1048575"})
            with urlopen(req, timeout=20, context=ctx) as resp:
                data = resp.read(2 * 1024 * 1024)

        fd, path = tempfile.mkstemp(suffix=".wav")
        os.write(fd, data)
        os.close(fd)
        return path
    except Exception:
        return None

# ---------------- Endpoints ----------------


@app.get("/", response_class=HTMLResponse)
def home() -> HTMLResponse:
    """Serve the main HTML interface."""
    try:
        html_path = Path(__file__).parent / "static" / "index.html"
        if html_path.exists():
            return HTMLResponse(html_path.read_text(encoding="utf-8"))
    except Exception:
        pass

    return HTMLResponse(
        "<!doctype html><meta charset='utf-8'><title>TTS</title>"
        "<p>Use <code>/synthesize</code> (POST) endpoint.</p>"
    )


@app.get("/health")
def health():
    """Health check endpoint with cache stats"""
    import torch
    with CACHE_LOCK:
        cache_size = len(SYNTHESIS_CACHE)

    gpu_info = {}
    if torch.cuda.is_available():
        gpu_info = {
            'gpu_name': torch.cuda.get_device_name(0),
            'gpu_memory_used': f"{torch.cuda.memory_allocated() / 1024**3:.2f} GB",
            'gpu_memory_cached': f"{torch.cuda.memory_reserved() / 1024**3:.2f} GB"
        }

    return {
        "ok": True,
        "cache_size": cache_size,
        "max_cache_size": MAX_CACHE_SIZE,
        **gpu_info
    }


@app.get("/voices")
def list_voices():
    try:
        kp = get_kokoro()
        voices = sorted({v for v in getattr(kp, "voices", [])} or {"af_heart"})
        return {"voices": voices}
    except Exception:
        return {"voices": ["af_heart"]}


@app.get("/recommended-engine")
async def get_recommended_engine_endpoint():
    """Get the recommended engine for this system"""
    from app.services.models import get_recommended_engine
    recommended = get_recommended_engine()
    return {"recommended_engine": recommended}

# ---------------- Main synthesis endpoint - OPTIMIZED ----------------


# Fixed version of the synthesize_full method
# Replace the existing synthesize_full method with this one:

@app.post("/synthesize")
async def synthesize_full(
    text: str = Form(None),
    file: UploadFile = File(None),
    engine: str = Form("auto"),
    voice: str = Form("af_heart"),
    speed: float = Form(1.0),
    align: str = Form("true"),
    post: str = Form(""),
    max_chars: int = Form(240),
    cosy_mode: str = Form("cross"),
    cosy_prompt: str = Form(""),
    cosy_ref: UploadFile = File(None),
):
    """
    Main synthesis endpoint that returns a ZIP file with audio.wav and captions.srt.
    Handles both text input and file uploads (PDF, ePub, txt).
    """
    try:
        # Auto-select engine based on system capabilities
        if engine == "auto":
            from app.services.models import get_recommended_engine
            engine = get_recommended_engine()
            print(f"Auto-selected engine: {engine}")
        
        # Extract text from input
        if file and file.filename:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
                content = await file.read()
                tmp.write(content)
                tmp.flush()
                input_text = extract_text(tmp.name)
                os.unlink(tmp.name)
        elif text:
            input_text = text.strip()
        else:
            return JSONResponse({"error": "No text or file provided"}, status_code=400)

        if not input_text:
            return JSONResponse({"error": "No text content found"}, status_code=400)

        # Split into chunks
        chunks = split_sentences(input_text, max_chars=max_chars)
        print(f"Processing {len(chunks)} chunks (max_chars={max_chars})")

        # Synthesize audio
        engine = engine.lower().strip()
        if engine == "kokoro":
            # Enable caching for better performance
            cache_dir = os.environ.get("TTS_CACHE_DIR", "cache")
            wavs, sr = synthesize_kokoro_chunks(
                chunks,
                voice=voice,
                lang_code="a",
                speed=speed,
                cache_dir=cache_dir,
            )
        elif engine == "cosyvoice2":
            # Handle reference audio if provided
            ref_path = None
            if cosy_ref and cosy_ref.filename:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                    content = await cosy_ref.read()
                    tmp.write(content)
                    tmp.flush()
                    ref_path = tmp.name

            wavs, sr = synthesize_cosyvoice2_chunks(
                chunks,
                model_dir=None,
                ref_wav=ref_path,
                prompt_text=cosy_prompt,
                stream=False,
                fp16=False,
                mode=cosy_mode,
                speed=speed,
            )

            # Clean up temp ref file
            if ref_path:
                try:
                    os.unlink(ref_path)
                except (OSError, IOError) as e:
                    # Log the error but don't fail the request
                    print(
                        f"Warning: Failed to delete temp file {ref_path}: {e}")
        else:
            return JSONResponse({"error": f"Unknown engine: {engine}"}, status_code=400)

        # Concatenate audio
        full_audio = concat_audio(wavs)

        # Create output directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Save audio
            audio_path = temp_path / "audio.wav"
            _save_full_wav(str(audio_path), full_audio, sr)

            # Generate subtitles
            srt_path = temp_path / "captions.srt"

            # Check if we should skip MFA alignment based on text length and system capabilities
            total_chars = sum(len(chunk) for chunk in chunks)
            
            # Adjust MFA threshold based on recommended engine (system capability)
            from app.services.models import get_recommended_engine
            recommended = get_recommended_engine()
            
            if recommended == "kokoro":
                # Lower-end system - be more conservative with MFA
                mfa_threshold = 300  # Use MFA only for very short texts
            else:
                # Higher-end system - can handle MFA on longer texts
                mfa_threshold = 1000
                
            use_simple_timing = total_chars > mfa_threshold
            
            if align.lower() == "true" and not use_simple_timing:
                try:
                    # Use MFA for precise alignment with more CPU cores
                    num_cores = min(os.cpu_count() or 4, 8)  # Use up to 8 cores
                    mfa_align_chunks_to_srt(
                        chunks,
                        wavs,
                        sr,
                        str(srt_path),
                        num_jobs=num_cores,
                        single_speaker=True,
                    )
                except Exception as e:
                    print(f"MFA alignment failed: {e}")
                    # Fallback to duration-based alignment
                    from app.utils.srt import srt_from_durations
                    durations_ms = [int(len(wav) / sr * 1000) for wav in wavs]
                    srt_content = srt_from_durations(chunks, durations_ms)
                    srt_path.write_text(srt_content, encoding="utf-8")
            else:
                # Duration-based alignment only (for short text or when align=false)
                if use_simple_timing:
                    print(f"Skipping MFA alignment for short text ({total_chars} chars). Using simple timing.")
                from app.utils.srt import srt_from_durations
                durations_ms = [int(len(wav) / sr * 1000) for wav in wavs]
                srt_content = srt_from_durations(chunks, durations_ms)
                srt_path.write_text(srt_content, encoding="utf-8")

            # Generate VTT
            vtt_path = temp_path / "captions.vtt"
            srt_to_vtt(str(srt_path), str(vtt_path))

            # Create ZIP file
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                zip_file.write(audio_path, "audio.wav")
                zip_file.write(srt_path, "captions.srt")
                zip_file.write(vtt_path, "captions.vtt")

            zip_buffer.seek(0)

            return Response(
                content=zip_buffer.getvalue(),
                media_type="application/zip",
                headers={
                    "Content-Disposition": "attachment; filename=tts_output.zip"
                }
            )

    except Exception as e:
        print(f"Synthesis error: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)

# ---------------- GET streaming endpoints (unchanged) ----------------


@app.get("/synthesize/stream_get")
def synthesize_stream_get(
    engine: str = Query("kokoro"),
    text: str = Query(...),
    voice: str = Query("af_heart"),
    max_chars: int = Query(60, ge=12, le=240),
    cosy_mode: str = Query("cross"),
    cosy_ref_id: str | None = Query(None),
    cosy_ref_url: str | None = Query(None),
    speed: float = Query(1.15),
    fmt: str = Query("wav"),
):
    """GET streaming endpoint - unchanged from original"""
    import itertools

    engine = engine.lower().strip()
    chunks = split_sentences(text, max_chars=max_chars)

    if engine == "kokoro":
        sr = 24000
        gen = stream_kokoro_chunks(chunks, voice=voice, speed=float(speed))
        if fmt.lower() == "pcm":
            primer = b"\x00" * int(sr * 2 * 120 / 1000)
            gen_pcm = itertools.chain([primer], gen)
            return StreamingResponse(
                pcm16_stream_from_chunks(
                    sr, gen_pcm, prepend_silence_ms=0, prebuffer_chunks=2),
                media_type="audio/L16",
                headers={"Cache-Control": "no-store",
                         "X-Audio-Format": "s16le; rate=24000; channels=1"},
            )
        else:
            return StreamingResponse(
                wav_stream_from_chunks(
                    sr, gen, prepend_silence_ms=80, prebuffer_chunks=1),
                media_type="audio/wav",
                headers={"Cache-Control": "no-store"},
            )

    if engine == "cosyvoice2":
        if cosy_mode.lower() != "cross":
            return JSONResponse({"error": "stream_get supports cosy_mode=cross"}, status_code=400)

        ref_path = _resolve_cosy_ref(cosy_ref_id, cosy_ref_url)
        sr, cosy_bytes = stream_cosyvoice2_cross(
            text, ref_path=ref_path, speed=float(speed or 1.15))

        if fmt.lower() == "pcm":
            primer = b"\x00" * int(sr * 2 * 120 / 1000)
            gen = itertools.chain([primer], cosy_bytes)
            return StreamingResponse(
                pcm16_stream_from_chunks(
                    sr, gen, prepend_silence_ms=0, prebuffer_chunks=1),
                media_type="audio/L16",
                headers={"Cache-Control": "no-store",
                         "X-Audio-Format": f"s16le; rate={sr}; channels=1"},
            )
        else:
            return StreamingResponse(
                wav_stream_from_chunks(
                    sr, cosy_bytes, prepend_silence_ms=40, prebuffer_chunks=0),
                media_type="audio/wav",
                headers={"Cache-Control": "no-store"},
            )

    return JSONResponse({"error": f"unknown engine '{engine}'"}, status_code=400)

# ---------------- POST/GET streaming endpoint (unchanged) ----------------


@app.api_route("/synthesize/stream", methods=["GET", "POST"])
async def synthesize_stream(
    text: str = Form(...),
    engine: str = Form("auto"),
    voice: str = Form("af_heart"),
    speed: float = Form(1.0),
    max_chars: int = Form(120),
    fmt: str = Form("wav"),
    cosy_mode: str | None = Form(None),
    cosy_ref_id: str | None = Form(None),
    cosy_ref_url: str | None = Form(None),
):
    """Streaming endpoint - unchanged from original"""
    # Auto-select engine based on system capabilities
    if engine == "auto":
        from app.services.models import get_recommended_engine
        engine = get_recommended_engine()
        print(f"Auto-selected engine: {engine}")
    
    engine = (engine or "").lower()
    fmt = (fmt or "wav").lower()
    chunks = split_sentences(text, max_chars=max_chars)

    streamer = wav_stream_from_chunks
    media = "audio/wav"
    if fmt == "pcm":
        streamer = pcm16_stream_from_chunks
        media = "audio/L16"

    if engine == "kokoro":
        sr = 24000
        gen = stream_kokoro_chunks(chunks, voice=voice, speed=float(speed))
        return StreamingResponse(
            streamer(sr, gen, prepend_silence_ms=80, prebuffer_chunks=3),
            media_type=media,
            headers={"Cache-Control": "no-store"},
        )

    if engine == "cosyvoice2":
        mode = (cosy_mode or "cross").lower()
        if mode != "cross":
            return JSONResponse({"error": "Only cosy_mode=cross is supported in this endpoint."}, status_code=400)
        ref_path = _resolve_cosy_ref(cosy_ref_id, cosy_ref_url)
        sr, gen = stream_cosyvoice2_cross(
            text, ref_path=ref_path, speed=float(speed))
        return StreamingResponse(
            pcm16_stream_from_chunks(
                sr, gen, prepend_silence_ms=120, prebuffer_chunks=2),
            media_type="application/octet-stream"
        )

    return JSONResponse({"error": f"unknown engine '{engine}'"}, status_code=400)

# ---------------- Startup event - CRITICAL FOR PERFORMANCE ----------------


@app.on_event("startup")
async def startup_event():
    """Preload models at startup to avoid first-request delay"""
    import torch

    print("=" * 60)
    print("STARTING TTS SERVER - OPTIMIZED VERSION")
    print("=" * 60)

    # Log system info
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(
            f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
    else:
        print("GPU: Not available, using CPU")

    print("Preloading models to avoid first-request delay...")

    # Preload models
    from app.services.models import preload_models
    await asyncio.get_event_loop().run_in_executor(executor, preload_models)

    # Warm up with CosyVoice2 reference
    def _warm_cosy():
        try:
            from app.utils.synthesize import stream_cosyvoice2_cross
            p = _build_ref_presets().get("ref")
            if p and p.exists():
                sr, it = stream_cosyvoice2_cross(
                    "ok", ref_path=str(p), speed=1.0)
                for _ in range(2):
                    next(it)
        except Exception as e:
            print(f"Failed to warm CosyVoice2: {e}")

    # Run warm-up in background
    threading.Thread(target=_warm_cosy, daemon=True).start()

    print("=" * 60)
    print("Server ready! First request should be fast now.")
    print("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    import torch
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    executor.shutdown(wait=False)
