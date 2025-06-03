const express = require('express');
const bodyParser = require('body-parser');
const path = require('path');
const fs = require('fs'); // For reading config.json
const { execFile } = require('child_process'); // Using execFile for better arg handling

// Constants
const SCRIPT_TIMEOUT = 30000; // 30 seconds timeout for scripts
const MAX_BUFFER_SIZE = 1024 * 5024; // 5MB buffer

// Load Configuration with environment support
function loadConfig() {
    // Determine environment - default to 'development' if not specified
    const env = process.env.NODE_ENV || 'development';
    console.log(`[CONFIG] Loading configuration for environment: ${env}`);
    
    // Try to load environment-specific config file first
    const envConfigPath = path.join(__dirname, `config.${env}.json`);
    const defaultConfigPath = path.join(__dirname, 'config.json');
    
    let configPath = fs.existsSync(envConfigPath) ? envConfigPath : defaultConfigPath;
    console.log(`[CONFIG] Using config file: ${configPath}`);
    
    try {
        const configFile = fs.readFileSync(configPath, 'utf-8');
        const configData = JSON.parse(configFile);
        
        // Apply environment variable overrides if present
        if (process.env.DEFAULT_SCAN_PATH) {
            console.log('[CONFIG] Overriding default_scan_path from environment variable');
            configData.default_scan_path = process.env.DEFAULT_SCAN_PATH;
        }
        
        if (process.env.POWERSHELL_SCRIPTS_PATH) {
            console.log('[CONFIG] Overriding powershell_scripts_path from environment variable');
            configData.powershell_scripts_path = process.env.POWERSHELL_SCRIPTS_PATH;
        }
        
        // Validate configuration
        if (!configData.powershell_scripts_path || !configData.temp_file_patterns) {
            throw new Error('Essential configuration (powershell_scripts_path, temp_file_patterns) missing.');
        }
        
        return configData;
    } catch (error) {
        console.error('[CONFIG ERROR] Failed to load or parse config:', error.message);
        process.exit(1); // Exit if config is invalid
    }
}

// Load the configuration
const config = loadConfig();

const SCRIPTS_PATH = path.join(__dirname, config.powershell_scripts_path);
const SCAN_SCRIPT = path.join(SCRIPTS_PATH, 'Scan-VisioTempFiles.ps1');
const REMOVE_SCRIPT = path.join(SCRIPTS_PATH, 'Remove-VisioTempFiles.ps1');

// Input validation helper functions
const isValidDirectory = (dir) => {
    try {
        return fs.existsSync(dir) && fs.statSync(dir).isDirectory();
    } catch (error) {
        return false;
    }
};

const isValidFilePath = (filePath) => {
    try {
        // Check if the path exists, is a file, and is accessible
        return fs.existsSync(filePath) && fs.statSync(filePath).isFile();
    } catch (error) {
        return false;
    }
};

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, 'web-ui', 'public')));

// Serve the main page
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'web-ui', 'views', 'index.html'));
});

// Health check endpoint
app.get('/health', (req, res) => {
    const scriptsExist = fs.existsSync(SCAN_SCRIPT) && fs.existsSync(REMOVE_SCRIPT);
    
    // Check if PowerShell is available
    execFile('powershell', ['-Command', 'echo "PowerShell Test"'], 
        { timeout: 5000 }, (error) => {
        const health = {
            status: !error && scriptsExist ? 'UP' : 'DOWN',
            uptime: process.uptime(),
            timestamp: new Date().toISOString(),
            environment: process.env.NODE_ENV || 'development',
            checks: [
                {
                    name: 'powershell',
                    status: !error ? 'UP' : 'DOWN'
                },
                {
                    name: 'scripts',
                    status: scriptsExist ? 'UP' : 'DOWN',
                    details: {
                        scan: fs.existsSync(SCAN_SCRIPT),
                        remove: fs.existsSync(REMOVE_SCRIPT)
                    }
                }
            ]
        };
        
        const healthStatus = health.status === 'UP' ? 200 : 503;
        res.status(healthStatus).json(health);
    });
});

