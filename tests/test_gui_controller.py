from pathlib import Path
import pytest

from src.gui import DownloadController


class DummyFormat:
    def __init__(self, format_id, ext=None, width=None, height=None, quality=None, filesize=None):
        self.format_id = format_id
        self.ext = ext
        self.width = width
        self.height = height
        self.quality = quality
        self.filesize = filesize


class DummyInfo:
    def __init__(self, formats):
        self.formats = formats


def test_extract_formats(monkeypatch):
    ctrl = DownloadController()

    def fake_extract_info(url):
        return DummyInfo([
            DummyFormat("22", ext="mp4", width=1280, height=720, quality="hd720", filesize=1024),
            DummyFormat("140", ext="m4a", width=None, height=None, quality="medium", filesize=512),
        ])

    monkeypatch.setattr("src.extractor.extract_info", fake_extract_info)

    lines = ctrl.extract_formats("https://example.com/watch?v=123")
    assert any("22" in l and "mp4" in l for l in lines)
    assert any("140" in l and "m4a" in l for l in lines)


def test_start_download_calls_downloader(monkeypatch, tmp_path):
    ctrl = DownloadController()

    def fake_download(url, output_dir, format_selector=None, verbose=False):
        # Verify arguments passed through
        assert url == "u"
        assert output_dir == tmp_path
        assert format_selector == "best"
        return tmp_path / "file.mp4"

    monkeypatch.setattr("src.downloader.download_with_yt_dlp", fake_download)

    out = ctrl.start_download("u", tmp_path, format_selector="best", verbose=False)
    assert out == tmp_path / "file.mp4"
