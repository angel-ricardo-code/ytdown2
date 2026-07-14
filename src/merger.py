from pathlib import Path
import subprocess
import shutil


def _find_ffmpeg_executable() -> str | None:
    # Prefer ffmpeg on PATH
    exe = shutil.which("ffmpeg") or shutil.which("ffmpeg.exe")
    if exe:
        return exe
    
    # Check sys._MEIPASS for frozen exe (PyInstaller)
    import sys
    if hasattr(sys, '_MEIPASS'):
        base = Path(sys._MEIPASS)
        for ff in ["ffmpeg.exe", "tools/portable/ffmpeg/ffmpeg.exe"]:
            p = base / ff
            if p.exists():
                return str(p)
    
    # Fallback to tools/portable in current or parent dir
    for check in [Path("."), Path(".."), Path(__file__).parent]:
        portable = check / "tools" / "portable"
        candidates = list(portable.rglob("ffmpeg.exe")) if portable.exists() else []
        if candidates:
            return str(candidates[0])
    return None


def merge_streams(video_path: Path, audio_path: Path, output_path: Path, container: str = "mp4", audio_bitrate: str = "192k") -> Path:
    """Merge separate video and audio files into one container using ffmpeg.

    Re-encodes audio to AAC for compatibility with MP4 container.
    """
    ffmpeg_exe = _find_ffmpeg_executable()
    if not ffmpeg_exe:
        raise RuntimeError("ffmpeg not found: install ffmpeg or place ffmpeg.exe under tools/portable")

    cmd = [
        ffmpeg_exe,
        "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", audio_bitrate,
        "-shortest",
        str(output_path),
    ]
    proc = subprocess.run(cmd, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {proc.stderr.decode(errors='ignore')}")

    try:
        video_path.unlink()
        audio_path.unlink()
    except Exception:
        pass
    return output_path
