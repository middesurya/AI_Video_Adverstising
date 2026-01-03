"""
Error Handling and Edge Case Tests
Run with: pytest test_error_handling.py -v
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestValidationErrors:
    """Test enhanced validation"""

    def test_invalid_mood_value_too_high(self):
        """Test that mood > 100 is rejected"""
        payload = {
            "productName": "TestProduct",
            "description": "Test description",
            "mood": 150  # Invalid: should be 0-100
        }

        response = client.post("/api/generate-script", json=payload)
        assert response.status_code == 422  # Validation error

    def test_invalid_mood_value_too_low(self):
        """Test that mood < 0 is rejected"""
        payload = {
            "productName": "TestProduct",
            "description": "Test description",
            "mood": -10  # Invalid: should be 0-100
        }

        response = client.post("/api/generate-script", json=payload)
        assert response.status_code == 422

    def test_invalid_energy_value(self):
        """Test that energy outside range is rejected"""
        payload = {
            "productName": "TestProduct",
            "description": "Test description",
            "energy": 200  # Invalid: should be 0-100
        }

        response = client.post("/api/generate-script", json=payload)
        assert response.status_code == 422

    def test_invalid_style(self):
        """Test that invalid style is rejected"""
        payload = {
            "productName": "TestProduct",
            "description": "Test description",
            "style": "invalid-style"  # Not in allowed list
        }

        response = client.post("/api/generate-script", json=payload)
        assert response.status_code == 422

    def test_invalid_archetype(self):
        """Test that invalid archetype is rejected"""
        payload = {
            "productName": "TestProduct",
            "description": "Test description",
            "archetype": "invalid-archetype"  # Not in allowed list
        }

        response = client.post("/api/generate-script", json=payload)
        assert response.status_code == 422

    def test_very_long_description(self):
        """Test that description > 5000 characters is rejected"""
        payload = {
            "productName": "TestProduct",
            "description": "A" * 6000  # Too long
        }

        response = client.post("/api/generate-script", json=payload)
        assert response.status_code == 422


class TestUnicodeHandling:
    """Test Unicode and special character handling"""

    def test_unicode_product_name(self):
        """Test that Unicode characters in product name work"""
        payload = {
            "productName": "产品测试 🎉",
            "description": "Test description"
        }

        response = client.post("/api/generate-script", json=payload)
        assert response.status_code == 200

    def test_emoji_in_description(self):
        """Test that emojis in description work"""
        payload = {
            "productName": "TestProduct",
            "description": "Amazing product 🚀 with great features ✨"
        }

        response = client.post("/api/generate-script", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True

    def test_unicode_call_to_action(self):
        """Test Unicode in call to action"""
        payload = {
            "productName": "TestProduct",
            "description": "Test description",
            "callToAction": "立即购买!"
        }

        response = client.post("/api/generate-script", json=payload)
        assert response.status_code == 200


class TestEdgeCases:
    """Test edge cases"""

    def test_whitespace_only_product_name(self):
        """Test that whitespace-only product name is rejected"""
        payload = {
            "productName": "   ",  # Just whitespace
            "description": "Test description"
        }

        response = client.post("/api/generate-script", json=payload)
        assert response.status_code == 422

    def test_whitespace_only_description(self):
        """Test that whitespace-only description is rejected"""
        payload = {
            "productName": "TestProduct",
            "description": "   "  # Just whitespace
        }

        response = client.post("/api/generate-script", json=payload)
        assert response.status_code == 422

    def test_minimal_valid_description(self):
        """Test single character description (edge case but valid)"""
        payload = {
            "productName": "A",
            "description": "A"
        }

        response = client.post("/api/generate-script", json=payload)
        assert response.status_code == 200

    def test_maximum_valid_mood_and_energy(self):
        """Test maximum valid values for mood and energy"""
        payload = {
            "productName": "TestProduct",
            "description": "Test description",
            "mood": 100,
            "energy": 100
        }

        response = client.post("/api/generate-script", json=payload)
        assert response.status_code == 200

    def test_minimum_valid_mood_and_energy(self):
        """Test minimum valid values for mood and energy"""
        payload = {
            "productName": "TestProduct",
            "description": "Test description",
            "mood": 0,
            "energy": 0
        }

        response = client.post("/api/generate-script", json=payload)
        assert response.status_code == 200


class TestNewHealthEndpoints:
    """Test new health check endpoints"""

    def test_liveness_probe(self):
        """Test Kubernetes liveness probe"""
        response = client.get("/health/liveness")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"

    def test_readiness_probe(self):
        """Test Kubernetes readiness probe"""
        response = client.get("/health/readiness")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert "checks" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
