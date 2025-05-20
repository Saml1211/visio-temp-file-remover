# Technology Context: Visio Temp File Remover

## Technology Stack

### Core Components
- **PowerShell Scripts**: Core file operations and business logic
  - Version requirements: PowerShell 5.1+ (included in Windows 10/11)
  - Key scripts:
    - `Scan-VisioTempFiles.ps1`
    - `Remove-VisioTempFiles.ps1`

### CLI Application
- **Python**: Command-line interface
  - Version: Python 3.8+
  - Key packages:
    - `questionary`: Interactive command-line interface
    - `colorama`: Terminal color support
  - Source: `cli-tool/visio_temp_file_remover.py`

### Web Application
- **Node.js**: Server-side application
  - Version: Node.js 14+
  - Framework: Express.js
  - Key packages:
    - `express`: Web framework
    - `body-parser`: Request parsing
    - `child_process`: PowerShell script execution
  - Source: `app.js`

- **Frontend**: Browser-based UI
  - Technologies: HTML, CSS, JavaScript (vanilla)
  - Key files:
    - `views/index.html`: Main page template
    - `public/styles.css`: Styling
    - `public/main.js`: Frontend interaction logic

### Configuration
- **JSON**: Shared configuration across components
  - Primary: `config.json`
  - Environment-specific: `config.[environment].json`
  - Override capability via environment variables

## Development Setup

### Prerequisites
1. Windows 10/11 with PowerShell 5.1+
2. Python 3.8+ with pip
3. Node.js 14+ with npm
4. PowerShell execution policy allowing script execution (`Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`)

### Development Installation

#### CLI Tool Setup
```bash
# Navigate to CLI tool directory
cd cli-tool

# Install Python dependencies
pip install -r requirements.txt

# Test the CLI tool
python visio_temp_file_remover.py
```

#### Web Application Setup
```bash
# Install Node.js dependencies
npm install

# Start the web server
node app.js

# Access the web interface at http://localhost:3000
```

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

## Technical Constraints

### Platform Limitations
- **Windows-only**: Dependency on PowerShell limits cross-platform support
- **File System Access**: Requires appropriate permissions for target directories
- **Execution Policy**: PowerShell execution policy must allow script execution

### Security Considerations
- **Input Validation**: All user input is validated before processing
  - Directory paths are checked for existence and permissions
  - File patterns are restricted to known safe patterns
  - System directories are protected against deletion
- **Process Isolation**: PowerShell scripts run as separate processes with controlled parameters
- **Script Execution**: Uses `-NoProfile` and `-ExecutionPolicy Bypass` for controlled execution
- **Error Handling**: Structured error reporting with appropriate HTTP status codes

### Performance Considerations
- **Large Directories**: Scanning performance depends on directory size and number of files
- **Timeouts**: Script execution has configurable timeouts to prevent hanging
- **Memory Usage**: 
  - Web: Buffer limits for PowerShell output (5MB default)
  - CLI: No explicit limits, but depends on available system memory

### Scalability Constraints
- **Concurrency**: Web server handles multiple concurrent requests, but each PowerShell process runs sequentially
- **File Count**: User interface may become unwieldy with extremely large file counts (thousands)
- **Network Paths**: Performance degradation when scanning network shares with high latency

## Dependencies and External Systems

### Microsoft Visio
- No direct integration with Visio
- Only interacts with file system where Visio creates temporary files
- Compatible with all modern Visio versions (2013, 2016, 2019, 2021, 365)

### External Libraries
All dependencies are managed through:
- `package.json` (Node.js)
- `requirements.txt` (Python)

No external APIs or services are required for operation.

## Testing Approach

### Manual Testing Areas
- Directory scanning with various path formats
- File selection in both interfaces
- Deletion operations with different file counts
- Error handling with invalid inputs
- Performance with large directories

### Future Testing Recommendations
- Unit tests for PowerShell scripts using Pester
- Integration tests for CLI tool
- API endpoint tests for web application
- End-to-end tests for complete workflows 