# CLAUDE.md - AI Assistant Guide for AI Video Advertising Platform

This document provides comprehensive guidance for AI assistants working on the AI-Powered Ad Video Generator codebase.

## Project Overview

**Project Name:** AI-Powered Ad Video Generator (AdVision AI)
**Purpose:** A web application that guides users through refining a creative brief and automatically generates one-minute AI video advertisements.
**Status:** MVP complete with mock video generation; ready for real AI model integration
**Repository Type:** Monorepo with separate frontend and backend

### Key Features
- Prompt refinement UI with mood sliders, tone selectors, and style pickers
- AI-powered conversational agent for ad requirement clarification
- Storyboard generation with visual scene breakdown and editing
- Video generation pipeline (currently mock, ready for API integration)
- Engagement metrics (hook score, retention predictions)
- Multi-format export (TikTok, Reels, Shorts, YouTube)

## Tech Stack

### Frontend
- **Framework:** Next.js 14 (React 18.2.0)
- **Styling:** CSS Modules with custom dark theme
- **HTTP Client:** Axios 1.6.0
- **Animations:** Framer Motion 10.16.0
- **Testing:** Jest 29.7.0, React Testing Library 14.0.0
- **Port:** 3000

### Backend
- **Framework:** FastAPI 0.104.1
- **ASGI Server:** Uvicorn 0.24.0
- **Validation:** Pydantic 2.5.0
- **HTTP Client:** httpx 0.25.0, requests 2.31.0
- **Testing:** pytest 7.4.3, pytest-asyncio 0.21.1
- **Video Processing:** ffmpeg-python 0.2.0
- **Port:** 8002 (or 8001, check START_SERVERS.md)

## Directory Structure

```
AI_Video_Adverstising/
├── frontend/                    # Next.js frontend application
│   ├── pages/                   # Next.js pages (routing)
│   │   ├── index.js            # Main application page (4-step wizard)
│   │   └── _app.js             # Next.js app wrapper
│   ├── components/              # React components
│   │   ├── PromptRefinement.js # Step 1: Creative brief input
│   │   ├── ChatInterface.js    # Step 2: AI chat refinement
│   │   ├── Storyboard.js       # Step 3: Scene editor
│   │   └── VideoPreview.js     # Step 4: Video preview & export
│   ├── styles/                  # CSS Modules
│   │   ├── Home.module.css
│   │   ├── ChatInterface.module.css
│   │   ├── PromptRefinement.module.css
│   │   └── Storyboard.module.css
│   ├── __tests__/               # Frontend tests
│   ├── package.json
│   ├── jest.config.js
│   └── next.config.js
│
├── backend/                     # FastAPI backend application
│   ├── main.py                 # Main FastAPI app (13 endpoints)
│   ├── video_service.py        # Video generation service (Runway ML, Stability AI)
│   ├── video_generator.py      # Video generation helpers
│   ├── requirements.txt        # Python dependencies
│   ├── videos/                 # Generated video output directory
│   ├── test_main.py            # Backend API tests (13 tests)
│   ├── test_simple.py          # Simple health check tests
│   ├── test_video_setup.py     # Video generation setup tests
│   ├── verify_setup.py         # Environment verification script
│   └── quick_test.py           # Quick test script
│
├── package.json                # Root package.json with monorepo scripts
├── .gitignore                  # Git ignore patterns
├── README.md                   # User-facing documentation
├── SETUP_INSTRUCTIONS.md       # Setup guide
├── VIDEO_GENERATION_SETUP.md   # Video API setup instructions
├── API_RECOMMENDATIONS.md      # Video API provider recommendations
├── START_SERVERS.md            # Server startup guide
└── CLAUDE.md                   # This file - AI assistant guide

```

## Key Files & Their Responsibilities

### Frontend Files

#### `frontend/pages/index.js` (274 lines)
**Primary application orchestrator.** Manages the 4-step wizard flow:
- **Step 1:** Brief creation (PromptRefinement)
- **Step 2:** Chat refinement (ChatInterface)
- **Step 3:** Storyboard editing (Storyboard)
- **Step 4:** Video preview (VideoPreview)

**State Management:**
- `adBrief` - Product details, mood, energy, style, archetype
- `script` - Generated script text
- `scenes` - Array of Scene objects
- `videoUrl` - Generated video URL
- `isGenerating` - Loading state
- `error` - Error messages

