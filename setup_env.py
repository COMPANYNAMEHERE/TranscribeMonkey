"""Setup script for creating a development environment."""

import os
import shutil
import subprocess
import sys
import time

BAR_LENGTH = 30


def print_header():
    """Display the setup header."""
    print("=" * 50)
    print("TranscribeMonkey Setup")
    print("=" * 50)


def progress(message, duration=1.5):
    """Simple progress bar animation."""
    steps = 10
    print(message, end="", flush=True)
    for i in range(steps):
        time.sleep(duration / steps)
        completed = int(BAR_LENGTH * (i + 1) / steps)
        bar = "[" + "#" * completed + " " * (BAR_LENGTH - completed) + "]"
        print(f"\r{message} {bar}", end="", flush=True)
    print()


def check_conda():
    """Return the path to conda or instruct the user to install it."""
    conda = shutil.which("conda")
    if not conda:
        print("Conda was not found. Please install Miniconda or Anaconda from https://conda.io and re-run this script.")
        sys.exit(1)
    return conda


def create_env(env_name, python_version):
    """Create the conda environment if it does not exist."""
    result = subprocess.run(["conda", "env", "list"], capture_output=True, text=True)
    if env_name in result.stdout:
        print(f"Environment '{env_name}' already exists.")
        return
    progress("Creating conda environment")
    subprocess.check_call(["conda", "create", "-y", "-n", env_name, f"python={python_version}"])


def install_requirements(env_name):
    """Install requirements using conda run."""
    progress("Installing requirements")
    subprocess.check_call(["conda", "run", "-n", env_name, "pip", "install", "-r", "requirements.txt"])


def check_ffmpeg(env_name):
    """Warn if ffmpeg is missing."""
    result = subprocess.run(["conda", "run", "-n", env_name, "ffmpeg", "-version"], capture_output=True)
    if result.returncode != 0:
        print("Warning: ffmpeg is not available. Please install it separately if audio processing fails.")


def main():
    """Entry point for the setup script."""
    print_header()
    check_conda()
    env = input("Enter conda environment name [transcribemonkey]: ") or "transcribemonkey"
    python_version = "3.8"
    create_env(env, python_version)
    install_requirements(env)
    check_ffmpeg(env)
    print()
    print("Setup complete!")
    print(f"Activate the environment with: conda activate {env}")
    print("Then launch the program with: python main.py")


if __name__ == "__main__":
    main()
