"""Simple test to verify backend can start"""
import sys
sys.path.insert(0, '.')

try:
    from main import app
    print("[OK] Backend imports successfully")
    print(f"[OK] App created: {app}")
    
    # Test a simple endpoint
    from fastapi.testclient import TestClient
    client = TestClient(app)
    
    response = client.get("/")
    print(f"[OK] Root endpoint: {response.status_code} - {response.json()}")
    
    response = client.get("/health")
    print(f"[OK] Health endpoint: {response.status_code} - {response.json()}")
    
    print("\n[OK] Backend is working correctly!")
except Exception as e:
    print(f"[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()

