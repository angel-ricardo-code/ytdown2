# youtubefake-downloader

A YouTube video downloader tool that uses yt-dlp as the extraction and download backend. Designed for YouTube and YouTube-like platforms.

## Requirements

- **Python 3.11+** (or use `py -3` launcher on Windows)
- **ffmpeg** (required only if merging separate video+audio streams)
- **yt-dlp** (installed automatically with dependencies)

### Installing Dependencies

```bash
# Using pip
pip install -r requirements.txt

# Or using py launcher (Windows)
py -3 -m pip install -r requirements.txt
```

### Installing ffmpeg

**Windows (manual)**:
1. Download ffmpeg from https://www.gyan.dev/ffmpeg/builds/
2. Extract the ZIP and add the `bin` folder to your PATH

**Windows (Chocolatey)**:
```bash
choco install ffmpeg -y
```

**macOS (Homebrew)**:
```bash
brew install ffmpeg
```

**Linux (Debian/Ubuntu)**:
```bash
sudo apt update && sudo apt install ffmpeg
```

## Usage

### Basic Download

```bash
# Download best quality
python main.py "https://www.youtube.com/watch?v=VIDEO_ID" -o downloads

# Or on Windows with py launcher
py -3 main.py "https://www.youtube.com/watch?v=VIDEO_ID" -o downloads
```

### Download Options

```bash
# Download only audio
python main.py "URL" --audio-only -o downloads

# Download specific quality (itag)
python main.py "URL" -f 137 -o downloads    # 1080p
python main.py "URL" -f 136 -o downloads    # 720p
python main.py "URL" -f 135 -o downloads    # 480p
python main.py "URL" -f 18 -o downloads     # 360p

# Download best video + best audio (merged with ffmpeg)
python main.py "URL" -f bestvideo+bestaudio -o downloads

# Verbose output (shows progress)
python main.py "URL" -o downloads -v
```

### Quality Reference (YouTube itags)

| itag | Quality   | Resolution |
|------|----------|-------------|
| 137  | 1080p    | 1920x1080   |
| 136  | 720p     | 1280x720    |
| 135  | 480p     | 854x480     |
| 134  | 360p     | 640x360     |
| 18   | 360p     | 640x360     |
| 139  | audio    | m4a (low)   |
| 140  | audio    | m4a (med)   |

## Project Structure

```
youtubefake-downloader/
├── src/
│   ├── __init__.py
│   ├── extractor.py   # Metadata extraction
│   ├── downloader.py # Download logic
│   ├── merger.py      # Video+audio merging
│   ├── models.py     # Pydantic models
│   ├── utils.py      # Helper functions
│   └── exceptions.py # Custom exceptions
├── tests/
│   └── test_extractor.py
├── main.py            # CLI entry point
├── requirements.txt # Dependencies
└── README.md
```

## Development

### Install Dependencies

```bash
pip install -r requirements.txt
pip install pytest
```

### Run Tests

```bash
# Full test suite
pytest -q

# Single test file
pytest tests/test_extractor.py -q

# Single test
pytest tests/test_extractor.py::test_extract_info_missing_yt_dlp -q
```

## Troubleshooting

### "Video unavailable" error

- The video may be private, deleted, or region-restricted
- Try with cookies: `python main.py "URL" --cookies cookies.txt`
- Export cookies from your browser using a browser extension

### "ffmpeg not found"

- Install ffmpeg and add it to your PATH
- Or place ffmpeg.exe in `tools/portable/ffmpeg/bin/`

### Unicode errors on Windows

- Run in PowerShell with UTF-8: `[Console]::OutputEncoding = [System.Text.Encoding]::UTF8`
- Or use a terminal like Windows Terminal that supports UTF-8

## Security & Legal Notice

- Only download content you have permission to download
- Respect robots.txt and rate limits
- Do not include credentials or API keys in the repository
- Use environment variables for sensitive configuration
- This tool is for educational purposes; respect the terms of service of the platforms you use

## License

MIT License - See LICENSE file for details.