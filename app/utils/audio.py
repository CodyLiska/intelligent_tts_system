import io
import numpy as np
import soundfile as sf


def write_wav_bytes(audio: np.ndarray, sr: int):
    buf = io.BytesIO()
    sf.write(buf, audio, sr, format="WAV")
    buf.seek(0)
    return buf
