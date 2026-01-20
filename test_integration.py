#!/usr/bin/env python3
"""
Integration test script for the Medical Guideline Assistant
"""

import requests
import json
import time
import sys
from pathlib import Path

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5173"

def test_backend_health():
    """Test if backend is running and healthy"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Backend health check passed: {data['status']}")
            return True
        else:
            print(f"✗ Backend health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Backend not reachable: {e}")
        return False

def test_backend_stats():
    """Test backend stats endpoint"""
    try:
        response = requests.get(f"{BACKEND_URL}/stats", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Backend stats: {data['total_documents']} documents")
            return True
        else:
            print(f"✗ Backend stats failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Backend stats error: {e}")
        return False

def test_backend_query():
    """Test backend query endpoint"""
    try:
        query_data = {"query": "What is hypertension?"}
        response = requests.post(
            f"{BACKEND_URL}/query", 
            json=query_data, 
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Backend query successful")
            print(f"  Answer length: {len(data['answer'])} characters")
            print(f"  Citations: {len(data['citations'])}")
            print(f"  Confidence: {data['confidence_score']:.2f}")
            return True
        else:
            print(f"✗ Backend query failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Backend query error: {e}")
        return False

def test_frontend_availability():
    """Test if frontend is running"""
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print("✓ Frontend is accessible")
            return True
        else:
            print(f"✗ Frontend returned status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Frontend not reachable: {e}")
        return False

def test_cors():
    """Test CORS configuration"""
    try:
        # Simulate a preflight request
        headers = {
            'Origin': FRONTEND_URL,
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        response = requests.options(f"{BACKEND_URL}/query", headers=headers, timeout=5)
        
        if response.status_code in [200, 204]:
            print("✓ CORS configuration appears correct")
            return True
        else:
            print(f"✗ CORS preflight failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ CORS test error: {e}")
        return False

def check_environment():
    """Check environment setup"""
    print("Checking environment setup...")
    
    # Check if .env exists
    if Path('.env').exists():
        print("✓ .env file found")
    else:
        print("✗ .env file not found - copy from .env.example")
        return False
    
    # Check if virtual environment exists
    if Path('medical-assistant-env').exists():
        print("✓ Virtual environment found")
    else:
        print("⚠ Virtual environment not found - run setup.py")
    
    # Check if frontend node_modules exists
    if Path('guideline-helper/node_modules').exists():
        print("✓ Frontend dependencies installed")
    else:
        print("✗ Frontend dependencies not installed - run npm install")
        return False
    
    return True

def main():
    """Main test function"""
    print("🧪 Medical Guideline Assistant Integration Test")
    print("=" * 60)
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment setup incomplete")
        return False
    
    print("\nTesting backend...")
    backend_tests = [
        test_backend_health(),
        test_backend_stats(),
        test_backend_query(),
        test_cors()
    ]
    
    print("\nTesting frontend...")
    frontend_tests = [
        test_frontend_availability()
    ]
    
    # Summary
    backend_passed = sum(backend_tests)
    frontend_passed = sum(frontend_tests)
    total_tests = len(backend_tests) + len(frontend_tests)
    total_passed = backend_passed + frontend_passed
    
    print(f"\n📊 Test Results:")
    print(f"Backend: {backend_passed}/{len(backend_tests)} tests passed")
    print(f"Frontend: {frontend_passed}/{len(frontend_tests)} tests passed")
    print(f"Total: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 All tests passed! Integration is working correctly.")
        print("\nNext steps:")
        print("1. Open http://localhost:5173 in your browser")
        print("2. Upload some medical guideline PDFs")
        print("3. Start asking questions!")
        return True
    else:
        print(f"\n❌ {total_tests - total_passed} tests failed.")
        print("\nTroubleshooting:")
        if backend_passed < len(backend_tests):
            print("- Make sure backend is running: python main.py")
            print("- Check your .env file has a valid OpenAI API key")
        if frontend_passed < len(frontend_tests):
            print("- Make sure frontend is running: cd guideline-helper && npm run dev")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)