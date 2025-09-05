#!/usr/bin/env zsh

# Create virtual environment if it doesn't exist
if [[ ! -d "myenv" ]]; then
    python3 -m venv myenv
fi

# Activate virtual environment
source myenv/bin/activate

# Install or update requirements
pip install -r requirements.txt

echo "Environment setup complete. Virtual environment 'myenv' is now activated."