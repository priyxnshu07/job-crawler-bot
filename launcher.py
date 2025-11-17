#!/usr/bin/env python3
"""
Job Crawler Bot - GUI Launcher
A simple graphical interface to start/stop the application without terminal commands.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import os
import sys
import threading
import time
import webbrowser
import signal
from pathlib import Path

# Colors
BG_COLOR = "#1e1e1e"
FG_COLOR = "#ffffff"
BUTTON_COLOR = "#007acc"
SUCCESS_COLOR = "#4caf50"
ERROR_COLOR = "#f44336"
WARNING_COLOR = "#ff9800"

class JobCrawlerLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Job Crawler Bot - Launcher")
        self.root.geometry("800x600")
        self.root.configure(bg=BG_COLOR)
        
        # Process tracking
        self.processes = {
            'flask': None,
            'worker': None,
            'beat': None,
            'redis': None
        }
        
        # State
        self.is_running = False
        self.redis_required = True
        
        self.setup_ui()
        self.check_dependencies()
        
    def setup_ui(self):
        """Create the user interface."""
        # Header
        header = tk.Frame(self.root, bg=BG_COLOR, pady=20)
        header.pack(fill=tk.X)
        
        title = tk.Label(
            header, 
            text="🚀 Job Crawler Bot", 
            font=("Arial", 24, "bold"),
            bg=BG_COLOR,
            fg=FG_COLOR
        )
        title.pack()
        
        subtitle = tk.Label(
            header,
            text="Automated Job Search with Email Alerts",
            font=("Arial", 12),
            bg=BG_COLOR,
            fg="#aaaaaa"
        )
        subtitle.pack()
        
        # Status Frame
        status_frame = tk.Frame(self.root, bg=BG_COLOR, pady=10)
        status_frame.pack(fill=tk.X, padx=20)
        
        self.status_label = tk.Label(
            status_frame,
            text="● Status: Stopped",
            font=("Arial", 12, "bold"),
            bg=BG_COLOR,
            fg=ERROR_COLOR
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Control Buttons
        button_frame = tk.Frame(self.root, bg=BG_COLOR, pady=10)
        button_frame.pack(fill=tk.X, padx=20)
        
        self.start_btn = tk.Button(
            button_frame,
            text="▶ Start Application",
            font=("Arial", 14, "bold"),
            bg=SUCCESS_COLOR,
            fg="white",
            command=self.start_app,
            padx=20,
            pady=10,
            cursor="hand2"
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(
            button_frame,
            text="■ Stop Application",
            font=("Arial", 14, "bold"),
            bg=ERROR_COLOR,
            fg="white",
            command=self.stop_app,
            padx=20,
            pady=10,
            state=tk.DISABLED,
            cursor="hand2"
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.open_btn = tk.Button(
            button_frame,
            text="🌐 Open in Browser",
            font=("Arial", 12),
            bg=BUTTON_COLOR,
            fg="white",
            command=self.open_browser,
            padx=15,
            pady=10,
            state=tk.DISABLED,
            cursor="hand2"
        )
        self.open_btn.pack(side=tk.LEFT, padx=5)
        
        # Logs Area
        log_frame = tk.Frame(self.root, bg=BG_COLOR, pady=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        log_label = tk.Label(
            log_frame,
            text="Application Logs:",
            font=("Arial", 10, "bold"),
            bg=BG_COLOR,
            fg=FG_COLOR
        )
        log_label.pack(anchor=tk.W)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=15,
            bg="#2d2d2d",
            fg="#ffffff",
            font=("Consolas", 9),
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Footer
        footer = tk.Frame(self.root, bg=BG_COLOR, pady=10)
        footer.pack(fill=tk.X)
        
        help_text = tk.Label(
            footer,
            text="💡 Tip: Make sure PostgreSQL and Redis are running before starting",
            font=("Arial", 9),
            bg=BG_COLOR,
            fg="#aaaaaa"
        )
        help_text.pack()
        
    def log(self, message, level="INFO"):
        """Add a message to the log area."""
        timestamp = time.strftime("%H:%M:%S")
        colors = {
            "INFO": "#ffffff",
            "SUCCESS": SUCCESS_COLOR,
            "ERROR": ERROR_COLOR,
            "WARNING": WARNING_COLOR
        }
        color = colors.get(level, "#ffffff")
        
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.tag_add(f"tag_{len(self.log_text.get('1.0', tk.END))}", f"end-{len(message)+10}c", "end-1c")
        self.log_text.tag_config(f"tag_{len(self.log_text.get('1.0', tk.END))}", foreground=color)
        self.log_text.see(tk.END)
        
    def check_dependencies(self):
        """Check if required dependencies are installed."""
        self.log("Checking dependencies...", "INFO")
        
        # Check Python
        if sys.version_info < (3, 9):
            self.log("ERROR: Python 3.9+ required", "ERROR")
            messagebox.showerror("Error", "Python 3.9 or higher is required!")
            return False
        
        # Check virtual environment
        venv_path = Path("venv")
        if not venv_path.exists():
            self.log("Virtual environment not found. Please run setup first.", "WARNING")
            response = messagebox.askyesno(
                "Setup Required",
                "Virtual environment not found.\n\nWould you like to run setup now?"
            )
            if response:
                self.run_setup()
            return False
        
        # Check requirements
        req_file = Path("requirements.txt")
        if not req_file.exists():
            self.log("requirements.txt not found", "ERROR")
            return False
        
        self.log("✓ Dependencies check complete", "SUCCESS")
        return True
        
    def run_setup(self):
        """Run the setup script."""
        self.log("Running setup script...", "INFO")
        try:
            subprocess.run(["./setup.sh"], check=True)
            self.log("✓ Setup completed successfully", "SUCCESS")
        except Exception as e:
            self.log(f"✗ Setup failed: {e}", "ERROR")
            messagebox.showerror("Setup Failed", f"Setup failed: {e}\n\nPlease run './setup.sh' manually.")
    
    def start_app(self):
        """Start all application services."""
        if self.is_running:
            messagebox.showwarning("Already Running", "Application is already running!")
            return
        
        self.log("Starting Job Crawler Bot...", "INFO")
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_label.config(text="● Status: Starting...", fg=WARNING_COLOR)
        
        # Start in background thread
        thread = threading.Thread(target=self._start_services, daemon=True)
        thread.start()
        
    def _start_services(self):
        """Start services in background."""
        try:
            # Activate venv and start services
            venv_python = Path("venv/bin/python")
            if not venv_python.exists():
                venv_python = Path("venv/Scripts/python.exe")  # Windows
            
            # Load .env if exists
            env = os.environ.copy()
            env_file = Path(".env")
            if env_file.exists():
                self.log("Loading .env file...", "INFO")
                with open(env_file) as f:
                    for line in f:
                        if '=' in line and not line.strip().startswith('#'):
                            key, value = line.strip().split('=', 1)
                            env[key] = value
            
            # Start Redis check
            self.log("Checking Redis...", "INFO")
            try:
                import redis
                r = redis.Redis(host='localhost', port=6379, db=0)
                r.ping()
                self.log("✓ Redis is running", "SUCCESS")
            except:
                self.log("⚠ Redis not running. Starting Redis...", "WARNING")
                # Try to start Redis
                try:
                    subprocess.Popen(["redis-server"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    time.sleep(2)
                    self.log("✓ Redis started", "SUCCESS")
                except:
                    self.log("✗ Could not start Redis. Please start it manually.", "ERROR")
            
            # Start Flask
            self.log("Starting Flask app...", "INFO")
            flask_log = open("flask.log", "w")
            self.processes['flask'] = subprocess.Popen(
                [str(venv_python), "app.py"],
                env=env,
                stdout=flask_log,
                stderr=flask_log
            )
            time.sleep(3)
            self.log("✓ Flask app started", "SUCCESS")
            
            # Start Celery Worker
            self.log("Starting Celery worker...", "INFO")
            worker_log = open("celery-worker.log", "w")
            self.processes['worker'] = subprocess.Popen(
                [str(venv_python), "-m", "celery", "-A", "tasks", "worker", "--loglevel", "INFO"],
                env=env,
                stdout=worker_log,
                stderr=worker_log
            )
            time.sleep(2)
            self.log("✓ Celery worker started", "SUCCESS")
            
            # Start Celery Beat
            self.log("Starting Celery scheduler...", "INFO")
            beat_log = open("celery-beat.log", "w")
            self.processes['beat'] = subprocess.Popen(
                [str(venv_python), "-m", "celery", "-A", "tasks", "beat", "--loglevel", "INFO"],
                env=env,
                stdout=beat_log,
                stderr=beat_log
            )
            time.sleep(2)
            self.log("✓ Celery scheduler started", "SUCCESS")
            
            # Update UI
            self.root.after(0, self._on_started)
            
        except Exception as e:
            self.log(f"✗ Failed to start: {e}", "ERROR")
            self.root.after(0, lambda: self._on_start_failed(str(e)))
    
    def _on_started(self):
        """Called when services are started."""
        self.status_label.config(text="● Status: Running", fg=SUCCESS_COLOR)
        self.open_btn.config(state=tk.NORMAL)
        self.log("✅ All services started successfully!", "SUCCESS")
        self.log("🌐 Application is available at: http://127.0.0.1:5001", "SUCCESS")
        messagebox.showinfo("Success", "Application started successfully!\n\nOpening browser...")
        self.open_browser()
    
    def _on_start_failed(self, error):
        """Called when start failed."""
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="● Status: Failed", fg=ERROR_COLOR)
        messagebox.showerror("Start Failed", f"Failed to start application:\n\n{error}")
    
    def stop_app(self):
        """Stop all application services."""
        if not self.is_running:
            return
        
        self.log("Stopping application...", "INFO")
        self.status_label.config(text="● Status: Stopping...", fg=WARNING_COLOR)
        
        # Stop all processes
        for name, process in self.processes.items():
            if process:
                try:
                    self.log(f"Stopping {name}...", "INFO")
                    process.terminate()
                    process.wait(timeout=5)
                    self.log(f"✓ {name} stopped", "SUCCESS")
                except:
                    try:
                        process.kill()
                    except:
                        pass
                self.processes[name] = None
        
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.open_btn.config(state=tk.DISABLED)
        self.status_label.config(text="● Status: Stopped", fg=ERROR_COLOR)
        self.log("✅ Application stopped", "SUCCESS")
    
    def open_browser(self):
        """Open the application in default browser."""
        url = "http://127.0.0.1:5001"
        try:
            webbrowser.open(url)
            self.log(f"Opened {url} in browser", "INFO")
        except Exception as e:
            self.log(f"Failed to open browser: {e}", "ERROR")
            messagebox.showwarning("Browser", f"Could not open browser automatically.\n\nPlease visit: {url}")
    
    def on_closing(self):
        """Handle window closing."""
        if self.is_running:
            if messagebox.askokcancel("Quit", "Application is running. Stop it and quit?"):
                self.stop_app()
                self.root.destroy()
        else:
            self.root.destroy()


def main():
    """Main entry point."""
    root = tk.Tk()
    app = JobCrawlerLauncher(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()


