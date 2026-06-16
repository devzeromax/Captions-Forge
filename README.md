# Captions-Forge
Captions Forge — open-source Windows desktop app for offline subtitle &amp; caption generation. Privacy-first
<p align="center">
  <img src="assets/banner.png" alt="Captions Forge" width="100%" />
</p>

<h1 align="center">Captions Forge</h1>

<p align="center">
  <strong>Open-source desktop subtitle and captioning studio.</strong><br />
  Local transcription. No cloud. No accounts. No subscriptions.
</p>

<p align="center">
  <a href="https://github.com/your-org/captions-forge/releases"><img src="https://img.shields.io/badge/version-3.0.0-blue?style=for-the-badge" alt="Version 3.0.0" /></a>
  <a href="https://github.com/your-org/captions-forge/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" alt="MIT License" /></a>
  <a href="#"><img src="https://img.shields.io/badge/platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Windows" /></a>
</p>

<p align="center">
  <a href="#"><img src="https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.12" /></a>
  <a href="#"><img src="https://img.shields.io/badge/FastAPI-local-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI" /></a>
  <a href="#"><img src="https://img.shields.io/badge/OpenAI-Whisper-412991?style=flat-square" alt="OpenAI Whisper" /></a>
  <a href="#"><img src="https://img.shields.io/badge/NVIDIA-CUDA-76B900?style=flat-square&logo=nvidia&logoColor=white" alt="CUDA" /></a>
</p>

<p align="center">
  <a href="#"><img src="https://img.shields.io/badge/offline--first-2ea44f?style=flat-square" alt="Offline first" /></a>
  <a href="#"><img src="https://img.shields.io/badge/no%20telemetry-2ea44f?style=flat-square" alt="No telemetry" /></a>
  <a href="#"><img src="https://img.shields.io/badge/local%20processing-2ea44f?style=flat-square" alt="Local processing" /></a>
  <a href="#"><img src="https://img.shields.io/badge/open%20source-2ea44f?style=flat-square" alt="Open source" /></a>
</p>

---

## What is Captions Forge?

**Captions Forge** is a free, open-source desktop application that generates subtitles and captions from any audio or video file — entirely on your own computer.

- **No internet required** for transcription (after models are downloaded)
- **No accounts** or sign-ups
- **No usage limits** or fees
- **Your media never leaves your machine**

