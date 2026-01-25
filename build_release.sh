#!/bin/bash
set -e

# Define variables
APP_NAME="QuickSpeechPi"
OUTPUT_DIR="release_dist"
VENV_PYTHON="./venv/bin/python"
PYINSTALLER="./venv/bin/pyinstaller"

echo "Starting build process for $APP_NAME..."

# Check if venv exists
if [ ! -f "$PYINSTALLER" ]; then
    echo "Error: PyInstaller not found in venv. Please run: python3 -m venv venv && ./venv/bin/pip install pyinstaller"
    exit 1
fi

# Clean previous builds
echo "Cleaning up..."
rm -rf build dist "$OUTPUT_DIR" *.spec

# Build with PyInstaller
echo "Running PyInstaller..."
# --onefile: Create a single executable
# --windowed: No console window
# --name: Name of the executable
# --clean: Clean PyInstaller cache
$PYINSTALLER --noconfirm --onefile --windowed --clean --name "$APP_NAME" tts_gui.py

# Create release structure
echo "Creating release package..."
mkdir -p "$OUTPUT_DIR/$APP_NAME"

# Copy files
cp "dist/$APP_NAME" "$OUTPUT_DIR/$APP_NAME/"
cp README.md "$OUTPUT_DIR/$APP_NAME/"
cp tts_gui.desktop "$OUTPUT_DIR/$APP_NAME/"
cp setup.sh "$OUTPUT_DIR/$APP_NAME/"

# Create archive
cd "$OUTPUT_DIR"
zip -r "${APP_NAME}-linux.zip" "$APP_NAME"
cd ..

echo "Build complete!"
echo "Release archive is available at: $OUTPUT_DIR/${APP_NAME}-linux.zip"
