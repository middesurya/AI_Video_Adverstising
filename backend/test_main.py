"""
QA Tests for AI Ad Video Generator Backend
Run with: pytest test_main.py -v
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test health and root endpoints"""
    
    def test_root_endpoint(self):
        """Test the root endpoint returns healthy status"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "AI Ad Video Generator API" in data["message"]
    
    def test_health_endpoint(self):
        """Test the detailed health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "services" in data
        assert data["services"]["script_generation"] == "ready"
        assert data["services"]["video_generation"] == "ready"
        assert data["services"]["tts"] == "ready"


class TestScriptGeneration:
    """Test script generation endpoints"""
    
    def test_generate_script_success(self):
        """Test successful script generation with valid input"""
        payload = {
            "productName": "FitTrack Pro",
            "description": "A smart fitness tracker that monitors your health 24/7",
            "mood": 70,
            "energy": 80,
            "style": "energetic",
            "archetype": "hero-journey",
            "targetAudience": "Health-conscious millennials",
            "callToAction": "Start your fitness journey today!"
        }
        
        response = client.post("/api/generate-script", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["script"] is not None
        assert "FitTrack Pro" in data["script"]
        assert len(data["scenes"]) > 0
    
    def test_generate_script_minimal_input(self):
        """Test script generation with minimal required fields"""
        payload = {
            "productName": "TestProduct",
            "description": "A test product description"
        }
        
        response = client.post("/api/generate-script", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["script"] is not None
        assert len(data["scenes"]) == 6  # Should have 6 scenes
    
    def test_generate_script_missing_product_name(self):
        """Test script generation fails without product name"""
        payload = {
            "productName": "",
            "description": "A test description"
        }

        response = client.post("/api/generate-script", json=payload)
        # Pydantic returns 422 for validation errors
        assert response.status_code in [400, 422]

    def test_generate_script_missing_description(self):
        """Test script generation fails without description"""
        payload = {
            "productName": "TestProduct",
            "description": ""
        }

        response = client.post("/api/generate-script", json=payload)
        # Pydantic returns 422 for validation errors
        assert response.status_code in [400, 422]
    
    def test_generate_script_all_archetypes(self):
        """Test script generation works with all archetypes"""
        archetypes = ["hero-journey", "testimonial", "problem-solution", "tutorial", "comedy", "lifestyle"]
        
        for archetype in archetypes:
            payload = {
                "productName": "TestProduct",
                "description": "Test description",
                "archetype": archetype
            }
            
            response = client.post("/api/generate-script", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert data["success"] == True, f"Failed for archetype: {archetype}"
    
    def test_script_scene_structure(self):
        """Test that generated scenes have proper structure"""
        payload = {
            "productName": "TestProduct",
            "description": "Test description"
        }
        
        response = client.post("/api/generate-script", json=payload)
        data = response.json()
        
        for scene in data["scenes"]:
            assert "description" in scene
            assert "duration" in scene
            assert "narration" in scene
            assert "visualEmoji" in scene
            assert "tags" in scene
            assert scene["duration"] > 0


class TestVideoGeneration:
    """Test video generation endpoints"""
    
    def test_generate_video_success(self):
        """Test successful video generation"""
        payload = {
            "scenes": [
                {
                    "description": "Opening hook",
                    "duration": 10,
                    "narration": "Introducing our product",
                    "visualEmoji": "✨",
                    "tags": ["hook", "intro"]
                },
                {
                    "description": "Call to action",
                    "duration": 10,
                    "narration": "Get it now!",
                    "visualEmoji": "🎯",
                    "tags": ["cta"]
                }
            ],
            "adBrief": {
                "productName": "TestProduct",
                "description": "Test description",
                "mood": 50,
                "energy": 50,
                "style": "cinematic",
                "archetype": "hero-journey"
            }
        }
        
        response = client.post("/api/generate-video", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["videoUrl"] is not None
        assert "testproduct" in data["videoUrl"].lower()
        assert data["hookScore"] is not None
        assert 0 <= data["hookScore"] <= 100
    
    def test_generate_video_empty_scenes(self):
        """Test video generation fails with empty scenes"""
        payload = {
            "scenes": [],
            "adBrief": {
                "productName": "TestProduct",
                "description": "Test description"
            }
        }
        
        response = client.post("/api/generate-video", json=payload)
        assert response.status_code == 400


class TestMetadataEndpoints:
    """Test metadata endpoints for archetypes and styles"""
    
    def test_get_archetypes(self):
        """Test getting available archetypes"""
        response = client.get("/api/archetypes")
        assert response.status_code == 200
        
        data = response.json()
        assert "archetypes" in data
        assert len(data["archetypes"]) > 0
        
        # Check structure of each archetype
        for archetype in data["archetypes"]:
            assert "id" in archetype
            assert "name" in archetype
            assert "description" in archetype
    
    def test_get_styles(self):
        """Test getting available styles"""
        response = client.get("/api/styles")
        assert response.status_code == 200
        
        data = response.json()
        assert "styles" in data
        assert len(data["styles"]) > 0
        
        # Check structure of each style
        for style in data["styles"]:
            assert "id" in style
            assert "name" in style
            assert "description" in style


class TestIntegration:
    """Integration tests for complete workflow"""
    
    def test_full_workflow(self):
        """Test complete workflow from script to video generation"""
        # Step 1: Generate script
        script_payload = {
            "productName": "SuperApp",
            "description": "The all-in-one productivity app",
            "mood": 60,
            "energy": 70,
            "style": "professional",
            "archetype": "tutorial",
            "targetAudience": "Business professionals",
            "callToAction": "Download SuperApp free!"
        }
        
        script_response = client.post("/api/generate-script", json=script_payload)
        assert script_response.status_code == 200
        script_data = script_response.json()
        assert script_data["success"] == True
        
        # Step 2: Generate video with the scenes
        video_payload = {
            "scenes": script_data["scenes"],
            "adBrief": script_payload
        }
        
        video_response = client.post("/api/generate-video", json=video_payload)
        assert video_response.status_code == 200
        video_data = video_response.json()
        assert video_data["success"] == True
        assert video_data["videoUrl"] is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

