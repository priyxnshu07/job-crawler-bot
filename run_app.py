#!/usr/bin/env python3
"""
Simple Python launcher - Alternative to GUI for users who prefer console.
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def print_banner():
    print("=" * 60)
    print("🚀 Job Crawler Bot - Launcher")
    print("=" * 60)
    print()

def check_setup():
    """Check if setup is complete."""
    venv = Path("venv")
    if not venv.exists():
        print("❌ Virtual environment not found!")
        print("\nPlease run setup first:")
        print("   ./setup.sh")
        print("   OR")
        print("   python setup.sh")
        return False
    
    if not Path("requirements.txt").exists():
        print("❌ requirements.txt not found!")
        return False
    
    return True

def load_env():
    """Load environment variables from .env file."""
    env = os.environ.copy()
    env_file = Path(".env")
    if env_file.exists():
        print("📄 Loading .env file...")
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env[key] = value
    return env

def start_services(env):
    """Start all services."""
    venv_python = Path("venv/bin/python")
    if sys.platform == "win32":
        venv_python = Path("venv/Scripts/python.exe")
    
    if not venv_python.exists():
        print("❌ Python not found in venv!")
        return None, None, None
    
    processes = {}
    
    print("\n🚀 Starting services...\n")
    
    # Start Flask
    print("   [1/3] Starting Flask app...")
    flask_log = open("flask.log", "w")
    processes['flask'] = subprocess.Popen(
        [str(venv_python), "app.py"],
        env=env,
        stdout=flask_log,
        stderr=flask_log
    )
    time.sleep(3)
    print("      ✓ Flask started")
    
    # Start Celery Worker
    print("   [2/3] Starting Celery worker...")
    worker_log = open("celery-worker.log", "w")
    processes['worker'] = subprocess.Popen(
        [str(venv_python), "-m", "celery", "-A", "tasks", "worker", "--loglevel", "INFO"],
        env=env,
        stdout=worker_log,
        stderr=worker_log
    )
    time.sleep(2)
    print("      ✓ Celery worker started")
    
    # Start Celery Beat
    print("   [3/3] Starting Celery scheduler...")
    beat_log = open("celery-beat.log", "w")
    processes['beat'] = subprocess.Popen(
        [str(venv_python), "-m", "celery", "-A", "tasks", "beat", "--loglevel", "INFO"],
        env=env,
        stdout=beat_log,
        stderr=beat_log
    )
    time.sleep(2)
    print("      ✓ Celery scheduler started")
    
    return processes['flask'], processes['worker'], processes['beat']

def main():
    """Main function."""
    print_banner()
    
    if not check_setup():
        sys.exit(1)
    
    env = load_env()
    
    print("✅ Setup complete!")
    print("\nStarting application...")
    
    flask, worker, beat = start_services(env)
    
    if not all([flask, worker, beat]):
        print("\n❌ Failed to start services!")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ Application is running!")
    print("=" * 60)
    print("\n🌐 Open your browser and visit:")
    print("   http://127.0.0.1:5001")
    print("\n📝 Logs:")
    print("   Flask:      tail -f flask.log")
    print("   Worker:     tail -f celery-worker.log")
    print("   Scheduler:  tail -f celery-beat.log")
    print("\n⏹️  Press Ctrl+C to stop all services")
    print("=" * 60)
    
    # Open browser
    try:
        time.sleep(2)
        webbrowser.open("http://127.0.0.1:5001")
    except:
        pass
    
    # Wait for interrupt
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping services...")
        flask.terminate()
        worker.terminate()
        beat.terminate()
        flask.wait()
        worker.wait()
        beat.wait()
        print("✅ All services stopped!")
        sys.exit(0)

if __name__ == "__main__":
    main()


