# Video Generation Integration Guide

## Current Status

The application currently uses **mock video generation**. The backend returns a placeholder video URL without actually generating video content. To enable real video generation, you need to integrate AI models and services.

## What's Currently Happening

The `generate_video` endpoint in `backend/main.py` (lines 230-237) currently:
1. ✅ Validates the request
2. ✅ Returns a mock video URL: `/videos/{product-name}-ad.mp4`
3. ✅ Returns a random hook score
4. ❌ **Does NOT actually generate video**

## Next Steps to Enable Real Video Generation

### Option 1: Use Cloud AI Video APIs (Easiest)

#### A. Runway ML API
```python
# Add to requirements.txt:
# runwayml

# In generate_video function:
import runway
from runway import generate

runway.api_key = os.getenv("RUNWAY_API_KEY")
video = generate(
    prompt=scene.description,
    duration=scene.duration
)
```

**Setup:**
1. Sign up at https://runwayml.com
2. Get API key
3. Add to `.env`: `RUNWAY_API_KEY=your_key_here`
4. Install: `pip install runwayml`

#### B. Pika Labs API
```python
# Similar integration pattern
# Requires API key from pika.art
```

#### C. Stability AI Video API
```python
# stability-sdk package
# Requires API key from stability.ai
```

### Option 2: Self-Hosted Models (More Complex)

#### A. Open-Sora (Open Source)
**Requirements:**
- GPU with 16GB+ VRAM
- CUDA installed
- Python environment

**Setup:**
```bash
# Install dependencies
pip install diffusers transformers accelerate

# Clone Open-Sora
git clone https://github.com/hpcaitech/Open-Sora.git
cd Open-Sora
pip install -r requirements.txt
```

**Integration:**
```python
from diffusers import DiffusionPipeline
import torch

pipe = DiffusionPipeline.from_pretrained(
    "stabilityai/stable-video-diffusion",
    torch_dtype=torch.float16
)
pipe = pipe.to("cuda")

# Generate video for each scene
video = pipe(scene.description, num_inference_steps=50).images
```

#### B. AnimateDiff
Similar setup, different model architecture.

### Option 3: Hybrid Approach (Recommended for MVP)

Use a **simpler text-to-image** model and create a slideshow:

```python
# 1. Generate images for each scene using Stable Diffusion
# 2. Add transitions between images
# 3. Add TTS audio
# 4. Combine with FFmpeg

# This is faster and requires less GPU power
```

## Required Components

### 1. Text-to-Video Model
- **Cloud API**: Runway, Pika, Stability AI
- **Self-hosted**: Open-Sora, AnimateDiff, Stable Video Diffusion

### 2. Text-to-Speech (TTS)
- **Bark** (open source, high quality)
- **Coqui TTS** (open source, customizable)
- **ElevenLabs API** (cloud, best quality)
- **Google Cloud TTS** (cloud, reliable)

### 3. Video Assembly
- **FFmpeg** (required for combining video + audio)
  ```bash
  pip install ffmpeg-python
  ```

### 4. Environment Variables (.env)

Create `backend/.env`:
```env
# Video Generation API Keys (choose one)
RUNWAY_API_KEY=your_runway_key
# OR
STABILITY_API_KEY=your_stability_key
# OR
PIKA_API_KEY=your_pika_key

# TTS API Keys
ELEVENLABS_API_KEY=your_elevenlabs_key
# OR use open source (Bark/Coqui) - no key needed

# Model Configuration
USE_GPU=true
GPU_DEVICE=0
MODEL_CACHE_DIR=./models
```

## Implementation Steps

### Step 1: Choose Your Approach
- **Quick Start**: Use Runway ML API (easiest, paid)
- **Budget-Friendly**: Use Stability AI API (paid but cheaper)
- **Full Control**: Self-host Open-Sora (free but requires GPU)

### Step 2: Install Dependencies

For **Cloud API approach**:
```bash
cd backend
pip install requests python-dotenv
```

For **Self-hosted approach**:
```bash
cd backend
pip install diffusers transformers accelerate torch torchvision ffmpeg-python
```

### Step 3: Update Backend Code

Replace the mock generation in `backend/main.py` (lines 230-237) with real model calls.

### Step 4: Add Video Storage

Create a `backend/videos/` directory to store generated videos:
```bash
mkdir backend/videos
```

### Step 5: Update Frontend

The frontend already expects a video URL. You just need to:
1. Serve the generated videos (add static file serving in FastAPI)
2. Ensure the video URL is accessible

## Recommended Quick Start (Runway ML)

1. **Sign up for Runway ML**: https://runwayml.com
2. **Get API key** from dashboard
3. **Create `.env` file**:
   ```bash
   cd backend
   echo "RUNWAY_API_KEY=your_key_here" > .env
   ```
4. **Install SDK**:
   ```bash
   pip install runwayml python-dotenv
   ```
5. **Update `generate_video` function** to call Runway API

## Cost Considerations

- **Runway ML**: ~$0.05 per second of video
- **Stability AI**: ~$0.02 per second
- **Self-hosted**: Free but requires GPU server ($0.50-2/hour)

## Testing Without Real Models

For now, you can:
1. Create placeholder video files in `backend/videos/`
2. Use the mock generation (current implementation)
3. Test the full flow without actual video generation

## Next Steps Checklist

- [ ] Choose video generation approach (Cloud API vs Self-hosted)
- [ ] Get API keys if using cloud services
- [ ] Install required dependencies
- [ ] Create `.env` file with API keys
- [ ] Update `generate_video` function in `backend/main.py`
- [ ] Add video storage directory
- [ ] Test video generation with one scene
- [ ] Integrate TTS for audio
- [ ] Use FFmpeg to combine video + audio
- [ ] Test full pipeline end-to-end

