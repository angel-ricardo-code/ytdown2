import sys
import os
import json
import threading
import time
import re
import shutil
import tempfile
from pathlib import Path
from datetime import datetime

try:
    from playwright.sync_api import sync_playwright
except Exception:
    sync_playwright = None

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QComboBox, QPushButton, QProgressBar,
    QTextEdit, QLabel, QFileDialog, QMessageBox, QDialog
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont

import yt_dlp


C = {
    "BG_WINDOW": "#F2F2F7",
    "BG_INPUT": "#FFFFFF",
    "BORDER": "#E5E5EA",
    "BORDER_FOCUS": "#007AFF",
    "TEXT_MAIN": "#1C1C1E",
    "TEXT_SECONDARY": "#8E8E93",
    "ACCENT": "#007AFF",
    "ACCENT_HOVER": "#0051D5",
    "DARK": "#1C1C1E",
    "DARK_HOVER": "#000000",
    "SUCCESS": "#34C759",
    "WARNING": "#FF9500",
    "DANGER": "#FF3B30",
    "BG_COMBO_DROP": "#FFFFFF",
    "BORDER_COMBO": "#E5E5EA",
    "ITEM_HOVER": "#E5F2FF",
    "PROGRESS_BG": "#E5E5EA",
}


def get_video_info(url, cookiefile=None):
    opts = {"quiet": True, "no_warnings": True, "skip_download": True}
    if cookiefile:
        opts["cookiefile"] = cookiefile
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            fmts = []
            for f in info.get("formats", []):
                if f.get("format_id"):
                    res = f"{f.get('width','')}x{f.get('height','')}" if f.get("width") else ""
                    q = f.get("format_note") or res or f.get("ext") or ""
                    fmts.append({
                        "id": str(f.get("format_id")),
                        "quality": q,
                        "size": f.get("filesize") or f.get("filesize_approx") or 0,
                        "acodec": f.get("acodec", "none"),
                    })
            return info.get("title","Unknown"), fmts
    except Exception as e:
        return str(e), []


class Worker(QThread):
    progress = Signal(int, int, int, float)
    done = Signal(str)  # emits downloaded file path
    error = Signal(str)

    def __init__(self, url, fmt, out_dir, cookiefile=None, ffmpeg_path=None, custom_tmpl=None):
        super().__init__()
        self.url = url
        self.fmt = fmt
        self.out_dir = out_dir
        self.cookiefile = cookiefile
        self.ffmpeg_path = ffmpeg_path
        self.custom_tmpl = custom_tmpl
        self.pause_ev = threading.Event()
        self.stop_ev = threading.Event()
        self.pause_ev.set()
        self.paused = False

    def run(self):
        def hook(d):
            if self.stop_ev.is_set():
                raise Exception("stopped")
            while not self.pause_ev.is_set() and not self.stop_ev.is_set():
                time.sleep(0.25)
            if self.stop_ev.is_set():
                raise Exception("stopped")
            if d.get("status") == "downloading":
                tot = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                down = d.get("downloaded_bytes") or 0
                spd = d.get("speed") or 0
                if tot:
                    self.progress.emit(int((down/tot)*100), down, tot, spd)

        # Use custom template if provided, otherwise default
        if self.custom_tmpl:
            tmpl = str(self.out_dir / self.custom_tmpl)
        else:
            tmpl = str(self.out_dir / "%(title)s [%(format_id)s] [%(height)sp].%(ext)s")
        opts = {
            "format": self.fmt,
            "outtmpl": tmpl,
            "quiet": True,
            "no_warnings": True,
            "no_progress": True,
            "progress_hooks": [hook],
            "continuedl": True,
            "overwrites": True,
            "retries": 5,
            "fragment_retries": 5,
            "nocheckcertificate": True,
            "http_chunk_size": 1048576,
            "extractor_retries": 3,
            "skipUnavailableFragments": False,
        }
        if self.cookiefile:
            opts["cookiefile"] = self.cookiefile
        if self.ffmpeg_path:
            opts["ffmpeg_location"] = str(self.ffmpeg_path)

        try:
            import yt_dlp
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(self.url, download=True)
                filename = None
                if isinstance(info, dict):
                    filename = info.get("_filename")
                    if not filename:
                        req = info.get("requested_downloads", [])
                        if req:
                            filename = req[0].get("_filename")
                self.done.emit(filename or "")
        except Exception as e:
            self.error.emit(str(e))

    def pause(self):
        self.pause_ev.clear()
        self.paused = True

    def resume(self):
        self.pause_ev.set()
        self.paused = False

    def cancel(self):
        self.stop_ev.set()


