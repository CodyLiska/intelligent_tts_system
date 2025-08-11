# TTS Starter (Kokoro + FastAPI) — sentence-level subtitles

A tiny, production-friendly starter that turns text, PDF, or ePub into high-quality audio with matching **sentence-level SRT subtitles** using the open-source **Kokoro** TTS model.

> Why Kokoro? It’s fast, Apache-2.0 licensed, and great for long-form reading.

---

## 1) Requirements

- Python 3.10–3.12
- FFmpeg (recommended for audio tooling): https://ffmpeg.org/download.html
- (Windows) Optional: install **espeak-ng** for best English fallback/multilingual text-to-phoneme support. See the Kokoro PyPI page for a Windows installer.

## 2) Setup

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

pip install --upgrade pip
pip install kokoro
pip install python-multipart
pip instal soundfile numpy nltk pypdf pymupdf ebooklib textgrid psutil
pip install -r requirements.txt
```

## 3) Run the API

```bash
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs to try it.

## 4) Endpoints

- `POST /synthesize/text` — JSON body with `{ "text": "...", "voice": "af_heart", "speed": 1.0 }`
- `POST /synthesize/file` — `multipart/form-data` with; `file (required)`, `voice (default af_heart)`, `speed (default 1.0)`, `lang_code (default a)`

Both return a ZIP containing:

- `audio.wav` — the full concatenated audiobook-style audio
- `subtitles.srt` — sentence-level subtitles aligned by measured audio durations

## 5) Notes on Voices & Language

- Default voice is `af_heart` (American English). Set `lang_code='a'` for American English inside code.
- You can change to other Kokoro voices by changing the `voice` parameter.
- For multilingual needs, make sure to **match** `lang_code` (pipeline) and the voice used.

### Parameters

#### voice (string)

⦁ Pick any Kokoro voice ID. A few good ones you can try right away:

##### American English (lang_code: "a")

⦁ af_heart, af_bella, af_nicole, af_aoede, af_kore, af_sarah, af_nova, af_sky, af_alloy, af_jessica, af_river, am_michael, am_fenrir, am_puck, am_echo, am_eric, am_liam, am_onyx, am_santa, am_adam.

##### British English (lang_code: "b")

⦁ bf_emma, bf_isabella, bf_alice, bf_lily, bm_george, bm_fable, bm_lewis, bm_daniel.

⦁ (There are also voices for Japanese, Mandarin Chinese, Spanish, French, Hindi, Italian, and Brazilian Portuguese. See the full list in Kokoro’s VOICES.md.)

#### speed (number)

⦁ Speaking-rate multiplier. Typical usable range: 0.5 → 2.0 (0.5 = slower, 2.0 = faster). The official demo exposes exactly this range. Default in our starter: 1.0.

#### lang_code (string)

⦁ Language selector for the pipeline. This must match the voice’s language (Kokoro picks the pipeline from the first letter of the voice ID). Valid codes: - a = American English - b = British English - e = Spanish - f = French - h = Hindi - i = Italian - j = Japanese (requires misaki[ja])
-p = Brazilian Portuguese - z = Mandarin Chinese (requires misaki[zh])

- (Why “match”? In the reference app, the pipeline is selected with pipelines[voice[0]], so if you pick bf_emma, you should use lang_code: "b", etc.)

### Ready-to-copy request bodies

⦁ American English (female) – Heart, normal speed
⦁ `{ "text": "Chapter 1. Call me Ishmael.", "voice": "af_heart", "speed": 1.0, "lang_code": "a" }`

⦁ American English (male) – Michael, slightly faster
⦁ `{ "text": "Welcome to our show!", "voice": "am_michael", "speed": 1.2, "lang_code": "a" }`

⦁ British English (female) – Emma, slower
⦁ `{ "text": "Good evening, everyone.", "voice": "bf_emma", "speed": 0.9, "lang_code": "b" }`

⦁ Spanish – Dora
⦁ `{ "text": "Bienvenidos a la narración.", "voice": "ef_dora", "speed": 1.0, "lang_code": "e" }`

⦁ Japanese – Alpha (install misaki[ja] first)
⦁ `{ "text": "これはテストです。", "voice": "jf_alpha", "speed": 1.0, "lang_code": "j" }`

⦁ Mandarin – Xiaoxiao (install misaki[zh] first)
⦁ `{ "text": "这是一段测试语音。", "voice": "zf_xiaoxiao", "speed": 1.0, "lang_code": "z" }`

## 6) Roadmap Upgrades (optional)

- **Word-level timestamps**: integrate WhisperX (MIT) for alignment to generate word timings.
- **Zero-shot cloning**: add a second engine (e.g., CosyVoice2) behind the same `TtsEngine` interface.
- **Paragraph-level granularity**: switch the splitter to paragraph mode for fewer, longer captions.
- **Streaming**: expose chunked synthesis via server-sent events or websockets for immediate playback.

---

## Troubleshooting

- If Kokoro complains about g2p/phoneme backend, install `espeak-ng` and restart the server.
- Very long documents: try paragraph mode or paginate chapters to keep memory usage stable.
