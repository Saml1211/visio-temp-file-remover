# Visio Temp File Remover GUI - v1.0.0

This initial release provides a standalone desktop application for finding and removing corrupted Visio temporary files.

## Highlights
- **Standalone Executable:** No installation needed, just run the `.exe` file.
- **Easy to Use:** A simple and intuitive graphical interface.
- **Powerful Scanning:** Quickly finds Visio temporary files in any directory.
- **Safe Deletion:** Review and select files before deleting them.

## Features
- Scan any directory for Visio temporary files (`~$*.vssx`).
- View file details: name, path, size, and last modified date.
- Select and delete multiple files at once.
- Confirmation prompt before deletion to prevent accidents.
- Built-in error handling and progress indicators.
- Uses PowerShell for robust file detection and removal.

## Installation and Usage
1.  Download the `VisioTempFileRemover.exe` file from the release assets.
2.  Run the application by double-clicking the `.exe` file.
3.  Alternatively, you can run from source by downloading the source code and running `run_gui.bat` or `python visio_gui.py`.
4.  Select a directory, scan for files, and delete the ones you want to remove.

## Requirements
- Windows OS
- Python 3.6+
- PowerShell
