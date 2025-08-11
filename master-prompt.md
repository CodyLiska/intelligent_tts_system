# Master Prompt — TTS MVP + Research + Benchmark
## Role:
- You are an expert AI engineer specializing in open-source Text-to-Speech and subtitle alignment. You think carefully, verify facts with current sources, and return copy-pasteable code and commands.

## Goal:
- Help me choose the best open and free TTS models for a tool that converts EPUB/PDF/TXT → high-quality audio + perfectly synced subtitles (SRT/VTT). Then sketch a minimal pipeline and provide a benchmark script to compare speed/quality on my machine.

## My context (fill if known, otherwise assume sensible defaults):
- OS: {{Windows 11 / macOS / Linux}}
- Python: {{3.9–3.12}}
- GPU: {{GTX970 on Windows PC / M4 Pro with 48gb ram on MacBook pro}}
- Use cases: Long-form reading (books, articles), English primary; bonus if multilingual and light voice-cloning.
- Preference: Apache-2.0/MIT/BSD licenses only.

## What to Deliver:
### 1. Model Shortlist (Open & Free) — 3–6 options
- For each model (e.g., Kokoro, CosyVoice 2, plus 1–3 strong contenders):
- Summary: What it is best at (1–2 lines).
- Pros / Cons (bullets).
- Specs: License, languages, voice cloning (zero-/few-shot), streaming, model size, GPU/CPU needs.
- Why it fits this app.
- Links & dates (home repo/paper, last release).
- Cite sources for non-obvious claims.

### 2. Recommendation & Rationale
- Primary engine for my MVP and fallback engine, with a short decision tree: “If user wants multilingual/zero-shot → CosyVoice 2; if ultra-fast stable long-form English → Kokoro,” etc.
- Call out any licensing or edge-case caveats (commercial use, voice cloning ethics).

### 3. Minimal Pipeline (copy-pasteable)
- A concise, battle-tested path from document to audio + captions:
- Text extraction: EPUB (ebooklib/calamares/epub2txt), PDF (pypdf/pymupdf), TXT.
- Normalization & sentence chunking: punctuation restore if needed, sentence splitter (spaCy or nltk), length rules for TTS.
- Synthesis: default Kokoro (Apache-2.0); optional CosyVoice 2 for multilingual/zero-shot.
- Forced alignment → SRT/VTT: aeneas or Montreal Forced Aligner (MFA).
- Muxing: generate SRT and VTT; ensure timecodes map to chunk boundaries.
- Include a tiny diagram and exact install commands for Windows and Linux (PowerShell + bash). 
- Include ffmpeg install.

### 4. Quick Benchmark Script
- A single Python script (benchmark_tts.py) that:
	- Loads 2–3 shortlisted models (at least Kokoro and CosyVoice 2).
	- Synthesizes the same short passage (≈150–300 words).
	- Measures Real-Time Factor (RTF), wall clock, memory, and writes WAVs.
	- Optionally runs a lightweight alignment to estimate timing accuracy (e.g., aeneas) and reports average word/phoneme sync error.
	- Uses dependency-pinned requirements.txt.
	- Works CPU-only if no GPU; auto-detects CUDA if present.

- Provide:
	- requirements.txt
	- benchmark_tts.py (well-commented)
	- Sample text blob inline

- How to run: `python benchmark_tts.py --engine kokoro`, etc.

### 5. Beginner-Friendly Setup
- Beginner-Friendly Setup
- Step-by-step for Windows (PowerShell, Python 3.9+), Linux, and optional Conda.
- Common gotchas (ffmpeg missing, PyTorch CUDA wheels, long path issues on Windows, MFA acoustic model download).
- Storage/network notes (model weights sizes, first-run download times).
- MVP Project Skeleton

### 6. MVP Project Skeleton
- Provide a minimal repo layout tree and the core files:
- extract_text.py, chunk_text.py, synthesize.py, align_subtitles.py, make_captions.py, main.py
- Each file: concise, production-lean code blocks I can paste.

CLI example:
`python main.py --in book.epub --out out/ --engine kokoro --lang en --format srt,vtt --voice default`

### 7. Quality & Next Steps
- How to evaluate naturalness (brief rubric), stability on long texts, and alignment accuracy.
- Next features: streaming synthesis, voice presets, multilingual switching, caching, parallel chunk queue, pause/resume, chapter-aware splitting.
- Risks/edge cases: PDFs with columns, tables, math; EPUB footnotes; hallucinated punctuation; VTT cue lengths; SSML support; memory spikes.

#### Constraints & Style
- Use only open/free models. Prefer Apache-2.0, MIT, BSD.
- Verify freshness: browse the web for current releases; provide citations with dates.
- Be concrete: show exact commands, version pins, and minimal code that runs.
- No hidden steps. Assume I’m new to TTS; avoid unexplained jargon.
- If a detail is uncertain, state the assumption and move on with a safe default.

### Output Format
- Start with a one-page executive summary.
- Then sections matching the deliverables above with clear headings.
- Include a small comparison table for the model shortlist.
- Provide code blocks for all scripts and configs.
- End with a Ready-to-Run checklist.

#### Optional Variables You Can Fill In Now
- OS: Windows 11
- Python: 3.9 (can use 3.11 if supported)
- GPU: {{on the windows pc its a gtx 970 and on the macbook pro its an m4 pro with 48gb of ram}}
- Primary language: English; bonus: multilingual
- License preference: Apache-2.0/MIT first


---

i want to build a powerful text-to-speech conversion tool that makes it easy to turn ePub, PDF, or text files into high-quality audio with matching subtitles in seconds but first i need help choosing the best open free tts model to use. can you research and find a few tts models that fit this bill? provide pros and cons for each as well as why its a good choice for this app. take your time and use all resources available to you.

sketch a minimal pipeline next (text extraction → sentence chunking → TTS (Kokoro/Cosy) → forced alignment → SRT/VTT mux), plus a quick benchmark script to compare speed/quality across these models on your hardware

MVP
- Start with Kokoro (Apache-2.0) as your default engine for speed + quality. 
- Add CosyVoice 2 (Apache-2.0) for zero-shot cloning and multilingual breadth. 
- Use aeneas or MFA to produce accurate subtitles from your synthesized audio

Next step following MVP
- make it “Feature-rich & flexible” add CosyVoice 2 for main synthesis (multilingual, zero-shot cloning, streaming).
- Fall back to Kokoro for ultra-fast, stable long-form voices (English-first). 
- a `/voices` endpoint that returns the full, up-to-date list straight from Kokoro so I can populate a dropdown in the UI

 I've never make or worked with a tts app so keep that in mind when walking me through these steps
