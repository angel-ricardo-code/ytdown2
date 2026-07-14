import sys
try:
    import tkinter as tk
    print('py', sys.version.split()[0])
    print('executable', sys.executable)
    print('tk', tk.TkVersion, 'tcl', tk.TclVersion)
    r = tk.Tk()
    print('created')
    r.update()
    r.destroy()
    print('destroyed')
except Exception as e:
    print('ERROR:', repr(e))
    sys.exit(1)
