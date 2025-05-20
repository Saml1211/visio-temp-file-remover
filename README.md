# Visio Temp File Remover

A utility for finding and removing temporary files created by Microsoft Visio. Provides both command-line and web interfaces for managing Visio temporary files.

## Features

- Scan directories for Visio temporary files
- Select specific files for deletion
- Secure deletion with validation
- Two interface options:
  - Python CLI for command-line use and automation
  - Node.js web application for browser-based use
- Shared PowerShell backend for consistent behavior

## Screenshots

*[Screenshots to be added]*

## Requirements

- Windows 10 or newer
- PowerShell 5.1 or newer
- Python 3.8+ (for CLI)
- Node.js 14+ (for web interface)

## Installation

### CLI Tool

1. Clone this repository
2. Navigate to the `cli-tool` directory
3. Install Python dependencies (the requirements.txt file is already included):
```bash
pip install -r requirements.txt
```

### Web Interface

1. Clone this repository
2. Install Node.js dependencies:
```bash
npm install
```
3. Start the server:
```bash
node app.js
```
4. Access the web interface at http://localhost:3000

## Usage

### CLI Tool

Run the CLI tool:

```bash
python cli-tool/visio_temp_file_remover.py
```

Follow the interactive prompts to:
1. Select a directory to scan
2. Choose files to delete
3. Confirm deletion

### Web Interface

1. Start the web server: `node app.js`
2. Navigate to http://localhost:3000 in your browser
3. Enter a directory path to scan
4. Select files to delete
5. Click "Delete Selected Files"

## Configuration

Configuration settings are stored in `config.json` in the root directory. Example:

```json
{
  "default_scan_path": "C:\\Users\\Public\\Documents\\Visio Files",
  "temp_file_patterns": [
    "~$$*.vssx",
    "~$$*.vsdx",
    "~$$*.vstx",
    "~$$*.vsdm",
    "~$$*.vsd"
  ],
  "powershell_scripts_path": "scripts",
  "cli_tool_path": "cli-tool"
}
```

### Environment-Specific Configuration

For different environments, create a `config.[environment].json` file (e.g., `config.development.json`). Set the `NODE_ENV` environment variable to load the appropriate configuration.

## Architecture

This project uses a layered architecture:
- User interfaces (Python CLI, Node.js web app)
- Shared configuration (JSON)
- PowerShell scripts for core file operations

PowerShell scripts return structured JSON data for consistent behavior across interfaces.

## Security

Recent security improvements include:
- Removal of command injection vulnerabilities
- Enhanced input validation at all levels
- Protection of system directories
- Timeout handling for script execution
- Pattern validation to ensure only legitimate Visio temp files are processed

## Development

### Project Structure

```
visio-temp-file-remover/
├── app.js                     # Main Node.js web application
├── config.json                # Shared configuration
├── config.development.json    # Development environment config
├── cli-tool/
│   ├── requirements.txt       # Python dependencies
│   └── visio_temp_file_remover.py  # Python CLI application
├── scripts/
│   ├── Scan-VisioTempFiles.ps1     # PowerShell scanning script
│   └── Remove-VisioTempFiles.ps1   # PowerShell deletion script
├── web-ui/
│   ├── public/                # Static web assets
│   │   ├── styles.css         # CSS styling
│   │   └── main.js            # Frontend JavaScript
│   └── views/
│       └── index.html         # Main HTML template
```

### Contributing

Contributions are welcome! Please check out our [contributing guidelines](CONTRIBUTING.md) for details.

## Roadmap

- Comprehensive documentation
- Automated testing
- Enhanced logging
- UI improvements
- Performance optimization
- Cross-platform support planning

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Original Python CLI tool team
- Original Node.js web application team
- All contributors to the unified codebase 