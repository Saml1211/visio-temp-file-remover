param (
    [Parameter(Mandatory=$true)]
    [string]$ScanPath,

    [Parameter(Mandatory=$true)]
    [string[]]$Patterns,

    [Parameter(Mandatory=$false)]
    [switch]$AsJson = $true, # Output as JSON by default

    [Parameter(Mandatory=$false)]
    [switch]$DebugOutput = $false # Debug mode - renamed from Debug to avoid built-in parameter collision
)

# Set output encoding to UTF-8 for consistency
$OutputEncoding = [System.Text.UTF8Encoding]::new($false) # $false for no BOM

# Use Write-Host for debug, as it goes to host directly, not standard output
if ($DebugOutput) {
    Write-Host "DEBUG: ScanScript Start" -ForegroundColor Cyan
    Write-Host "DEBUG: ScanScript Params Parsed. ScanPath: $ScanPath, Patterns: $($Patterns -join ';')" -ForegroundColor Cyan
}

try {
    if (-not (Test-Path -Path $ScanPath -PathType Container)) {
        Write-Error "Scan path '$ScanPath' not found or is not a directory."
        if ($AsJson) { 
            # Ensure clean JSON output
            Write-Output "[]"
        }
        exit 1
    }

    $foundFiles = @()

    # No patterns means no files to find
    if ($Patterns.Count -eq 0) {
        Write-Warning "No valid patterns provided to search for."
        if ($AsJson) { 
            # Ensure clean JSON output
            Write-Output "[]"
            exit 0 
        } else { 
            exit 0 
        }
    }

    # Get all files recursively from the directory
    try {
        # Use Get-ChildItem directly without Invoke-Expression for security
        $files = Get-ChildItem -Path $ScanPath -Recurse -Force -File -ErrorAction Stop
        
        if ($DebugOutput) {
            Write-Host "DEBUG: Found $($files.Count) total files in directory" -ForegroundColor Cyan
        }
        
        # Filter files based on patterns
        $matchingFiles = $files | Where-Object {
            $file = $_
            foreach ($pattern in $Patterns) {
                if ($file.Name -like $pattern) {
                    return $true
                }
            }
            return $false
        }

        if ($null -ne $matchingFiles -and $matchingFiles.Count -gt 0) {
            if ($DebugOutput) {
                Write-Host "DEBUG: Matched $($matchingFiles.Count) files with patterns" -ForegroundColor Green
            }
            $foundFiles = $matchingFiles | ForEach-Object {
                @{
                    FullName = $_.FullName
                    Name = $_.Name
                    Directory = $_.DirectoryName
                    LastModified = $_.LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
                    Size = $_.Length
                }
            }
        } else {
            if ($DebugOutput) {
                Write-Host "DEBUG: No matching files found" -ForegroundColor Yellow
            }
            # Ensure foundFiles is a proper empty array
            $foundFiles = @()
        }
    }
    catch {
        Write-Error "Error during file scan: $($_.Exception.Message)"
        if ($AsJson) { 
            # Ensure clean JSON output
            Write-Output "[]"
            exit 1 
        } else { 
            exit 1 
        }
    }

    if ($AsJson) {
        # Ensure clean JSON output with proper handling of empty arrays
        if ($foundFiles.Count -eq 0) {
            Write-Output "[]"
        } else {
            Write-Output ($foundFiles | ConvertTo-Json -Depth 3)
        }
    } else {
        return $foundFiles
    }
}
catch {
    Write-Error "Error during file scan: $($_.Exception.Message)"
    if ($AsJson) { 
        # Ensure clean JSON output
        Write-Output "[]"
        exit 1 
    } else { 
        exit 1 
    } # Output empty JSON array on error
} 