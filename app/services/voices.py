# app/services/voices.py
from __future__ import annotations
import os
import json
from pathlib import Path
from typing import List, Dict
from threading import Lock

DEFAULT_REPO = "hexgrad/Kokoro-82M"

# In-process cache keyed by repo_id
_cache: dict[str, List[Dict[str, str]]] = {}
_lock = Lock()


def _discover_voices_from_dir(root: Path) -> List[Dict[str, str]]:
    """
    Try a voices manifest; fall back to scanning a voices/ folder for *.npz/*.pt etc.
    Returns a list of {"id": "...", "label": "..."}.
    """
    # 1) JSON-style manifest (several possible filenames/structures)
    for name in ("voices.json", "voices/voices.json"):
        p = root / name
        if p.is_file():
            try:
                with p.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                items = data.get("voices", data) if isinstance(
                    data, dict) else data
                out: List[Dict[str, str]] = []
                if isinstance(items, list):
                    for it in items:
                        if isinstance(it, str):
                            out.append({"id": it, "label": it})
                        elif isinstance(it, dict):
                            vid = it.get("id") or it.get(
                                "name") or it.get("voice") or it.get("key")
                            if vid:
                                out.append(
                                    {"id": vid, "label": it.get("label", vid)})
                if out:
                    return out
            except Exception:
                pass

    # 2) Fallback: scan voices directory
    voices_dir = root / "voices"
    candidates: list[str] = []
    if voices_dir.is_dir():
        for f in voices_dir.rglob("*"):
            if f.suffix.lower() in (".npz", ".npy", ".pt", ".pth", ".bin"):
                candidates.append(f.stem)
    uniq = sorted(set(candidates))
    return [{"id": v, "label": v} for v in uniq]


def get_kokoro_voices(repo_id: str | None = None, force_refresh: bool = False) -> List[Dict[str, str]]:
    """
    Pull voices from the Kokoro HF repo (default hexgrad/Kokoro-82M).
    Caches results in-process; set force_refresh=True to re-check HF.
    """
    repo_id = repo_id or os.getenv("KOKORO_REPO_ID", DEFAULT_REPO)

    # If we already have them and no refresh requested, return cache
    if not force_refresh:
        with _lock:
            if repo_id in _cache:
                return _cache[repo_id]

    # Try to download a light snapshot with just voices/ and json files
    try:
        from huggingface_hub import snapshot_download
        local_dir = snapshot_download(
            repo_id=repo_id,
            allow_patterns=["voices*", "voices/**", "*.json"],
            # disable symlinks on Windows to avoid permission issues
            local_dir_use_symlinks=False,
        )
        voices = _discover_voices_from_dir(Path(local_dir))
    except Exception:
        # Fallback minimal list so the endpoint always works
        voices = [{"id": "af_heart", "label": "af_heart"}]

    with _lock:
        _cache[repo_id] = voices
    return voices
