from typing import List


def _fmt(ts_ms: int) -> str:
    ts = ts_ms // 1000
    ms = ts_ms % 1000
    h = ts // 3600
    m = (ts % 3600) // 60
    s = ts % 60
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def srt_from_durations(sentences: List[str], durations_ms: List[int]) -> str:
    lines = []
    t = 0
    for i, (text, dur) in enumerate(zip(sentences, durations_ms), start=1):
        start = _fmt(t)
        end = _fmt(t + dur)
        lines.append(str(i))
        lines.append(f"{start} --> {end}")
        lines.append(text)
        lines.append("")
        t += dur
    return "\n".join(lines)
