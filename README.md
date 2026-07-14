# Downloader

A modern, feature-rich video downloader powered by `yt-dlp`. Download videos from YouTube and hundreds of other sites with a beautiful Qt interface or from the command line.

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11+-blue?style=flat&logo=python" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/yt--dlp-powered-brightgreen?style=flat" alt="yt-dlp">
  <img src="https://img.shields.io/badge/license-MIT-blue?style=flat" alt="MIT License">
</p>

## ✨ Features

- **Dual interface** — sleek Qt6 GUI for casual use, powerful CLI for power users
- **Multi-format** — choose quality, resolution, or let it auto-select the best
- **Separate video + audio** — download high-quality streams and merge them with ffmpeg
- **Pause / Resume / Cancel** — full control over active downloads
- **Cookie support** — manual file upload or auto-capture via Playwright
- **FFmpeg auto-detection** — checks PATH, bundled portable copy, or custom location
- **Persistent config** — remembers your output folder, cookies, and ffmpeg path
- **Cross-platform** — Windows, Linux, macOS
- **Merge tool** — built-in dialog to combine downloaded video and audio files

---

## 📦 Installation

### Prerequisites

- **Python 3.11+**
- **ffmpeg** (optional — only needed for merging video+audio streams)

### 1. Clone or download

```bash
git clone <repo-url> downloader
cd downloader
```

Or simply download and extract the source code.

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

<details>
<summary><b>📄 requirements.txt contents</b></summary>

```
yt-dlp>=2024.12.0
typer[all]
rich
pydantic
httpx
PySide6
playwright
```

</details>

### 3. (Optional) Install ffmpeg

FFmpeg is only needed when downloading **separate video + audio streams** (typically 720p and above). Choose one:

#### Option A — Bundled (Windows only)

The repository includes a portable ffmpeg at `tools/portable/ffmpeg/ffmpeg.exe`. It is detected automatically — no setup required.

#### Option B — System-wide

| OS | Command |
|----|---------|
| **Windows** (Chocolatey) | `choco install ffmpeg -y` |
| **Windows** (manual) | Download from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/), extract, add `bin` to `PATH` |
| **Linux** (Debian/Ubuntu) | `sudo apt update && sudo apt install ffmpeg -y` |
| **Linux** (Fedora) | `sudo dnf install ffmpeg -y` |
| **Linux** (Arch) | `sudo pacman -S ffmpeg` |
| **macOS** (Homebrew) | `brew install ffmpeg` |

#### Option C — Point the GUI to your own copy

In the GUI, click **Locate** next to "FFmpeg" and select the folder containing `ffmpeg.exe`.

---

## 🚀 Usage

### GUI (Desktop Application)

```bash
python main_gui.py
```

The main window contains:

| Control | Description |
|---------|-------------|
| **URL input** | Paste a video link — formats load automatically |
| **Quality dropdown** | Choose resolution (or let it pick the best) |
| **Browse** | Choose where to save the file |
| **Cookies** | Upload a Netscape cookies file or auto-capture via Playwright |
| **FFmpeg Locate** | Point to your ffmpeg folder if not found automatically |
| **Download** | Start downloading |
| **Pause / Resume** | Pause and resume downloads |
| **Cancel** | Abort the current download |
| **Merge Files** | Open the merge dialog to combine separate video + audio |

#### Auto-capture cookies

1. Click **Auto** next to the cookies field
2. A Chromium browser window opens to the video URL
3. Complete any human verification (login, captcha, age gate)
4. Cookies are exported automatically to a temporary file

---

### CLI (Command Line)

```bash
python main.py <URL> [options]
```

#### Basic download

```bash
# Download best quality
python main.py "https://www.youtube.com/watch?v=VIDEO_ID" -o downloads

# Download with verbose progress
python main.py "https://www.youtube.com/watch?v=VIDEO_ID" -o downloads -v
```

#### Format selection

