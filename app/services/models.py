from __future__ import annotations
import os
import sys
import threading
import torch
import inspect
import logging
import time
from pathlib import Path
from typing import Optional
from functools import lru_cache
import hashlib

__all__ = ["get_kokoro", "get_cosyvoice2", "preload_models", "get_recommended_engine"]

_COSYVOICE2_SINGLETON = None
_cosy_lock = threading.Lock()
_KOKORO = None
_KOKORO_LOCK = threading.Lock()

# Add synthesis cache
_SYNTHESIS_CACHE = {}
_CACHE_LOCK = threading.Lock()
_MAX_CACHE_SIZE = 100  # Adjust based on memory


def get_cache_key(text: str, voice: str, speed: float, engine: str) -> str:
    """Generate cache key for synthesis results"""
    key_str = f"{engine}:{voice}:{speed}:{text[:200]}"
    return hashlib.md5(key_str.encode()).hexdigest()


def cache_synthesis(key: str, audio_data: bytes, duration: float):
    """Cache synthesis results"""
    with _CACHE_LOCK:
        # Implement LRU by removing oldest if at capacity
        if len(_SYNTHESIS_CACHE) >= _MAX_CACHE_SIZE:
            oldest = min(_SYNTHESIS_CACHE.items(),
                         key=lambda x: x[1]['timestamp'])
            del _SYNTHESIS_CACHE[oldest[0]]

        _SYNTHESIS_CACHE[key] = {
            'audio': audio_data,
            'duration': duration,
            'timestamp': time.time()
        }


def get_cached_synthesis(key: str):
    """Get cached synthesis if available"""
    with _CACHE_LOCK:
        if key in _SYNTHESIS_CACHE:
            # Update timestamp for LRU
            _SYNTHESIS_CACHE[key]['timestamp'] = time.time()
            return _SYNTHESIS_CACHE[key]
    return None


def _find_cosy_root() -> Path:
    """Locate CosyVoice repo root so 'cosyvoice' can be imported."""
    env = os.getenv("COSYVOICE_DIR")
    if env:
        p = Path(env)
        if p.exists():
            return p.resolve()

    here = Path(__file__).resolve()
    candidates = [
        here.parents[2] / "third_party" / "CosyVoice",
        here.parents[1] / "third_party" / "CosyVoice",
        Path("third_party") / "CosyVoice",
        Path("CosyVoice"),
    ]
    for c in candidates:
        if c.exists():
            return c.resolve()
    raise FileNotFoundError(
        "Could not find CosyVoice root. Set COSYVOICE_DIR.")


def _find_cosy_model_dir(root: Path) -> Path:
    """Return the folder that actually contains 'cosyvoice2.yaml'."""
    env_dir = os.getenv("COSYVOICE2_DIR")
    if env_dir:
        d = Path(env_dir)
        if (d / "cosyvoice2.yaml").exists():
            return d.resolve()

    common = [
        root, root / "asset", root / "assets", root / "models",
        root / "model", root / "pretrained_models", root / "checkpoints",
        root / "weights",
    ]

    for base in list(common):
        if base.exists() and base.is_dir():
            try:
                for sub in base.iterdir():
                    if sub.is_dir():
                        common.append(sub)
            except Exception:
                pass

    for d in common:
        if (d / "cosyvoice2.yaml").exists():
            return d.resolve()

    try:
        hit = next(root.rglob("cosyvoice2.yaml"))
        return hit.parent.resolve()
    except StopIteration:
        pass

    for hit in root.rglob("cosyvoice*.yaml"):
        return hit.parent.resolve()

    raise FileNotFoundError(
        f"cosyvoice2.yaml not found under {root}. "
        "Set COSYVOICE2_DIR to the folder that contains it."
    )


