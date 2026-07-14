from pathlib import Path
from typing import List
import threading

from . import extractor, downloader
from .models import VideoInfo, VideoFormat


class DownloadController:
    """Controller that performs extraction and download logic.

    Kept separate from the Tkinter UI so it can be tested without a display.
    """

    def extract_formats(self, url: str) -> List[str]:
        info = extractor.extract_info(url)
        # Return human friendly strings for each available format
        lines: List[str] = []
        for f in info.formats:
            res = f"{f.width}x{f.height}" if f.width and f.height else ""
            size = str(f.filesize) if f.filesize else ""
            lines.append(f"{f.format_id} | {f.ext or ''} | {f.quality or ''} | {res} | {size}")
        return lines

    def start_download(self, url: str, output_dir: Path, format_selector: str | None = None, verbose: bool = False) -> Path:
        # Delegate to downloader; this is synchronous and returns the Path
        return downloader.download_with_yt_dlp(url, output_dir, format_selector=format_selector, verbose=verbose)


try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox


    class App:
        def __init__(self, master=None, controller: DownloadController | None = None):
            self.master = master or tk.Tk()
            self.controller = controller or DownloadController()

            self.master.title("YouTubeFake Downloader")

            frm = ttk.Frame(self.master, padding=12)
            frm.grid(row=0, column=0, sticky="nsew")

            ttk.Label(frm, text="Video URL:").grid(row=0, column=0, sticky="w")
            self.url_var = tk.StringVar()
            ttk.Entry(frm, textvariable=self.url_var, width=60).grid(row=0, column=1, columnspan=3, sticky="ew")

            ttk.Button(frm, text="Fetch Formats", command=self.on_fetch).grid(row=0, column=4, sticky="e")

            ttk.Label(frm, text="Formats:").grid(row=1, column=0, sticky="nw")
            self.formats_list = tk.Listbox(frm, height=8, width=80)
            self.formats_list.grid(row=1, column=1, columnspan=4, sticky="ew")

            ttk.Label(frm, text="Output:").grid(row=2, column=0, sticky="w")
            self.output_var = tk.StringVar(value=str(Path("downloads")))
            ttk.Entry(frm, textvariable=self.output_var, width=50).grid(row=2, column=1, sticky="w")
            ttk.Button(frm, text="Browse", command=self.on_browse).grid(row=2, column=2, sticky="w")

            self.format_var = tk.StringVar(value="best")
            ttk.Label(frm, text="Format:").grid(row=3, column=0, sticky="w")
            ttk.Entry(frm, textvariable=self.format_var, width=20).grid(row=3, column=1, sticky="w")

            self.audio_only_var = tk.BooleanVar(value=False)
            ttk.Checkbutton(frm, text="Audio only", variable=self.audio_only_var).grid(row=3, column=2, sticky="w")

            self.verbose_var = tk.BooleanVar(value=False)
            ttk.Checkbutton(frm, text="Verbose", variable=self.verbose_var).grid(row=3, column=3, sticky="w")

            self.download_btn = ttk.Button(frm, text="Download", command=self.on_download)
            self.download_btn.grid(row=4, column=4, sticky="e")

            self.status = tk.StringVar(value="Idle")
            ttk.Label(frm, textvariable=self.status).grid(row=5, column=0, columnspan=5, sticky="w")

        def on_browse(self):
            path = filedialog.askdirectory(initialdir=self.output_var.get() or ".")
            if path:
                self.output_var.set(path)

        def on_fetch(self):
            url = self.url_var.get().strip()
            if not url:
                messagebox.showwarning("Input required", "Please enter a video URL")
                return
            try:
                self.status.set("Fetching formats...")
                lines = self.controller.extract_formats(url)
                self.formats_list.delete(0, tk.END)
                for l in lines:
                    self.formats_list.insert(tk.END, l)
                self.status.set(f"Found {len(lines)} formats")
            except Exception as e:
                messagebox.showerror("Error", str(e))
                self.status.set("Error fetching formats")

        def on_download(self):
            url = self.url_var.get().strip()
            if not url:
                messagebox.showwarning("Input required", "Please enter a video URL")
                return
            selected = self.formats_list.curselection()
            fmt = self.format_var.get() or None
            if selected:
                # extract format id from list entry like "22 | mp4 | ..."
                entry = self.formats_list.get(selected[0])
                fmt = entry.split("|")[0].strip()

            out = Path(self.output_var.get())
            verbose = bool(self.verbose_var.get())
            self.status.set("Starting download...")
            self.download_btn.config(state="disabled")

            def _run():
                try:
                    res = self.controller.start_download(url, out, format_selector=fmt, verbose=verbose)
                    messagebox.showinfo("Downloaded", f"Saved to: {res}")
                    self.status.set("Download complete")
                except Exception as e:
                    messagebox.showerror("Download failed", str(e))
                    self.status.set("Download failed")
                finally:
                    self.download_btn.config(state="normal")

            t = threading.Thread(target=_run, daemon=True)
            t.start()

except Exception:
    # If tkinter isn't available or fails to import (headless environments), avoid crashing on import.
    tk = None