**Key Functions:**
- `handleBriefUpdate()` - Updates ad brief
- `handleGenerateScript()` - Calls `/api/generate-script`
- `handleGenerateVideo()` - Calls `/api/generate-video`

**Important:** Contains debug logging statements (agent log regions) - these can be cleaned up in production.

#### `frontend/components/PromptRefinement.js`
Collects initial creative brief with sliders for mood/energy, dropdowns for style/archetype.

#### `frontend/components/ChatInterface.js`
AI chat interface for refining the brief before script generation.

#### `frontend/components/Storyboard.js`
Displays generated scenes, allows editing, triggers video generation.

#### `frontend/components/VideoPreview.js`
Shows generated video with download/export options.

### Backend Files

#### `backend/main.py` (366 lines)
**Main FastAPI application.** Defines all API endpoints and data models.

**Pydantic Models:**
- `AdBrief` - Creative brief data
- `Scene` - Individual scene data
- `ScriptResponse` - Script generation response
- `VideoRequest` - Video generation request
- `VideoResponse` - Video generation response

**Key Endpoints:**
- `GET /` - Health check
- `GET /health` - Detailed health status
- `POST /api/generate-script` - Generate script from brief
- `POST /api/generate-video` - Generate video from scenes
- `GET /api/archetypes` - List story archetypes
- `GET /api/styles` - List visual styles
- `GET /videos/{filename}` - Static video file serving

**CORS Configuration:** Allows localhost:3000, 5173, 127.0.0.1:3000, and all origins (*)

**Important:** Contains debug logging to hardcoded Windows path (line 223) - should be cleaned up or made configurable.

#### `backend/video_service.py` (327+ lines)
**Video generation service class.** Handles integration with external video APIs.

**API Priority:**
1. Runway ML (preferred for video)
2. Stability AI (fallback, may not support video)
3. Mock mode (for development)

**Environment Variables:**
- `STABILITY_API_KEY` - Stability AI key
- `RUNWAY_API_KEY` - Runway ML key
- `ELEVENLABS_API_KEY` - ElevenLabs TTS key
- `USE_MOCK_VIDEO` - "true"/"false" to enable mock mode

**Key Methods:**
- `generate_video_for_scene()` - Main entry point
- `_generate_with_runway()` - Runway ML integration
- `_generate_with_stability()` - Stability AI integration
- `generate_audio_for_scene()` - TTS audio generation

**Important:** Contains hardcoded Windows log paths - needs cleanup.

#### `backend/video_generator.py`
Helper functions for video generation (to be verified).

## API Endpoints Reference

| Endpoint | Method | Request Body | Response | Purpose |
|----------|--------|--------------|----------|---------|
| `/` | GET | - | `{"message": "...", "status": "healthy"}` | Health check |
| `/health` | GET | - | Health status with services | Detailed health |
| `/api/generate-script` | POST | `AdBrief` | `ScriptResponse` | Generate ad script |
| `/api/generate-video` | POST | `VideoRequest` | `VideoResponse` | Generate video |
| `/api/archetypes` | GET | - | List of archetypes | Get story templates |
| `/api/styles` | GET | - | List of styles | Get visual styles |
| `/videos/{filename}` | GET | - | Video file | Serve generated videos |

### Example Request/Response

**Generate Script:**
```json
POST /api/generate-script
{
  "productName": "EcoBottle",
  "description": "Sustainable water bottle",
  "mood": 70,
  "energy": 80,
  "style": "cinematic",
  "archetype": "hero-journey",
  "targetAudience": "Millennials",
  "callToAction": "Buy now"
}

Response:
{
  "success": true,
  "script": "...",
  "scenes": [...]
}
```

## Development Workflow

### Initial Setup

1. **Install frontend dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Install backend dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Configure environment variables** (optional for mock mode):
   ```bash
   # backend/.env
   RUNWAY_API_KEY=your_runway_key
   STABILITY_API_KEY=your_stability_key
   ELEVENLABS_API_KEY=your_elevenlabs_key
   USE_MOCK_VIDEO=true  # Set to false to use real APIs
   ```

### Running the Application

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn main:app --reload --port 8002
# or
python -m uvicorn main:app --host 127.0.0.1 --port 8002 --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8002
- API Docs: http://localhost:8002/docs

### Testing

**Backend tests:**
```bash
cd backend
pytest test_main.py -v           # 13 tests
pytest test_simple.py -v         # Simple tests
pytest test_video_setup.py -v    # Video setup tests
pytest                           # All tests
```

