#!/usr/bin/env python3
"""
Setup script for the Medical Guideline Assistant
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and return success status"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            text=True
        )
        if result.returncode != 0:
            print(f"Error running command: {command}")
            print(f"Error output: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"Exception running command {command}: {e}")
        return False

def check_python():
    """Check if Python 3.8+ is available"""
    try:
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            print(f"✓ Python {version.major}.{version.minor} found")
            return True
        else:
            print(f"✗ Python 3.8+ required, found {version.major}.{version.minor}")
            return False
    except:
        print("✗ Python not found")
        return False

def check_node():
    """Check if Node.js is available"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✓ Node.js {version} found")
            return True
        else:
            print("✗ Node.js not found")
            return False
    except:
        print("✗ Node.js not found")
        return False

def setup_backend():
    """Setup Python backend"""
    print("\n🐍 Setting up Python backend...")
    
    # Create virtual environment if it doesn't exist
    if not os.path.exists('medical-assistant-env'):
        print("Creating virtual environment...")
        if not run_command('python -m venv medical-assistant-env'):
            return False
    
    # Activate virtual environment and install dependencies
    if sys.platform == "win32":
        pip_cmd = 'medical-assistant-env\\Scripts\\pip'
        python_cmd = 'medical-assistant-env\\Scripts\\python'
    else:
        pip_cmd = 'medical-assistant-env/bin/pip'
        python_cmd = 'medical-assistant-env/bin/python'
    
    print("Installing Python dependencies...")
    if not run_command(f'{pip_cmd} install -r requirements.txt'):
        return False
    
    # Check if .env exists
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            print("Creating .env file from .env.example...")
            shutil.copy('.env.example', '.env')
            print("⚠️  Please edit .env file and add your OpenAI API key")
        else:
            print("⚠️  Please create .env file with your OpenAI API key")
    
    print("✓ Backend setup complete")
    return True

def setup_frontend():
    """Setup React frontend"""
    print("\n⚛️  Setting up React frontend...")
    
    frontend_dir = Path('guideline-helper')
    if not frontend_dir.exists():
        print("✗ Frontend directory not found")
        return False
    
    print("Installing Node.js dependencies...")
    if not run_command('npm install', cwd=frontend_dir):
        return False
    
    print("✓ Frontend setup complete")
    return True

def main():
    """Main setup function"""
    print("🏥 Medical Guideline Assistant Setup")
    print("=" * 50)
    
    # Check prerequisites
    print("Checking prerequisites...")
    if not check_python():
        print("Please install Python 3.8 or higher")
        return False
    
    if not check_node():
        print("Please install Node.js")
        return False
    
    # Setup backend
    if not setup_backend():
        print("✗ Backend setup failed")
        return False
    
    # Setup frontend
    if not setup_frontend():
        print("✗ Frontend setup failed")
        return False
    
    print("\n🎉 Setup complete!")
    print("\nTo start the application:")
    print("1. Start the backend:")
    if sys.platform == "win32":
        print("   medical-assistant-env\\Scripts\\python main.py")
    else:
        print("   medical-assistant-env/bin/python main.py")
    
    print("2. In another terminal, start the frontend:")
    print("   cd guideline-helper")
    print("   npm run dev")
    
    print("\n3. Open http://localhost:5173 in your browser")
    print("\nMake sure to:")
    print("- Add your OpenAI API key to the .env file")
    print("- Upload medical guideline PDFs through the web interface")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)