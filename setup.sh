#!/bin/bash
echo "Installing dependencies for the TTS GUI..."
sudo apt-get update
sudo apt-get install -y python3-tk espeak
echo "Installation complete."
