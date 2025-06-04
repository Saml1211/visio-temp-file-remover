# Visio Temp File Remover

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

A specialized web application designed to find and remove corrupted temporary Visio files that can cause errors in Microsoft Visio environments.

![Visio Temp File Remover Screenshot](https://via.placeholder.com/800x400?text=Visio+Temp+File+Remover)

## 🔍 Overview

The Visio Temp File Remover tool addresses a common problem in Microsoft Visio environments where temporary files (specifically those matching the pattern `~$$*.~vssx`) can cause errors and corruption in Visio shapes and templates. These files are often hidden by default and difficult to locate and remove through normal file management tools.

This application provides an intuitive web interface that allows users to:
1. Scan directories for problematic temporary files
2. Review what will be deleted before taking action
3. Safely remove these files with proper permission handling

## ✨ Features

- **Smart Scanning**: Recursively scans specified directories for Visio temporary files matching `~$$*.~vssx` pattern
- **Hidden File Detection**: Uses PowerShell with proper escaping to find hidden system files that Windows Explorer might not display
- **Preview Before Deletion**: Lists all found files with full paths before any deletion occurs
- **Selective Deletion**: Choose which files to delete rather than removing all matches
- **User-Friendly Interface**: Simple web interface that requires no technical knowledge to operate
- **Secure Operations**: All file operations are performed server-side with proper error handling

## 🛠️ Technology Stack

- **Backend**: Node.js with Express.js
- **Frontend**: HTML5, CSS3, and vanilla JavaScript
- **System Integration**: PowerShell commands for file operations
- **Styling**: Bootstrap for responsive design
- **HTTP Requests**: Fetch API for AJAX operations

## 📋 Requirements

- Windows environment (PowerShell required)
- Node.js (v12.0.0 or higher)
- Administrative privileges (for accessing system folders)
- Web browser (Chrome, Firefox, Edge recommended)

## 🚀 Getting Started

For quick setup and usage instructions, please refer to the [QUICKSTART.md](QUICKSTART.md) file.

Basic steps include:
1. Clone this repository
2. Install dependencies with `npm install`
3. Start the server with `npm start` or by running `start.bat`
4. Access the web interface at http://localhost:3000

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

```
MIT License

Copyright (c) 2023 Visio Temp File Remover

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