```bash
# Download a specific quality by itag
python main.py "URL" -f 137 -o downloads     # 1080p
python main.py "URL" -f 136 -o downloads     # 720p
python main.py "URL" -f 18 -o downloads      # 360p

# Best video + best audio (merged with ffmpeg)
python main.py "URL" -f bestvideo+bestaudio -o downloads

# Audio only
python main.py "URL" --audio-only -o downloads
```

#### Common YouTube itags

| itag | Quality | Resolution | Type |
|------|---------|------------|------|
| 137 | 1080p | 1920×1080 | Video only |
| 136 | 720p | 1280×720 | Video only |
| 135 | 480p | 854×480 | Video only |
| 134 | 360p | 640×360 | Video only |
| 18 | 360p | 640×360 | Video + Audio |
| 22 | 720p | 1280×720 | Video + Audio |
| 139 | Low | — | Audio only (m4a) |
| 140 | Medium | — | Audio only (m4a) |
| 251 | Medium | — | Audio only (opus) |

---

## 🧩 Project Structure

```
downloader/
├── main.py              # CLI entry point (Typer + Rich)
├── main_gui.py          # GUI entry point (PySide6 Qt)
├── requirements.txt     # Python dependencies
├── README.md            # This file
├── AGENTS.md            # Development guide
├── src/
│   ├── __init__.py
│   ├── extractor.py     # yt-dlp metadata extraction
│   ├── downloader.py    # Download logic
│   ├── merger.py        # ffmpeg stream merging
│   ├── manual_merge.py  # Manual merge dialog backend
│   ├── models.py        # Pydantic models
│   ├── utils.py         # Helper functions
│   └── exceptions.py    # Custom exceptions
├── tests/
│   └── test_extractor.py
├── tools/
│   ├── setup_portables.ps1
│   ├── install_ffmpeg_fallback.ps1
│   ├── download_wheels.ps1
│   ├── install_from_wheels.ps1
│   └── portable/
│       └── ffmpeg/      # Bundled ffmpeg (Windows)
└── .github/workflows/
    └── python-package.yml
```

---

## 🛠 Development

### Install dev dependencies

```bash
pip install -r requirements.txt
pip install pytest
```

### Run tests

```bash
# All tests
pytest -q

# Single test file
pytest tests/test_extractor.py -q

# Single test case
pytest tests/test_extractor.py::test_extract_info_missing_yt_dlp -q
```

---

## ❓ Troubleshooting

### "ffmpeg not found" / merge fails

The tool looks for ffmpeg in this order:

1. User-configured path (set via GUI **Locate** button)
2. System `PATH` environment variable
3. Bundled copy at `tools/portable/ffmpeg/ffmpeg.exe`
4. Saved config path (persisted across sessions)

If none of these work, open the GUI, click **Locate** next to "FFmpeg", and point it to the folder containing `ffmpeg.exe`.

### "Video unavailable" error

- The video may be private, deleted, or region-restricted
- Try exporting cookies from your browser (use the **Auto** button in the GUI)
- Pass cookies manually via the cookies file selector

### Download stuck / slow

- The GUI supports **Pause** and **Resume** — try pausing and resuming
- Cancel and re-try — yt-dlp supports partial downloads (`continuedl: true`)
- Check your internet connection

### Unicode / encoding issues on Windows

Run in a terminal that supports UTF-8:

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

Windows Terminal or PowerShell 7+ work best.

### GUI won't open (Linux headless / SSH)

Install a virtual framebuffer:

```bash
sudo apt install xvfb
xvfb-run python main_gui.py
```

---

## 🔒 Legal Notice

This tool is for **educational purposes only**. Only download content you have permission to download. Respect:

- The terms of service of the platforms you use
- `robots.txt` and rate limits
- Copyright and intellectual property laws

The authors are not responsible for any misuse of this software.

---

## 📄 License

MIT License — see the [LICENSE](LICENSE) file for details.
