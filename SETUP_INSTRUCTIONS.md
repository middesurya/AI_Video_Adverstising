# Live Video Generation Setup Instructions

## Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This will install:
- `python-dotenv` - For loading environment variables
- `requests` - For API calls
- `ffmpeg-python` - For video/audio processing

## Step 2: Choose Your Video Generation API

### Option A: Stability AI (Recommended - Good Balance)

1. **Sign up**: https://platform.stability.ai/
2. **Get API key**: Go to Account → API Keys
3. **Add to `.env`**:
   ```env
   STABILITY_API_KEY=your_key_here
   USE_MOCK_VIDEO=false
   ```

### Option B: Runway ML (Easiest)

1. **Sign up**: https://runwayml.com
2. **Get API key**: Dashboard → API
3. **Install SDK**: `pip install runwayml`
4. **Add to `.env`**:
   ```env
   RUNWAY_API_KEY=your_key_here
   USE_MOCK_VIDEO=false
   ```

### Option C: Use Mock (For Testing)

Keep `USE_MOCK_VIDEO=true` in `.env` to test without API keys.

## Step 3: Set Up Text-to-Speech (Optional)

### Option A: ElevenLabs (Best Quality)

1. **Sign up**: https://elevenlabs.io
2. **Get API key**: Profile → API Key
3. **Add to `.env`**:
   ```env
   ELEVENLABS_API_KEY=your_key_here
   ```

### Option B: Use Open Source (Free)

No API key needed, but requires additional setup (Bark/Coqui TTS).

## Step 4: Configure Environment

Edit `backend/.env`:

```env
# Video Generation
STABILITY_API_KEY=your_stability_key_here
# OR
RUNWAY_API_KEY=your_runway_key_here

# Text-to-Speech (Optional)
ELEVENLABS_API_KEY=your_elevenlabs_key_here

# Configuration
USE_MOCK_VIDEO=false  # Set to true to use mock videos
```

## Step 5: Install FFmpeg (Required for Video Assembly)

### Windows:
1. Download from: https://ffmpeg.org/download.html
2. Extract and add to PATH
3. Or use: `choco install ffmpeg` (if you have Chocolatey)

### Verify FFmpeg:
```bash
ffmpeg -version
```

## Step 6: Test the Setup

1. **Start backend**:
   ```bash
   cd backend
   uvicorn main:app --host 127.0.0.1 --port 8002 --reload
   ```

2. **Test video generation**:
   - Use the frontend to generate a video
   - Check `backend/videos/` directory for generated files
   - Check backend logs for any errors

## Step 7: Troubleshooting

### Issue: "API key not found"
- Make sure `.env` file is in `backend/` directory
- Check that variable names match exactly
- Restart the backend server after changing `.env`

### Issue: "FFmpeg not found"
- Install FFmpeg and add to PATH
- Restart terminal/IDE after installation

### Issue: "Video not playing"
- Check that videos are in `backend/videos/` directory
- Verify static file serving is working: http://localhost:8002/videos/
- Check browser console for CORS or loading errors

### Issue: "API rate limits"
- Check your API provider's rate limits
- Consider using mock mode for development: `USE_MOCK_VIDEO=true`

## Current Implementation Status

✅ **Working:**
- Mock video generation (returns placeholder URLs)
- Video preview page navigation
- Static file serving setup
- Environment variable loading

🔄 **Ready for Integration:**
- Stability AI API integration (code ready, needs API key)
- Runway ML API integration (code ready, needs API key)
- ElevenLabs TTS integration (code ready, needs API key)
- FFmpeg video assembly (code ready, needs FFmpeg installed)

## Next Steps After Setup

1. **Test with mock videos first**: Set `USE_MOCK_VIDEO=true`
2. **Add a real API key**: Choose Stability AI or Runway ML
3. **Test single scene generation**: Generate video for one scene
4. **Add TTS**: Configure ElevenLabs for audio
5. **Combine scenes**: Generate videos for all scenes and combine
6. **Optimize**: Add caching, error handling, progress tracking

## Cost Estimates

- **Stability AI**: ~$0.02 per second of video
- **Runway ML**: ~$0.05 per second of video
- **ElevenLabs**: ~$0.30 per 1000 characters
- **60-second ad**: ~$1.20-3.00 total (depending on API)

## Support

If you encounter issues:
1. Check backend logs in terminal
2. Check browser console (F12)
3. Verify API keys are correct
4. Test API directly using curl/Postman
5. Check `backend/videos/` directory for generated files

