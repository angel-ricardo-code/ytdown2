from typing import Dict
from pathlib import Path
from .models import VideoInfo, VideoFormat
from .exceptions import VideoUnavailable, AgeRestrictedError


def extract_info(url: str, headers: Dict | None = None) -> VideoInfo:
    """Extract metadata from a video URL using yt-dlp as the extractor backend.

    This is a pragmatic implementation that delegates the heavy lifting to
    yt-dlp. The returned object normalizes fields used by the rest of the tool.
    """
    # Prefer using the yt-dlp Python package when available. Only fall back to
    # the yt-dlp executable if the package import itself fails.
    try:
        import yt_dlp
    except ImportError:
        # Fallback to calling yt-dlp.exe if available
        import shutil
        import subprocess
        import json

        exe = shutil.which("yt-dlp") or shutil.which("yt-dlp.exe") or Path("tools/portable/yt-dlp.exe")
        if not exe or not Path(exe).exists():
            raise RuntimeError("yt-dlp python package not installed and yt-dlp executable not found")

        # Use yt-dlp --dump-json to get info as JSON
        try:
            res = subprocess.run([str(exe), "--dump-json", url], capture_output=True, text=True, check=True)
            info = json.loads(res.stdout)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"yt-dlp executable failed: {e.stderr}") from e
    else:
        # Use the package; let extraction errors propagate to the caller so they
        # can be handled (e.g., video unavailable, network errors).
        ydl_opts = {"skip_download": True, "quiet": True, "no_warnings": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

    if info is None:
        raise VideoUnavailable("No information could be extracted")

    if info.get("age_limit", 0) >= 18:
        # Not a perfect check; callers may handle auth separately
        raise AgeRestrictedError("Content appears age restricted")

    def _to_int(value):
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    formats = []
    for f in info.get("formats", []):
        vf = VideoFormat(
            format_id=str(f.get("format_id")),
            ext=f.get("ext"),
            url=f.get("url"),
            mimeType=f.get("mime_type"),
            bitrate=_to_int(f.get("tbr") or f.get("abr") or f.get("vbr")),
            width=f.get("width"),
            height=f.get("height"),
            quality=f.get("format_note") or f.get("quality"),
            acodec=f.get("acodec"),
            vcodec=f.get("vcodec"),
            filesize=_to_int(f.get("filesize") or f.get("filesize_approx")),
        )
        formats.append(vf)

    video_info = VideoInfo(
        video_id=info.get("id") or info.get("webpage_url"),
        title=info.get("title", "untitled"),
        uploader=info.get("uploader"),
        duration=info.get("duration"),
        formats=formats,
    )
    return video_info
