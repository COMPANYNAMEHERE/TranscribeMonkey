# utils.py
import os
import platform
import subprocess
from tkinter import messagebox

def open_output_folder(file_path):
    directory = os.path.dirname(os.path.abspath(file_path))
    try:
        if platform.system() == "Windows":
            os.startfile(directory)
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(["open", directory])
        else:  # Linux and others
            subprocess.Popen(["xdg-open", directory])
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open directory:\n{e}")

