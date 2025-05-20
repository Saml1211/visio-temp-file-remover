param (
    [Parameter(Mandatory=$true)]
    [string]$ScanPath,

    [Parameter(Mandatory=$true)]
    [string[]]$Patterns,

    [Parameter(Mandatory=$false)]
    [switch]$AsJson = $true # Output as JSON by default
)

try {
    if (-not (Test-Path -Path $ScanPath -PathType Container)) {
        Write-Error "Scan path '$ScanPath' not found or is not a directory."
        exit 1
    }

    $foundFiles = @()

    # No patterns means no files to find
    if ($Patterns.Count -eq 0) {
        Write-Warning "No valid patterns provided to search for."
        if ($AsJson) { Write-Output "[]"; exit 0 } else { exit 0 }
    }

    # Get all files recursively from the directory
    try {
        # Use Get-ChildItem directly without Invoke-Expression for security
        $files = Get-ChildItem -Path $ScanPath -Recurse -Force -File -ErrorAction Stop
        
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

        if ($null -ne $matchingFiles) {
            $foundFiles = $matchingFiles | ForEach-Object {
                @{
                    FullName = $_.FullName
                    Name = $_.Name
                    Directory = $_.DirectoryName
                    LastModified = $_.LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
                    Size = $_.Length
                }
            }
        }
    }
    catch {
        Write-Error "Error during file scan: $($_.Exception.Message)"
        if ($AsJson) { Write-Output "[]"; exit 1 } else { exit 1 }
    }

    if ($AsJson) {
        Write-Output ($foundFiles | ConvertTo-Json -Depth 3)
    } else {
        return $foundFiles
    }
}
catch {
    Write-Error "Error during file scan: $($_.Exception.Message)"
    if ($AsJson) { Write-Output "[]"; exit 1 } else { exit 1 } # Output empty JSON array on error
} 