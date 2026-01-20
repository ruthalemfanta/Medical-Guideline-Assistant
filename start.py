#!/usr/bin/env python3
"""
Start script for the Medical Guideline Assistant
Starts both backend and frontend servers
"""

import subprocess
import sys
import time
import signal
import os
from pathlib import Path

def start_backend():
    """Start the backend server"""
    print("🐍 Starting backend server...")
    
    # Determine the correct Python executable
    if Path('medical-assistant-env').exists():
        if sys.platform == "win32":
            python_cmd = 'medical-assistant-env\\Scripts\\python'
        else:
            python_cmd = 'medical-assistant-env/bin/python'
    else:
        python_cmd = 'python'
    
    try:
        backend_process = subprocess.Popen(
            [python_cmd, 'main.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(f"✓ Backend started with PID {backend_process.pid}")
        return backend_process
    except Exception as e:
        print(f"✗ Failed to start backend: {e}")
        return None

def start_frontend():
    """Start the frontend server"""
    print("⚛️  Starting frontend server...")
    
    frontend_dir = Path('guideline-helper')
    if not frontend_dir.exists():
        print("✗ Frontend directory not found")
        return None
    
    try:
        frontend_process = subprocess.Popen(
            ['npm', 'run', 'dev'],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(f"✓ Frontend started with PID {frontend_process.pid}")
        return frontend_process
    except Exception as e:
        print(f"✗ Failed to start frontend: {e}")
        return None

def wait_for_servers():
    """Wait for servers to be ready"""
    import requests
    
    print("⏳ Waiting for servers to be ready...")
    
    # Wait for backend
    backend_ready = False
    for i in range(30):  # Wait up to 30 seconds
        try:
            response = requests.get('http://localhost:8000/health', timeout=1)
            if response.status_code == 200:
                backend_ready = True
                print("✓ Backend is ready")
                break
        except:
            pass
        time.sleep(1)
    
    if not backend_ready:
        print("⚠ Backend may not be ready yet")
    
    # Wait for frontend
    frontend_ready = False
    for i in range(30):  # Wait up to 30 seconds
        try:
            response = requests.get('http://localhost:5173', timeout=1)
            if response.status_code == 200:
                frontend_ready = True
                print("✓ Frontend is ready")
                break
        except:
            pass
        time.sleep(1)
    
    if not frontend_ready:
        print("⚠ Frontend may not be ready yet")
    
    return backend_ready and frontend_ready

def main():
    """Main function"""
    print("🏥 Medical Guideline Assistant Startup")
    print("=" * 50)
    
    # Check prerequisites
    if not Path('.env').exists():
        print("✗ .env file not found. Please copy from .env.example and add your OpenAI API key")
        return False
    
    if not Path('guideline-helper/node_modules').exists():
        print("✗ Frontend dependencies not installed. Please run: cd guideline-helper && npm install")
        return False
    
    # Start servers
    backend_process = start_backend()
    if not backend_process:
        return False
    
    # Give backend a moment to start
    time.sleep(2)
    
    frontend_process = start_frontend()
    if not frontend_process:
        backend_process.terminate()
        return False
    
    # Wait for servers to be ready
    servers_ready = wait_for_servers()
    
    if servers_ready:
        print("\n🎉 Both servers are running!")
        print("📱 Frontend: http://localhost:5173")
        print("🔧 Backend API: http://localhost:8000")
        print("📚 API Docs: http://localhost:8000/docs")
        print("\nPress Ctrl+C to stop both servers")
    else:
        print("\n⚠ Servers started but may not be fully ready")
        print("📱 Frontend: http://localhost:5173")
        print("🔧 Backend API: http://localhost:8000")
        print("\nPress Ctrl+C to stop both servers")
    
    # Handle shutdown
    def signal_handler(sig, frame):
        print("\n🛑 Shutting down servers...")
        frontend_process.terminate()
        backend_process.terminate()
        
        # Wait for processes to terminate
        try:
            frontend_process.wait(timeout=5)
            backend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            frontend_process.kill()
            backend_process.kill()
        
        print("✓ Servers stopped")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if backend_process.poll() is not None:
                print("⚠ Backend process stopped unexpectedly")
                break
            
            if frontend_process.poll() is not None:
                print("⚠ Frontend process stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        signal_handler(None, None)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)