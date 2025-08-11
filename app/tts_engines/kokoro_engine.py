from typing import List, Tuple
import numpy as np
from kokoro import KPipeline

class KokoroEngine:
    def __init__(self, voice: str = "af_heart", speed: float = 1.0, lang_code: str = "a"):
        self.voice = voice
        self.speed = float(speed)
        self.sr = 24000
        self.pipeline = KPipeline(lang_code=lang_code)

    def synthesize_sentences(self, sentences: List[str]) -> Tuple[np.ndarray, int, List[int]]:
        audios = []
        durations = []
        for text in sentences:
            gen = self.pipeline(text, voice=self.voice, speed=self.speed)
            _, _, audio = next(iter(gen))  # (graphemes, phonemes, audio)
            if not isinstance(audio, np.ndarray):
                import numpy as _np
                audio = _np.array(audio, dtype=_np.float32)
            audios.append(audio.astype(np.float32))
            ms = int(round(len(audio) / self.sr * 1000.0))
            durations.append(ms)
        if audios:
            import numpy as _np
            full = _np.concatenate(audios, axis=0)
        else:
            import numpy as _np
            full = _np.zeros((0,), dtype=_np.float32)
        return full, self.sr, durations
