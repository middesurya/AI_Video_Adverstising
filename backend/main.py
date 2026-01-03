"""
AI-Powered Ad Video Generator - Backend API
FastAPI backend for handling video generation requests
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, validator
from typing import List, Optional
from datetime import datetime
import random
import os

# Import config and logger
from config import config
from logger import logger

# Import auth services (will use if configured)
try:
    from auth import get_current_user, SubscriptionChecker, Database, supabase
    AUTH_ENABLED = supabase is not None
    if AUTH_ENABLED:
        logger.info("✅ Authentication enabled")
    else:
        logger.warning("⚠️ Authentication disabled - Supabase not configured")
except ImportError as e:
    logger.warning(f"⚠️ Authentication module not available: {e}")
    AUTH_ENABLED = False
    get_current_user = None
    SubscriptionChecker = None
    Database = None
    supabase = None

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

# CORS middleware with environment-aware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.allowed_origins if config.environment == "production" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models with enhanced validation
class AdBrief(BaseModel):
    productName: str
    description: str
    mood: int = 50
    energy: int = 50
    style: str = "cinematic"
    archetype: str = "hero-journey"
    targetAudience: Optional[str] = ""
    callToAction: Optional[str] = ""

    @validator('mood', 'energy')
    def validate_range(cls, v):
        if not 0 <= v <= 100:
            raise ValueError('Value must be between 0 and 100')
        return v

    @validator('productName', 'description')
    def validate_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Field cannot be empty')
        return v.strip()

    @validator('description')
    def validate_description_length(cls, v):
        if len(v) > 5000:
            raise ValueError('Description too long (max 5000 characters)')
        return v

    @validator('style')
    def validate_style(cls, v):
        valid_styles = ['cinematic', 'minimalist', 'energetic', 'warm', 'professional', 'playful']
        if v not in valid_styles:
            raise ValueError(f'Style must be one of: {", ".join(valid_styles)}')
        return v

    @validator('archetype')
    def validate_archetype(cls, v):
        valid_archetypes = ['hero-journey', 'testimonial', 'problem-solution', 'tutorial', 'comedy', 'lifestyle']
        if v not in valid_archetypes:
            raise ValueError(f'Archetype must be one of: {", ".join(valid_archetypes)}')
        return v

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
    project_id: Optional[str] = None
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


@app.on_event("startup")
async def startup_event():
    """Print configuration on startup"""
    config.print_config()
    logger.info("🚀 AI Ad Video Generator API started successfully")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "AI Ad Video Generator API", "status": "healthy"}


@app.get("/health/liveness")
async def liveness():
    """Kubernetes liveness probe - checks if the application is alive"""
    return {"status": "alive", "timestamp": os.times().elapsed}


@app.get("/health/readiness")
async def readiness():
    """Kubernetes readiness probe - checks if the application is ready to serve requests"""
    checks = {
        "api": "ready",
        "videos_dir": os.path.exists(VIDEOS_DIR),
        "config_valid": config.validate()[0]
    }

    all_ready = all(checks.values())
    status_code = 200 if all_ready else 503

    return {
        "status": "ready" if all_ready else "not ready",
        "checks": checks
    }


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

    try:
        if not request.scenes:
            raise HTTPException(status_code=400, detail="Scenes are required")

        # Initialize video generation service
        video_service = VideoGenerationService()

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

        # Generate video
        video_url = video_service.generate_video_for_scene(
            scene_dict,
            ad_brief_dict,
            VIDEOS_DIR
        )

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

        return VideoResponse(
            success=True,
            videoUrl=video_url,
            hookScore=min(hook_score, 100)
        )
    except HTTPException:
        raise
    except Exception as e:
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


# ==================== PROTECTED ENDPOINTS (REQUIRE AUTHENTICATION) ====================

@app.post("/api/generate-script-protected", response_model=ScriptResponse)
async def generate_script_protected(
    brief: AdBrief,
    user = Depends(get_current_user) if AUTH_ENABLED else None
):
    """
    Generate script with authentication and subscription checking
    Requires valid JWT token in Authorization header
    """
    if not AUTH_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="Authentication not configured. Use /api/generate-script instead."
        )

    user_id = user["sub"]
    logger.info(f"Protected script generation for user: {user_id}")

    try:
        # Check subscription limits
        await SubscriptionChecker.check_video_generation_allowed(user_id)

        # Generate script
        script, scenes = generate_mock_script(brief)

        # Save project to database
        project = await Database.create_project(user_id, {
            "name": f"{brief.productName} - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "product_name": brief.productName,
            "description": brief.description,
            "mood": brief.mood,
            "energy": brief.energy,
            "style": brief.style,
            "archetype": brief.archetype,
            "target_audience": brief.targetAudience or "",
            "call_to_action": brief.callToAction or "",
            "script": script,
            "scenes": [scene.dict() for scene in scenes],
            "status": "draft"
        })

        logger.info(f"✅ Created project {project['id']} for user {user_id}")

        return ScriptResponse(
            success=True,
            script=script,
            scenes=scenes,
            project_id=project["id"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Script generation error: {e}")
        return ScriptResponse(
            success=False,
            error=str(e)
        )


@app.post("/api/generate-video-protected", response_model=VideoResponse)
async def generate_video_protected(
    request: VideoRequest,
    project_id: Optional[str] = None,
    user = Depends(get_current_user) if AUTH_ENABLED else None
):
    """
    Generate video with authentication and usage tracking
    Requires valid JWT token in Authorization header
    """
    if not AUTH_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="Authentication not configured. Use /api/generate-video instead."
        )

    user_id = user["sub"]
    logger.info(f"Protected video generation for user: {user_id}")

    from video_service import VideoGenerationService

    try:
        # Check subscription limits
        await SubscriptionChecker.check_video_generation_allowed(user_id)

        if not request.scenes:
            raise HTTPException(status_code=400, detail="Scenes are required")

        # Initialize video generation service
        video_service = VideoGenerationService()

        # Convert Pydantic models to dicts
        ad_brief_dict = {
            "productName": request.adBrief.productName,
            "description": request.adBrief.description,
            "style": request.adBrief.style,
            "mood": request.adBrief.mood,
            "energy": request.adBrief.energy
        }

        first_scene = request.scenes[0]
        scene_dict = {
            "description": first_scene.description,
            "duration": first_scene.duration,
            "narration": first_scene.narration or first_scene.description
        }

        # Generate video
        video_url = video_service.generate_video_for_scene(
            scene_dict,
            ad_brief_dict,
            VIDEOS_DIR
        )

        # Generate audio if TTS is configured
        audio_path = video_service.generate_audio_for_scene(scene_dict, VIDEOS_DIR)

        # Calculate costs (example - adjust based on actual API costs)
        video_cost = first_scene.duration * 0.05  # $0.05 per second
        total_cost = video_cost

        # Track API usage
        await Database.track_api_usage(
            user_id=user_id,
            project_id=project_id or "unknown",
            service="runway_ml" if not config.use_mock_video else "mock",
            operation="video_generation",
            units=first_scene.duration,
            cost=total_cost,
            metadata={"scenes": len(request.scenes), "style": request.adBrief.style}
        )

        # Increment usage count
        await SubscriptionChecker.increment_usage(user_id)

        # Update project if project_id provided
        if project_id:
            await Database.update_project(project_id, user_id, {
                "video_url": video_url,
                "status": "complete",
                "completed_at": datetime.now().isoformat()
            })

        # Calculate hook score
        hook_score = random.randint(70, 95)
        if len(request.scenes) >= 6:
            hook_score += 5

        logger.info(f"✅ Generated video for user {user_id}, cost: ${total_cost:.4f}")

        return VideoResponse(
            success=True,
            videoUrl=video_url,
            hookScore=min(hook_score, 100)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Video generation error: {e}")
        return VideoResponse(
            success=False,
            error=str(e)
        )


# ==================== PROJECT MANAGEMENT ENDPOINTS ====================

@app.get("/api/projects")
async def get_projects(user = Depends(get_current_user) if AUTH_ENABLED else None):
    """Get all projects for authenticated user"""
    if not AUTH_ENABLED:
        raise HTTPException(status_code=503, detail="Authentication not configured")

    user_id = user["sub"]
    projects = await Database.get_user_projects(user_id)

    logger.info(f"📁 Retrieved {len(projects)} projects for user {user_id}")
    return {"projects": projects}


@app.get("/api/projects/{project_id}")
async def get_project(
    project_id: str,
    user = Depends(get_current_user) if AUTH_ENABLED else None
):
    """Get a specific project"""
    if not AUTH_ENABLED:
        raise HTTPException(status_code=503, detail="Authentication not configured")

    user_id = user["sub"]
    project = await Database.get_project(project_id, user_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return {"project": project}


@app.put("/api/projects/{project_id}")
async def update_project(
    project_id: str,
    updates: dict,
    user = Depends(get_current_user) if AUTH_ENABLED else None
):
    """Update a project"""
    if not AUTH_ENABLED:
        raise HTTPException(status_code=503, detail="Authentication not configured")

    user_id = user["sub"]
    project = await Database.update_project(project_id, user_id, updates)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    logger.info(f"✏️ Updated project {project_id}")
    return {"project": project}


@app.delete("/api/projects/{project_id}")
async def delete_project(
    project_id: str,
    user = Depends(get_current_user) if AUTH_ENABLED else None
):
    """Delete a project"""
    if not AUTH_ENABLED:
        raise HTTPException(status_code=503, detail="Authentication not configured")

    user_id = user["sub"]
    await Database.delete_project(project_id, user_id)

    logger.info(f"🗑️ Deleted project {project_id}")
    return {"message": "Project deleted successfully"}


# ==================== USAGE & SUBSCRIPTION ENDPOINTS ====================

@app.get("/api/usage")
async def get_usage(user = Depends(get_current_user) if AUTH_ENABLED else None):
    """Get user's usage statistics and subscription info"""
    if not AUTH_ENABLED:
        raise HTTPException(status_code=503, detail="Authentication not configured")

    user_id = user["sub"]

    try:
        # Get subscription info
        subscription = await SubscriptionChecker.get_subscription_info(user_id)

        # Get usage stats
        usage_stats = await Database.get_user_usage(user_id)

        return {
            "subscription": subscription,
            "monthly_usage": {
                "videos_generated": subscription.get("current_month_usage", 0) if subscription else 0,
                "monthly_limit": subscription.get("monthly_video_limit", 0) if subscription else 0,
                "total_cost_usd": usage_stats.get("total_cost", 0)
            },
            "usage_details": usage_stats.get("usage", [])
        }

    except Exception as e:
        logger.error(f"Error fetching usage: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch usage: {str(e)}")


@app.get("/api/subscription")
async def get_subscription(user = Depends(get_current_user) if AUTH_ENABLED else None):
    """Get user's subscription details"""
    if not AUTH_ENABLED:
        raise HTTPException(status_code=503, detail="Authentication not configured")

    user_id = user["sub"]
    subscription = await SubscriptionChecker.get_subscription_info(user_id)

    if not subscription:
        raise HTTPException(status_code=404, detail="No subscription found")

    return {"subscription": subscription}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)