def _pick_device_and_dtype(force_device: str | None = None, force_dtype: str | None = None):
    """Optimized device selection for both GTX 970 and M4 Pro"""
    import torch
    import platform

    if force_device:
        dev = force_device
    else:
        system = platform.system()

        # Check for Apple Silicon first
        if system == "Darwin" and platform.processor() == 'arm':
            if torch.backends.mps.is_available():
                # Enable MPS fallback for unsupported operations
                os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
                logging.info("Using Apple Silicon MPS acceleration with CPU fallback enabled")
                dev = "mps"
            else:
                dev = "cpu"
        # Check for CUDA
        elif torch.cuda.is_available():
            # Get GPU info
            gpu_name = torch.cuda.get_device_name(0)
            vram = torch.cuda.get_device_properties(0).total_memory

            # GTX 970 has 4GB VRAM - force CPU mode for stability
            if "970" in gpu_name.lower():
                logging.info(f"GTX 970 detected - forcing CPU mode due to insufficient VRAM")
                dev = "cpu"
            elif vram < 6 * 1024**3:
                logging.info(f"Low VRAM GPU detected - using CPU mode")
                dev = "cpu"
            else:
                dev = "cuda"
        else:
            dev = "cpu"

    # Dtype selection
    if force_dtype is not None:
        dt = getattr(torch, force_dtype, torch.float32)
    else:
        if dev == "cuda":
            # GTX 970 doesn't have good FP16 support, use FP32
            gpu_name = torch.cuda.get_device_name(
                0) if torch.cuda.is_available() else ""
            if "970" in gpu_name.lower():
                dt = torch.float32
            else:
                dt = torch.float16
        elif dev == "mps":
            dt = torch.float32  # MPS works better with FP32
        else:
            dt = torch.float32

    return dev, dt

# ---------- Kokoro (hexgrad/Kokoro-82M) ----------


def get_kokoro(*, repo_id: Optional[str] = None, lang_code: str = "a"):
    """Process-level, thread-safe singleton for Kokoro's KPipeline."""
    global _KOKORO
    with _KOKORO_LOCK:
        if _KOKORO is None:
            logging.info("Loading Kokoro model...")
            start = time.time()
            from kokoro import KPipeline
            if repo_id is None:
                repo_id = os.environ.get("KOKORO_REPO", "hexgrad/Kokoro-82M")

            # Ensure model is on correct device
            _KOKORO = KPipeline(lang_code=lang_code, repo_id=repo_id)

            # Move to GPU if available and not GTX 970
            if torch.cuda.is_available() and hasattr(_KOKORO, 'model'):
                gpu_name = torch.cuda.get_device_name(0).lower()
                if "970" not in gpu_name:  # Don't use GPU for GTX 970
                    try:
                        _KOKORO.model = _KOKORO.model.cuda()
                        torch.cuda.empty_cache()  # Clear cache after loading
                        logging.info("Kokoro moved to GPU")
                    except Exception as e:
                        logging.warning(f"Failed to move Kokoro to GPU: {e}")
                else:
                    logging.info("GTX 970 detected - keeping Kokoro on CPU for stability")

            logging.info(f"Kokoro loaded in {time.time() - start:.2f}s")
        return _KOKORO

# ---------- CosyVoice2 ----------


def _env_bool(name: str, default: Optional[bool] = None) -> Optional[bool]:
    v = os.environ.get(name)
    if v is None:
        return default
    v = v.strip().lower()
    if v in ("1", "true", "yes", "y", "on"):
        return True
    if v in ("0", "false", "no", "n", "off"):
        return False
    return default


