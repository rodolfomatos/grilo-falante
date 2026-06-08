#!/bin/bash
set -e

echo "Installing Grilo Falante dependencies..."

VENV_DIR="${VENV_DIR:-.venv}"

create_venv() {
    echo "Creating virtual environment at $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    echo "Virtual environment created and activated."
}

if [ -d "$VENV_DIR" ]; then
    echo "Virtual environment found at $VENV_DIR"
    source "$VENV_DIR/bin/activate"
else
    create_venv
fi

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing grilo-falante with dev dependencies..."
pip install -e ".[all]"

echo ""
echo "Installation complete!"
echo "Activate the virtual environment with: source $VENV_DIR/bin/activate"
