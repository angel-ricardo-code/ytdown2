# AGENTS.md — YouTube Downloader

## Build / Lint / Test Commands

### Running the full test suite
```bash
py -3 -m pytest -q
```

### Running a single test file
```bash
py -3 -m pytest tests/test_extractor.py -q
```

### Running a single test
```bash
py -3 -m pytest tests/test_extractor.py::test_extract_info_missing_yt_dlp -q
```

### Install dependencies
```bash
py -3 -m pip install -r requirements.txt
py -3 -m pip install pytest
```

### Run the GUI
```bash
py -3 main_gui.py
```

### Run the CLI
```bash
py -3 main.py "https://www.youtube.com/watch?v=VIDEO_ID" -o downloads -v
```

### GitHub Actions (CI)
The repo includes `.github/workflows/python-package.yml` that runs `pip install -r requirements.txt` and `pytest -q` on Ubuntu with Python 3.11. No custom linting or type-checking commands are defined yet.

---

## Code Style Guidelines

### General
- **Python version**: target 3.11+. Use `py -3` launcher on Windows.
- **No comments**: do not add comments unless explicitly required by the user.
- **Type annotations**: use them for function signatures; prefer `typing` module (e.g. `Dict | None`, `str | None`) or modern syntax (compatible with Python 3.10+).
- **Docstrings**: one-line docstrings are fine for simple utilities; be concise.

### Imports
- Standard library imports first, then third-party, then relative.
- Group by: stdlib, third-party, local/relative.
- Do not use wildcard imports.
- Example:
  ```python
  from typing import Dict
  from pathlib import Path

  from pydantic import BaseModel

  from src.models import VideoInfo, VideoFormat
  ```

### Naming Conventions
- **Modules**: lowercase, underscore-separated (`downloader.py`, `video_utils.py`).
- **Classes**: CapWords (`VideoInfo`, `VideoFormat`, `AgeRestrictedError`).
- **Functions/methods**: snake_case (`extract_info`, `download_with_yt_dlp`).
- **Constants**: SCREAMING_SNAKE_CASE when module-level.
- **Variables**: snake_case; avoid single-letter names except loop counters.
- **Types (Pydantic models)**: `format_id` (snake_case), `mimeType` (keep yt-dlp field names), `acodec`, `vcodec`.

### Formatting
- Indent: 4 spaces (no tabs).
- Max line length: ~120 chars (use line continuation for readability).
- Trailing commas on multi-line structures when applicable.
- Sort imports with a standard group order (stdlib, third-party, relative).

### GUI-Specific Guidelines (main_gui.py)
- Use PySide6 for GUI components (QWidget, QVBoxLayout, QHBoxLayout, etc.).
- Use Qt.AlignCenter, Qt.AlignRight for alignment (not strings).
- Font weights via QFont.Weight enum: QFont.Bold, QFont.Medium (not raw integers).
- Colors defined in `C` dictionary constant with HEX tokens (e.g., `C["ACCENT"]`, `C["BG_WINDOW"]`).
- Widget heights: 44px for inputs, 48px for main buttons, 36px for secondary.
- Border-radius: 10px for inputs, 12px for main buttons, 8px for ghost buttons.
- Spacing: 18px between widgets, 40px margins for large layouts.
- Use `setFixedSize()` for non-resizable windows.
- Use `setItemData(index, value)` to store format IDs in combo boxes; read with `currentData()`.

### Error Handling
- Raise custom exceptions from `src/exceptions.py` (`VideoUnavailable`, `AgeRestrictedError`) for domain-specific errors.
- Use generic `Exception` only for truly unexpected/unrecoverable cases; prefer specific types.
- Propagate errors up to the GUI/CLI layer; let main handle presentation.
- Never swallow errors silently — either reraise with context or log.
- Example pattern:
  ```python
  try:
      info = extractor.extract_info(url)
  except Exception as e:
      console.print(f"[red]Extraction failed:[/red] {e}")
      raise typer.Exit(code=1)
  ```

### Custom Exceptions (`src/exceptions.py`)
- `VideoUnavailable` — raised when a video cannot be found or is removed.
- `AgeRestrictedError` — raised for age-restricted content.
- Both inherit from `Exception`. Add new ones as needed for domain errors.

### Pydantic Models (`src/models.py`)
- All models inherit from `pydantic.BaseModel`.
- Fields should be typed; use `Optional[...]` when a field may be `None`.
- Keep field names consistent with yt-dlp output (e.g. `format_id`, `mimeType`, `acodec`, `vcodec`).

### CLI (`main.py`)
- Use **Typer** for argument parsing (already in use).
- Use **Rich** for console output (`rich.table.Table`, `rich.console.Console`).
- Wrap the entry point in `_main()` to handle `KeyboardInterrupt` cleanly.
- Always include `--help` via Typer; no custom help text needed unless user asks.

### File Paths
- Use `pathlib.Path` for all file/path operations. Never use string concatenation for paths.
- Cross-platform: avoid hardcoded separators; use `/` (Path handles it) or `Path("...") / "subdir"`.

### Dependencies (runtime resolution)
- Prefer Python package imports (`import yt_dlp`) with graceful fallback to the executable (`yt-dlp.exe`).
- Do not hardcode absolute paths to external tools. Use `shutil.which()` to locate them.
- For ffmpeg, search PATH first, then `tools/portable` as a fallback.
- All third-party dependencies are listed in `requirements.txt`. Keep it updated.

### Testing
- Use **pytest** for all tests.
- Tests go in `tests/` directory.
- Use `monkeypatch` (pytest fixture) to mock or simulate missing dependencies.
- Name test functions: `test_<what_is_being_tested>`.
- Each test should be self-contained and deterministic.
- Edge cases: test missing dependencies (no yt-dlp), network errors, invalid URLs.

### Security & Ethics
- Never commit credentials, API keys, or tokens.
- Use environment variables for sensitive configuration.
- Respect robots.txt and rate limits when accessing external services.
- Follow the legal notice in `Instrucciones_Descargador_Video.txt`: only use this tool with explicit written permission on authorized platforms.

### Project Structure
```
src/
  __init__.py
  extractor.py   # yt-dlp metadata extraction
  downloader.py  # yt-dlp download + httpx direct download
  merger.py      # ffmpeg stream merging
  models.py      # pydantic models
  utils.py       # helpers (sanitize_filename, etc.)
  exceptions.py  # custom exception classes
main.py          # CLI entry point (Typer + Rich)
main_gui.py     # GUI entry point (PySide6)
tests/
  test_extractor.py
  test_gui_controller.py
requirements.txt
README.md
AGENTS.md
tools/
  setup_portables.ps1
  install_ffmpeg_fallback.ps1
  download_wheels.ps1
  install_from_wheels.ps1
  portable/ffmpeg/
.github/workflows/python-package.yml
```