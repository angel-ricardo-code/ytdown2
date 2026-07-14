import typer
from pathlib import Path
from rich.table import Table
from rich.console import Console

from src import extractor, downloader, utils
from src import gui as gui_module

app = typer.Typer(help="YouTubeFake downloader (prototype)")
console = Console()


@app.command()
def download(
    url: str = typer.Argument(..., help="Video URL to download"),
    format: str | None = typer.Option(None, "-f", "--format", help="Format selector (itag or 'best')"),
    output: Path = typer.Option(Path("downloads"), "-o", "--output", help="Output directory"),
    audio_only: bool = typer.Option(False, "--audio-only", help="Download only audio"),
    threads: int = typer.Option(4, "-t", "--threads"),
    verbose: bool = typer.Option(False, "-v", "--verbose"),
):
    """High level CLI. Uses yt-dlp as backend for reliability."""
    try:
        info = extractor.extract_info(url)
    except Exception as e:
        console.print(f"[red]Extraction failed:[/red] {e}")
        raise typer.Exit(code=1)

    table = Table(title=f"Formats for: {info.title}")
    table.add_column("format_id")
    table.add_column("ext")
    table.add_column("quality")
    table.add_column("resolution")
    table.add_column("filesize")
    for f in info.formats:
        res = f"{f.width}x{f.height}" if f.width and f.height else ""
        table.add_row(str(f.format_id), str(f.ext or ""), str(f.quality or ""), res, str(f.filesize or ""))

    console.print(table)

    # Select format
    chosen = format or "best"
    if audio_only:
        chosen = "bestaudio"

    console.print(f"Downloading [green]{info.title}[/green] with format '[bold]{chosen}[/bold]' to {output}\n")

    try:
        out = downloader.download_with_yt_dlp(url, output, format_selector=chosen, verbose=verbose)
        console.print(f"[green]Downloaded:[/green] {out}")
    except Exception as e:
        console.print(f"[red]Download failed:[/red] {e}")
        raise typer.Exit(code=2)


def _main():
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[red]Interrupción por el usuario. Saliendo...[/red]")


@app.command()
def gui_cmd():
    """Launch the Tkinter GUI (if available)."""
    # Import here to avoid Tkinter import at module import time for CLI-only users
    try:
        if getattr(gui_module, "tk", None) is None:
            console.print("[red]Tkinter not available in this environment.[/red]")
            raise typer.Exit(code=2)
        # Also write a small log file so we can diagnose invisible-window cases
        log_path = Path("gui_start.log")
        def log(msg: str):
            try:
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(msg + "\n")
            except Exception:
                pass

        console.print("Launching GUI...")
        log("Launching GUI...")

        try:
            root = gui_module.tk.Tk()
        except Exception as e:
            console.print(f"[red]Unable to create Tk root window:[/red] {e}")
            log(f"Unable to create Tk root window: {e}")
            raise typer.Exit(code=2)

        # Print some environment/debug info to help visibility in headless cases
        tk_ver = getattr(gui_module.tk, "TkVersion", None)
        tcl_ver = getattr(gui_module.tk, "TclVersion", None)
        console.print(f"tkinter version={tk_ver} tcl={tcl_ver}")
        log(f"tkinter version={tk_ver} tcl={tcl_ver}")
        try:
            sw = root.winfo_screenwidth()
            sh = root.winfo_screenheight()
            console.print(f"screen size={sw}x{sh}")
            log(f"screen size={sw}x{sh}")
        except Exception:
            console.print("screen size not available")
            log("screen size not available")

        app_ui = gui_module.App(master=root)

        # Try to ensure the window becomes visible and on top for a moment
        try:
            root.update()
            root.deiconify()
            root.lift()
            root.attributes("-topmost", True)
            root.update()
            # briefly keep topmost then clear so it doesn't stay above other apps
            root.after(500, lambda: root.attributes("-topmost", False))
            log("Performed topmost/deiconify/lift sequence")
        except Exception as e:
            log(f"Window focus/topmost sequence failed: {e}")

        console.print("Entering GUI mainloop (window should appear). Close the window to continue.")
        log("Entering GUI mainloop")
        root.mainloop()
        console.print("GUI mainloop exited")
        log("GUI mainloop exited")
    except Exception as e:
        console.print(f"[red]Failed to start GUI:[/red] {e}")
        raise typer.Exit(code=1)


@app.command(name="gui")
def gui():
    """Alias for gui-cmd: launch the Tkinter GUI."""
    return gui_cmd()