**Frontend tests:**
```bash
cd frontend
npm test                         # Run all tests
npm run test:watch              # Watch mode
```

**From root:**
```bash
npm run test:all                # Run both frontend and backend tests
```

### Git Workflow

**Current Branch:** `claude/add-claude-documentation-R0AEb`

**Committing Changes:**
1. Make your changes
2. Test thoroughly
3. Commit with descriptive messages
4. Push to the branch: `git push -u origin claude/add-claude-documentation-R0AEb`

**Branch Naming:** All Claude branches should start with `claude/` and match the session ID.

## Code Patterns & Conventions

### Frontend Conventions

1. **Component Structure:**
   - Use functional components with hooks
   - Props destructuring at the top
   - State declarations next
   - Effect hooks
   - Event handlers
   - Return JSX

2. **Styling:**
   - CSS Modules (`.module.css` files)
   - Dark theme with custom properties
   - Responsive design patterns

3. **State Management:**
   - Local state with `useState`
   - Props drilling for parent-child communication
   - No global state management library

4. **API Calls:**
   - Use `fetch` API with `async/await`
   - Timeout handling (10 seconds)
   - Error boundaries and user-friendly error messages
   - Loading states during async operations

5. **Error Handling:**
   - Display errors in UI with dismiss button
   - Log errors to console
   - Graceful degradation

### Backend Conventions

1. **API Design:**
   - RESTful endpoints
   - Pydantic models for validation
   - Consistent response formats: `{success, data/error}`

2. **Error Handling:**
   - Use `HTTPException` for HTTP errors
   - Try-catch blocks for all endpoints
   - Return error in response body

3. **Code Organization:**
   - Main app in `main.py`
   - Services in separate files (`video_service.py`)
   - Models defined with Pydantic

4. **Environment Configuration:**
   - Use `python-dotenv` for env vars
   - Load `.env` at startup
   - Provide sensible defaults

### Naming Conventions

- **Files:** lowercase with underscores (Python) or PascalCase (JS components)
- **Variables:** camelCase (JS), snake_case (Python)
- **Components:** PascalCase
- **CSS Classes:** kebab-case
- **Constants:** UPPER_SNAKE_CASE

## Story Archetypes

Available archetypes (defined in `backend/main.py:75-82`):
- `hero-journey` - Hero emerges, faces challenges, triumphs
- `testimonial` - Real people share experiences
- `problem-solution` - Show struggle, then solution
- `tutorial` - Step-by-step how-to
- `comedy` - Humorous approach
- `lifestyle` - Aspirational, emotional

## Visual Styles

Available styles (defined in `backend/main.py:349-360`):
- `cinematic` - Epic, movie-like visuals
- `minimalist` - Clean, simple aesthetics
- `energetic` - Fast-paced, dynamic
- `warm` - Cozy, inviting feel
- `professional` - Corporate, polished
- `playful` - Fun, whimsical style

## Scene Generation

Each storyboard typically contains 6 scenes:
1. **Opening Hook** (10s) - Attention-grabbing intro
2. **The Problem** (8s) - Show pain point
3. **The Solution** (12s) - Reveal product
4. **Transformation** (12s) - Before/after results
5. **Social Proof** (8s) - Testimonials
6. **Call to Action** (10s) - Closing CTA

Total duration: ~60 seconds

## Video Generation APIs

### Current Status
- **Mock Mode:** Enabled by default (`USE_MOCK_VIDEO=true`)
- **Runway ML:** Recommended, requires API key
- **Stability AI:** Fallback, video API may not work (404 errors reported)

### Integration Priority
1. Runway ML (best for video)
2. Stability AI (works for images, not video)
3. Mock mode (development/testing)

### Cost Estimates
- Runway ML: ~$0.05 per second
- Stability AI: ~$0.02 per second
- ElevenLabs TTS: ~$0.30 per 1000 characters
- **60-second ad:** $1.20-$3.00 total

See `API_RECOMMENDATIONS.md` for detailed setup instructions.

## Important Notes for AI Assistants

### Before Making Changes

1. **Read before modifying:** Always read files before editing them
2. **Understand context:** Review related files to understand dependencies
3. **Check tests:** Verify existing tests before changing functionality
4. **Preserve patterns:** Follow existing code patterns and conventions

### Common Tasks

#### Adding a New API Endpoint

1. Define Pydantic models in `backend/main.py`
2. Create endpoint handler with proper error handling
3. Add to API documentation (docstring)
4. Write tests in `test_main.py`
5. Update frontend to call the new endpoint

