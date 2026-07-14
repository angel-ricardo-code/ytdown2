import builtins
import pytest
from src import extractor


def test_extract_info_missing_yt_dlp(monkeypatch):
    """If yt-dlp is not installed, extractor.extract_info should raise RuntimeError."""
    orig_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "yt_dlp":
            raise ImportError("No module named yt_dlp")
        return orig_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    with pytest.raises(RuntimeError):
        extractor.extract_info("https://example.com/nonexistent")