// API to scan for files
app.post('/api/scan', (req, res) => {
    const targetDir = req.body.directory || config.default_scan_path || process.cwd(); // Fallback to config or CWD
    
    // Validate directory
    if (!isValidDirectory(targetDir)) {
        console.error(`[SCAN VALIDATION ERROR] Invalid directory: ${targetDir}`);
        return res.status(400).json({
            error: "Invalid directory",
            details: "The specified directory does not exist or is not accessible"
        });
    }
    
    // Validate patterns - ensure they're safe
    const safePatterns = config.temp_file_patterns.filter(pattern => 
        // Only allow safe characters in patterns (alphanumeric, wildcards, and common Visio extensions)
        /^[~$*.A-Za-z0-9\-_]+$/.test(pattern)
    );
    
    if (safePatterns.length === 0) {
        console.error(`[SCAN VALIDATION ERROR] No valid patterns found in configuration`);
        return res.status(400).json({
            error: "Invalid patterns",
            details: "No valid search patterns found in configuration"
        });
    }
    
    console.log(`[SCAN] Scanning directory: ${targetDir}`);

    // Use -Command approach similar to the CLI tool for robust argument handling
    const quotedScanScript = `'${SCAN_SCRIPT.replace(/'/g, "''")}'`; // Single quote script path, escape internal single quotes
    const quotedTargetDir = `'${targetDir.replace(/'/g, "''")}'`;   // Single quote target dir, escape internal single quotes
    
    // Fix: Create a PowerShell array string for patterns instead of passing as separate arguments
    // This matches how the CLI tool handles patterns
    const patternsArray = "@(" + safePatterns.map(p => `"${p}"`).join(',') + ")";
    
    // This format is suitable for PowerShell's -Command execution context
    const psCommand = `& ${quotedScanScript} -ScanPath ${quotedTargetDir} -Patterns ${patternsArray} -AsJson`;

    execFile('powershell', [
        '-NoProfile', 
        '-ExecutionPolicy', 'Bypass', 
        '-Command', psCommand 
        ], 
        { 
            maxBuffer: MAX_BUFFER_SIZE, 
            timeout: SCRIPT_TIMEOUT 
        }, 
        (error, stdout, stderr) => {
            // Handle timeout specifically
            if (error && error.killed) {
                console.error(`[SCAN TIMEOUT] Script execution timed out after ${SCRIPT_TIMEOUT/1000} seconds`);
                return res.status(504).json({
                    error: "Operation timed out",
                    details: "The scan operation took too long and was aborted"
                });
            }
            
            if (error) {
                console.error(`[SCAN SCRIPT ERROR] Error scanning files: ${error.message}`);
                console.error(`[SCAN SCRIPT STDERR] ${stderr}`);
                return res.status(500).json({
                    error: error.message,
                    details: stderr || 'Error executing PowerShell scan script'
                });
            }

            if (stderr && !stderr.toLowerCase().startsWith('warning:')) { // Log significant stderr
                console.warn(`[SCAN SCRIPT STDERR] ${stderr}`);
            }

            try {
                // PowerShell script outputs JSON directly
                const filesData = JSON.parse(stdout.trim() || '[]'); 
                const fileArray = Array.isArray(filesData) ? filesData : []; // Ensure it's an array
                
                console.log(`[SCAN] Found ${fileArray.length} files matching the pattern.`);
                res.json({
                    files: fileArray, // Script now returns objects with Name, FullName, Directory etc.
                    message: `Found ${fileArray.length} file(s)`,
                    scannedDirectory: targetDir
                });
            } catch (e) {
                console.error(`[SCAN PARSE ERROR] Error parsing PowerShell output: ${e.message}`);
                console.error(`[SCAN RAW STDOUT] ${stdout.substring(0, 500)}`);
                res.status(500).json({
                    error: `Failed to parse file list: ${e.message}`,
                    details: 'The PowerShell scan script executed but returned invalid JSON.',
                    rawOutput: stdout.substring(0, 200)
                });
            }
        }
    );
});

