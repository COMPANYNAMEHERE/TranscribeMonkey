"""Application entry point for TranscribeMonkey.

The original Tkinter GUI has been replaced by a Node.js/React frontend located
in the `gui` directory. This script now simply informs users how to launch the
new interface.
"""


def main():
    """Print instructions for starting the Node.js interface."""
    print(
        "TranscribeMonkey's GUI is now a Node.js/React app.\n"
        "Run `npm install` and `npm start` inside the `gui` directory to launch it."
    )


if __name__ == "__main__":
    main()
