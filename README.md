# QuickSpeechPi

A modern, lightweight Python application that provides a graphical interface for Text-to-Speech (TTS). It supports both offline local synthesis and high-quality cloud synthesis.

## Features
- **Dual-Engine Support:**
  - **Local Engine (eSpeak):** Fully offline, lightweight, supporting voice variants (Male, Female, Whisper, Croak), pitch, and speed adjustments.
  - **Cloud Engine (Gemini TTS):** High-fidelity, natural-sounding neural voices (Kore, Puck, Fenrir, Charon, Aoede) using the Google GenAI SDK.
- **Cancel/Stop Playback:** Instantly stop speech playback mid-sentence with a dedicated **STOP** button.
- **Export to WAV:** Save generated speech directly to a `.wav` audio file (works with both local and cloud engines) without playing it aloud.
- **Live Text Stats:** Dynamic display of character and word counts as you type.
- **Modern UI:** Styled with a custom Charcoal/Slate dark theme and includes scrollbar support for text editing.
- **Graceful Fallbacks:** The app starts and runs offline using eSpeak even if the Gemini SDK or API key is not configured.

## Prerequisites
- Linux operating system (tested on Debian/Ubuntu/Raspberry Pi OS).
- Python 3.
- `espeak` engine.
- `tkinter` (Python's standard GUI library).

## Setup & API Key (Optional for Cloud Features)
To use the realistic Gemini Cloud TTS voices:
1. Obtain an API Key from Google AI Studio.
2. Save it in a `.env` file in the application directory or your user home directory:
   ```env
   GEMINI_API_KEY="your_api_key_here"
   ```

## Installation

### Option 1: Debian Package (Pi/Ubuntu/Debian)
Download the latest `.deb` file and install it:
```bash
sudo apt update
sudo apt install ./quickspeechpi_1.2.1_all.deb
```

### Option 2: Standalone Release Zip
1. Download `QuickSpeechPi-linux.zip` from the Releases page.
2. Extract the zip file.
3. Ensure system dependencies are installed:
   ```bash
   sudo apt install espeak python3-tk
   ```
4. Run the `QuickSpeechPi` executable.

### Building From Source
1. Clone this repository.
2. Run the setup script to install dependencies:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```
3. Set up the Python virtual environment and install GenAI packages:
   ```bash
   python3 -m venv venv
   ./venv/bin/pip install -r requirements.txt
   ```
4. Run the app:
   ```bash
   ./venv/bin/python tts_gui.py
   ```

## License
MIT License
