# Video Generation API Recommendations

## Current Status

**Stability AI**: ❌ Video generation API returns 404 (not available or discontinued)

## Recommended Solutions

### Option 1: Runway ML (BEST CHOICE) ⭐

**Why**: 
- ✅ Working API with good documentation
- ✅ High quality video generation
- ✅ Easy integration
- ✅ Reliable service

**Setup**:
1. Sign up: https://runwayml.com
2. Get API key: Dashboard → API Keys
3. Add to `backend/.env`:
   ```env
   RUNWAY_API_KEY=your_runway_key_here
   USE_MOCK_VIDEO=false
   ```
4. The code is already set up to use Runway ML if you have the key!

**Cost**: ~$0.05 per second of video

---

### Option 2: Pika Labs

**Why**:
- ✅ Good quality
- ✅ Text-to-video support
- ✅ Active development

**Setup**:
1. Sign up: https://pika.art
2. Get API key
3. Add to `backend/.env`:
   ```env
   PIKA_API_KEY=your_pika_key_here
   ```
4. Would need code integration (similar to Runway ML)

**Cost**: Varies by plan

---

### Option 3: Luma Labs Dream Machine

**Why**:
- ✅ Free tier available
- ✅ Good quality
- ✅ Newer service

**Setup**:
1. Sign up: https://lumalabs.ai
2. Get API key
3. Add to `backend/.env`:
   ```env
   LUMA_API_KEY=your_luma_key_here
   ```
4. Would need code integration

**Cost**: Free tier + paid plans

---

### Option 4: Keep Stability AI for Images Only

**Current Status**:
- ✅ Image generation works perfectly
- ❌ Video generation doesn't work

**Workaround**: 
- Use Stability AI to generate images
- Convert images to simple video slideshows using FFmpeg
- Add transitions and effects

---

## Quick Start with Runway ML

1. **Get API Key**:
   - Go to https://runwayml.com
   - Sign up / Log in
   - Navigate to Dashboard → API
   - Copy your API key

2. **Update `.env`**:
   ```env
   RUNWAY_API_KEY=your_key_here
   USE_MOCK_VIDEO=false
   ```

3. **Restart Backend**:
   ```bash
   cd backend
   uvicorn main:app --host 127.0.0.1 --port 8002 --reload
   ```

4. **Test Video Generation**:
   - The code will automatically use Runway ML if the key is present
   - Runway ML is now prioritized over Stability AI for video

---

## Code Priority Order

The code now tries APIs in this order:
1. **Runway ML** (if API key present) - BEST for video
2. **Stability AI** (if API key present) - Works for images, not video
3. **Mock mode** (fallback)

---

## Recommendation

**Use Runway ML** - It's the most reliable option for video generation right now. Your Stability AI key is still useful for image generation, but for video, Runway ML is the way to go.

