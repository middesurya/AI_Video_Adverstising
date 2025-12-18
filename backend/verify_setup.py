"""
Quick setup verification script
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("=== Setup Verification ===\n")

# Check imports
print("1. Checking Python packages...")
try:
    import requests
    print("   OK - requests")
except ImportError:
    print("   FAIL - requests not installed")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    print("   OK - python-dotenv")
except ImportError:
    print("   FAIL - python-dotenv not installed")
    sys.exit(1)

# Check video service
print("\n2. Checking video service...")
try:
    from video_service import VideoGenerationService
    service = VideoGenerationService()
    print("   OK - VideoGenerationService imported")
except Exception as e:
    print(f"   FAIL - {e}")
    sys.exit(1)

# Check API keys
print("\n3. Checking API configuration...")
stability_key = os.getenv("STABILITY_API_KEY")
runway_key = os.getenv("RUNWAY_API_KEY")

if runway_key:
    print(f"   OK - Runway ML API key found (length: {len(runway_key)})")
    print("   Will use Runway ML for video generation")
elif stability_key:
    print(f"   OK - Stability AI API key found (length: {len(stability_key)})")
    print("   WARNING: Stability AI video API may not work (404 error)")
else:
    print("   WARNING - No video API key found")
    print("   Set USE_MOCK_VIDEO=true to use mock mode")

# Check mock mode
use_mock = os.getenv("USE_MOCK_VIDEO", "true").lower() == "true"
print(f"   Mock mode: {use_mock}")

# Check videos directory
print("\n4. Checking directories...")
videos_dir = os.path.join(os.path.dirname(__file__), "videos")
if os.path.exists(videos_dir):
    print(f"   OK - Videos directory exists: {videos_dir}")
else:
    print(f"   WARNING - Videos directory missing: {videos_dir}")
    os.makedirs(videos_dir, exist_ok=True)
    print(f"   Created videos directory")

print("\n=== Setup Complete ===")
print("\nYou can now start the backend server:")
print("  uvicorn main:app --host 127.0.0.1 --port 8002 --reload")

