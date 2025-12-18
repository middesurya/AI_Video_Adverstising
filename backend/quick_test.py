"""Quick test to verify backend works"""
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

print("Testing backend endpoints...")
print("-" * 50)

# Test health
r = client.get("/health")
print(f"Health check: {r.status_code} - {r.json()}")

# Test script generation
test_data = {
    "productName": "TestProduct",
    "description": "A test product"
}
r = client.post("/api/generate-script", json=test_data)
print(f"\nScript generation: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"Success: {data['success']}")
    print(f"Scenes: {len(data['scenes'])}")
    print("Backend is working correctly!")
else:
    print(f"Error: {r.text}")

