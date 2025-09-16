# Visio Temp File Remover GUI Setup

This script will help you create a standalone executable for the Visio Temp File Remover GUI.

## Requirements

1. Python 3.6 or higher
2. pip (Python package installer)

## Installation Steps

1. Install the required Python packages:
   ```
   pip install pyinstaller
   ```

2. Create the standalone executable:
   ```
   pyinstaller --onefile --windowed --name "VisioTempFileRemover" --add-data "scripts;scripts" visio_gui.py
   ```

3. The executable will be created in the `dist` folder

## Running the Executable

After creating the executable:
1. Copy the `scripts` folder to the same directory as the executable
2. Run the `VisioTempFileRemover.exe` file

## Notes

- The executable will be quite large due to the Python runtime
- You may need to run the executable as Administrator depending on the directories you're scanning
- Windows SmartScreen may warn about the executable since it's not signed