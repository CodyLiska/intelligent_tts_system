import os
import shutil
import subprocess
import tempfile
import wave
from pathlib import Path
from typing import List, Sequence


def _write_wav(path: str, audio, sr: int) -> None:
    import numpy as np
    a16 = (np.clip(audio, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(
            sr)
        w.writeframes(a16.tobytes())


def _fmt_srt(t: float) -> str:
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(
        ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def _conda_exe_candidates() -> List[str]:
    return list(filter(os.path.isfile, [
        os.environ.get("CONDA_EXE"),
        r"C:\Users\hxchi\miniconda3\Scripts\conda.exe",
        r"C:\ProgramData\miniconda3\Scripts\conda.exe",
        r"C:\miniconda3\Scripts\conda.exe",
    ]))


def _mfa_cmd(conda_env: str = "aligner") -> List[str]:
    # Prefer conda run to avoid DLL path issues on Windows
    for c in _conda_exe_candidates():
        return [c, "run", "-n", conda_env, "mfa"]
    mfa = os.environ.get("MFA_EXE") or shutil.which("mfa")
    if not mfa:
        raise FileNotFoundError(
            "MFA not found. Install via conda or set MFA_EXE.")
    # Best-effort DLL path injection for direct exe use
    try:
        root = Path(mfa).parent.parent
        lib_bin = root / "Library" / "bin"
        if lib_bin.exists():
            os.environ["PATH"] = str(
                lib_bin) + os.pathsep + str(root) + os.pathsep + os.environ["PATH"]
    except Exception:
        pass
    return [str(mfa)]


def mfa_align_chunks_to_srt(
    chunks: Sequence[str],
    wavs: Sequence,
    sr: int,
    out_srt: str,
    dict_name: str = "english_us_arpa",
    acoustic_name: str = "english_mfa",
    *,
    num_jobs: int = 4,
    single_speaker: bool = True,
    conda_env: str = "aligner",
    verbose: bool = False,
) -> None:
    assert len(chunks) == len(wavs), "chunks and wavs length mismatch"

    tmp = Path(tempfile.mkdtemp(prefix="mfa_"))
    corpus = tmp / "corpus"
    aligned = tmp / "aligned"
    corpus.mkdir(parents=True, exist_ok=True)

    durations = []
    for i, (txt, wav) in enumerate(zip(chunks, wavs), 1):
        _write_wav(str(corpus / f"utt_{i:04}.wav"), wav, sr)
        (corpus / f"utt_{i:04}.lab").write_text(txt, encoding="utf-8")
        durations.append(len(wav) / sr)

    cmd = _mfa_cmd(conda_env) + [
        "align",
        str(corpus),
        dict_name,
        acoustic_name,
        str(aligned),
        "--clean",
        "--num_jobs",
        str(int(max(1, num_jobs))),
    ]
    if single_speaker:
        cmd.append("--single_speaker")
    if verbose:
        print("MFA command:", " ".join(cmd))

    try:
        subprocess.check_call(cmd)
    except FileNotFoundError as e:
        shutil.rmtree(tmp, ignore_errors=True)
        raise FileNotFoundError(
            f"Failed to launch MFA. Command: {' '.join(cmd)}\nDetails: {e}"
        )
    except subprocess.CalledProcessError as e:
        shutil.rmtree(tmp, ignore_errors=True)
        raise RuntimeError(
            f"MFA failed with exit code {e.returncode}. Command: {' '.join(cmd)}"
        ) from e

    from textgrid import TextGrid

    def bounds(tg_path: Path):
        tg = TextGrid.fromFile(str(tg_path))
        tier = tg[0]
        words = [itv for itv in tier if getattr(itv, "mark", "").strip()]
        if words:
            return float(words[0].minTime), float(words[-1].maxTime)
        return float(tier.minTime), float(tier.maxTime)

    entries, offset = [], 0.0
    for i, chunk in enumerate(chunks, 1):
        st, et = bounds(aligned / f"utt_{i:04}.TextGrid")
        entries.append((offset + st, offset + et, chunk.strip()))
        offset += durations[i - 1]

    out_path = Path(out_srt)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for idx, (st, et, txt) in enumerate(entries, 1):
            f.write(f"{idx}\n{_fmt_srt(st)} --> {_fmt_srt(et)}\n{txt}\n\n")

    shutil.rmtree(tmp, ignore_errors=True)
