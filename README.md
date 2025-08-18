# Intelligent TTS System

An intelligent text-to-speech system that **automatically selects the optimal TTS engine** based on your hardware capabilities. Supports both **Kokoro** (fast, lightweight) and **CosyVoice2** (high-quality, resource-intensive) engines with professional-grade subtitle generation.

## ✨ Key Features

- 🧠 **Smart Engine Selection**: Automatically detects system capabilities and chooses the best TTS engine
- ⚡ **Performance Optimized**: ~3 seconds synthesis on lower-end systems, high-quality output on powerful hardware
- 📝 **Multiple Input Formats**: Text, PDF, ePub file uploads
- 🎯 **Precise Subtitles**: MFA-aligned captions for short texts, duration-based for longer content
- 🌐 **Multi-language Support**: Supports multiple languages and voice options
- 💾 **Smart Caching**: Reduces re-synthesis time for repeated content

## 🎯 System Intelligence

The system automatically chooses:
- **Kokoro** → GTX 970/lower-end systems (fast synthesis)
- **CosyVoice2** → M4 MacBook Pro/high-end systems (premium quality)
- **Optimized MFA alignment** → Based on text length and system capabilities

## 📋 Requirements

- Python 3.10–3.12
- FFmpeg: https://ffmpeg.org/download.html
- **For CosyVoice2**: 8GB+ VRAM or Apple Silicon with 16GB+ unified memory
- **For MFA alignment**: Montreal Forced Alignment toolkit (optional)

## 🚀 Quick Start

```bash
# Clone and setup
git clone <your-repo>
cd tts-starter
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS/Linux  
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

## 🏃 Run the Server

```bash
uvicorn app.api:app --reload
```

Open http://127.0.0.1:8000 for the web interface or http://127.0.0.1:8000/docs for API documentation.

## 🔧 API Endpoints

### Main Synthesis Endpoint
`POST /synthesize`
- **Engine**: `auto` (recommended), `kokoro`, or `cosyvoice2`
- **Input**: Text or file upload (PDF, ePub, TXT)
- **Output**: ZIP file containing `audio.wav` + `captions.srt`

### Additional Endpoints
- `GET /recommended-engine` — Get recommended engine for current system
- `GET /voices` — List available voices
- `POST /synthesize/stream` — Streaming audio synthesis

## 🎛️ Configuration Options

### Engine Selection
- **auto** (recommended): Automatically selects optimal engine
- **kokoro**: Fast, lightweight TTS (1-3 seconds)
- **cosyvoice2**: High-quality TTS with voice cloning

### Voice Options (Kokoro)
**American English**: `af_heart`, `af_bella`, `af_nicole`, `am_michael`, `am_eric`  
**British English**: `bf_emma`, `bf_isabella`, `bm_george`, `bm_lewis`  
**Other Languages**: Spanish, French, Japanese, Chinese, Hindi, Italian, Portuguese

### Parameters
- **Speed**: 0.5-2.0 (speech rate multiplier)
- **Alignment**: Enable/disable MFA for precise subtitles
- **Post Filter**: Audio enhancement options

### CosyVoice2 Options
- **Mode**: `cross`, `zero`, `auto`
- **Reference Audio**: Upload custom voice samples
- **Prompt**: Text description for voice characteristics

## 📊 Performance Benchmarks

| System | Engine | Text Length | Processing Time |
|--------|--------|-------------|----------------|
| GTX 970 | Kokoro | 800 words | ~3 seconds |
| M4 MacBook Pro | CosyVoice2 | 800 words | ~8-12 seconds |
| M4 MacBook Pro | Kokoro | 800 words | ~1-2 seconds |

## 🔧 Advanced Setup

### Environment Variables
```bash
# Force specific engine (overrides auto-detection)
export COSY_DEVICE=cpu          # Force CosyVoice2 to CPU
export COSY_DEVICE=gpu          # Force CosyVoice2 to GPU

# Model directories
export COSYVOICE_DIR=/path/to/CosyVoice
export COSYVOICE2_DIR=/path/to/models

# Cache settings
export TTS_CACHE_DIR=./cache
```

### CosyVoice2 Model Setup
1. Download CosyVoice2 models to `third_party/CosyVoice/pretrained_models/`
2. Ensure `cosyvoice2.yaml` is in the model directory
3. Models are auto-detected at startup

## 🚨 Troubleshooting

### Common Issues
- **CUDA OOM**: System automatically falls back to CPU or Kokoro
- **MFA slow**: Disable alignment for long texts or upgrade system
- **Missing models**: Check `third_party/CosyVoice/pretrained_models/`

### Performance Tips
- Use `auto` engine selection for optimal performance
- Disable MFA alignment for texts >1000 characters on lower-end systems
- Enable caching for frequently used text

## 🗺️ Roadmap

- ✅ Smart engine selection
- ✅ Dual engine support (Kokoro + CosyVoice2)
- ✅ Intelligent MFA alignment
- 🔄 Real-time streaming synthesis
- 📋 Batch processing for multiple files
- 🎨 Custom voice training integration