// API to delete files
app.post('/api/delete', (req, res) => {
    const filesToDelete = req.body.files; // Expecting an array of full file paths

    if (!filesToDelete || !Array.isArray(filesToDelete) || filesToDelete.length === 0) {
        console.warn(`[DELETE] No files specified for deletion.`);
        return res.status(400).json({
            error: 'No files specified for deletion',
            details: 'Request must include a "files" array with full file paths.'
        });
    }

    // Validate all file paths
    const invalidFiles = filesToDelete.filter(file => !isValidFilePath(file));
    if (invalidFiles.length > 0) {
        console.error(`[DELETE VALIDATION ERROR] Invalid files: ${invalidFiles.join(', ')}`);
        return res.status(400).json({
            error: 'Invalid file paths',
            details: 'One or more specified files do not exist or are not accessible',
            invalidFiles: invalidFiles
        });
    }

    console.log(`[DELETE] Attempting to delete ${filesToDelete.length} files.`);

    // Use -Command approach similar to the CLI tool for robust argument handling
    const quotedRemoveScript = `'${REMOVE_SCRIPT.replace(/'/g, "''")}'`; // Single quote script path, escape internal single quotes
    
    // Create a PowerShell array string for file paths similar to how patterns are handled in the scan API
    const filePathsArray = "@(" + filesToDelete.map(file => `'${file.replace(/'/g, "''")}'`).join(',') + ")";
    // This format is suitable for PowerShell's -Command execution context

    const psCommand = `& ${quotedRemoveScript} -FilePaths ${filePathsArray} -AsJson`;

    execFile('powershell', [
        '-NoProfile', 
        '-ExecutionPolicy', 'Bypass', 
        '-Command', psCommand 
        ], 
        { 
            maxBuffer: MAX_BUFFER_SIZE, 
            timeout: SCRIPT_TIMEOUT 
        },
        (error, stdout, stderr) => {
            // Handle timeout specifically
            if (error && error.killed) {
                console.error(`[DELETE TIMEOUT] Script execution timed out after ${SCRIPT_TIMEOUT/1000} seconds`);
                return res.status(504).json({
                    error: "Operation timed out",
                    details: "The delete operation took too long and was aborted"
                });
            }
            
            if (error) {
                console.error(`[DELETE SCRIPT ERROR] Error deleting files: ${error.message}`);
                console.error(`[DELETE SCRIPT STDERR] ${stderr}`);
                // Even on error, the script might have partial results in stdout (JSON)
                try {
                    const results = JSON.parse(stdout.trim() || '{}');
                    return res.status(500).json({
                        error: error.message,
                        details: stderr || 'Error executing PowerShell delete script',
                        deleted: results.deleted || [],
                        failed: results.failed || [{Path: 'Multiple files', Error: stderr}]
                    });
                } catch (parseError) {
                     return res.status(500).json({
                        error: error.message,
                        details: stderr || 'Error executing PowerShell delete script (and failed to parse partial results)'
                    });
                }
            }

            if (stderr) { // Log any stderr for delete operations
                console.warn(`[DELETE SCRIPT STDERR] ${stderr}`);
            }

            try {
                // PowerShell script outputs JSON: { deleted: [...], failed: [...] }
                const results = JSON.parse(stdout.trim() || '{}');
                const numDeleted = results.deleted ? results.deleted.length : 0;
                const numFailed = results.failed ? results.failed.length : 0;

                console.log(`[DELETE SUCCESS] Processed delete command. Deleted: ${numDeleted}, Failed: ${numFailed}`);
                
                if (numFailed > 0 && numDeleted === 0 && filesToDelete.length > 0) {
                     // All failed, this is more like an error or partial failure
                     return res.status(207).json({ // Multi-Status
                        partialSuccess: false, // Or true if some succeeded
                        message: `Attempted to delete ${filesToDelete.length} file(s). ${numDeleted} succeeded, ${numFailed} failed.`,
                        details: stderr || 'Some files may not have been deleted successfully.',
                        deleted: results.deleted || [],
                        failed: results.failed || [],
                        filesAttempted: filesToDelete.length
                    });
                }

                res.json({
                    success: numFailed === 0,
                    message: `${numDeleted} file(s) deleted. ${numFailed} failed.`,
                    deleted: results.deleted || [],
                    failed: results.failed || []
                });
            } catch (e) {
                console.error(`[DELETE PARSE ERROR] Error parsing PowerShell output: ${e.message}`);
                console.error(`[DELETE RAW STDOUT] ${stdout.substring(0, 500)}`);
                res.status(500).json({
                    error: `Failed to parse delete results: ${e.message}`,
                    details: 'The PowerShell delete script may have run, but its output was unreadable.',
                    rawOutput: stdout.substring(0, 200)
                });
            }
        }
    );
});

// Middleware for handling other unhandled errors
app.use((err, req, res, next) => {
    console.error(`[SERVER ERROR] Unhandled exception: ${err.message}`);
    console.error(err.stack);
    if (res.headersSent) {
        return next(err);
    }
    res.status(500).json({
        error: 'Internal server error',
        message: err.message || 'An unexpected error occurred.',
        path: req.path
    });
});

// Start the server
app.listen(PORT, () => {
    console.log(`-----------------------------------------------`);
    console.log(`| Visio Temp File Remover Server (Refactored) |`);
    console.log(`-----------------------------------------------`);
    console.log(`Server running at http://localhost:${PORT}`);
    console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);
    console.log(`Using config file: ${path.join(__dirname, 'config.json')}`);
    console.log(`Scan script: ${SCAN_SCRIPT}`);
    console.log(`Remove script: ${REMOVE_SCRIPT}`);
    console.log(`API endpoints available at:`);
    console.log(`  - POST http://localhost:${PORT}/api/scan`);
    console.log(`  - POST http://localhost:${PORT}/api/delete`);
    console.log(`  - GET  http://localhost:${PORT}/health`);
    console.log(`Press Ctrl+C to stop the server`);
}); 