from pathlib import Path
import subprocess
import shutil
from PySide6.QtCore import QThread, Signal


def _find_ffmpeg_executable() -> str | None:
    exe = shutil.which("ffmpeg") or shutil.which("ffmpeg.exe")
    if exe:
        return exe
    
    import sys
    if hasattr(sys, '_MEIPASS'):
        base = Path(sys._MEIPASS)
        for ff in ["ffmpeg.exe", "tools/portable/ffmpeg/ffmpeg.exe"]:
            p = base / ff
            if p.exists():
                return str(p)
    
    for check in [Path("."), Path(".."), Path(__file__).parent]:
        portable = check / "tools" / "portable"
        candidates = list(portable.rglob("ffmpeg.exe")) if portable.exists() else []
        if candidates:
            return str(candidates[0])
    return None


def manual_merge(video_path: Path, audio_path: Path, output_path: Path, audio_bitrate: str = "192k", delete_originals: bool = False) -> Path:
    """Merge video + audio with re-encode to AAC."""
    ffmpeg_exe = _find_ffmpeg_executable()
    if not ffmpeg_exe:
        raise RuntimeError("ffmpeg not found")

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

    if delete_originals:
        try:
            video_path.unlink()
            audio_path.unlink()
        except Exception:
            pass
    
    return output_path


class MergeThread(QThread):
    progress = Signal(int)
    done = Signal()
    error = Signal(str)

    def __init__(self, video_path: Path, audio_path: Path, output_path: Path, bitrate: str = "192k"):
        super().__init__()
        self.video = video_path
        self.audio = audio_path
        self.output = output_path
        self.bitrate = bitrate

    def run(self):
        try:
            manual_merge(self.video, self.audio, self.output, self.bitrate, delete_originals=False)
            self.done.emit()
        except Exception as e:
            self.error.emit(str(e))