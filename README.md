# Intelligent TTS System

An intelligent text-to-speech system that **automatically selects the optimal TTS engine** based on your hardware capabilities. Features **CosyVoice2** (high-quality, Apple Silicon optimized) engine with professional-grade subtitle generation. Kokoro support available with additional setup.

## Key Features

- **Smart Engine Selection**: Automatically detects system capabilities and chooses the best TTS engine
- **Performance Optimized**: ~3 seconds synthesis on lower-end systems, high-quality output on powerful hardware
- **Multiple Input Formats**: Text, PDF, ePub file uploads
- **Precise Subtitles**: MFA-aligned captions for short texts, duration-based for longer content
- **Multi-language Support**: Supports multiple languages and voice options
- **Smart Caching**: Reduces re-synthesis time for repeated content

## System Intelligence

The system automatically chooses:

- **CosyVoice2** → Apple Silicon/high-end systems (premium quality, MPS accelerated)
- **Kokoro** → Available with hexgrad/Kokoro-82M setup (fast synthesis)
- **Optimized MFA alignment** → Based on text length and system capabilities

## Requirements

- Python 3.10–3.12
- FFmpeg: https://ffmpeg.org/download.html
- **For CosyVoice2**: 8GB+ VRAM or Apple Silicon with 16GB+ unified memory
- **For MFA alignment**: Montreal Forced Alignment toolkit (optional)

## Quick Start

```bash
# Clone and setup
git clone <your-repo>
cd intelligent_tts_system
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Initialize CosyVoice2 submodule (for high-quality synthesis)
git submodule update --init --recursive

# Download CosyVoice2 models (recommended for best quality)
python -c "from modelscope import snapshot_download; snapshot_download('iic/CosyVoice2-0.5B', local_dir='./third_party/CosyVoice/pretrained_models/CosyVoice2-0.5B')"
```

## Run the Server

### macOS (with Homebrew espeak-ng)

```bash
ESPEAK_DATA_PATH="/opt/homebrew/share/espeak-ng-data" uvicorn app.api:app --reload
```

### Linux/Windows

```bash
uvicorn app.api:app --reload
```

Open http://127.0.0.1:8000 for the web interface or http://127.0.0.1:8000/docs for API documentation.

## API Endpoints

### Main Synthesis Endpoint

`POST /synthesize`

- **Engine**: `auto` (recommended), `kokoro`, or `cosyvoice2`
- **Input**: Text or file upload (PDF, ePub, TXT)
- **Output**: ZIP file containing `audio.wav` + `captions.srt`

### Additional Endpoints

- `GET /recommended-engine` — Get recommended engine for current system
- `GET /voices` — List available voices
- `POST /synthesize/stream` — Streaming audio synthesis

## Configuration Options

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

## Performance Benchmarks

| System         | Engine     | Text Length | Processing Time |
| -------------- | ---------- | ----------- | --------------- |
| GTX 970        | Kokoro     | 800 words   | ~3 seconds      |
| M4 MacBook Pro | CosyVoice2 | 800 words   | ~8-12 seconds   |
| M4 MacBook Pro | Kokoro     | 800 words   | ~1-2 seconds    |

## Advanced Setup

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

1. **Auto-download** (recommended):
   ```bash
   python -c "from modelscope import snapshot_download; snapshot_download('iic/CosyVoice2-0.5B', local_dir='./third_party/CosyVoice/pretrained_models/CosyVoice2-0.5B')"
   ```
2. **Manual setup**:
   - Download models to `third_party/CosyVoice/pretrained_models/`
   - Ensure `cosyvoice2.yaml` is in the model directory
3. Models are auto-detected at startup

**Note**: CosyVoice2 models are ~988MB. The system is optimized for CosyVoice2 on Apple Silicon with MPS acceleration.

## Current Status

### **Fully Working:**

- **CosyVoice2 Engine**: Complete with Apple Silicon MPS acceleration
- **Model Auto-Download**: Models download automatically on first run
- **Web Interface**: FastAPI server with Gradio components
- **Error-Free Startup**: All dependencies resolved

### **Requires Additional Setup:**

- **Kokoro Engine**: Needs hexgrad/Kokoro-82M package (different from PyPI kokoro-tts)
- **Montreal Forced Alignment**: Install via conda if precise alignment needed

## Troubleshooting

### Common Issues

- **Missing models**: Run model download command or check `third_party/CosyVoice/pretrained_models/`
- **EspeakWrapper issues**: Set `ESPEAK_DATA_PATH` environment variable
- **Import errors**: Ensure all dependencies installed with `pip install -r requirements.txt`
- **Audio distortion**: System applies automatic RMS normalization to prevent clipping
- **Kokoro unavailable**: Install hexgrad/Kokoro-82M separately if needed
- **grpcio compilation**: Fixed in requirements.txt with pre-compiled wheels

### macOS Specific

- Install espeak-ng: `brew install espeak-ng`
- Use `ESPEAK_DATA_PATH="/opt/homebrew/share/espeak-ng-data"` when running
- System will automatically detect MPS (Metal Performance Shaders) acceleration

### Performance Tips

- CosyVoice2 automatically selected on Apple Silicon for optimal performance
- Disable MFA alignment for texts >1000 characters on lower-end systems
- Enable caching for frequently used text
- Apple Silicon: Automatic MPS (Metal Performance Shaders) acceleration
- Models preload at startup to avoid first-request delay

## Roadmap

- [x] Smart engine selection and hardware detection
- [x] CosyVoice2 engine with Apple Silicon optimization
- [x] Intelligent MFA alignment
- [x] Complete dependency resolution and error-free startup
- [ ] Kokoro engine integration (hexgrad/Kokoro-82M)
- [ ] Real-time streaming synthesis
- [ ] Batch processing for multiple files
- [ ] Custom voice training integration
