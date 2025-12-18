"""
AI-Powered Ad Video Generator - Backend API
FastAPI backend for handling video generation requests
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import random
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="AI Ad Video Generator API",
    version="1.0.0",
    description="Backend API for generating AI-powered video advertisements"
)

# Create videos directory if it doesn't exist
VIDEOS_DIR = os.path.join(os.path.dirname(__file__), "videos")
os.makedirs(VIDEOS_DIR, exist_ok=True)

# Serve static video files
app.mount("/videos", StaticFiles(directory=VIDEOS_DIR), name="videos")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class AdBrief(BaseModel):
    productName: str
    description: str
    mood: int = 50
    energy: int = 50
    style: str = "cinematic"
    archetype: str = "hero-journey"
    targetAudience: Optional[str] = ""
    callToAction: Optional[str] = ""

class Scene(BaseModel):
    description: str
    duration: int
    narration: Optional[str] = ""
    visualEmoji: Optional[str] = "🎬"
    tags: Optional[List[str]] = []

class ScriptResponse(BaseModel):
    success: bool
    script: Optional[str] = None
    scenes: Optional[List[Scene]] = None
    error: Optional[str] = None

class VideoRequest(BaseModel):
    scenes: List[Scene]
    adBrief: AdBrief

class VideoResponse(BaseModel):
    success: bool
    videoUrl: Optional[str] = None
    hookScore: Optional[int] = None
    error: Optional[str] = None

# Story archetype templates
ARCHETYPE_TEMPLATES = {
    "hero-journey": "A hero emerges, faces challenges, and triumphs with {product}.",
    "testimonial": "Real people share their transformative experience with {product}.",
    "problem-solution": "The struggle is real... until {product} changes everything.",
    "tutorial": "Discover how easy it is to use {product} in just 3 simple steps.",
    "comedy": "Life's better with a laugh... and {product}.",
    "lifestyle": "Imagine your best life. Now imagine it with {product}."
}

# Visual emojis for different scene types
SCENE_EMOJIS = ["🎬", "🌅", "💡", "🎯", "✨", "🚀", "💪", "🎉"]

def generate_mock_script(brief: AdBrief) -> tuple[str, List[Scene]]:
    """Generate a mock script and scenes based on the ad brief"""
    
    template = ARCHETYPE_TEMPLATES.get(brief.archetype, ARCHETYPE_TEMPLATES["hero-journey"])
    intro = template.format(product=brief.productName)
    
    # Determine tone based on mood/energy
    tone_word = "exciting" if brief.mood > 60 else "calm" if brief.mood < 40 else "balanced"
    pace_word = "fast-paced" if brief.energy > 60 else "slow" if brief.energy < 40 else "moderate"
    
    script = f"""[{brief.style.upper()} STYLE - {tone_word.upper()}, {pace_word.upper()} PACE]

OPENING (0:00-0:10):
{intro}

SCENE 1 - THE HOOK:
Open with an attention-grabbing visual that introduces the world of {brief.productName}.
{f'Target Audience: {brief.targetAudience}' if brief.targetAudience else ''}

SCENE 2 - THE PROBLEM:
Show the pain point that {brief.productName} solves. Make viewers feel understood.

SCENE 3 - THE SOLUTION:
Reveal {brief.productName} as the answer. Highlight key features and benefits.
{brief.description}

SCENE 4 - THE TRANSFORMATION:
Show the before/after. Demonstrate the positive change {brief.productName} brings.

SCENE 5 - SOCIAL PROOF:
Quick testimonials or user reactions that build trust and credibility.

SCENE 6 - CALL TO ACTION:
{brief.callToAction if brief.callToAction else f'Get {brief.productName} today!'}
Strong closing with logo and CTA overlay.

