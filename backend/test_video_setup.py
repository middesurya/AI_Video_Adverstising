"""
Test script to verify video generation setup
Run this to check if everything is configured correctly
"""
import os
from dotenv import load_dotenv

load_dotenv()

def test_setup():
    """Test video generation setup"""
    print("=== Video Generation Setup Test ===\n")
    
    # Check environment variables
    print("1. Checking environment variables...")
    stability_key = os.getenv("STABILITY_API_KEY")
    runway_key = os.getenv("RUNWAY_API_KEY")
    elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
    use_mock = os.getenv("USE_MOCK_VIDEO", "true").lower()
    
    if stability_key:
        print("   ✅ STABILITY_API_KEY found")
    else:
        print("   ⚠️  STABILITY_API_KEY not set")
    
    if runway_key:
        print("   ✅ RUNWAY_API_KEY found")
    else:
        print("   ⚠️  RUNWAY_API_KEY not set")
    
    if elevenlabs_key:
        print("   ✅ ELEVENLABS_API_KEY found")
    else:
        print("   ⚠️  ELEVENLABS_API_KEY not set (optional)")
    
    print(f"   USE_MOCK_VIDEO: {use_mock}")
    
    # Check videos directory
    print("\n2. Checking videos directory...")
    videos_dir = os.path.join(os.path.dirname(__file__), "videos")
    if os.path.exists(videos_dir):
        print(f"   ✅ Videos directory exists: {videos_dir}")
    else:
        print(f"   ❌ Videos directory missing: {videos_dir}")
        os.makedirs(videos_dir, exist_ok=True)
        print(f"   ✅ Created videos directory")
    
    # Check dependencies
    print("\n3. Checking Python dependencies...")
    try:
        import requests
        print("   ✅ requests installed")
    except ImportError:
        print("   ❌ requests not installed (pip install requests)")
    
    try:
        from dotenv import load_dotenv
        print("   ✅ python-dotenv installed")
    except ImportError:
        print("   ❌ python-dotenv not installed (pip install python-dotenv)")
    
    try:
        import ffmpeg
        print("   ✅ ffmpeg-python installed")
    except ImportError:
        print("   ⚠️  ffmpeg-python not installed (optional, for video assembly)")
    
    # Check FFmpeg binary
    print("\n4. Checking FFmpeg binary...")
    import subprocess
    try:
        result = subprocess.run(["ffmpeg", "-version"], 
                              capture_output=True, 
                              timeout=5)
        if result.returncode == 0:
            print("   ✅ FFmpeg binary found")
        else:
            print("   ⚠️  FFmpeg found but returned error")
    except FileNotFoundError:
        print("   ⚠️  FFmpeg binary not found in PATH")
        print("      Install from: https://ffmpeg.org/download.html")
    except Exception as e:
        print(f"   ⚠️  Error checking FFmpeg: {e}")
    
    # Test video service import
    print("\n5. Testing video service...")
    try:
        from video_service import VideoGenerationService
        service = VideoGenerationService()
        print("   ✅ VideoGenerationService imported successfully")
        print(f"   Mock mode: {service.use_mock}")
    except ImportError as e:
        print(f"   ❌ Failed to import VideoGenerationService: {e}")
    except Exception as e:
        print(f"   ⚠️  Error initializing service: {e}")
    
    # Summary
    print("\n=== Summary ===")
    if stability_key or runway_key:
        print("✅ API key configured - ready for real video generation")
    elif use_mock == "true":
        print("✅ Mock mode enabled - will use placeholder videos")
    else:
        print("⚠️  No API keys found and mock mode disabled")
        print("   Set USE_MOCK_VIDEO=true or add an API key")
    
    print("\nNext steps:")
    print("1. If using real APIs, test with a simple video generation")
    print("2. Check backend/videos/ directory for generated files")
    print("3. Verify videos are accessible at http://localhost:8002/videos/")

if __name__ == "__main__":
    test_setup()

