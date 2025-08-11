import re


def srt_to_vtt(srt_path: str, vtt_path: str) -> None:
    """Convert SRT → WebVTT, fixing comma milliseconds and adding header."""
    with open(srt_path, "r", encoding="utf-8") as f:
        srt = f.read()

    # Remove numeric indices and normalize newlines
    srt = re.sub(r"(?m)^\s*\d+\s*$", "", srt).strip()
    # Convert 00:00:01,234 --> 00:00:01.234
    srt = re.sub(r"(\d\d:\d\d:\d\d),(\d{3})", r"\1.\2", srt)

    cues = srt.replace("\r\n", "\n").split("\n\n")
    out = ["WEBVTT", ""]
    out.extend(cues)
    with open(vtt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(out).strip() + "\n")