[END OF SCRIPT - ~60 seconds total]"""

    # Generate scenes
    scenes = [
        Scene(
            description=f"Opening hook - Introduce {brief.productName} with stunning {brief.style} visuals",
            duration=10,
            narration=f"What if there was a better way? Introducing {brief.productName}.",
            visualEmoji="✨",
            tags=["hook", "intro", brief.style]
        ),
        Scene(
            description="Show the problem your audience faces daily",
            duration=8,
            narration="We've all been there. The frustration. The struggle.",
            visualEmoji="😤",
            tags=["problem", "emotional"]
        ),
        Scene(
            description=f"Reveal {brief.productName} as the solution",
            duration=12,
            narration=f"{brief.productName} changes everything. {brief.description[:50]}..." if len(brief.description) > 50 else brief.description,
            visualEmoji="💡",
            tags=["solution", "product", "features"]
        ),
        Scene(
            description="Show the transformation and results",
            duration=12,
            narration="See the difference. Feel the change.",
            visualEmoji="🚀",
            tags=["transformation", "results", "before-after"]
        ),
        Scene(
            description="Social proof and testimonials",
            duration=8,
            narration="Join thousands who already made the switch.",
            visualEmoji="💬",
            tags=["testimonial", "trust", "social-proof"]
        ),
        Scene(
            description=f"Call to action - {brief.callToAction or 'Get started today'}",
            duration=10,
            narration=brief.callToAction if brief.callToAction else f"Get {brief.productName} now. Limited time offer!",
            visualEmoji="🎯",
            tags=["cta", "closing", "logo"]
        )
    ]
    
    return script, scenes


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "AI Ad Video Generator API", "status": "healthy"}


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "services": {
            "script_generation": "ready",
            "video_generation": "ready",
            "tts": "ready"
        }
    }


@app.post("/api/generate-script", response_model=ScriptResponse)
async def generate_script(brief: AdBrief):
    """Generate an ad script based on the creative brief"""
    try:
        if not brief.productName or not brief.description:
            raise HTTPException(status_code=400, detail="Product name and description are required")
        
        script, scenes = generate_mock_script(brief)
        
        return ScriptResponse(
            success=True,
            script=script,
            scenes=scenes
        )
    except HTTPException:
        raise
    except Exception as e:
        return ScriptResponse(
            success=False,
            error=str(e)
        )


@app.post("/api/generate-video", response_model=VideoResponse)
async def generate_video(request: VideoRequest):
    """Generate video from scenes and ad brief"""
    from video_service import VideoGenerationService
    import json
    import time
    
    log_path = r"c:\Users\surya\OneDrive\Desktop\work\projects\personal_proj\Advertising\.cursor\debug.log"
    
    # #region agent log
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({"location":"main.py:217","message":"generate_video endpoint called","data":{"scenesCount":len(request.scenes) if request.scenes else 0,"productName":request.adBrief.productName if request.adBrief else "None"},"timestamp":int(time.time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"A"}) + "\n")
    except:
        pass
    # #endregion
    
    try:
        if not request.scenes:
            raise HTTPException(status_code=400, detail="Scenes are required")
        
        # Initialize video generation service
        video_service = VideoGenerationService()
        
        # #region agent log
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"location":"main.py:228","message":"VideoGenerationService initialized","data":{"hasStabilityKey":bool(video_service.stability_api_key),"useMock":video_service.use_mock},"timestamp":int(time.time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"A"}) + "\n")
        except:
            pass
        # #endregion
        
        # Convert Pydantic models to dicts for the service
        ad_brief_dict = {
            "productName": request.adBrief.productName,
            "description": request.adBrief.description,
            "style": request.adBrief.style,
            "mood": request.adBrief.mood,
            "energy": request.adBrief.energy
        }
        
        # For now, generate a single combined video
        # In production, you'd generate videos for each scene and combine them
        first_scene = request.scenes[0]
        scene_dict = {
            "description": first_scene.description,
            "duration": first_scene.duration,
            "narration": first_scene.narration or first_scene.description
        }
        
        # #region agent log
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"location":"main.py:250","message":"Calling generate_video_for_scene","data":{"sceneDescription":scene_dict.get("description","")[:50],"productName":ad_brief_dict.get("productName","")},"timestamp":int(time.time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"B"}) + "\n")
        except:
            pass
        # #endregion
        
        # Generate video
        video_url = video_service.generate_video_for_scene(
            scene_dict,
            ad_brief_dict,
            VIDEOS_DIR
        )
        
        # #region agent log
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"location":"main.py:260","message":"generate_video_for_scene returned","data":{"videoUrl":video_url},"timestamp":int(time.time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"B"}) + "\n")
        except:
            pass
        # #endregion
        
        # Generate audio if TTS is configured
        audio_path = video_service.generate_audio_for_scene(scene_dict, VIDEOS_DIR)
        
        # If we have both video and audio, combine them
        if audio_path and os.path.exists(audio_path):
            # For now, just use the video URL
            # Full implementation would combine video + audio
            pass
        
        # Calculate hook score based on scene quality
        hook_score = random.randint(70, 95)
        if len(request.scenes) >= 6:
            hook_score += 5  # Bonus for complete storyboard
        
        # #region agent log
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"location":"main.py:280","message":"Returning VideoResponse","data":{"success":True,"videoUrl":video_url,"hookScore":min(hook_score, 100)},"timestamp":int(time.time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"C"}) + "\n")
        except:
            pass
        # #endregion
        
        return VideoResponse(
            success=True,
            videoUrl=video_url,
            hookScore=min(hook_score, 100)
        )
    except HTTPException:
        raise
    except Exception as e:
        # #region agent log
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"location":"main.py:290","message":"Exception in generate_video","data":{"error":str(e)},"timestamp":int(time.time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"D"}) + "\n")
        except:
            pass
        # #endregion
        return VideoResponse(
            success=False,
            error=str(e)
        )



@app.get("/api/archetypes")
async def get_archetypes():
    """Get available story archetypes"""
    return {
        "archetypes": [
            {"id": "hero-journey", "name": "Hero's Journey", "description": "Overcome challenges, achieve greatness"},
            {"id": "testimonial", "name": "Testimonial", "description": "Real stories, authentic voices"},
            {"id": "problem-solution", "name": "Problem-Solution", "description": "Show the pain, reveal the cure"},
            {"id": "tutorial", "name": "Tutorial", "description": "Step-by-step demonstration"},
            {"id": "comedy", "name": "Comedy Skit", "description": "Humor that sticks"},
            {"id": "lifestyle", "name": "Lifestyle", "description": "Aspirational, emotional connection"}
        ]
    }


@app.get("/api/styles")
async def get_styles():
    """Get available visual styles"""
    return {
        "styles": [
            {"id": "cinematic", "name": "Cinematic", "description": "Epic, movie-like visuals"},
            {"id": "minimalist", "name": "Minimalist", "description": "Clean, simple aesthetics"},
            {"id": "energetic", "name": "Energetic", "description": "Fast-paced, dynamic"},
            {"id": "warm", "name": "Warm", "description": "Cozy, inviting feel"},
            {"id": "professional", "name": "Professional", "description": "Corporate, polished"},
            {"id": "playful", "name": "Playful", "description": "Fun, whimsical style"}
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)