It uses [OpenAI Whisper](https://github.com/openai/whisper) for state-of-the-art speech recognition and supports GPU acceleration via NVIDIA CUDA for faster processing.

---

## Table of Contents

- [Features](#features)
- [Download](#download)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Privacy](#privacy)
- [Building from Source](#building-from-source)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Credits](#credits)

---

## Features

- **Automatic transcription** — powered by OpenAI Whisper (tiny → large models)
- **Language detection** — auto-detect source language or choose manually
- **Subtitle translation** — translate output into any supported language
- **Live preview** — watch subtitle segments stream in real time as transcription runs
- **SRT export** — standard `.srt` files compatible with any video player or editor
- **Burned-in video** — optionally render subtitles directly into the video (Beta)
- **GPU acceleration** — NVIDIA CUDA support for significantly faster transcription
- **Offline after setup** — no internet required once models are downloaded
- **Privacy-first** — zero telemetry, no analytics, no cloud uploads

---

## Download

| File | Description |
|------|-------------|
| **[`CaptionForge-Setup-3.0.0.exe`](https://github.com/your-org/captions-forge/releases/latest)** | Windows installer — full desktop app **(recommended)** |
| **[`captionforge.py`](captionforge.py)** | Lightweight Python GUI — for users who prefer running from source |

> **Recommended:** Use the `.exe` installer. It includes the App, local speech engine, and all required packaging. No command line needed for basic use.

---

## Requirements

| Requirement | Details |
|-------------|---------|
| **OS** | Windows 10 or 11 (64-bit) |
| **Python 3.12** | Download from [python.org](https://www.python.org/downloads/) — check **"Add Python to PATH"** during install |
| **FFmpeg** | Must be available on your system `PATH` — see [FFmpeg installation guide](https://ffmpeg.org/download.html) |
| **NVIDIA GPU** | Optional — enables CUDA-accelerated transcription |

### Python dependencies

These are installed automatically via the in-app setup wizard. To install manually:

```bash
pip install fastapi "uvicorn[standard]" sse-starlette python-multipart \
            openai-whisper torch torchaudio psutil deep-translator
```

Whisper models are downloaded on demand and cached at `%USERPROFILE%\.cache\whisper\`.

---

## Installation

### Option A — Windows Installer (recommended)

1. Download **`CaptionForge-Setup-3.0.0.exe`** from the [Releases page](https://github.com/your-org/captions-forge/releases/latest)
2. Close any existing Captions Forge windows
3. Run the installer and follow the on-screen steps
4. Launch **Captions Forge** from the Start menu or desktop shortcut
5. On first launch, complete the **in-app engine setup** (installs Python dependencies and a Whisper model)

No command line is required.

---

### Option B — Python Script

For users who prefer a lightweight option without the Electron shell:

**1. Install prerequisites**

- [Python 3.12](https://www.python.org/downloads/) (check "Add to PATH")
- [FFmpeg](https://ffmpeg.org/download.html) (on system PATH)

**2. Install dependencies**

```bash
pip install openai-whisper torch torchaudio
```

**3. Run**

```bash
python captionforge.py
```

Missing packages are detected and installed automatically on first launch.

---

## Usage

1. Open **Captions Forge**
2. Complete the setup wizard on first launch (Python engine, Whisper model)
3. Click **Select File** and choose your audio or video file
4. Set an **output folder** for the generated `.srt` file
5. Choose a **Whisper model** — `tiny` is fastest, `large` is most accurate
6. Set the **source language** (`auto` is recommended) and **output/subtitle language**
7. Click **Generate** — subtitle segments stream into the dashboard in real time
8. Find your `.srt` file in the output folder when complete

---

## Privacy

Captions Forge is designed with privacy as a core principle.

- All transcription runs **locally on your PC** — your media is never uploaded anywhere
- The UI communicates only with a local engine
- **No analytics, telemetry, or crash reporting** of any kind
- **No user accounts**, login, or registration

### Optional network activity

The only times Captions Forge may access the internet are:

- Downloading Whisper models on first use (from OpenAI's servers)
- Subtitle translation, if you choose to use it (via Google Translate)

Both are user-initiated. Neither happens automatically.

### Local data locations

| Path | Contents |
|------|----------|
| `%LOCALAPPDATA%\CaptionForge\jobs\` | Job progress and file paths |
| `%APPDATA%\app\logs\engine.log` | Engine log (local only) |
| `%USERPROFILE%\.cache\whisper\` | Downloaded Whisper models |

---

## Building from Source

Make sure Captions Forge is not running before building.

### Prerequisites

- [Node.js](https://nodejs.org/) (LTS recommended)
- [Python 3.12](https://www.python.org/downloads/)

### Steps

```bash
# 1. Build the frontend
cd frontend
npm install
npm run build:release

# 2. Build the Electron app
cd ../electron
npm install
npm run build
```

The installer will be output to:

```
electron/release-private/CaptionForge-Setup-3.0.0.exe
```

---

## Troubleshooting

| Symptom | Solution |
|---------|----------|
| **Engine stopped / won't start** | Ensure Python 3.12 is installed and on PATH; rerun in-app setup. Check `%APPDATA%\app\logs\engine.log` for details |
| **"Python not found" error** | Reinstall Python 3.12 and check **"Add Python to PATH"** during setup; restart Captions Forge |
| **Model not ready** | Open settings and download or select a Whisper model |
| **Build file locked** | Quit Captions Forge and close any Explorer windows pointing to `release-private/` |
| **Slow transcription** | Switch to a smaller model (e.g. `tiny` or `base`), or enable GPU acceleration in settings |

If your issue isn't listed above, please [open an issue](https://github.com/your-org/captions-forge/issues) with your `engine.log` attached.

---

## Contributing

Contributions are welcome! To get started:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push to your fork: `git push origin feature/your-feature`
5. Open a Pull Request

Please open an issue first for significant changes so we can discuss the approach.

---

## License

This project is licensed under the **MIT License** — free to use, modify, and distribute. See [LICENSE](LICENSE) for the full text.

---

## Credits

Captions Forge is built on the shoulders of excellent open-source projects:

- [OpenAI Whisper](https://github.com/openai/whisper) — speech recognition engine
- [PyTorch](https://pytorch.org) — ML framework powering Whisper
- [FFmpeg](https://ffmpeg.org) — audio/video processing
- [FastAPI](https://fastapi.tiangolo.com) — local backend server
- [React](https://react.dev) — UI framework
