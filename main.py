"""Application entry point for TranscribeMonkey."""

import tkinter as tk
from gui import TranscribeMonkeyGUI

def main():
    root = tk.Tk()
    app = TranscribeMonkeyGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

