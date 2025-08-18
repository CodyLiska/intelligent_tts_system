# app/utils/streaming.py
from __future__ import annotations
from typing import Iterable, Iterator, Union, Protocol, runtime_checkable
import struct
import numpy as np


@runtime_checkable
class PCMLike(Protocol):
    """Objects that can be converted to bytes() for PCM payloads."""

    def __bytes__(self) -> bytes: ...


def _wav_streaming_header(sr: int) -> bytes:
    # RIFF/WAVE header with unknown data size (0xFFFFFFFF)
    import struct
    byte_rate = sr * 2 * 1  # 16-bit mono
    block_align = 2
    # data size placeholder
    hdr = b"RIFF" + struct.pack("<I", 0xFFFFFFFF) + b"WAVE"
    hdr += b"fmt " + struct.pack("<IHHIIHH", 16, 1,
                                 1, sr, byte_rate, block_align, 16)
    hdr += b"data" + struct.pack("<I", 0xFFFFFFFF)
    return hdr


def wav_stream_from_chunks(
    sample_rate: int,
    chunks: Iterable[bytes],
    *,
    prepend_silence_ms: int = 0,
    prebuffer_chunks: int = 2,
) -> Iterator[bytes]:
    yield _wav_streaming_header(sample_rate)

    if prepend_silence_ms > 0:
        silence = b"\x00" * int(sample_rate * 2 * prepend_silence_ms / 1000)
        if silence:
            yield silence  # bytes

    buf = bytearray()
    it = iter(chunks)

    for _ in range(max(0, prebuffer_chunks)):
        try:
            c = next(it)
            if not c:
                continue
            buf += bytes(c)
        except StopIteration:
            break

    if buf:
        yield bytes(buf)
        buf.clear()

    for c in it:
        if not c:
            continue
        yield bytes(c)


# --- ADD: raw PCM (s16le) streaming, no WAV header ---
def pcm16_stream_from_chunks(
    sr: int,
    chunks: Iterable[PCMLike],
    *,
    prepend_silence_ms: int = 0,
    prebuffer_chunks: int = 2,
) -> Iterator[bytes]:
    """
    Stream raw PCM16 (s16le) safely. Guarantees only even-sized writes.
    - Optionally sends a short priming silence.
    - Small prebuffer smooths start-up for players.
    """
    # Primer: sr * 2 bytes (mono 16-bit) * ms/1000
    if prepend_silence_ms > 0:
        nbytes = int(sr * 2 * (prepend_silence_ms / 1000.0))
        if nbytes & 1:
            nbytes += 1  # keep it even
        if nbytes:
            yield b"\x00" * nbytes

    it = iter(chunks)
    pending = bytearray()

    # Prebuffer a few chunks to avoid tiny initial packets
    for _ in range(max(0, prebuffer_chunks)):
        try:
            c = next(it)
        except StopIteration:
            break
        pending += bytes(c)

    def flush_even() -> bytes:
        nonlocal pending
        even = len(pending) & ~1  # drop an odd trailing byte, if any
        if even:
            out = bytes(pending[:even])
            del pending[:even]
            return out
        return b""

    first = flush_even()
    if first:
        yield first

    for c in it:
        pending += bytes(c)
        out = flush_even()
        if out:
            yield out

    # Finish: if a single trailing byte remains, pad with one zero
    if pending:
        if len(pending) & 1:
            pending.append(0)
        yield bytes(pending)
