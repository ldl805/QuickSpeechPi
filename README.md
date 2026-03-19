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

## Installation (Recommended)

### Option 1: Debian Package (Pi/Ubuntu/Debian)

Download the latest `.deb` file from the [Releases](https://github.com/ldl805/QuickSpeechPi/releases) page and install it using:

```bash
sudo apt update
sudo apt install ./quickspeechpi_1.1_all.deb
```

### Option 2: Standalone Zip

1.  Download `QuickSpeechPi-linux.zip` from the Releases page.
2.  Extract the zip file.
3.  Ensure system dependencies are installed: `sudo apt install espeak python3-tk`
4.  Run the `QuickSpeechPi` binary.

## Installation (From Source)

1.  **Clone this repository.**
2.  **Run the setup script** to install necessary system dependencies:
    ```bash
    chmod +x setup.sh
    ./setup.sh
    ```
3.  **Run the application:**
    ```bash
    python3 tts_gui.py
    ```

## Usage

Run the application directly with Python:
```bash
python3 tts_gui.py
```

## License
MIT License
