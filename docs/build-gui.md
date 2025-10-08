# Building the GUI Executable

This guide provides instructions for creating a standalone Windows executable (`.exe`) from the Python source code using PyInstaller.

## Why Build an Executable?

Building an executable allows you to distribute the desktop GUI application to users who may not have Python or the necessary technical knowledge to run the application from source. The executable bundles the Python interpreter and all necessary files into a single, easy-to-run file.

## Prerequisites

Before you begin, ensure you have the following installed:

-   [Python](https://www.python.org/downloads/) (3.6 or higher)
-   [pip](https://pip.pypa.io/en/stable/installation/) (usually comes with Python)

## Build Steps

1.  **Install PyInstaller:**
    Open a command prompt or PowerShell and install PyInstaller using pip:
    ```bash
    pip install pyinstaller
    ```

2.  **Navigate to the Project Directory:**
    In your terminal, change to the root directory of the project.

3.  **Run the PyInstaller Command:**
    Execute the following command to create the executable:
    ```bash
    pyinstaller --onefile --windowed --name "VisioTempFileRemover" visio_gui.py
    ```

    **Command Breakdown:**
    -   `--onefile`: Bundles everything into a single executable file.
    -   `--windowed`: Prevents a console window from appearing when the application is run.
    -   `--name "VisioTempFileRemover"`: Sets the name of the executable.
    -   `visio_gui.py`: The main Python script for the application.

4.  **Find the Executable:**
    The standalone executable will be created in the `dist` directory.

## Running the Executable

Once the build is complete, you can find `VisioTempFileRemover.exe` in the `dist` directory. Double-click this file to run the application.

## Troubleshooting

-   **Large File Size:** The executable will be relatively large because it includes a full Python interpreter. This is normal.
-   **Windows SmartScreen:** Windows may show a warning when you first run the executable because it is not code-signed. You can typically bypass this by clicking "More info" and then "Run anyway."
-   **Administrator Privileges:** Depending on the directories you need to scan, you may need to run the executable as an administrator. Right-click the `.exe` file and select "Run as administrator."
