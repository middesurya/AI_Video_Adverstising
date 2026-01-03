"""
Configuration and environment variable validation
"""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration with validation"""

    def __init__(self):
        # Video Generation APIs
        self.stability_api_key: Optional[str] = os.getenv("STABILITY_API_KEY")
        self.runway_api_key: Optional[str] = os.getenv("RUNWAY_API_KEY")
        self.elevenlabs_api_key: Optional[str] = os.getenv("ELEVENLABS_API_KEY")

        # Configuration
        self.use_mock_video: bool = os.getenv("USE_MOCK_VIDEO", "true").lower() == "true"
        self.environment: str = os.getenv("ENV", "development")
        self.allowed_origins: list = os.getenv(
            "ALLOWED_ORIGINS",
            "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000"
        ).split(",")

        # Server configuration
        self.host: str = os.getenv("HOST", "127.0.0.1")
        self.port: int = int(os.getenv("PORT", "8002"))
        self.debug: bool = os.getenv("DEBUG", "true").lower() == "true"

    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate configuration

        Returns:
            tuple: (is_valid, list of warnings/errors)
        """
        warnings = []

        # Check video API configuration
        if not self.use_mock_video:
            if not self.stability_api_key and not self.runway_api_key:
                warnings.append(
                    "⚠️  No video API configured. Set RUNWAY_API_KEY or STABILITY_API_KEY, "
                    "or set USE_MOCK_VIDEO=true for development"
                )

        # Log API key status
        if self.runway_api_key:
            warnings.append("✓ Runway ML API key configured")
        if self.stability_api_key:
            warnings.append("✓ Stability AI API key configured")
        if self.elevenlabs_api_key:
            warnings.append("✓ ElevenLabs API key configured")

        # Mock mode notification
        if self.use_mock_video:
            warnings.append("ℹ️  Running in MOCK mode - no real videos will be generated")

        # Production warnings
        if self.environment == "production":
            if self.debug:
                warnings.append("⚠️  DEBUG mode enabled in production - should be disabled")
            if "*" in self.allowed_origins:
                warnings.append("⚠️  CORS allows all origins (*) - should restrict in production")

        return True, warnings

    def print_config(self):
        """Print configuration summary"""
        print("\n" + "="*60)
        print("🚀 AI Ad Video Generator - Configuration")
        print("="*60)
        print(f"Environment: {self.environment}")
        print(f"Server: {self.host}:{self.port}")
        print(f"Debug Mode: {self.debug}")
        print(f"Mock Video: {self.use_mock_video}")
        print(f"CORS Origins: {len(self.allowed_origins)} configured")

        is_valid, messages = self.validate()
        print("\nConfiguration Status:")
        for msg in messages:
            print(f"  {msg}")
        print("="*60 + "\n")

        return is_valid


# Global config instance
config = Config()
