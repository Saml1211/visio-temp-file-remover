# Visio Temp File Remover

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

A simple and effective tool to find and remove corrupted temporary Visio files that cause errors.

<!-- Add a nice screenshot of the application here -->
<!-- ![Visio Temp File Remover Screenshot](path/to/screenshot.png) -->

## The Problem

If you've ever encountered frustrating errors in Microsoft Visio related to shapes and templates, the cause is often hidden, corrupted temporary files (`~$*.vssx`). These files are hard to find and remove manually.

## The Solution

This tool provides a simple interface to scan for and delete these problematic files, keeping your Visio environment clean and error-free. It is available as a standalone desktop application and a web-based tool.

## Features

-   **Find and Delete:** Quickly scan any directory to find and remove temporary Visio files.
-   **Safe and Secure:** Preview the files before deletion and confirm your action. All operations are performed locally on your machine.
-   **Two Interfaces:** Choose between a user-friendly desktop GUI or a web interface for server environments.
-   **Powered by PowerShell:** Uses robust PowerShell scripts for reliable file detection and removal.

## Getting Started

### Standalone Executable (Recommended)

This is the easiest way to use the tool on a Windows machine.

1.  **Download the Executable:**
    Go to the [Releases](https://github.com/Saml1211/visio-temp-file-remover/releases) page and download the latest `VisioTempFileRemover.exe` file.

2.  **Run the Application:**
    Double-click the downloaded `.exe` file to start the application.

### From Source

If you want to run the tool from the source code, you have two options:

#### Desktop GUI

1.  **Prerequisites:**
    *   Python 3.6+
    *   PowerShell
2.  **Clone the repository:**
    ```bash
    git clone https://github.com/Saml1211/visio-temp-file-remover.git
    cd visio-temp-file-remover
    ```
3.  **Run the application:**
    *   Double-click `scripts/run_gui.bat` (on Windows).
    *   Or run `python visio_gui.py` from your terminal.

#### Web Interface

1.  **Prerequisites:**
    *   Node.js v12.0+
    *   npm
    *   PowerShell
2.  **Clone the repository:**
    ```bash
    git clone https://github.com/Saml1211/visio-temp-file-remover.git
    cd visio-temp-file-remover
    ```
3.  **Install dependencies:**
    ```bash
    npm install
    ```
4.  **Start the server:**
    *   Double-click `scripts/start.bat` (on Windows).
    *   Or run `npm start` from your terminal.
5.  **Access the application:**
    Open your web browser and go to `http://localhost:3000`.

## Documentation

For more detailed information, please see the [documentation](docs/index.md).

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.