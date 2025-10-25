#!/usr/bin/env python3

"""
FastScribe - Local Virtual Environment Setup
This script creates a local venv so all packages are isolated to this project
"""

import os
import sys
import subprocess
import venv
from pathlib import Path


def run_command(cmd, description=""):
    """Run a shell command and return success status."""
    try:
        if description:
            print(description)
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"Error executing command: {e}")
        return False


def remove_directory(path):
    """Remove a directory recursively with permission handling."""
    try:
        import shutil
        # On macOS, sometimes shutil.rmtree fails due to permissions
        # Use a more robust approach
        shutil.rmtree(path, ignore_errors=True)

        # If it still exists, try using system command
        if path.exists():
            run_command(f'rm -rf "{path}"', "")

        return not path.exists()
    except Exception as e:
        print(f"Warning: Could not remove directory: {e}")
        return False


def check_venv_health(venv_dir):
    """Check if virtual environment is corrupted (e.g., from directory move)."""
    if not venv_dir.exists():
        return True  # No venv exists, so it's "healthy" (will be created)

    # Determine platform-specific pip path
    if sys.platform == "win32":
        pip_exe = venv_dir / "Scripts" / "pip.exe"
    else:
        pip_exe = venv_dir / "bin" / "pip"

    # Check if pip exists
    if not pip_exe.exists():
        return False

    # Try to read the shebang line to detect bad interpreter paths
    try:
        with open(pip_exe, 'rb') as f:
            first_line = f.readline().decode('utf-8', errors='ignore').strip()
            if first_line.startswith('#!'):
                # Check if the interpreter path in shebang exists
                interpreter_path = first_line[2:].strip().split()[0]
                if not os.path.exists(interpreter_path):
                    return False
    except Exception:
        pass  # If we can't read it, we'll try running it

    # Try running pip --version as final check
    try:
        result = subprocess.run(
            [str(pip_exe), '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False


def main():
    # Get project root directory (where this script is located)
    project_root = Path(__file__).parent.absolute()
    venv_dir = project_root / ".venv"

    print("=" * 50)
    print("Setting up local environment")
    print("=" * 50)
    print()

    # Check Python version
    if sys.version_info < (3, 9):
        print(f"Error: Python 3.9 or later required. You have {sys.version}")
        sys.exit(1)

    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"Using Python {python_version}")
    print()

    # Check if venv already exists and is healthy
    if venv_dir.exists():
        print(f"Virtual environment found at {venv_dir}")
        print("Checking virtual environment health...")

        if not check_venv_health(venv_dir):
            print("⚠ Virtual environment is corrupted (likely from directory move/rename)")
            print("Automatically removing and recreating...")
            if remove_directory(venv_dir):
                print("✓ Removed corrupted venv")
            else:
                print("Warning: Could not fully remove existing venv, will attempt to recreate...")
            print()
        else:
            print("✓ Virtual environment is healthy")
            response = input("Do you want to recreate it anyway? (y/n): ").strip().lower()
            if response == "y":
                print("Removing existing virtual environment...")
                if remove_directory(venv_dir):
                    print("✓ Removed existing venv")
                else:
                    print("Warning: Could not fully remove existing venv, creating new one...")
                print()
            else:
                print("Skipping creation. Using existing venv...")
                print()

    # Create virtual environment
    if not venv_dir.exists():
        print("Creating virtual environment...")
        try:
            venv.create(venv_dir, with_pip=True)
            print("✓ Virtual environment created")
            print()
        except Exception as e:
            print(f"Error creating virtual environment: {e}")
            sys.exit(1)

    # Determine platform-specific paths
    if sys.platform == "win32":
        python_exe = venv_dir / "Scripts" / "python.exe"
        pip_exe = venv_dir / "Scripts" / "pip.exe"
        activate_cmd = str(venv_dir / "Scripts" / "activate.bat")
    else:
        python_exe = venv_dir / "bin" / "python"
        pip_exe = venv_dir / "bin" / "pip"
        activate_cmd = f"source {venv_dir / 'bin' / 'activate'}"

    # Upgrade pip
    print("Upgrading pip...")
    if not run_command(f'"{pip_exe}" install --upgrade pip', ""):
        print("Warning: Could not upgrade pip, continuing anyway...")
    print()

    # Install requirements
    requirements_file = project_root / "scripts" / "requirements.txt"
    if not requirements_file.exists():
        print(f"Error: requirements.txt not found at {requirements_file}")
        sys.exit(1)

    print("Installing packages locally (this may take a few minutes)...")
    if not run_command(f'"{pip_exe}" install -r "{requirements_file}"', ""):
        print("Error: Failed to install requirements")
        sys.exit(1)

    print()

    # Create input and output directories
    input_dir = project_root / "input"
    output_dir = project_root / "output"

    print("Creating project directories...")
    input_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)
    print(f"✓ Created {input_dir}")
    print(f"✓ Created {output_dir}")
    print()

    print("=" * 50)
    print("✓ Setup complete!")
    print("=" * 50)
    print()

    if sys.platform == "win32":
        print("To activate the environment in future sessions, run:")
        print(f"  {activate_cmd}")
        print()
        print("Or use python3 transcribe.py to run directly")
    else:
        print("To activate the environment in future sessions, run:")
        print(f"  source {venv_dir / 'bin' / 'activate'}")
        print()
        print("To deactivate, run:")
        print("  deactivate")
        print()
        print("Or use python3 transcribe.py to run directly")

    print()
    print("Next steps:")
    print(f"  1. Place your video files in: {input_dir}")
    print("  2. Run: python3 transcribe.py --default")
    print(f"  3. Find transcripts in: {output_dir}")
    print()
    print("To delete the local environment:")
    print(f"  rm -rf {venv_dir}")
    print()


if __name__ == "__main__":
    main()
