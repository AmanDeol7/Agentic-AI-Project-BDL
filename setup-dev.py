#!/usr/bin/env python3
"""
Agentic AI Project - Local Development Setup
============================================

This script sets up the complete development environment for the Agentic AI Project.
It handles dependency installation, Ollama setup, model downloads, and environment configuration.

Usage:
    python setup-dev.py            # Full setup
    python setup-dev.py --deps     # Install dependencies only
    python setup-dev.py --ollama   # Setup Ollama only
    python setup-dev.py --models   # Download models only
    python setup-dev.py --start    # Start the application after setup
"""

import os
import sys
import subprocess
import requests
import time
import argparse
import shutil
from pathlib import Path
from typing import List, Optional

# Project constants
PROJECT_ROOT = Path(__file__).parent
REQUIRED_PYTHON_VERSION = (3, 8)
DEFAULT_MODELS = ["llama3.2:1b", "mistral:7b"]

class Colors:
    """ANSI color codes for terminal output."""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    NC = '\033[0m'  # No Color

class Logger:
    """Simple logger with colored output."""
    
    @staticmethod
    def info(msg: str):
        print(f"{Colors.BLUE}[INFO]{Colors.NC} {msg}")
    
    @staticmethod
    def success(msg: str):
        print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {msg}")
    
    @staticmethod
    def warning(msg: str):
        print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {msg}")
    
    @staticmethod
    def error(msg: str):
        print(f"{Colors.RED}[ERROR]{Colors.NC} {msg}")
    
    @staticmethod
    def header(msg: str):
        print(f"\n{Colors.WHITE}{'='*60}{Colors.NC}")
        print(f"{Colors.WHITE}{msg:^60}{Colors.NC}")
        print(f"{Colors.WHITE}{'='*60}{Colors.NC}\n")

