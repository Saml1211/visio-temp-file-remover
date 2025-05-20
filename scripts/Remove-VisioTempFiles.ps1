param (
    [Parameter(Mandatory=$true)]
    [string[]]$FilePaths,

    [Parameter(Mandatory=$false)]
    [switch]$AsJson = $true
)

$results = @{
    deleted = @()
    failed = @()
}

# Input validation
if ($FilePaths.Count -eq 0) {
    Write-Error "No file paths provided for deletion."
    if ($AsJson) {
        Write-Output ($results | ConvertTo-Json -Depth 3)
    } else {
        return $results
    }
    exit 1
}

foreach ($filePath in $FilePaths) {
    try {
        # Validate path is not a system path or critical area
        $fileObj = Get-Item -Path $filePath -ErrorAction Stop
        $invalidPaths = @(
            $env:windir, 
            "$env:windir\System32", 
            "$env:windir\System",
            "$env:ProgramFiles",
            "$env:ProgramFiles(x86)",
            "$env:ProgramData"
        )
        
        # Check if file is in a forbidden/system directory
        $isProtectedLocation = $false
        foreach ($protectedPath in $invalidPaths) {
            if ($fileObj.FullName.StartsWith($protectedPath)) {
                $isProtectedLocation = $true
                break
            }
        }
        
        if ($isProtectedLocation) {
            $results.failed += @{ 
                Path = $filePath
                Error = "Cannot delete files in system directories for security reasons." 
            }
            continue
        }
        
        # Make sure it's actually a file, not a directory
        if (Test-Path -Path $filePath -PathType Leaf) {
            # Make sure file matches one of Visio temporary file patterns
            $isVisioTempFile = $false
            $visioPatterns = @('~$$*.vssx', '~$$*.vsdx', '~$$*.vstx', '~$$*.vsdm', '~$$*.vsd')
            
            foreach ($pattern in $visioPatterns) {
                if ($fileObj.Name -like $pattern) {
                    $isVisioTempFile = $true
                    break
                }
            }
            
            if (-not $isVisioTempFile) {
                $results.failed += @{ 
                    Path = $filePath
                    Error = "File does not match Visio temporary file pattern for safety." 
                }
                continue
            }
            
            # Now we can safely remove the file
            Remove-Item -Path $filePath -Force -ErrorAction Stop
            $results.deleted += $filePath
        } else {
            $results.failed += @{ Path = $filePath; Error = "File not found or is a directory." }
        }
    }
    catch {
        $results.failed += @{ Path = $filePath; Error = $_.Exception.Message }
    }
}

if ($AsJson) {
    Write-Output ($results | ConvertTo-Json -Depth 3)
} else {
    return $results
} 