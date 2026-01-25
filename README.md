# QuickSpeechPi

A simple, lightweight Python application that provides a graphical interface for the `espeak` text-to-speech synthesizer.

## Features
- **Voice Selection:** Choose from various male, female, and special effect voices (Whisper, Croak).
- **Pitch Control:** Adjust the tone of the voice.
- **Speed Control:** Speed up or slow down the speech rate.
- **Simple Interface:** Easy-to-use text box with "Speak" and "Clear" buttons.

## Prerequisites
- Linux operating system (tested on Debian/Ubuntu based systems).
- Python 3.
- `espeak` engine.
- `tkinter` (Python's standard GUI library).

## Downloading a Release (Recommended)

If you don't want to install Python or manage code, you can download the latest pre-built version from the **Releases** page on GitHub.

1.  Download `QuickSpeechPi-linux.zip`.
2.  Extract the zip file.
3.  Ensure `espeak` is installed (`sudo apt install espeak`).
4.  Double-click `QuickSpeechPi` to run.

## Installation (From Source)

1.  **Clone or download this repository.**
2.  **Run the setup script** to install necessary system dependencies (`espeak` and `python3-tk`):
    ```bash
    chmod +x setup.sh
    ./setup.sh
    ```

## Usage

Run the application directly with Python:
```bash
python3 tts_gui.py
```

### Desktop Shortcut
A `.desktop` file is included for easier access. To install it:

1.  Open `tts_gui.desktop` and ensure the paths match your installation location.
2.  Copy it to your applications folder:
    ```bash
    cp tts_gui.desktop ~/.local/share/applications/
    ```

## License
MIT License