class DevSetup:
    """Main setup class for development environment."""
    
    def __init__(self):
        self.logger = Logger()
        
    def check_python_version(self) -> bool:
        """Check if Python version meets requirements."""
        current_version = sys.version_info[:2]
        if current_version < REQUIRED_PYTHON_VERSION:
            self.logger.error(f"Python {REQUIRED_PYTHON_VERSION[0]}.{REQUIRED_PYTHON_VERSION[1]}+ required, found {current_version[0]}.{current_version[1]}")
            return False
        
        self.logger.success(f"Python {current_version[0]}.{current_version[1]} detected")
        return True
    
    def check_command(self, command: str) -> bool:
        """Check if a command exists in PATH."""
        return shutil.which(command) is not None
    
    def run_command(self, command: List[str], check: bool = True, capture_output: bool = False) -> Optional[subprocess.CompletedProcess]:
        """Run a shell command with error handling."""
        try:
            result = subprocess.run(
                command, 
                check=check, 
                capture_output=capture_output,
                text=True
            )
            return result
        except subprocess.CalledProcessError as e:
            if check:
                self.logger.error(f"Command failed: {' '.join(command)}")
                self.logger.error(f"Error: {e}")
            return None
        except FileNotFoundError:
            self.logger.error(f"Command not found: {command[0]}")
            return None
    
    def check_service(self, url: str, timeout: int = 5) -> bool:
        """Check if a service is running at the given URL."""
        try:
            response = requests.get(url, timeout=timeout)
            return response.status_code == 200
        except:
            return False
    
    def install_dependencies(self) -> bool:
        """Install Python dependencies."""
        self.logger.info("Installing Python dependencies...")
        
        # Check for uv first (faster)
        if self.check_command("uv"):
            self.logger.info("Using uv for fast dependency installation...")
            if self.run_command(["uv", "sync"]):
                self.logger.success("Dependencies installed with uv")
                return True
        
        # Fall back to pip
        if self.check_command("pip"):
            self.logger.info("Using pip for dependency installation...")
            if self.run_command(["pip", "install", "-r", "requirements.txt"]):
                self.logger.success("Dependencies installed with pip")
                return True
        
        self.logger.error("Neither uv nor pip found. Please install pip first.")
        return False
    
    def install_ollama(self) -> bool:
        """Install Ollama if not present."""
        if self.check_command("ollama"):
            self.logger.success("Ollama already installed")
            return True
        
        self.logger.info("Installing Ollama...")
        
        # Download and run Ollama installer
        try:
            result = subprocess.run(
                ["curl", "-fsSL", "https://ollama.ai/install.sh"],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Run the installer
            process = subprocess.Popen(
                ["sh"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input=result.stdout)
            
            if process.returncode == 0 and self.check_command("ollama"):
                self.logger.success("Ollama installed successfully")
                return True
            else:
                self.logger.error("Failed to install Ollama")
                self.logger.error(stderr)
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to install Ollama: {e}")
            self.logger.info("Please install manually from https://ollama.ai")
            return False
    
    def start_ollama(self) -> bool:
        """Start Ollama service if not running."""
        # Check if already running
        if self.check_service("http://localhost:11434/api/tags"):
            self.logger.success("Ollama service is already running")
            return True
        
        self.logger.info("Starting Ollama service...")
        
        # Start Ollama in background
        try:
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Wait for service to start
            for i in range(30):  # Wait up to 30 seconds
                time.sleep(1)
                if self.check_service("http://localhost:11434/api/tags"):
                    self.logger.success("Ollama service started successfully")
                    return True
                if i % 5 == 0:
                    self.logger.info(f"Waiting for Ollama to start... ({i}s)")
            
            self.logger.error("Ollama service failed to start within 30 seconds")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to start Ollama: {e}")
            return False
    
    def download_models(self, models: List[str] = None) -> bool:
        """Download AI models."""
        if models is None:
            models = DEFAULT_MODELS
        
        self.logger.info("Downloading AI models...")
        
        # Check available models
        try:
            result = self.run_command(["ollama", "list"], capture_output=True)
            if result:
                existing_models = result.stdout
            else:
                existing_models = ""
        except:
            existing_models = ""
        
        success_count = 0
        for model in models:
            if model in existing_models:
                self.logger.success(f"{model} already available")
                success_count += 1
                continue
            
            self.logger.info(f"⬇️  Downloading {model} (this may take several minutes)...")
            
            if self.run_command(["ollama", "pull", model], check=False):
                self.logger.success(f"{model} downloaded successfully")
                success_count += 1
            else:
                self.logger.warning(f"Failed to download {model}")
        
        if success_count > 0:
            self.logger.success(f"{success_count}/{len(models)} models available")
            return True
        else:
            self.logger.warning("No models were downloaded successfully")
            return False
    
    def create_directories(self) -> bool:
        """Create necessary project directories."""
        self.logger.info("Creating necessary directories...")
        
        directories = [
            "data/uploads",
            "uploads",
            "backend/__pycache__",
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        
        self.logger.success("Directories created")
        return True
    
    def verify_setup(self) -> bool:
        """Verify that the setup was successful."""
        self.logger.info("Verifying setup...")
        
        # Check Ollama API
        if self.check_service("http://localhost:11434/api/tags"):
            self.logger.success("Ollama API is accessible")
            
            # Show available models
            try:
                result = self.run_command(["ollama", "list"], capture_output=True)
                if result and result.stdout:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:  # More than just header
                        self.logger.success(f"{len(lines)-1} AI model(s) available")
                        print(f"\n{Colors.CYAN}Available models:{Colors.NC}")
                        print(result.stdout)
                    else:
                        self.logger.warning("No models found")
                else:
                    self.logger.warning("Could not list models")
            except:
                self.logger.warning("Could not verify models")
        else:
            self.logger.warning("Ollama API not accessible")
            return False
        
        # Check main files exist
        required_files = ["main.py", "backend/api_server.py", "requirements.txt"]
        for file in required_files:
            if not os.path.exists(file):
                self.logger.error(f"Required file missing: {file}")
                return False
        
        self.logger.success("Setup verification completed")
        return True
    
    def start_application(self):
        """Start the Streamlit application."""
        self.logger.info("Starting Streamlit application...")
        
        try:
            # Change to project directory
            os.chdir(PROJECT_ROOT)
            
            # Start Streamlit
            subprocess.run(["streamlit", "run", "main.py"], check=True)
        except KeyboardInterrupt:
            self.logger.info("Application stopped by user")
        except Exception as e:
            self.logger.error(f"Failed to start application: {e}")
    
    def show_completion_message(self):
        """Show setup completion message with next steps."""
        print(f"\n{Colors.GREEN}{'='*60}{Colors.NC}")
        print(f"{Colors.GREEN}{'Setup Complete!':^60}{Colors.NC}")
        print(f"{Colors.GREEN}{'='*60}{Colors.NC}\n")
        
        print(f"{Colors.BLUE}Next Steps:{Colors.NC}")
        print(f"   1. Start the Streamlit application:")
        print(f"      {Colors.YELLOW}streamlit run main.py{Colors.NC}")
        print(f"")
        print(f"   2. Or start the backend API server:")
        print(f"      {Colors.YELLOW}python backend/api_server.py{Colors.NC}")
        print(f"")
        print(f"   3. Access the web interface at:")
        print(f"      {Colors.YELLOW}http://localhost:8501{Colors.NC}")
        print(f"")
        print(f"{Colors.BLUE}Tips:{Colors.NC}")
        print(f"   • Use Ctrl+C to stop services")
        print(f"   • Run 'python dev.py' for development mode")
        print(f"   • Check logs if you encounter issues")
        print(f"")
    
    def full_setup(self, start_app: bool = False) -> bool:
        """Run the complete setup process."""
        self.logger.header("Agentic AI Development Setup")
        
        # Check system requirements
        if not self.check_python_version():
            return False
        
        # Check we're in the right directory
        if not os.path.exists("main.py") or not os.path.exists("backend"):
            self.logger.error("Please run this script from the Agentic-AI-Project-BDL directory")
            return False
        
        # Step-by-step setup
        steps = [
            ("Installing dependencies", self.install_dependencies),
            ("Installing Ollama", self.install_ollama),
            ("Starting Ollama service", self.start_ollama),
            ("Downloading AI models", self.download_models),
            ("Creating directories", self.create_directories),
            ("Verifying setup", self.verify_setup),
        ]
        
        for step_name, step_func in steps:
            self.logger.info(f"{step_name}...")
            if not step_func():
                self.logger.error(f"Failed: {step_name}")
                return False
        
        self.show_completion_message()
        
        if start_app:
            response = input("Would you like to start the application now? (y/n): ")
            if response.lower().startswith('y'):
                self.start_application()
        
        return True

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Agentic AI Project Development Setup")
    parser.add_argument("--deps", action="store_true", help="Install dependencies only")
    parser.add_argument("--ollama", action="store_true", help="Setup Ollama only")
    parser.add_argument("--models", action="store_true", help="Download models only")
    parser.add_argument("--start", action="store_true", help="Start application after setup")
    parser.add_argument("--verify", action="store_true", help="Verify setup only")
    
    args = parser.parse_args()
    
    setup = DevSetup()
    
    try:
        if args.deps:
            setup.install_dependencies()
        elif args.ollama:
            setup.install_ollama()
            setup.start_ollama()
        elif args.models:
            setup.download_models()
        elif args.verify:
            setup.verify_setup()
        elif args.start:
            setup.start_application()
        else:
            # Full setup
            success = setup.full_setup(start_app=True)
            if not success:
                sys.exit(1)
                
    except KeyboardInterrupt:
        setup.logger.info("Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        setup.logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