def _decide_cosy_policy() -> tuple[bool, bool]:
    """Optimized policy that properly supports GTX 970"""
    device_override = os.environ.get("COSY_DEVICE", "auto").strip().lower()
    fp16_override = _env_bool("COSY_FP16", None)

    if device_override == "cpu":
        return True, False
    if device_override == "gpu":
        # Force GPU even for GTX 970
        return False, False  # No FP16 for GTX 970

    # Auto mode - optimized
    try:
        import torch
        if not torch.cuda.is_available():
            return True, False

        name = torch.cuda.get_device_name(0).lower()
        major, minor = torch.cuda.get_device_capability(0)
        vram = torch.cuda.get_device_properties(0).total_memory

        # GTX 970 specific optimization - force CPU due to insufficient VRAM
        if "970" in name or (major == 5 and minor == 2):
            logging.info("GTX 970 detected - forcing CPU mode due to insufficient VRAM")
            return True, False  # Force CPU mode

        # Other older GPUs
        if major < 6:  # Pre-Pascal
            return True, False  # CPU mode

        # Modern GPUs with low VRAM
        if vram < 6 * 1024**3:
            # Low VRAM - use CPU to avoid OOM
            return True, False

        # Good GPU - use FP16
        return False, True

    except Exception:
        return True, False


def get_cosyvoice2(force_device: str | None = None, force_dtype: str | None = None):
    """Optimized CosyVoice2 singleton with better GPU support"""
    global _COSYVOICE2_SINGLETON
    if _COSYVOICE2_SINGLETON is not None:
        return _COSYVOICE2_SINGLETON

    with _cosy_lock:
        if _COSYVOICE2_SINGLETON is not None:
            return _COSYVOICE2_SINGLETON

        logging.info("Loading CosyVoice2 model...")
        start = time.time()

        root = _find_cosy_root()
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))
        mpath = root / "third_party" / "Matcha-TTS"
        if mpath.exists() and str(mpath) not in sys.path:
            sys.path.insert(0, str(mpath))

        model_dir_path = _find_cosy_model_dir(root)
        model_dir = str(model_dir_path)

        from cosyvoice.cli.cosyvoice import CosyVoice2

        device, dtype = _pick_device_and_dtype(force_device, force_dtype)

        # Clear GPU cache before loading
        if device == "cuda" and torch.cuda.is_available():
            torch.cuda.empty_cache()
            # For GTX 970, also run garbage collection
            import gc
            gc.collect()
            torch.cuda.empty_cache()

        kwargs = {}
        sig = inspect.signature(CosyVoice2.__init__)
        if "device" in sig.parameters:
            kwargs["device"] = device
        if "dtype" in sig.parameters:
            kwargs["dtype"] = dtype
        if "fp16" in sig.parameters:
            try:
                kwargs["fp16"] = (dtype == torch.float16)
            except Exception:
                pass

        try:
            cv = CosyVoice2(model_dir, **kwargs)
        except TypeError:
            cv = CosyVoice2(model_dir)
        except torch.cuda.OutOfMemoryError:
            # Fallback to CPU if CUDA OOM
            logging.warning("CUDA OOM detected, falling back to CPU mode")
            torch.cuda.empty_cache()
            device = "cpu"
            dtype = torch.float32
            kwargs = {}
            sig = inspect.signature(CosyVoice2.__init__)
            if "device" in sig.parameters:
                kwargs["device"] = device
            if "dtype" in sig.parameters:
                kwargs["dtype"] = dtype
            try:
                cv = CosyVoice2(model_dir, **kwargs)
            except TypeError:
                cv = CosyVoice2(model_dir)

        _COSYVOICE2_SINGLETON = cv

        # Clear cache after loading
        if device == "cuda" and torch.cuda.is_available():
            torch.cuda.empty_cache()

        logging.info(
            f"CosyVoice2 loaded in {time.time() - start:.2f}s on {device}")
        return cv


