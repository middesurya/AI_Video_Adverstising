# AI-Powered Ad Video Generator

A web application that guides users through refining a creative brief and automatically generates one-minute AI video ads.

## Features

- **Prompt Refinement UI**: Mood sliders, tone selectors, style pickers, and story archetype selection
- **Conversational Agent**: AI-powered chat to clarify ad requirements
- **Storyboard Generation**: Visual scene breakdown with editing capabilities
- **Video Generation**: Mock video generation pipeline (ready for real AI model integration)
- **Engagement Metrics**: Hook score and retention predictions
- **Multi-format Export**: Support for TikTok, Reels, Shorts, and standard YouTube formats

## Tech Stack

### Frontend
- React/Next.js
- CSS Modules with custom dark theme
- Responsive design

### Backend
- Python FastAPI
- Pydantic for data validation
- RESTful API design

## Project Structure

```
├── frontend/
│   ├── pages/          # Next.js pages
│   ├── components/     # React components
│   ├── styles/         # CSS modules
│   └── __tests__/      # Frontend tests
├── backend/
│   ├── main.py         # FastAPI application
│   └── test_main.py    # Backend tests
└── package.json        # Root package.json with scripts
```

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.9+
- npm or yarn

### Installation

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

### Running the Application

1. **Start the backend (Terminal 1):**
```bash
cd backend
uvicorn main:app --reload --port 8002
```

2. **Start the frontend (Terminal 2):**
```bash
cd frontend
npm run dev
```

3. **Open your browser:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8002
   - API Docs: http://localhost:8002/docs

## Running Tests

### Backend Tests
```bash
cd backend
pytest test_main.py -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/health` | GET | Detailed health status |
| `/api/generate-script` | POST | Generate ad script from brief |
| `/api/generate-video` | POST | Generate video from scenes |
| `/api/archetypes` | GET | List available story archetypes |
| `/api/styles` | GET | List available visual styles |

## Development Timeline

- **Week 1**: Prompt & UI Foundation ✅
- **Week 2**: Conversational Agent & LLM Chat ✅
- **Week 3**: Script to Scenes ✅
- **Week 4**: Video Generation Integration (Mock) ✅
- **Week 5**: TTS and Audio Sync (Ready for integration)
- **Week 6**: Video Assembly & Branding ✅
- **Week 7**: Platform Formatting & Export ✅
- **Week 8**: Feedback & Polish ✅

## Future Enhancements

- Integration with real AI models:
  - Open-Sora / AnimateDiff for video generation
  - Bark / Coqui TTS for voiceover
  - Llama 2 for script generation
- FFmpeg integration for actual video assembly
- User authentication and project saving
- Cloud deployment with GPU support