class Fetcher(QThread):
    ready = Signal(str, list)
    fail = Signal(str)

    def __init__(self, url, cookiefile=None):
        super().__init__()
        self.url = url
        self.cookiefile = cookiefile

    def run(self):
        try:
            title, fmts = get_video_info(self.url, self.cookiefile)
            if fmts:
                self.ready.emit(title, fmts)
            else:
                self.fail.emit(title)
        except Exception as e:
            self.fail.emit(str(e))


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.audio_worker = None
        self.formats = []
        self.last_url = ""
        self.url = ""  # Current URL for downloads
        self.out_dir = Path.home() / "Downloads"
        self.cookies_file = None
        self.ffmpeg_path = None
        self.video_done = False
        self.audio_done = False
        self.video_title = ""
        self._video_base_name = ""
        self._current_height = 0
        self.video_file_path = None
        self.audio_file_path = None

        # Config paths
        self.config_dir = Path(os.getenv('APPDATA', str(Path.home()))) / 'YouTubeDownloader'
        self.config_file = self.config_dir / 'config.json'

        self.setWindowTitle("Downloader")
        self.setFixedSize(560, 720)
        self.setStyleSheet(f"background: {C['BG_WINDOW']};")
        self.move(200, 50)

        # Load config first
        self._load_config()
        self._build()
        self._detect_ffmpeg()

    def _load_config(self):
        """Load configuration from AppData"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Load saved paths
                if config.get('out_dir'):
                    self.out_dir = Path(config['out_dir'])
                if config.get('cookies_file'):
                    self.cookies_file = config['cookies_file']
                    
                print(f"[CONFIG] Loaded: out_dir={self.out_dir}, cookies={self.cookies_file}")
        except Exception as e:
            print(f"[CONFIG] Load error: {e}")

    def _save_config(self):
        """Save configuration to AppData"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            config = {
                'out_dir': str(self.out_dir),
                'cookies_file': self.cookies_file or "",
                'ffmpeg_path': str(self.ffmpeg_path) if self.ffmpeg_path else "",
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            print(f"[CONFIG] Saved")
        except Exception as e:
            print(f"[CONFIG] Save error: {e}")

    def _is_frozen(self):
        """Check if running as frozen exe"""
        return getattr(sys, 'frozen', False)

    def _get_base_path(self):
        """Get base path for frozen or dev mode"""
        if self._is_frozen():
            return Path(sys._MEIPASS)
        return Path.cwd()

    def _detect_ffmpeg(self):
        # First check config if already saved
        saved_ffmpeg = None
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    saved_ffmpeg = config.get('ffmpeg_path')
        except:
            pass
        
        # Check saved path first
        if saved_ffmpeg:
            p = Path(saved_ffmpeg) / 'ffmpeg.exe'
            if p.exists():
                self.ffmpeg_path = Path(saved_ffmpeg)
                self.ffmpeg_lbl.setText("FFmpeg: found (saved)")
                self.ffmpeg_lbl.setStyleSheet(f"color: {C['SUCCESS']}; font-size: 11px;")
                return
        
        # Check system PATH
        ff = shutil.which("ffmpeg")
        if ff:
            self.ffmpeg_path = Path(ff).parent
            self.ffmpeg_lbl.setText("FFmpeg: found")
            self.ffmpeg_lbl.setStyleSheet(f"color: {C['SUCCESS']}; font-size: 11px;")
            return
            
        # Check portable in base path (works for both dev and frozen)
        base = self._get_base_path()
        p = base / "tools" / "portable" / "ffmpeg" / "ffmpeg.exe"
        if p.exists():
            self.ffmpeg_path = p.parent
            self.ffmpeg_lbl.setText("FFmpeg: found")
            self.ffmpeg_lbl.setStyleSheet(f"color: {C['SUCCESS']}; font-size: 11px;")
            return
            
        # Check current directory fallback
        p = Path("tools/portable/ffmpeg/ffmpeg.exe")
        if p.exists():
            self.ffmpeg_path = p.parent
            self.ffmpeg_lbl.setText("FFmpeg: found")
            self.ffmpeg_lbl.setStyleSheet(f"color: {C['SUCCESS']}; font-size: 11px;")
            return
            
        # Not found
        self.ffmpeg_lbl.setText("FFmpeg: not found")
        self.ffmpeg_lbl.setStyleSheet(f"color: {C['TEXT_SECONDARY']}; font-size: 11px;")
        if ff:
            self.ffmpeg_path = Path(ff).parent
            self.ffmpeg_lbl.setText("FFmpeg: found")
            self.ffmpeg_lbl.setStyleSheet(f"color: {C['SUCCESS']}; font-size: 11px;")
        else:
            p = Path("tools/portable/ffmpeg/ffmpeg.exe")
            if p.exists():
                self.ffmpeg_path = p.parent
                self.ffmpeg_lbl.setText("FFmpeg: found")
                self.ffmpeg_lbl.setStyleSheet(f"color: {C['SUCCESS']}; font-size: 11px;")
            else:
                self.ffmpeg_lbl.setText("FFmpeg: not found")
                self.ffmpeg_lbl.setStyleSheet(f"color: {C['TEXT_SECONDARY']}; font-size: 11px;")

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(40, 36, 40, 36)
        lay.setSpacing(18)

        # [A] Title
        title = QLabel("Downloader")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setStyleSheet(f"color: {C['TEXT_MAIN']}; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignCenter)
        lay.addWidget(title)

        # [B] URL Input
        self.url_in = QLineEdit()
        self.url_in.setPlaceholderText("Paste URL here...")
        self.url_in.setFixedHeight(44)
        self.url_in.setFont(QFont("Segoe UI", 11))
        self.url_in.setStyleSheet(f"""
            background: {C['BG_INPUT']};
            border: 1.5px solid {C['BORDER']};
            border-radius: 10px;
            padding: 0 14px;
        """)
        self.url_in.textChanged.connect(self._fetch)
        lay.addWidget(self.url_in)

        # [C] Quality ComboBox
        self.quality = QComboBox()
        self.quality.addItem("Select quality...")
        self.quality.setFixedHeight(44)
        self.quality.setFont(QFont("Segoe UI", 11))
        self.quality.setStyleSheet(f"""
            background: {C['BG_INPUT']};
            border: 1.5px solid {C['BORDER']};
            border-radius: 10px;
            padding: 0 14px 0 14px;
        """)
        self.quality.setEnabled(False)
        self.quality.view().setStyleSheet(f"""
            QComboBoxPopup {{
                background: {C['BG_COMBO_DROP']};
                border: 1px solid {C['BORDER_COMBO']};
                border-radius: 10px;
                padding: 6px;
            }}
            QComboBoxListView {{
                background: {C['BG_COMBO_DROP']};
                border: none;
            }}
            QComboBoxListView::item {{
                min-height: 32px;
                border-radius: 6px;
                padding: 0 10px;
            }}
            QComboBoxListView::item:selected {{
                background: {C['ACCENT']};
                color: white;
            }}
            QComboBoxListView::item:hover {{
                background: {C['ITEM_HOVER']};
            }}
        """)
        lay.addWidget(self.quality)

        # [D] Save path row
        save_row = QHBoxLayout()
        save_row.setSpacing(10)
        self.folder_in = QLineEdit()
        self.folder_in.setFixedHeight(44)
        self.folder_in.setFont(QFont("Segoe UI", 11))
        self.folder_in.setReadOnly(True)
        self.folder_in.setText(str(self.out_dir))
        self.folder_in.setStyleSheet(f"""
            background: {C['BG_INPUT']};
            border: 1.5px solid {C['BORDER']};
            border-radius: 10px;
            padding: 0 14px;
        """)
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.setFixedHeight(36)
        self.browse_btn.setMinimumWidth(80)
        self.browse_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.browse_btn.setStyleSheet(f"""
            background: transparent;
            color: {C['ACCENT']};
            border: 1.5px solid {C['BORDER']};
            border-radius: 8px;
            padding: 0 16px;
        """)
        self.browse_btn.clicked.connect(self._browse)
        save_row.addWidget(self.folder_in, 1)
        save_row.addWidget(self.browse_btn)
        lay.addLayout(save_row)

        # [E] Cookies row
        cookies_row = QHBoxLayout()
        cookies_row.setSpacing(10)
        self.cookies_in = QLineEdit()
        self.cookies_in.setPlaceholderText("Cookies file (optional)")
        self.cookies_in.setFixedHeight(44)
        self.cookies_in.setFont(QFont("Segoe UI", 11))
        self.cookies_in.setStyleSheet(f"""
            background: {C['BG_INPUT']};
            border: 1.5px solid {C['BORDER']};
            border-radius: 10px;
            padding: 0 14px;
        """)
        self.cookies_btn = QPushButton("...")
        self.cookies_btn.setFixedSize(40, 44)
        self.cookies_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.cookies_btn.setStyleSheet(f"""
            background: transparent;
            color: {C['ACCENT']};
            border: 1.5px solid {C['BORDER']};
            border-radius: 8px;
        """)
        self.cookies_btn.clicked.connect(self._select_cookies)
        self.cookies_auto_btn = QPushButton("Auto")
        self.cookies_auto_btn.setFixedSize(50, 44)
        self.cookies_auto_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.cookies_auto_btn.setStyleSheet(f"""
            background: transparent;
            color: {C['ACCENT']};
            border: 1.5px solid {C['BORDER']};
            border-radius: 8px;
        """)
        self.cookies_auto_btn.clicked.connect(self._auto_cookies)
        cookies_row.addWidget(self.cookies_in, 1)
        cookies_row.addWidget(self.cookies_btn)
        cookies_row.addWidget(self.cookies_auto_btn)
        lay.addLayout(cookies_row)

        # [F] FFmpeg row
        ff_row = QHBoxLayout()
        ff_row.setSpacing(10)
        self.ffmpeg_lbl = QLabel("FFmpeg: not found")
        self.ffmpeg_lbl.setFont(QFont("Segoe UI", 11))
        self.ffmpeg_lbl.setStyleSheet(f"color: {C['TEXT_SECONDARY']};")
        self.ffmpeg_btn = QPushButton("Locate")
        self.ffmpeg_btn.setFixedHeight(36)
        self.ffmpeg_btn.setMinimumWidth(80)
        self.ffmpeg_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.ffmpeg_btn.setStyleSheet(f"""
            background: transparent;
            color: {C['ACCENT']};
            border: 1.5px solid {C['BORDER']};
            border-radius: 8px;
            padding: 0 16px;
        """)
        self.ffmpeg_btn.clicked.connect(self._locate_ffmpeg)
        ff_row.addWidget(self.ffmpeg_lbl, 1)
        ff_row.addWidget(self.ffmpeg_btn)
        lay.addLayout(ff_row)

        # [G] Paste button
        self.paste_btn = QPushButton("Paste from clipboard")
        self.paste_btn.setFixedHeight(48)
        self.paste_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.paste_btn.setStyleSheet(f"""
            background: {C['DARK']};
            color: white;
            border-radius: 12px;
        """)
        self.paste_btn.clicked.connect(self._paste)
        lay.addWidget(self.paste_btn)

        # [I] Progress section (hidden initially)
        self.progress_widget = QWidget()
        self.progress_widget.setVisible(False)
        self.progress_widget.setStyleSheet("background: transparent;")
        pl = QVBoxLayout(self.progress_widget)
        pl.setContentsMargins(0, 0, 0, 0)
        pl.setSpacing(12)

        self.bar = QProgressBar()
        self.bar.setFixedHeight(5)
        self.bar.setTextVisible(False)
        self.bar.setRange(0, 100)
        self.bar.setStyleSheet(f"""
            QProgressBar {{
                background: {C['PROGRESS_BG']};
                border-radius: 3px;
                border-width: 0;
            }}
            QProgressBar::chunk {{
                background: {C['ACCENT']};
                border-radius: 3px;
            }}
        """)
        pl.addWidget(self.bar)

        meta = QHBoxLayout()
        meta.setSpacing(20)
        self.speed_lbl = QLabel("--")
        self.speed_lbl.setFont(QFont("Consolas", 12, QFont.Medium))
        self.speed_lbl.setStyleSheet(f"color: {C['TEXT_MAIN']};")
        self.size_lbl = QLabel("--")
        self.size_lbl.setFont(QFont("Consolas", 12))
        self.size_lbl.setStyleSheet(f"color: {C['TEXT_SECONDARY']};")
        self.eta_lbl = QLabel("ETA --")
        self.eta_lbl.setFont(QFont("Consolas", 12))
        self.eta_lbl.setStyleSheet(f"color: {C['TEXT_SECONDARY']};")
        self.status_lbl = QLabel("Starting...")
        self.status_lbl.setFont(QFont("Segoe UI", 11))
        self.status_lbl.setStyleSheet(f"color: {C['ACCENT']};")
        self.status_lbl.setAlignment(Qt.AlignRight)
        meta.addWidget(self.speed_lbl)
        meta.addWidget(self.size_lbl)
        meta.addWidget(self.eta_lbl)
        meta.addWidget(self.status_lbl, 1)
        pl.addLayout(meta)

        ctrl = QHBoxLayout()
        ctrl.setSpacing(12)
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.setFixedHeight(36)
        self.pause_btn.setMinimumWidth(90)
        self.pause_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.pause_btn.setStyleSheet(f"""
            background: transparent;
            color: {C['ACCENT']};
            border: 1.5px solid {C['BORDER']};
            border-radius: 8px;
        """)
        self.pause_btn.clicked.connect(self._toggle_pause)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setFixedHeight(36)
        self.cancel_btn.setMinimumWidth(90)
        self.cancel_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.cancel_btn.setStyleSheet(f"""
            background: transparent;
            color: {C['DANGER']};
            border: 1.5px solid {C['DANGER']};
            border-radius: 8px;
        """)
        self.cancel_btn.clicked.connect(self._cancel_dl)
        ctrl.addWidget(self.pause_btn)
        ctrl.addWidget(self.cancel_btn)
        ctrl.addStretch(1)
        pl.addLayout(ctrl)

        lay.addWidget(self.progress_widget)

        # Spacer
        lay.addStretch(1)

        # [H] Download button
        self.download_btn = QPushButton("Download")
        self.download_btn.setFixedHeight(48)
        self.download_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.download_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C['ACCENT']};
                color: white;
                border-radius: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {C['ACCENT_HOVER']};
            }}
            QPushButton:disabled {{
                background: #C7C7CC;
                color: white;
            }}
        """)
        self.download_btn.clicked.connect(self._download)
        self.download_btn.setEnabled(False)
        lay.addWidget(self.download_btn)

        # [H] Merge button
        self.merge_btn = QPushButton("Merge Archivos")
        self.merge_btn.setFixedHeight(44)
        self.merge_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C['BG_INPUT']};
                border: 1px solid {C['BORDER']};
                border-radius: 10px;
            }}
            QPushButton:hover {{
                border-color: {C['ACCENT']};
                color: {C['ACCENT']};
            }}
        """)
        self.merge_btn.clicked.connect(self._open_merge_dialog)
        lay.addWidget(self.merge_btn)

        # Footer
        footer = QLabel("yt-dlp powered")
        footer.setFont(QFont("Segoe UI", 9))
        footer.setStyleSheet(f"color: {C['TEXT_SECONDARY']}; margin-top: 14px;")
        footer.setAlignment(Qt.AlignCenter)
        lay.addWidget(footer)

    def _paste(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if text and text.startswith("http"):
            self.url_in.setText(text)

    def _fetch(self):
        url = self.url_in.text().strip()
        if not url or url == self.last_url or not url.startswith("http"):
            return
        self.last_url = url
        self.quality.setCurrentText("Loading...")
        self.quality.setEnabled(False)
        self.download_btn.setEnabled(False)

        if hasattr(self, 'fetcher') and self.fetcher and self.fetcher.isRunning():
            return
        self.fetcher = Fetcher(url, self.cookies_file)
        self.fetcher.ready.connect(self._on_ready)
        self.fetcher.fail.connect(self._on_fail)
        self.fetcher.start()

    def _on_ready(self, title, fmts):
        self.formats = fmts
        self.video_title = title
        self.quality.clear()
        self.quality.addItem("Best quality")
        for idx, f in enumerate(fmts):
            mb = f["size"] / (1024*1024) if f["size"] else 0
            tag = "[VIDEO] " if f.get("acodec") == "none" else ""
            txt = tag + f["quality"] + (f" ({mb:.0f}MB)" if mb else "")
            self.quality.addItem(txt)
            self.quality.setItemData(idx + 1, f["id"])
            print(f"[DEBUG] Item {idx}: '{txt}' -> format_id={f['id']}")
        self.quality.setEnabled(True)
        self.download_btn.setEnabled(True)

    def _on_fail(self, msg):
        self.quality.clear()
        self.quality.addItem("Error")
        QMessageBox.warning(self, "Error", msg)

    def _browse(self):
        d = QFileDialog.getExistingDirectory(self, "Save location", str(self.out_dir))
        if d:
            self.out_dir = Path(d)
            self.folder_in.setText(d)
            self._save_config()

    def _select_cookies(self):
        d, _ = QFileDialog.getOpenFileName(self, "Cookies file", str(Path.home() / "Downloads"), "Cookies (*.txt)")
        if d:
            self.cookies_file = d
            self._save_config()
            self.cookies_in.setText(Path(d).name)

    def _auto_cookies(self):
        if sync_playwright is None:
            QMessageBox.warning(self, "Warning", "Playwright not installed. Run: pip install playwright")
            return
        url = self.url_in.text().strip()
        if not url:
            QMessageBox.warning(self, "Warning", "Enter a URL first")
            return
        self.status_lbl.setText("Opening browser...")
        QApplication.processEvents()
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)
                context = browser.new_context()
                page = context.new_page()
                page.goto(url, wait_until="networkidle", timeout=60000)
                page.wait_for_timeout(2000)
                cookies = context.cookies()
                browser.close()
            if not cookies:
                QMessageBox.warning(self, "Warning", "No cookies found")
                return
            tf = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w")
            tf.write("# Netscape HTTP Cookie File\n")
            for c in cookies:
                domain = c.get("domain", "")
                flag = "TRUE" if domain.startswith(".") else "FALSE"
                path = c.get("path", "/")
                secure = "TRUE" if c.get("secure") else "FALSE"
                expires = str(int(c.get("expires", 0)))
                name = c.get("name", "")
                value = c.get("value", "")
                tf.write(f"{domain}\t{flag}\t{path}\t{secure}\t{expires}\t{name}\t{value}\n")
            tf.close()
            self.cookies_file = tf.name
            self.cookies_in.setText(Path(tf.name).name)
            self.status_lbl.setText("Cookies obtained")
            self.status_lbl.setStyleSheet(f"color: {C['SUCCESS']};")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to get cookies: {e}")

    def _locate_ffmpeg(self):
        d = QFileDialog.getExistingDirectory(self, "FFmpeg folder", str(Path.cwd() / "tools"))
        if d:
            p = Path(d) / "ffmpeg.exe"
            if p.exists():
                self.ffmpeg_path = Path(d)
                self.ffmpeg_lbl.setText("FFmpeg: found")
                self.ffmpeg_lbl.setStyleSheet(f"color: {C['SUCCESS']}; font-size: 11px;")
                self._save_config()

    def _download(self):
        url = self.url_in.text().strip()
        if not url:
            QMessageBox.warning(self, "Warning", "Enter a URL first")
            return

        idx = self.quality.currentIndex()
        fmt_id = self.quality.currentData()
        txt = self.quality.currentText()
        print(f"[DEBUG] currentIndex={idx}, currentData={fmt_id}, currentText={txt}")
        
        # Check if it's a video-only format (marked with [VIDEO])
        is_video_only = "[VIDEO]" in txt
        print(f"[DEBUG] is_video_only: {is_video_only}")
        
        if is_video_only:
            # For video-only, we need to download video + audio separately
            # Known YouTube audio format IDs
            audio_format_ids = {"139", "140", "249", "251", "250", "171", "172"}
            audio_fmt_id = None
            
            # First try by format ID (most reliable)
            for f in self.formats:
                fid = str(f.get("id"))
                if fid in audio_format_ids:
                    audio_fmt_id = fid
                    print(f"[DEBUG] Found audio format by ID: {fid}")
                    break
            
            # Fallback: look for audio by extension or no video codec
            if not audio_fmt_id:
                for f in self.formats:
                    ext = f.get("ext", "")
                    if f.get("vcodec") == "none" and ext in ("m4a", "mp3", "webm"):
                        audio_fmt_id = str(f.get("id"))
                        print(f"[DEBUG] Found audio format by ext: {audio_fmt_id}")
                        break
            
            if audio_fmt_id:
                # Start two downloads: video + audio
                video_fmt = str(fmt_id)
                audio_fmt = audio_fmt_id
                
                # Save URL for audio worker
                self.url = url
                
                self.progress_widget.setVisible(True)
                self.bar.setValue(0)
                self.speed_lbl.setText("--")
                self.size_lbl.setText("--")
                self.eta_lbl.setText("ETA --")
                self.status_lbl.setText(f"Downloading video({video_fmt}) + audio({audio_fmt})...")
                self.download_btn.setEnabled(False)
                self.video_done = False
                self.audio_done = False
                self.video_file_path = None
                self.audio_file_path = None
                
                # Same base name for both files
                base_file = "%(title)s [%(height)sp]"
                self._video_base_name = f"{self.video_title} [{self._current_height}p]" if self.video_title else base_file
                
                # Video worker
                self.worker = Worker(url, video_fmt, self.out_dir, self.cookies_file, self.ffmpeg_path, f"{base_file}.%(ext)s")
                self.worker.progress.connect(self._on_progress)
                self.worker.done.connect(self._on_video_done)
                self.worker.error.connect(self._on_error)
                self.worker.start()
                
                # Audio worker with matching name
                self.audio_worker = Worker(url, audio_fmt, self.out_dir, self.cookies_file, self.ffmpeg_path, f"{base_file}.%(ext)s")
                self.audio_worker.progress.connect(self._on_audio_progress)
                self.audio_worker.done.connect(self._on_audio_done)
                self.audio_worker.error.connect(self._on_audio_error)
                QTimer.singleShot(1500, self.audio_worker.start)
            else:
                # No audio found, download video only
                fmt = str(fmt_id)
                print(f"[DEBUG] No audio found, downloading video only: {fmt}")
                self._start_download(fmt)
        elif fmt_id:
            # For combined formats, use height-based selection  
            import re
            m = re.search(r"(\d+)p", txt)
            height = int(m.group(1)) if m else 0
            self._current_height = height
            print(f"[DEBUG] Height: {height}")
            
            if height >= 720:
                fmt = f"bestvideo[height={height}]+bestaudio/best[height={height}]/best"
                print(f"[DEBUG] Requesting HD combined: {fmt}")
            else:
                fmt = str(fmt_id)
                print(f"[DEBUG] Using SD format: {fmt}")
            self._start_download(fmt)
        else:
            self._start_download("best")

    def _start_download(self, fmt):
        """Helper to start a download"""
        url = self.url_in.text().strip()
        if not url:
            QMessageBox.warning(self, "Warning", "Enter a URL first")
            return
        
        self.progress_widget.setVisible(True)
        self.bar.setValue(0)
        self.speed_lbl.setText("--")
        self.size_lbl.setText("--")
        self.eta_lbl.setText("ETA --")
        self.status_lbl.setText("Starting...")
        self.download_btn.setEnabled(False)
        
        self.worker = Worker(url, fmt, self.out_dir, self.cookies_file, self.ffmpeg_path)
        self.worker.progress.connect(self._on_progress)
        self.worker.done.connect(self._on_done)
        self.worker.error.connect(self._on_error)
        self.worker.start()

        self.progress_widget.setVisible(True)
        self.bar.setValue(0)
        self.speed_lbl.setText("--")
        self.size_lbl.setText("--")
        self.eta_lbl.setText("ETA --")
        self.status_lbl.setText("Starting...")
        self.status_lbl.setStyleSheet(f"color: {C['ACCENT']};")
        self.pause_btn.setText("Pause")
        self.download_btn.setEnabled(False)

        self.worker = Worker(url, fmt, self.out_dir, self.cookies_file, self.ffmpeg_path)
        self.worker.progress.connect(self._on_progress)
        self.worker.done.connect(self._on_done)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_progress(self, pct, down, total, spd):
        self.bar.setValue(pct)
        self.status_lbl.setText("Downloading...")
        mb_s = spd / (1024*1024) if spd else 0
        self.speed_lbl.setText(f"{mb_s:.1f} MB/s" if mb_s else "--")
        tot_mb = total / (1024*1024) if total else 0
        self.size_lbl.setText(f"{tot_mb:.0f} MB" if tot_mb else "--")
        if spd and total:
            remaining_bytes = total - down
            eta_seconds = remaining_bytes / spd
            eta_min = int(eta_seconds // 60)
            eta_sec = int(eta_seconds % 60)
            self.eta_lbl.setText(f"ETA {eta_min:02d}:{eta_sec:02d}")
        else:
            self.eta_lbl.setText("ETA --")

    def _on_done(self, filename):
        self.progress_widget.setVisible(False)
        self.download_btn.setEnabled(True)
        self.status_lbl.setText("Completed")
        self.status_lbl.setStyleSheet(f"color: {C['SUCCESS']};")
        name = Path(filename).name if filename else "video"
        QMessageBox.information(self, "Done", f"Downloaded: {name}")

    def _on_error(self, msg):
        self.progress_widget.setVisible(False)
        self.download_btn.setEnabled(True)
        self.status_lbl.setText("Error")
        self.status_lbl.setStyleSheet(f"color: {C['DANGER']};")
        QMessageBox.critical(self, "Error", msg)

    def _on_video_done(self, filename):
        """Called when video download completes"""
        self.video_done = True
        self.video_file_path = Path(filename) if filename else None
        print(f"[DEBUG] Video done: {filename}")
        # Check if audio also done
        if self.audio_done:
            self._on_both_done()

    def _on_audio_progress(self, pct, down, total, spd):
        """Progress for audio download"""
        # Just show audio progress in status
        self.status_lbl.setText(f"Video: {self.bar.value()}% | Audio: {pct}%")

    def _on_audio_done(self, filename):
        """Called when audio download completes"""
        self.audio_done = True
        self.audio_file_path = Path(filename) if filename else None
        print(f"[DEBUG] Audio done: {filename}")
        # Check if video also done
        if self.video_done:
            self._on_both_done()

    def _on_audio_error(self, msg):
        """Error in audio download"""
        print(f"[DEBUG] Audio error: {msg}")
        # Continue even if audio fails - video might still work

    def _on_both_done(self):
        self.progress_widget.setVisible(False)
        self.download_btn.setEnabled(True)
        self.status_lbl.setText("Merging video + audio...")
        self.status_lbl.setStyleSheet(f"color: {C['ACCENT']};")

        vf = self.video_file_path
        af = self.audio_file_path

        if vf and af and vf.exists() and af.exists():
            try:
                from src.merger import merge_streams
                output = vf.parent / f"{vf.stem.replace(' [merged]', '')} [merged].mp4"
                merge_streams(vf, af, output, "mp4")
                self.status_lbl.setText(f"Done: {output.name}")
                self.status_lbl.setStyleSheet(f"color: {C['SUCCESS']};")
                QMessageBox.information(self, "Done", f"Downloaded and merged!\n\n{output.name}")
            except Exception as e:
                self.status_lbl.setText("Merge failed")
                self.status_lbl.setStyleSheet(f"color: {C['DANGER']};")
                QMessageBox.warning(self, "Merge Failed", f"Downloaded but merge failed:\n{e}")
        else:
            self.status_lbl.setText("Completed - files saved separately")
            self.status_lbl.setStyleSheet(f"color: {C['SUCCESS']};")
            QMessageBox.information(self, "Done", "Video and audio downloaded separately.")

    def _toggle_pause(self):
        if not self.worker:
            return
        if self.worker.paused:
            self.worker.resume()
            self.pause_btn.setText("Pause")
            self.status_lbl.setText("Resuming...")
            self.status_lbl.setStyleSheet(f"color: {C['ACCENT']};")
        else:
            self.worker.pause()
            self.pause_btn.setText("Resume")
            self.status_lbl.setText("Paused")
            self.status_lbl.setStyleSheet(f"color: {C['WARNING']};")

    def _open_merge_dialog(self):
        d = MergeDialog(self)
        d.exec()

    def _cancel_dl(self):
        if self.worker:
            self.worker.cancel()
        self.progress_widget.setVisible(False)
        self.download_btn.setEnabled(True)


class MergeThread(QThread):
    progress = Signal(int)
    done = Signal()
    error = Signal(str)

    def __init__(self, video_path, audio_path, output_path, bitrate="192k"):
        super().__init__()
        self.video = video_path
        self.audio = audio_path
        self.output = output_path
        self.bitrate = bitrate

    def run(self):
        try:
            from src.manual_merge import manual_merge
            manual_merge(self.video, self.audio, self.output, self.bitrate, delete_originals=False)
            self.done.emit()
        except Exception as e:
            self.error.emit(str(e))


class MergeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.video_path = None
        self.audio_path = None
        self.output_path = None
        self._build()

    def _build(self):
        self.setWindowTitle("Merge Video + Audio")
        self.setFixedSize(520, 320)
        self.setModal(True)
        self.setStyleSheet(f"background: {C['BG_WINDOW']};")

        layout = QVBoxLayout()
        layout.setSpacing(18)
        layout.setContentsMargins(40, 30, 40, 30)

        self.video_edit = QLineEdit()
        self.video_edit.setFixedHeight(44)
        self.video_edit.setReadOnly(True)
        self.video_edit.setStyleSheet(f"background: {C['BG_INPUT']}; border: 1px solid {C['BORDER']}; border-radius: 10px; padding: 0 12px;")

        self.audio_edit = QLineEdit()
        self.audio_edit.setFixedHeight(44)
        self.audio_edit.setReadOnly(True)
        self.audio_edit.setStyleSheet(f"background: {C['BG_INPUT']}; border: 1px solid {C['BORDER']}; border-radius: 10px; padding: 0 12px;")

        self.output_edit = QLineEdit()
        self.output_edit.setFixedHeight(44)
        self.output_edit.setReadOnly(True)
        self.output_edit.setStyleSheet(f"background: {C['BG_INPUT']}; border: 1px solid {C['BORDER']}; border-radius: 10px; padding: 0 12px;")

        self.bitrate_combo = QComboBox()
        self.bitrate_combo.addItems(["128k", "192k", "256k", "320k"])
        self.bitrate_combo.setCurrentText("192k")
        self.bitrate_combo.setFixedWidth(100)

        self.delete_check = QPushButton("Eliminar archivos originales")
        self.delete_check.setCheckable(True)
        self.delete_check.setFixedHeight(36)
        self.delete_check.setStyleSheet("""
            QPushButton { border: none; text-align: left; padding-left: 0; }
            QPushButton:checked { color: #34C759; }
        """)

        self.status = QLabel("")
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setStyleSheet(f"color: {C['TEXT_SECONDARY']};")

        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.setFixedHeight(48)
        self.cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C['BG_INPUT']};
                border: 1px solid {C['BORDER']};
                border-radius: 12px;
                font-weight: medium;
            }}
            QPushButton:hover {{ background: {C['BORDER']}; }}
        """)

        self.merge_btn = QPushButton("Merge")
        self.merge_btn.setFixedHeight(48)
        self.merge_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C['ACCENT']};
                color: white;
                border-radius: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background: {C['ACCENT_HOVER']}; }}
            QPushButton:disabled {{ background: {C['BORDER']}; }}
        """)

        def browse(edit, attr, filter_):
            path, _ = QFileDialog.getOpenFileName(self, filter_, self.video_edit.text() or str(Path.home()))
            if path:
                setattr(self, attr, Path(path))
                edit.setText(path)
                if not self.output_edit.text() and attr == "video_path":
                    vp = Path(path)
                    self.output_edit.setText(str(vp.parent / f"{vp.stem} [merged].mp4"))

        def browse_video():
            browse(self.video_edit, "video_path", "Seleccionar Video")

        def browse_audio():
            browse(self.audio_edit, "audio_path", "Seleccionar Audio")

        def browse_output():
            path, _ = QFileDialog.getSaveFileName(self, "Guardar como", self.output_edit.text() or str(Path.home() / "merged.mp4"), "MP4 (*.mp4)")
            if path:
                self.output_path = Path(path)
                self.output_edit.setText(path)

        for label, edit in [("Video:", self.video_edit), ("Audio:", self.audio_edit), ("Output:", self.output_edit)]:
            lbl = QLabel(label)
            lbl.setStyleSheet(f"font-weight: medium; color: {C['TEXT_MAIN']};")
            layout.addWidget(lbl)
            row = QHBoxLayout()
            row.addWidget(edit)
            btn = QPushButton("📁")
            btn.setFixedSize(44, 44)
            if label == "Video:":
                btn.clicked.connect(browse_video)
            elif label == "Audio:":
                btn.clicked.connect(browse_audio)
            else:
                btn.clicked.connect(browse_output)
            row.addWidget(btn)
            layout.addLayout(row)

        bitrate_row = QHBoxLayout()
        bitrate_row.addWidget(QLabel("Audio:"))
        bitrate_row.addWidget(self.bitrate_combo)
        bitrate_row.addStretch()
        layout.addLayout(bitrate_row)

        layout.addWidget(self.delete_check)
        layout.addWidget(self.status)

        btn_row = QHBoxLayout()
        btn_row.addWidget(self.cancel_btn)
        btn_row.addStretch()
        btn_row.addWidget(self.merge_btn)
        layout.addLayout(btn_row)

        self.setLayout(layout)

        self.cancel_btn.clicked.connect(self.reject)
        self.merge_btn.clicked.connect(self._on_merge)

    def _on_merge(self):
        if not self.video_path or not self.audio_path:
            QMessageBox.warning(self, "Error", "Selecciona video y audio")
            return

        if not self.output_path:
            self.output_path = self.video_path.parent / f"{self.video_path.stem} [merged].mp4"

        bitrate = self.bitrate_combo.currentText()
        self.status.setText("Merging...")
        self.merge_btn.setEnabled(False)

        self.thread = MergeThread(self.video_path, self.audio_path, self.output_path, bitrate)
        self.thread.done.connect(self._on_done)
        self.thread.error.connect(self._on_error)
        self.thread.start()

    def _on_done(self):
        if self.delete_check.isChecked():
            try:
                self.video_path.unlink()
                self.audio_path.unlink()
            except:
                pass
        self.status.setText("✓ Merge completado!")
        self.status.setStyleSheet(f"color: {C['SUCCESS']};")
        QTimer.singleShot(1500, self.accept)

    def _on_error(self, msg):
        self.status.setText("Error en merge")
        self.status.setStyleSheet(f"color: {C['DANGER']};")
        self.merge_btn.setEnabled(True)
        QMessageBox.critical(self, "Error", msg)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 11))
    w = App()
    w.show()
    sys.exit(app.exec())