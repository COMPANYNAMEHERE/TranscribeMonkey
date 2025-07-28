#!/usr/bin/env bash
set -e

print_header() {
    printf '%s\n' '=================================================='
    echo 'TranscribeMonkey Setup'
    printf '%s\n' '=================================================='
}

check_conda() {
    if ! command -v conda >/dev/null 2>&1; then
        echo "Conda was not found. Please install Miniconda or Anaconda from https://conda.io and re-run this script."
        exit 1
    fi
}

create_env() {
    local env_name="$1"
    local python_version="3.8"
    if conda env list | grep -q "^$env_name"; then
        echo "Environment '$env_name' already exists."
        return
    fi
    echo "Creating conda environment..."
    conda create -y -n "$env_name" "python=$python_version"
}

install_requirements() {
    local env_name="$1"
    echo "Installing requirements..."
    conda run -n "$env_name" pip install -r requirements.txt
}

check_ffmpeg() {
    local env_name="$1"
    if ! conda run -n "$env_name" ffmpeg -version >/dev/null 2>&1; then
        echo "Warning: ffmpeg is not available. Please install it separately if audio processing fails."
    fi
}

print_header
check_conda
read -p 'Enter conda environment name [transcribemonkey]: ' ENV_NAME
ENV_NAME=${ENV_NAME:-transcribemonkey}
create_env "$ENV_NAME"
install_requirements "$ENV_NAME"
check_ffmpeg "$ENV_NAME"

echo
echo "Setup complete!"
echo "Activate the environment with: conda activate $ENV_NAME"
echo "Then launch the program with: python main.py"
