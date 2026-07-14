from pathlib import Path
from typing import Optional
import subprocess


def download_with_yt_dlp(url: str, output_dir: Path, format_selector: Optional[str] = None, verbose: bool = False) -> Path:
    """Download the given URL using yt-dlp. Returns path to downloaded file.

    format_selector: a yt-dlp format string (e.g. "best", "22", "bestvideo+bestaudio")
    """
    import shutil, subprocess, json

    output_dir.mkdir(parents=True, exist_ok=True)

    # Prefer python yt-dlp if available
    try:
        import yt_dlp

        outtmpl = str(output_dir / "%(title)s.%(ext)s")
        ydl_opts = {
            "outtmpl": outtmpl,
            "noprogress": False,
            "quiet": not verbose,
            "no_warnings": True,
            "continuedl": True,  # resume
        }
        if format_selector:
            ydl_opts["format"] = format_selector

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        filename = None
        if isinstance(info, dict):
            filename = info.get("_filename") or info.get("requested_downloads", [{}])[0].get("_filename")

        if filename:
            return Path(filename)
        return output_dir
    except Exception:
        # Fallback to yt-dlp executable
        exe = shutil.which("yt-dlp") or shutil.which("yt-dlp.exe") or Path("tools/portable/yt-dlp.exe")
        if not exe or not Path(exe).exists():
            raise RuntimeError("yt-dlp python package not installed and yt-dlp executable not found")

        cmd = [str(exe)]
        if format_selector:
            cmd += ["-f", format_selector]
        cmd += ["-o", str(output_dir / "%(title)s.%(ext)s"), url]

        subprocess.run(cmd, check=True)
        # Can't reliably determine filename here; return output_dir
        return output_dir


def download_file_direct(url: str, output_path: Path, headers: dict | None = None, chunk_size: int = 8192):
    """Download a direct URL with streaming. Supports simple resume using Range if file exists."""
    import httpx

    output_path = Path(output_path)
    temp_path = output_path.with_suffix(output_path.suffix + ".part")
    headers = headers or {}

    mode = "wb"
    resume_pos = 0
    if temp_path.exists():
        resume_pos = temp_path.stat().st_size
        headers = {**headers, "Range": f"bytes={resume_pos}-"}
        mode = "ab"

    with httpx.stream("GET", url, headers=headers, timeout=30.0) as r:
        r.raise_for_status()
        with open(temp_path, mode) as f:
            for chunk in r.iter_bytes(chunk_size):
                if chunk:
                    f.write(chunk)

    temp_path.replace(output_path)
    return output_path
