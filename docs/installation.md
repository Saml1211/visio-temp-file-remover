# Visio Temp File Remover GUI - Complete Installation Guide

## Overview
This guide will help you install and use the Visio Temp File Remover GUI application. This tool helps find and remove corrupted Visio temporary files that can cause errors in Microsoft Visio environments.

## System Requirements
- Windows operating system (Windows 10 or later recommended)
- PowerShell (included with Windows)

## Installation Options

### Option 1: Standalone Executable (Recommended)
1.  Download the `VisioTempFileRemover.exe` file from the latest release on GitHub.
2.  Save the file to a location of your choice.
3.  Double-click on `VisioTempFileRemover.exe` to start the application.

### Option 2: Running from Source
1.  Download and install Python from [python.org](https://www.python.org/downloads/) (version 3.6 or higher).
2.  During installation, make sure to check "Add Python to PATH".
3.  Download the source code from the GitHub repository (e.g., by cloning the repository or downloading the ZIP file).
4.  Open a command prompt in the root directory of the source code.
5.  Run `python visio_gui.py` to start the application.
6.  Alternatively, you can run `scripts/run_gui.bat` on Windows.

## Verifying Python Installation (for running from source)
To verify that Python is properly installed:

1. Open Command Prompt (cmd.exe)
2. Type: `python --version`
3. You should see output like: `Python 3.x.x`

If you get an error, you may need to:
- Reinstall Python and ensure "Add Python to PATH" is checked
- Restart your computer after installation

## Using the Application

### Starting the Application
- **Method 1 (Standalone):** Double-click on `VisioTempFileRemover.exe`
- **Method 2 (from Source):** Run `python visio_gui.py` from Command Prompt or double-click `scripts/run_gui.bat`.

### Main Interface
1. **Directory Selection**:
   - Enter the path to scan in the text box
   - Or click "Browse..." to select a directory using the file dialog

2. **Scanning for Files**:
   - Click "Scan for Files" to search for Visio temporary files
   - The application looks for files matching these patterns:
     - `~$*.vssx`
     - `~$*.vsdx`
     - `~$*.vstx`
     - `~$*.vsdm`
     - `~$*.vsd`

3. **Reviewing Results**:
   - Found files are displayed in the table
   - The table shows: File Name, Path (relative to scan directory), Size, and Last Modified date
   - Paths are shown relative to make them easier to read

4. **Deleting Files**:
   - Select one or more files by clicking on them (use Ctrl or Shift to select multiple)
   - Click "Delete Selected Files"
   - Confirm the deletion when prompted
   - The application will show how many files were successfully deleted

## Troubleshooting

### Common Issues

#### PowerShell Error Message
If you see a message about PowerShell not being available:
- Ensure PowerShell is enabled on your system
- Try running the application as Administrator

#### Files Not Found
If no files are found during scanning:
- Verify the directory path is correct
- Ensure the directory contains Visio temporary files
- Check that you have permission to access the directory

#### Permission Errors
If you get permission errors when deleting files:
- Try running the application as Administrator
- Ensure the files are not currently in use by another program
- Check that you have write permissions for the directory

#### Python Not Found (for running from source)
If you get an error that Python is not found:
- Reinstall Python and ensure "Add Python to PATH" is checked
- Restart your computer after installation
- Verify installation by running `python --version` in Command Prompt

### Running as Administrator
To run the application as Administrator:
1. Right-click on `VisioTempFileRemover.exe` or `scripts/run_gui.bat`
2. Select "Run as administrator"

## Security Notes
- This application only runs locally and does not connect to the internet
- It uses PowerShell scripts that are included in the package when running from source
- All file operations are performed on your local system
- The application only deletes files that match specific Visio temporary file patterns

## Updating the Application
To update to a new version:
1. Download the new `VisioTempFileRemover.exe` from the latest release.
2. Replace the old `.exe` file with the new one.

## Support
For issues not covered in this guide, please check:
- The main README.md file
- The GitHub repository issues page (if available)
