# Personal Voice Assistant

A Python desktop voice assistant project with speech-related functionality, a graphical interface, and integrations with external services.

## Features and Technologies

- Python-based desktop application.
- Tkinter graphical user interface.
- Speech recognition using SpeechRecognition.
- Text-to-speech using gTTS.
- Online information retrieval using Requests and Wikipedia.
- Additional utilities using PyWhatKit and PyJokes.
- Environment configuration using python-dotenv.

## Project Structure

| File | Description |
| --- | --- |
| `aman.py` | Voice assistant implementation |
| `Changes.py` | Voice assistant implementation |
| `FChanges.py` | Alternative implementation |
| `gui.py` | GUI-oriented implementation |
| `VA.py` | Voice assistant implementation |
| `VoiceA.py` | Voice assistant implementation |
| `requirements.txt` | Python dependencies |
| `.env.example` | Environment variable template |

These scripts represent different implementations. Inspect the selected script before running it.

## Requirements

- Windows
- Python 3.10 or later recommended
- pip
- Microphone and audio output for voice features
- Internet connection for online features

Some microphone configurations require PyAudio, which may need to be installed separately.

## Installation

Clone the repository:

``bash
git clone https://github.com/Vishal45-hub/Personal-Voice-Assistant.git
cd Personal-Voice-Assistant
``

Create and activate a virtual environment in PowerShell:

``powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
``

Install the dependencies:

``powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
``

## Configuration

Copy `.env.example` to `.env` and add your own credentials and configuration values as needed.

Never commit `.env` or expose API keys and personal contact information.

## Running the Application

Choose the script whose functionality you want to use. For example:

``powershell
python Changes.py
``

The startup method and required configuration may differ between scripts.

## Troubleshooting

- Check Windows microphone permissions if voice input fails.
- Verify API credentials and internet connectivity if online features fail.
- Check audio output settings if playback fails.
- Review installation errors for missing dependencies.

## Future Improvements

- Consolidate duplicate implementations.
- Improve error handling and configuration validation.
- Add automated tests.
- Improve documentation and GUI accessibility.

## License

No license has been specified. All rights remain with the respective copyright holder unless a license is added.
