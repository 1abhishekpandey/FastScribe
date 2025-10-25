#!/usr/bin/env python3

"""
FastScribe - Main Entry Point
Activates the local virtual environment and runs the transcriber.
"""

import sys
import subprocess
from pathlib import Path


def main():
    # Get project root directory (where this script is located)
    project_root = Path(__file__).parent.absolute()
    venv_dir = project_root / ".venv"

    # Determine platform-specific Python executable
    if sys.platform == "win32":
        python_exe = venv_dir / "Scripts" / "python.exe"
    else:
        python_exe = venv_dir / "bin" / "python"

    # Check if venv exists
    if not venv_dir.exists():
        print("Virtual environment not found!")
        print("Run setup first: python3 scripts/setup_local.py")
        sys.exit(1)

    # Path to the main transcriber script
    transcriber_script = project_root / "scripts" / "transcribe_parallel.py"

    # Run the transcriber with the venv's Python interpreter in unbuffered mode
    try:
        result = subprocess.run(
            [str(python_exe), "-u", str(transcriber_script)] + sys.argv[1:],
            check=False
        )
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error running transcriber: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
