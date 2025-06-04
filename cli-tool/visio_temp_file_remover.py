import json
import os
import subprocess
import platform
import sys
import re
from pathlib import Path

import questionary # type: ignore
from questionary import Choice # type: ignore
from colorama import Fore, Style, init # type: ignore
init() # Initialize colorama

# Constants
SCRIPT_TIMEOUT = 30  # 30 seconds timeout for PowerShell scripts

# Editable: Patterns for Visio temp/backup files
# TEMP_PATTERNS = [ # Commented out, will be loaded from config
#     '~$$*.vssx',
#     '~$$*.vsdx',
#     '~$$*.vstx',
#     '~$$*.vsdm',
#     '~$$*.vsd',
# ]

# DEFAULT_DIR = r'Z:\ENGINEERING TEMPLATES\VISIO SHAPES 2025' # Commented out, will be loaded from config

CONFIG_FILE_PATH = Path(__file__).resolve().parent.parent / 'config.json'

def load_config():
    """Loads configuration from config.json"""
    try:
        with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        # Basic validation
        if not isinstance(config_data.get('temp_file_patterns'), list):
            raise ValueError("'temp_file_patterns' must be a list in config.json")
        default_path = config_data.get('default_scan_path')
        if not isinstance(default_path, str) and default_path is not None and default_path != "":
            raise ValueError("'default_scan_path' must be a string or empty in config.json")
        if not config_data.get('powershell_scripts_path'):
            raise ValueError("'powershell_scripts_path' must be defined in config.json")
        
        # Validate pattern safety
        safe_patterns = []
        for pattern in config_data.get('temp_file_patterns', []):
            # Only allow safe characters in patterns
            if re.match(r'^[~$*.A-Za-z0-9\-_]+$', pattern):
                safe_patterns.append(pattern)
            else:
                print(f"{Fore.YELLOW}Warning: Ignoring potentially unsafe pattern: {pattern}{Style.RESET_ALL}")
        
        if not safe_patterns:
            raise ValueError("No valid file patterns found in configuration")
        
        config_data['temp_file_patterns'] = safe_patterns
        return config_data
    except FileNotFoundError:
        print(f"{Fore.RED}Error: Configuration file not found at {CONFIG_FILE_PATH}{Style.RESET_ALL}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"{Fore.RED}Error: Could not decode JSON from {CONFIG_FILE_PATH}{Style.RESET_ALL}")
        sys.exit(1)
    except ValueError as ve:
        print(f"{Fore.RED}Error in configuration: {ve}{Style.RESET_ALL}")
        sys.exit(1)
    return None # Should not be reached if sys.exit works

config = load_config()
if config is None: # Should have exited, but as a safeguard
    sys.exit("Failed to load configuration.")

TEMP_PATTERNS = config['temp_file_patterns']
DEFAULT_DIR = config.get('default_scan_path', '') # Use .get for safety, provide default
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / config['powershell_scripts_path']
SCAN_SCRIPT_PATH = SCRIPTS_DIR / 'Scan-VisioTempFiles.ps1'
REMOVE_SCRIPT_PATH = SCRIPTS_DIR / 'Remove-VisioTempFiles.ps1'

def validate_scripts_exist():
    """Validate that PowerShell scripts exist and are accessible"""
    if not SCAN_SCRIPT_PATH.is_file():
        print(f"{Fore.RED}Error: Scan script not found at {SCAN_SCRIPT_PATH}{Style.RESET_ALL}")
        return False
    if not REMOVE_SCRIPT_PATH.is_file():
        print(f"{Fore.RED}Error: Remove script not found at {REMOVE_SCRIPT_PATH}{Style.RESET_ALL}")
        return False
    return True

def validate_powershell_available():
    """Check if PowerShell is available on the system"""
    try:
        result = subprocess.run(
            ["powershell", "-Command", "Write-Output 'PowerShell Test'"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def get_directory_to_scan():
    """
    Prompts the user to choose a directory for scanning.
    Returns a Path object if a directory is selected, or None if the user cancels/exits.
    """
    while True:
        default_path_obj = Path(DEFAULT_DIR) if DEFAULT_DIR else None
        default_path_valid = default_path_obj.is_dir() if default_path_obj else False

        choices = []
        if default_path_valid and default_path_obj:
            choices.append(Choice(title=f"Default: {DEFAULT_DIR}", value="default"))
        choices.append(Choice(title="Enter custom directory path", value="custom"))
        choices.append(Choice(title="Exit program", value="exit"))

        selection_prompt_message = "Select an option for the directory to scan:"
        if DEFAULT_DIR and not default_path_valid:
            selection_prompt_message = (
                f"{Fore.YELLOW}Configured default directory '{DEFAULT_DIR}' is invalid or not accessible.{Style.RESET_ALL}\n"
                "Select an option:"
            )
        elif not DEFAULT_DIR:
             selection_prompt_message = (
                f"{Fore.YELLOW}No default directory configured.{Style.RESET_ALL}\n"
                "Select an option:"
            )

        action = questionary.select(
            selection_prompt_message,
            choices=choices,
            qmark="?"
        ).ask()

        if action == "default":
            if default_path_valid and default_path_obj:
                print(f"{Fore.GREEN}Using default directory: {DEFAULT_DIR}{Style.RESET_ALL}")
                return default_path_obj.resolve()
            else:
                print(f"{Fore.RED}Error: Default directory was selected but is invalid or not configured.{Style.RESET_ALL}")
                if questionary.confirm("Try entering a custom path instead? (No to exit)").ask():
                    action = "custom"
                else:
                    return None
        
        if action == "custom":
            path_str = questionary.text(
                "Enter the directory path to scan:",
                validate=lambda text: True if text and Path(text.strip('"'" ").strip("'")).is_dir()
                                   else ("Path is not a valid directory or does not exist."
                                         if text else "Input cannot be empty. Press ESC to cancel."),
            ).ask()

            if path_str is None:
                print(f"{Fore.YELLOW}Custom path entry cancelled. Returning to options.{Style.RESET_ALL}")
                continue
            else:
                chosen_path = Path(path_str.strip('"'" ").strip("'")).resolve()
                print(f"{Fore.GREEN}Selected directory: {chosen_path}{Style.RESET_ALL}")
                return chosen_path
        elif action == "exit" or action is None:
            return None
        elif action != "custom":
            continue
    return None # Should be unreachable

def find_temp_files(directory: Path, patterns: list[str]) -> list[Path]:
    """Find files using the Scan-VisioTempFiles.ps1 PowerShell script."""
    if not SCAN_SCRIPT_PATH.is_file():
        print(f"{Fore.RED}Error: Scan script not found at {SCAN_SCRIPT_PATH}{Style.RESET_ALL}")
        return []

    dir_str = str(directory)
    
    # Validate parameters before passing to PowerShell
    if not os.path.isdir(dir_str):
        print(f"{Fore.RED}Error: Directory does not exist or is not accessible: {dir_str}{Style.RESET_ALL}")
        return []
    
    # Validate each pattern for safety
    safe_patterns = []
    for pattern in patterns:
        if re.match(r'^[~$*.A-Za-z0-9\-_]+$', pattern):
            safe_patterns.append(pattern)
        else:
            print(f"{Fore.YELLOW}Warning: Skipping potentially unsafe pattern: {pattern}{Style.RESET_ALL}")
    
    if not safe_patterns:
        print(f"{Fore.RED}Error: No valid safe patterns to scan with.{Style.RESET_ALL}")
        return []
    
    # Escape paths with quotes to handle spaces and special characters
    dir_str_quoted = f'"{dir_str}"'  # Double quotes for PowerShell
    
    # Create a list of patterns with proper quoting
    patterns_list = [f'"{p}"' for p in safe_patterns]  # Quote each pattern
    patterns_array = "@(" + ",".join(patterns_list) + ")"  # Create PowerShell array
    
    # Build PowerShell command as a single string
    # Call the script directly without ampersand operator to avoid parameter confusion
    ps_command = f"& {SCAN_SCRIPT_PATH} -ScanPath {dir_str_quoted} -Patterns {patterns_array} -AsJson"
    
    ps_cmd_list = [
        "powershell", 
        "-NoProfile", 
        "-ExecutionPolicy", "Bypass",
        "-Command", ps_command
    ]

    print(f"{Fore.CYAN}Running PowerShell scan script: {SCAN_SCRIPT_PATH} for {dir_str} with patterns {','.join(safe_patterns)}{Style.RESET_ALL}")
    
    try:
        completed = subprocess.run(
            ps_cmd_list,
            capture_output=True,
            text=True,
            check=False,
            encoding='utf-8',
            timeout=SCRIPT_TIMEOUT  # Add timeout to prevent hanging
        )

        if completed.stderr and not completed.stderr.lower().strip().startswith("warning:"):
            is_actual_error = True
            try:
                json_stderr = json.loads(completed.stderr.strip())
                if isinstance(json_stderr, list) and not json_stderr:
                    is_actual_error = False 
            except json.JSONDecodeError:
                pass 
            if is_actual_error:
                 print(f"{Fore.RED}PowerShell script error/warning:{Style.RESET_ALL}\n{Fore.YELLOW}{completed.stderr.strip()}{Style.RESET_ALL}")

        # Check for empty output
        if not completed.stdout or completed.stdout.strip() == "":
            print(f"{Fore.RED}PowerShell script returned no output.{Style.RESET_ALL}")
            return []

        # Check if output is valid JSON
        try:
            result_data = json.loads(completed.stdout.strip())
            
            # If we got an empty array, it means no files were found
            if isinstance(result_data, list) and len(result_data) == 0:
                print(f"{Fore.GREEN}No matching temporary Visio files found in the specified location.{Style.RESET_ALL}")
                return []
                
            found_files = [Path(item['FullName']) for item in result_data if isinstance(item, dict) and 'FullName' in item]
            print(f"{Fore.GREEN}Found {len(found_files)} temporary Visio files.{Style.RESET_ALL}")
            return sorted(found_files)
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Error parsing scan JSON: {e}{Style.RESET_ALL}")
            print(f"{Fore.MAGENTA}Raw STDOUT:\n{completed.stdout.strip()}{Style.RESET_ALL}")
            
            # Despite the JSON error, let's check if we need to show 'no files found' message
            if "No matching" in completed.stdout or completed.stdout.strip() == "[]":
                print(f"{Fore.GREEN}No matching temporary Visio files found in the specified location.{Style.RESET_ALL}")
            
            return []
    except subprocess.TimeoutExpired:
        print(f"{Fore.RED}Error: PowerShell script timed out after {SCRIPT_TIMEOUT} seconds.{Style.RESET_ALL}")
        return []
    except FileNotFoundError:
        print(f"{Fore.RED}Error: 'powershell' not found. Ensure it's in PATH.{Style.RESET_ALL}")
        return []
    except Exception as e:
        print(f"{Fore.RED}Unexpected error running scan script: {e}{Style.RESET_ALL}")
        return []
    return [] # Fallback

def select_files_for_deletion(file_list: list[Path], base_directory: Path) -> list[Path]:
    """Prompt user to select files to delete."""
    if not file_list:
        print(f"{Fore.GREEN}No Visio temp files found.{Style.RESET_ALL}")
        return []
    
    choices = []
    for f_path in file_list:
        try:
            rel_parent = f_path.parent.relative_to(base_directory)
        except ValueError:
            rel_parent = f_path.parent # Fallback to absolute if not under base_directory
        display = f"{f_path.name} (in {rel_parent})"
        choices.append(Choice(title=display, value=str(f_path))) # Store as string for Q
        
    selected_str_paths = questionary.checkbox(
        "Select files to delete (Space to toggle, Enter to confirm):",
        choices=choices,
        # validate=lambda vals: True if vals else "Select at least one file or ESC to cancel."
    ).ask()
    
    return [Path(p) for p in selected_str_paths] if selected_str_paths else []

def delete_files(selected_paths: list[Path]):
    """Delete selected files using direct PowerShell commands similar to the web UI's approach."""
    if not selected_paths:
        return

    if not validate_powershell_available():
        print(f"{Fore.RED}Error: PowerShell is not available on this system.{Style.RESET_ALL}")
        return

    confirm_delete = questionary.confirm(
        f"Are you sure you want to delete {len(selected_paths)} selected file(s)?"
    ).ask()
    if not confirm_delete:
        print(f"{Fore.YELLOW}Deletion cancelled by user.{Style.RESET_ALL}")
        return

    # Validate that all files exist before attempting deletion
    invalid_paths = [p for p in selected_paths if not p.is_file()]
    if invalid_paths:
        print(f"{Fore.RED}Error: The following files don't exist or are not accessible:{Style.RESET_ALL}")
        for p in invalid_paths:
            print(f"  - {p}")
        if not questionary.confirm("Continue with deleting only valid files?").ask():
            print(f"{Fore.YELLOW}Deletion cancelled by user.{Style.RESET_ALL}")
            return
        # Filter out invalid paths
        selected_paths = [p for p in selected_paths if p.is_file()]
        if not selected_paths:
            print(f"{Fore.YELLOW}No valid files remaining to delete.{Style.RESET_ALL}")
            return

    # Collect paths as strings
    file_paths = [str(p) for p in selected_paths]
    
    # Escape paths for PowerShell - escape single quotes by doubling them
    # and wrap each path in single quotes
    quoted_paths = [f"'{path.replace('\'', '\'\'')}'" for path in file_paths]
    
    # Build a PowerShell command that pipelines the paths through ForEach-Object
    # This is similar to what the web UI does which works successfully
    ps_command = f"""
    $filesToDelete = @({','.join(quoted_paths)})
    $results = @{{
        deleted = @()
        failed = @()
    }}
    
    foreach ($file in $filesToDelete) {{
        try {{
            if (Test-Path -LiteralPath $file -PathType Leaf) {{
                Remove-Item -LiteralPath $file -Force -ErrorAction Stop
                $results.deleted += $file
                Write-Host "Deleted: $file" -ForegroundColor Green
            }} else {{
                $results.failed += @{{ Path = $file; Error = "File not found or is not a regular file." }}
                Write-Host "Not found: $file" -ForegroundColor Yellow
            }}
        }} catch {{
            $results.failed += @{{ Path = $file; Error = $_.Exception.Message }}
            Write-Host "Error: $file - $($_.Exception.Message)" -ForegroundColor Red
        }}
    }}
    
    # Output summary
    Write-Host "----RESULTS----"
    Write-Host "Deleted: $($results.deleted.Count) files"
    Write-Host "Failed: $($results.failed.Count) files"
    
    # Return results as JSON for parsing
    $results | ConvertTo-Json -Depth 3
    """
    
    print(f"{Fore.YELLOW}Executing PowerShell delete command for {len(file_paths)} files...{Style.RESET_ALL}")
    
    try:
        completed = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_command],
            capture_output=True,
            text=True,
            check=False,
            encoding='utf-8',
            timeout=SCRIPT_TIMEOUT
        )
        
        # Process any standard error output
        if completed.stderr and completed.stderr.strip():
            print(f"{Fore.RED}PowerShell error output:{Style.RESET_ALL}\n{Fore.YELLOW}{completed.stderr.strip()}{Style.RESET_ALL}")
        
        # Try to parse JSON results if available
        try:
            # Look for JSON in the output - it will be after the "----RESULTS----" line
            output_lines = completed.stdout.strip().split('\n')
            json_start = -1
            
            for i, line in enumerate(output_lines):
                if "----RESULTS----" in line:
                    json_start = i + 3  # Skip the summary lines
                    break
            
            if json_start >= 0 and json_start < len(output_lines):
                json_str = '\n'.join(output_lines[json_start:])
                result_data = json.loads(json_str)
                
                deleted = result_data.get('deleted', [])
                failed = result_data.get('failed', [])
                
                if deleted:
                    print(f"{Fore.GREEN}Successfully deleted:{Style.RESET_ALL}")
                    for path in deleted:
                        print(f"  - {path}")
                
                if failed:
                    print(f"\n{Fore.RED}Failed to delete:{Style.RESET_ALL}")
                    for item in failed:
                        if isinstance(item, dict):
                            print(f"  - {item.get('Path', 'Unknown')}: {item.get('Error', 'Unknown error')}")
                        else:
                            print(f"  - {item}: Unknown error")
                
                print(f"\n{Style.BRIGHT}Summary:{Style.RESET_ALL} {len(deleted)} deleted, {len(failed)} failed.\n")
            else:
                print(f"{Fore.YELLOW}Could not find JSON results in PowerShell output. Raw output:{Style.RESET_ALL}")
                print(completed.stdout)
                
        except json.JSONDecodeError:
            # If JSON parsing fails, just show the raw output
            print(f"{Fore.RED}Could not parse JSON results. Raw PowerShell output:{Style.RESET_ALL}")
            print(completed.stdout)
            
    except subprocess.TimeoutExpired:
        print(f"{Fore.RED}Error: PowerShell command timed out after {SCRIPT_TIMEOUT} seconds.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Unexpected error running delete command: {e}{Style.RESET_ALL}")

def main():
    print(f"{Fore.CYAN}{Style.BRIGHT}Welcome to the Visio Temporary File Remover Wizard!{Style.RESET_ALL}")

    # Validate environment before starting
    if not validate_powershell_available():
        print(f"{Fore.RED}Error: PowerShell is not available on this system.{Style.RESET_ALL}")
        print(f"{Fore.RED}This tool requires PowerShell to run. Please install PowerShell and try again.{Style.RESET_ALL}")
        sys.exit(1)
    
    if not validate_scripts_exist():
        print(f"{Fore.RED}Error: Required PowerShell scripts are missing.{Style.RESET_ALL}")
        sys.exit(1)
    
    try:
        while True:
            target_directory = get_directory_to_scan()

            if target_directory is None:
                print(f"{Fore.CYAN}Exiting program.{Style.RESET_ALL}")
                break

            print(f"{Fore.BLUE}Scanning {Style.BRIGHT}{target_directory}{Style.NORMAL} for files...{Style.RESET_ALL}")
            found_temp_files = find_temp_files(target_directory, TEMP_PATTERNS)
            
            if not found_temp_files:
                print(f"{Fore.GREEN}No matching temporary Visio files found in the specified location.{Style.RESET_ALL}")
            else:
                files_to_delete = select_files_for_deletion(found_temp_files, target_directory)
                if files_to_delete:
                    delete_files(files_to_delete)
            
            if not questionary.confirm("Would you like to scan another location or exit?", default=True, qmark="?").ask():
                print(f"{Fore.CYAN}Exiting program.{Style.RESET_ALL}")
                break
    finally:
        init() # Ensure colorama is re-initialized if deinit was called elsewhere, or handle this better.

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Program interrupted by user. Exiting.{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}An unexpected error occurred: {e}{Style.RESET_ALL}")
        # import traceback
        # traceback.print_exc()
    finally:
        import colorama
        colorama.deinit() # type: ignore 