#### Adding a New Frontend Component

1. Create component in `frontend/components/`
2. Create corresponding CSS module in `frontend/styles/`
3. Import and use in `pages/index.js` or other pages
4. Write tests in `frontend/__tests__/`

#### Modifying Video Generation

1. Check `backend/video_service.py`
2. Update API integration methods
3. Test with mock mode first
4. Update environment variable documentation
5. Test with real API keys

### Critical Files to Preserve

- `frontend/pages/index.js` - Main app logic
- `backend/main.py` - API definitions
- `backend/video_service.py` - Video generation
- All test files - Maintain test coverage

### Known Issues & Cleanup Needed

1. **Hardcoded Windows paths** in `backend/main.py` and `backend/video_service.py`
   - Lines with `r"c:\Users\surya\OneDrive\Desktop\work\projects\personal_proj\Advertising\.cursor\debug.log"`
   - Should be made configurable or removed

2. **Debug logging regions** throughout frontend and backend
   - `#region agent log` blocks can be cleaned up for production

3. **Port inconsistency:** Documentation mentions ports 8001 and 8002
   - Standard: Use 8002 for backend
   - Update `START_SERVERS.md` if needed

4. **CORS wildcard:** Backend allows all origins (`"*"`)
   - Should be restricted in production

5. **Error handling:** Some endpoints could use more specific error messages

### Testing Requirements

- **Backend:** Minimum 13 tests passing
- **Frontend:** Minimum 44 tests passing
- Always run tests before committing: `npm run test:all`

### Performance Considerations

- Frontend timeouts set to 10 seconds
- Video generation may take longer with real APIs
- Consider adding progress indicators for long operations
- Static file serving for generated videos

### Security Notes

- Environment variables stored in `.env` (gitignored)
- API keys should never be committed
- CORS configured for development (needs production review)
- No authentication system currently implemented

## Environment Variables

Create `backend/.env`:

```bash
# Video Generation APIs
RUNWAY_API_KEY=your_runway_key_here
STABILITY_API_KEY=your_stability_key_here

# Text-to-Speech (Optional)
ELEVENLABS_API_KEY=your_elevenlabs_key_here

# Configuration
USE_MOCK_VIDEO=true  # Set to false to use real APIs
```

## Resources & Documentation

- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **Next.js Docs:** https://nextjs.org/docs
- **Runway ML API:** https://runwayml.com
- **Stability AI:** https://platform.stability.ai/
- **ElevenLabs:** https://elevenlabs.io

## Quick Reference Commands

```bash
# Installation
npm run install:all                    # Install all dependencies

# Development
npm run dev:frontend                   # Start frontend dev server
npm run dev:backend                    # Start backend dev server

# Testing
npm run test:frontend                  # Run frontend tests
npm run test:backend                   # Run backend tests
npm run test:all                       # Run all tests

# From backend directory
cd backend
pytest test_main.py -v                 # Run backend tests
python verify_setup.py                 # Verify environment setup
python quick_test.py                   # Quick health check
uvicorn main:app --reload --port 8002  # Start backend

# From frontend directory
cd frontend
npm run dev                            # Start frontend (port 3000)
npm test                               # Run frontend tests
npm run build                          # Build for production
```

## Development Checklist

When working on this codebase:

- [ ] Read relevant files before modifying
- [ ] Follow existing code patterns
- [ ] Update tests for any functionality changes
- [ ] Test both frontend and backend
- [ ] Check for hardcoded paths or values
- [ ] Verify API endpoint compatibility
- [ ] Update documentation if needed
- [ ] Run full test suite before committing
- [ ] Use descriptive commit messages
- [ ] Push to correct branch (starts with `claude/`)

## Project Status

**Current State:** MVP Complete
- ✅ Frontend UI with 4-step workflow
- ✅ Backend API with mock video generation
- ✅ Script generation from creative brief
- ✅ Storyboard editing
- ✅ Video preview and export UI
- ✅ All tests passing (13 backend, 44 frontend)

**Next Steps:**
- Integrate real video generation APIs (Runway ML recommended)
- Implement TTS for voiceovers
- Add FFmpeg video assembly
- Implement user authentication
- Add project saving/loading
- Cloud deployment with GPU support

---

**Last Updated:** 2026-01-03
**Maintained for:** Claude Code and other AI assistants
**Questions?** Refer to README.md, SETUP_INSTRUCTIONS.md, or API_RECOMMENDATIONS.md