def get_recommended_engine() -> str:
    """
    Automatically detect system capabilities and recommend the best TTS engine.
    Returns 'kokoro' for lower-end systems, 'cosyvoice2' for high-end systems.
    """
    import platform
    import psutil
    
    try:
        system = platform.system()
        
        # Get system specs
        ram_gb = psutil.virtual_memory().total / (1024**3)
        cpu_count = psutil.cpu_count()
        
        # Check if we have CUDA available
        cuda_available = False
        vram_gb = 0
        gpu_name = ""
        
        if torch.cuda.is_available():
            cuda_available = True
            vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            gpu_name = torch.cuda.get_device_name(0).lower()
        
        # Apple Silicon (M1/M2/M3/M4) - always use CosyVoice2
        if system == "Darwin" and platform.processor() == 'arm':
            if ram_gb >= 16:  # Unified memory
                logging.info(f"Apple Silicon detected with {ram_gb:.1f}GB RAM - recommending CosyVoice2")
                return "cosyvoice2"
            else:
                logging.info(f"Apple Silicon with low RAM ({ram_gb:.1f}GB) - recommending Kokoro")
                return "kokoro"
        
        # High-end NVIDIA GPUs
        if cuda_available and vram_gb >= 8:
            logging.info(f"High-end GPU detected ({gpu_name}, {vram_gb:.1f}GB VRAM) - recommending CosyVoice2")
            return "cosyvoice2"
        
        # GTX 970 and other 4GB cards - force Kokoro
        if cuda_available and ("970" in gpu_name or vram_gb <= 4):
            logging.info(f"Low VRAM GPU detected ({gpu_name}, {vram_gb:.1f}GB VRAM) - recommending Kokoro")
            return "kokoro"
        
        # High-end CPU systems (32GB+ RAM, 16+ cores)
        if ram_gb >= 32 and cpu_count >= 16:
            logging.info(f"High-end CPU system ({cpu_count} cores, {ram_gb:.1f}GB RAM) - recommending CosyVoice2")
            return "cosyvoice2"
        
        # Default to Kokoro for everything else
        logging.info(f"Standard system ({cpu_count} cores, {ram_gb:.1f}GB RAM) - recommending Kokoro")
        return "kokoro"
        
    except Exception as e:
        logging.warning(f"Failed to detect system capabilities: {e}, defaulting to Kokoro")
        return "kokoro"


def preload_models():
    """Preload all models at startup - call this in your startup event"""
    logging.info("Preloading TTS models...")
    start = time.time()

    # Load models in parallel
    threads = []

    def load_kokoro():
        try:
            get_kokoro()
            # Warm up with a dummy inference
            from app.utils.synthesize import synthesize_kokoro_chunks
            chunks = ["test"]
            synthesize_kokoro_chunks(chunks, voice="af_heart", speed=1.0)
        except Exception as e:
            logging.error(f"Failed to preload Kokoro: {e}")

    def load_cosy():
        try:
            import numpy as np
            import sys
            import os
            from pathlib import Path
            
            # Test if the critical import works first
            try:
                from transformers import Qwen2ForCausalLM
            except ImportError as import_e:
                logging.warning(f"CosyVoice2 preload skipped due to import issue: {import_e}")
                logging.info("CosyVoice2 will initialize on first request instead")
                return
            
            # Ensure CosyVoice path is available in executor context
            cosy_path = str(Path(__file__).parent.parent.parent / "third_party" / "CosyVoice")
            if cosy_path not in sys.path:
                sys.path.insert(0, cosy_path)
            
            cv = get_cosyvoice2()
            logging.info("CosyVoice2 loaded successfully in preload")
            
            # Warm up with a dummy inference to initialize CUDA kernels
            ref_dummy = torch.zeros(1, 16000, dtype=torch.float32)
            try:
                # Quick warmup inference
                cv.inference_cross_lingual("test", ref_dummy, stream=False)
                logging.info("CosyVoice2 warmed up successfully")
            except Exception as warmup_e:
                logging.warning(f"CosyVoice2 warmup failed: {warmup_e}")
        except Exception as e:
            logging.warning(f"CosyVoice2 preload had issues: {e}")
            logging.info("CosyVoice2 will initialize on first request instead")

    t1 = threading.Thread(target=load_kokoro)
    t2 = threading.Thread(target=load_cosy)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    logging.info(f"All models preloaded in {time.time() - start:.2f}s")

    # Clear GPU memory after preload
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
