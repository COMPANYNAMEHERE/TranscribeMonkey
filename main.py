# main.py
import tkinter as tk
from src.gui import TranscribeMonkeyGUI

def main():
    root = tk.Tk()
    app = TranscribeMonkeyGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

