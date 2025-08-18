# 🍎 MacBook Pro M4 Setup Instructions

  1. Clone your repo (replace with your actual GitHub URL)
     - git clone https://github.com/yourusername/tts-starter.git
     - cd tts-starter

  2. Python Environment Setup
     - python3 -m venv .venv
     - source .venv/bin/activate

  >Optional Upgrade pip
  >- pip install --upgrade pip

  3. Install core dependencies
     - pip install -r requirements.txt

  4. Download CosyVoice2 Models (Required for High-Quality TTS)
     - You'll need to manually download the CosyVoice2 models since they're large files (several GB):

  5. Create the models directory
     - mkdir -p third_party/CosyVoice/pretrained_models/CosyVoice2-0.5B

  >Option A: Download via git (if you have git-lfs)
  >- cd third_party
  >- git clone https://huggingface.co/FunAudioLLM/CosyVoice2-0.5B
  >- mv CosyVoice2-0.5B CosyVoice/pretrained_models/CosyVoice2-0.5B

  >Option B: Manual download from HuggingFace
  >- Go to: https://huggingface.co/FunAudioLLM/CosyVoice2-0.5B
  >- Download all files to: third_party/CosyVoice/pretrained_models/CosyVoice2-0.5B/

  6. Install Additional CosyVoice2 Dependencies
     - Since your M4 MacBook will use CosyVoice2, install these additional packages:
     - pip install diffusers transformers onnxruntime accelerate

  7. Create Reference Audio Directory
     - mkdir -p data/refs
     - Copy a reference audio file (16kHz mono WAV) to data/refs/ref.wav
     - Or the system will use a default silence reference

  8. Install Optional Dependencies for Best Experience and better audio processing
     - brew install ffmpeg

  9. For MFA alignment (optional but recommended for subtitles)
     - pip install montreal-forced-alignment

  10. Verify Installation and Test the system
  - python -c "from app.services.models import get_recommended_engine print(f'Recommended engine: {get_recommended_engine()}')"

  11. Run the Server
     - uvicorn app.api:app --reload
     - Open http://127.0.0.1:8000 in your browser

  ## 🎯 Expected Results on M4 MacBook Pro
  - Auto-selected engine: CosyVoice2 (high quality)
  - Performance: ~8-12 seconds for 800-word texts
  - Quality: Premium voice synthesis with cloning capabilities
  - MFA alignment: Full support for precise subtitles

  ### 📁 Manual Downloads Required

  #### Essential (for CosyVoice2):

  1. CosyVoice2 models (~3-5GB) from HuggingFace
    - Download: https://huggingface.co/FunAudioLLM/CosyVoice2-0.5B
    - Place in: third_party/CosyVoice/pretrained_models/CosyVoice2-0.5B/

  Optional:

  1. Reference audio file (16kHz mono WAV) for voice cloning
    - Place in: data/refs/ref.wav

  🚨 Troubleshooting

  #### If CosyVoice2 models aren't found:

  - The system will automatically fall back to Kokoro (still fast)
  - Check the model path: third_party/CosyVoice/pretrained_models/CosyVoice2-0.5B/cosyvoice2.yaml should exist       

  #### If you get MPS (Apple Silicon GPU) errors:

  export PYTORCH_ENABLE_MPS_FALLBACK=1

  #### For development without large models:

  - Just run with Kokoro (no manual downloads needed)
  - Set engine to "kokoro" manually in the UI

  #### 🎉 Quick Test

  - Once everything is running, test with this text to see the M4's performance:
  "This is a test of the intelligent TTS system running on Apple Silicon."
  - You should see it auto-select CosyVoice2 and produce high-quality audio in ~3-5 seconds for short texts.