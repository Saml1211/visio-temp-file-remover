import json
import os
import subprocess
import platform
import sys
import re
import time
from pathlib import Path

import questionary # type: ignore
from questionary import Choice, Style as QStyle, Validator # type: ignore
from colorama import Fore, Style, Back, init, AnsiToWin32 # type: ignore
import os

# Initialize colorama for Windows PowerShell
try:
    # Try using just_fix_windows_console() first (available in newer colorama versions)
    from colorama import just_fix_windows_console
    just_fix_windows_console()
except ImportError:
    # Fall back to older method if needed
    init(autoreset=True, convert=True, strip=False, wrap=True)
    
    # Additional handling for Windows PowerShell if necessary
    if platform.system() == 'Windows':
        import sys
        # Re-initialize for PowerShell compatibility
        init(autoreset=True, convert=True, strip=False, wrap=True)
        # Only wrap if not already wrapped
        if not isinstance(sys.stdout, AnsiToWin32):
            sys.stdout = AnsiToWin32(sys.stdout, strip=False, convert=True).stream
        if not isinstance(sys.stderr, AnsiToWin32):
            sys.stderr = AnsiToWin32(sys.stderr, strip=False, convert=True).stream

# Set up a cleanup function to ensure we reset terminal state properly
def reset_terminal_state():
    """Reset terminal state to prevent issues with raw ANSI codes"""
    try:
        init(autoreset=True, convert=True, strip=False, wrap=True)
    except Exception:
        pass

# More reliable PowerShell detection
def is_running_in_powershell():
    """Determine if we're running in PowerShell with high reliability"""
    # Check environment variables
    if "POWERSHELL_DISTRIBUTION_CHANNEL" in os.environ:
        return True
    if "PSModulePath" in os.environ:
        return True
    # Check shell info in sys.argv
    for arg in sys.argv:
        if "powershell" in arg.lower():
            return True
    # Check Windows platform
    if platform.system() == 'Windows':
        return True
    return False

# Set flag for PowerShell environment
IS_POWERSHELL = is_running_in_powershell()

# Instead of trying to create a plain style with QStyle which requires proper style
# formatting strings, we'll take a different approach for PowerShell environments

# For non-PowerShell environments, use the standard colorful style
COLORFUL_STYLE = QStyle([
    ('qmark', 'fg:cyan bold'),         # question mark
    ('question', 'bold'),              # question text
    ('answer', 'fg:green bold'),       # submitted answer text
    ('pointer', 'fg:cyan bold'),       # pointer used in select and checkbox prompts
    ('highlighted', 'fg:cyan bold'),   # pointed-at choice in select and checkbox prompts
    ('selected', 'fg:green'),          # selected choice in checkbox prompts
    ('instruction', 'fg:yellow'),      # user instructions for select, rawselect, checkbox
    ('text', ''),                      # plain text
    ('disabled', 'fg:gray italic')     # disabled choices for select and checkbox prompts
])

# For PowerShell, we'll use a different approach:
# 1. Disable styling completely in PowerShell by setting strip=True in colorama
# 2. Use plain text prompt strings instead of styled ones

# Only use the style for non-PowerShell environments
questionary_style = COLORFUL_STYLE

# Constants
SCRIPT_TIMEOUT = 30  # 30 seconds timeout for PowerShell scripts
VERSION = "1.1.0"

# ASCII art banner (simple)
BANNER = f"""
{Fore.CYAN}{Style.BRIGHT}╔══════════════════════════════════════════════════════╗
║      Visio Temporary File Remover Utility v{VERSION}      ║
╚══════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""

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

def print_status(message, status_type="info"):
    """Print a formatted status message with appropriate colors and symbols"""
    symbols = {
        "info": f"{Fore.BLUE}[i]{Style.RESET_ALL}",
        "success": f"{Fore.GREEN}[+]{Style.RESET_ALL}",
        "warning": f"{Fore.YELLOW}[!]{Style.RESET_ALL}",
        "error": f"{Fore.RED}[x]{Style.RESET_ALL}",
        "question": f"{Fore.MAGENTA}[?]{Style.RESET_ALL}",
        "working": f"{Fore.CYAN}[*]{Style.RESET_ALL}"
    }
    
    colors = {
        "info": Fore.BLUE,
        "success": Fore.GREEN,
        "warning": Fore.YELLOW,
        "error": Fore.RED,
        "question": Fore.MAGENTA,
        "working": Fore.CYAN
    }
    
    symbol = symbols.get(status_type, symbols["info"])
    color = colors.get(status_type, "")
    
    print(f"{symbol} {color}{message}{Style.RESET_ALL}")

def show_spinner(duration=0.5, message="Working"):
    """Show a simple spinner animation for the given duration"""
    spinner_chars = ['|', '/', '-', '\\']
    start_time = time.time()
    i = 0
    
    try:
        while time.time() - start_time < duration:
            sys.stdout.write(f"\r{Fore.CYAN}{spinner_chars[i]} {message}...{Style.RESET_ALL}")
            sys.stdout.flush()
            time.sleep(0.1)
            i = (i + 1) % len(spinner_chars)
        sys.stdout.write("\r" + " " * (len(message) + 15) + "\r")
        sys.stdout.flush()
    except KeyboardInterrupt:
        sys.stdout.write("\r" + " " * (len(message) + 15) + "\r")
        sys.stdout.flush()
        raise

def print_help():
    """Display help information about the tool"""
    help_text = f"""
{Fore.CYAN}{Style.BRIGHT}ABOUT{Style.RESET_ALL}
  This tool helps you find and delete temporary Visio files
  that may be taking up space or causing issues.
  
{Fore.CYAN}{Style.BRIGHT}WORKFLOW{Style.RESET_ALL}
  1. Select or enter a directory to scan
  2. Review found temporary files
  3. Select files to delete
  4. Confirm deletion

{Fore.CYAN}{Style.BRIGHT}FILE PATTERNS{Style.RESET_ALL}
  The tool searches for these Visio temporary file patterns:
    """
    
    print(help_text)
    
    # Load and display the actual patterns from config
    try:
        with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
            patterns = config_data.get('temp_file_patterns', [])
            
            for pattern in patterns:
                print(f"  • {Fore.GREEN}{pattern}{Style.RESET_ALL}")
    except:
        print("  • Could not load patterns from config")
    
    print()
    input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

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
                print_status(f"Ignoring potentially unsafe pattern: {pattern}", "warning")
        
        if not safe_patterns:
            raise ValueError("No valid file patterns found in configuration")
        
        config_data['temp_file_patterns'] = safe_patterns
        return config_data
    except FileNotFoundError:
        print_status(f"Configuration file not found at {CONFIG_FILE_PATH}", "error")
        sys.exit(1)
    except json.JSONDecodeError:
        print_status(f"Could not decode JSON from {CONFIG_FILE_PATH}", "error")
        sys.exit(1)
    except ValueError as ve:
        print_status(f"Error in configuration: {ve}", "error")
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
        print_status(f"Scan script not found at {SCAN_SCRIPT_PATH}", "error")
        return False
    if not REMOVE_SCRIPT_PATH.is_file():
        print_status(f"Remove script not found at {REMOVE_SCRIPT_PATH}", "error")
        return False
    return True

def validate_powershell_available():
    """Check if PowerShell is available on the system"""
    # On Windows, we first check if we're already running in PowerShell
    if platform.system() == 'Windows' and IS_POWERSHELL:
        # We're already in PowerShell, so it's definitely available
        return True
    
    # Try different PowerShell executables
    powershell_cmds = ["powershell", "pwsh"]
    
    for ps_cmd in powershell_cmds:
        try:
            result = subprocess.run(
                [ps_cmd, "-Command", "Write-Output 'PowerShell Test'"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return True
        except (subprocess.SubprocessError, FileNotFoundError):
            continue
    
    # If we're on Windows, PowerShell should always be available
    # So as a last resort, if we're on Windows, we'll assume PowerShell is available
    if platform.system() == 'Windows':
        print_status("PowerShell detection failed, but since we're on Windows, assuming it's available.", "warning")
        return True
        
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
        
        if IS_POWERSHELL:
            choices.append(Choice(title="Enter custom directory path", value="custom"))
            choices.append(Choice(title="Show help information", value="help"))
            choices.append(Choice(title="Exit program", value="exit"))
        else:
            choices.append(Choice(title="Enter custom directory path", value="custom"))
            choices.append(Choice(title="Show help information", value="help"))
            choices.append(Choice(title=f"{Fore.YELLOW}Exit program{Style.RESET_ALL}", value="exit"))

        selection_prompt_message = "Select an option for the directory to scan:"
        if DEFAULT_DIR and not default_path_valid:
            print_status(f"Configured default directory '{DEFAULT_DIR}' is invalid or not accessible.", "warning")
            selection_prompt_message = "Select an option:"
        elif not DEFAULT_DIR:
            print_status("No default directory configured.", "info")
            selection_prompt_message = "Select an option:"

        if IS_POWERSHELL:
            # For PowerShell, use minimal styling to avoid ANSI codes
            action = questionary.select(
                selection_prompt_message,
                choices=choices,
                qmark="?"
            ).ask()
        else:
            # For other terminals, use colorful styling
            action = questionary.select(
                selection_prompt_message,
                choices=choices,
                style=questionary_style,
                qmark=f"{Fore.CYAN}?{Style.RESET_ALL}"
            ).ask()

        if action == "help":
            print_help()
            continue
        elif action == "default":
            if default_path_valid and default_path_obj:
                print_status(f"Using default directory: {DEFAULT_DIR}", "success")
                return default_path_obj.resolve()
            else:
                print_status("Default directory was selected but is invalid or not configured.", "error")
                if IS_POWERSHELL:
                    if questionary.confirm("Try entering a custom path instead? (No to exit)").ask():
                        action = "custom"
                    else:
                        return None
                else:
                    if questionary.confirm("Try entering a custom path instead? (No to exit)", style=questionary_style).ask():
                        action = "custom"
                    else:
                        return None
        
        if action == "custom":
            # Define validation function
            validator = lambda text: True if text and Path(text.strip('"'" ").strip("'")).is_dir() else ("Path is not a valid directory or does not exist." if text else "Input cannot be empty. Press ESC to cancel.")
            
            if IS_POWERSHELL:
                path_str = questionary.text(
                    "Enter the directory path to scan:",
                    validate=validator
                ).ask()
            else:
                path_str = questionary.text(
                    "Enter the directory path to scan:",
                    validate=validator,
                    style=questionary_style
                ).ask()

            if path_str is None:
                print_status("Custom path entry cancelled. Returning to options.", "warning")
                continue
            else:
                chosen_path = Path(path_str.strip('"'" ").strip("'")).resolve()
                print_status(f"Selected directory: {chosen_path}", "success")
                return chosen_path
        elif action == "exit" or action is None:
            return None
        elif action != "custom":
            continue
    return None # Should be unreachable

def find_temp_files(directory: Path, patterns: list[str]) -> list[Path]:
    """Find files using the Scan-VisioTempFiles.ps1 PowerShell script."""
    if not SCAN_SCRIPT_PATH.is_file():
        print_status(f"Scan script not found at {SCAN_SCRIPT_PATH}", "error")
        return []

    dir_str = str(directory)
    
    # Validate parameters before passing to PowerShell
    if not os.path.isdir(dir_str):
        print_status(f"Directory does not exist or is not accessible: {dir_str}", "error")
        return []
    
    # Validate each pattern for safety
    safe_patterns = []
    for pattern in patterns:
        if re.match(r'^[~$*.A-Za-z0-9\-_]+$', pattern):
            safe_patterns.append(pattern)
        else:
            print_status(f"Skipping potentially unsafe pattern: {pattern}", "warning")
    
    if not safe_patterns:
        print_status("No valid safe patterns to scan with.", "error")
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

    print_status(f"Scanning {dir_str} with {len(safe_patterns)} patterns...", "working")
    show_spinner(1, "Starting scan")
    
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
                print_status("PowerShell script error/warning:", "error")
                print(f"{Fore.YELLOW}{completed.stderr.strip()}{Style.RESET_ALL}")

        # Check for empty output
        if not completed.stdout or completed.stdout.strip() == "":
            print_status("PowerShell script returned no output.", "error")
            return []

        # Check if output is valid JSON
        try:
            result_data = json.loads(completed.stdout.strip())
            
            # If we got an empty array, it means no files were found
            if isinstance(result_data, list) and len(result_data) == 0:
                print_status("No matching temporary Visio files found in the specified location.", "info")
                return []
                
            found_files = [Path(item['FullName']) for item in result_data if isinstance(item, dict) and 'FullName' in item]
            print_status(f"Found {len(found_files)} temporary Visio files.", "success")
            return sorted(found_files)
        except json.JSONDecodeError as e:
            print_status(f"Error parsing scan JSON: {e}", "error")
            print(f"{Fore.MAGENTA}Raw STDOUT:\n{completed.stdout.strip()}{Style.RESET_ALL}")
            
            # Despite the JSON error, let's check if we need to show 'no files found' message
            if "No matching" in completed.stdout or completed.stdout.strip() == "[]":
                print_status("No matching temporary Visio files found in the specified location.", "info")
            
            return []
    except subprocess.TimeoutExpired:
        print_status(f"PowerShell script timed out after {SCRIPT_TIMEOUT} seconds.", "error")
        return []
    except FileNotFoundError:
        print_status("'powershell' not found. Ensure it's in PATH.", "error")
        return []
    except Exception as e:
        print_status(f"Unexpected error running scan script: {e}", "error")
        return []
    return [] # Fallback

def display_file_list(file_list: list[Path], base_directory: Path):
    """Display a formatted list of files with numerical index"""
    if not file_list:
        return
    
    print(f"\n{Fore.CYAN}{Style.BRIGHT}Found {len(file_list)} temporary Visio files:{Style.RESET_ALL}")
    print("─" * 80)
    print(f"{Fore.CYAN}{'#':>3} | {'Filename':<30} | {'Location':<40}{Style.RESET_ALL}")
    print("─" * 80)
    
    for i, f_path in enumerate(file_list, 1):
        try:
            rel_parent = f_path.parent.relative_to(base_directory)
        except ValueError:
            rel_parent = f_path.parent # Fallback to absolute if not under base_directory
        
        # Format the filename and location for better readability
        filename = f_path.name
        location = str(rel_parent)
        
        # Truncate if too long
        if len(filename) > 28:
            filename = filename[:25] + "..."
        if len(location) > 38:
            location = "..." + location[-35:]
            
        print(f"{i:>3} | {Fore.GREEN}{filename:<30}{Style.RESET_ALL} | {location:<40}")
    
    print("─" * 80)
    print()

def select_files_for_deletion(file_list: list[Path], base_directory: Path) -> list[Path]:
    """Prompt user to select files to delete."""
    if not file_list:
        print_status("No Visio temp files found.", "info")
        return []
    
    # First display a formatted list of all files
    display_file_list(file_list, base_directory)
    
    # Modify choices based on environment
    choices = []
    if IS_POWERSHELL:
        choices = [
            Choice(title="Select all files", value="all"),
            Choice(title="Select individual files", value="individual"),
            Choice(title="Cancel", value="cancel")
        ]
    else:
        # Use colorful styling for non-PowerShell terminals
        choices = [
            Choice(title="Select all files", value="all"),
            Choice(title="Select individual files", value="individual"),
            Choice(title=f"{Fore.YELLOW}Cancel{Style.RESET_ALL}", value="cancel")
        ]
    
    if IS_POWERSHELL:
        selection_method = questionary.select(
            "How would you like to select files for deletion?",
            choices=choices,
            qmark="?"
        ).ask()
    else:
        selection_method = questionary.select(
            "How would you like to select files for deletion?",
            choices=choices,
            style=questionary_style,
            qmark=f"{Fore.CYAN}?{Style.RESET_ALL}"
        ).ask()
    
    if selection_method == "cancel" or selection_method is None:
        return []
    
    if selection_method == "all":
        return file_list
    
    # For individual selection
    choices = []
    for i, f_path in enumerate(file_list):
        try:
            rel_parent = f_path.parent.relative_to(base_directory)
        except ValueError:
            rel_parent = f_path.parent # Fallback to absolute if not under base_directory
        display = f"{f_path.name} (in {rel_parent})"
        choices.append(Choice(title=display, value=str(f_path))) # Store as string for Q
        
    if IS_POWERSHELL:
        selected_str_paths = questionary.checkbox(
            "Select files to delete (Space to toggle, Enter to confirm):",
            choices=choices,
            # validate=lambda vals: True if vals else "Select at least one file or ESC to cancel."
        ).ask()
    else:
        selected_str_paths = questionary.checkbox(
            "Select files to delete (Space to toggle, Enter to confirm):",
            choices=choices,
            style=questionary_style,
            # validate=lambda vals: True if vals else "Select at least one file or ESC to cancel."
        ).ask()
    
    return [Path(p) for p in selected_str_paths] if selected_str_paths else []

def delete_files(selected_paths: list[Path]):
    """Delete selected files using direct PowerShell commands similar to the web UI's approach."""
    if not selected_paths:
        return

    if not validate_powershell_available():
        print_status("PowerShell is not available on this system.", "error")
        return

    # Display the files selected for deletion in a clear format
    print(f"\n{Fore.YELLOW}{Style.BRIGHT}Files selected for deletion:{Style.RESET_ALL}")
    for i, path in enumerate(selected_paths, 1):
        print(f"{i:>3}. {path.name} ({path.parent})")
    print()

    if IS_POWERSHELL:
        confirm_delete = questionary.confirm(
            f"Are you sure you want to delete these {len(selected_paths)} file(s)?"
        ).ask()
    else:
        confirm_delete = questionary.confirm(
            f"Are you sure you want to delete these {len(selected_paths)} file(s)?",
            style=questionary_style
        ).ask()
    if not confirm_delete:
        print_status("Deletion cancelled by user.", "warning")
        return

    # Validate that all files exist before attempting deletion
    invalid_paths = [p for p in selected_paths if not p.is_file()]
    if invalid_paths:
        print_status("The following files don't exist or are not accessible:", "error")
        for p in invalid_paths:
            print(f"  - {p}")
        if IS_POWERSHELL:
            if not questionary.confirm("Continue with deleting only valid files?").ask():
                print_status("Deletion cancelled by user.", "warning")
                return
        else:
            if not questionary.confirm("Continue with deleting only valid files?", style=questionary_style).ask():
                print_status("Deletion cancelled by user.", "warning")
                return
        # Filter out invalid paths
        selected_paths = [p for p in selected_paths if p.is_file()]
        if not selected_paths:
            print_status("No valid files remaining to delete.", "warning")
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
    
    print_status(f"Deleting {len(file_paths)} files...", "working")
    show_spinner(1.5, "Processing")
    
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
            print_status("PowerShell error output:", "error")
            print(f"{Fore.YELLOW}{completed.stderr.strip()}{Style.RESET_ALL}")
        
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
                
                print("\n" + "─" * 80)
                print(f"{Style.BRIGHT}{Fore.CYAN}DELETION RESULTS{Style.RESET_ALL}")
                print("─" * 80)
                
                if deleted:
                    print(f"{Fore.GREEN}{Style.BRIGHT}Successfully deleted: {len(deleted)}{Style.RESET_ALL}")
                    for path in deleted[:5]:  # Show first 5 only if many
                        print(f"  {Fore.GREEN}+{Style.RESET_ALL} {Path(path).name}")
                    if len(deleted) > 5:
                        print(f"  {Fore.GREEN}...and {len(deleted) - 5} more files{Style.RESET_ALL}")
                
                if failed:
                    print(f"\n{Fore.RED}{Style.BRIGHT}Failed to delete: {len(failed)}{Style.RESET_ALL}")
                    for item in failed:
                        if isinstance(item, dict):
                            path = item.get('Path', 'Unknown')
                            error = item.get('Error', 'Unknown error')
                            print(f"  {Fore.RED}x{Style.RESET_ALL} {Path(path).name}: {error}")
                        else:
                            print(f"  {Fore.RED}x{Style.RESET_ALL} {item}: Unknown error")
                
                print("\n" + "─" * 80)
                print(f"{Style.BRIGHT}Summary:{Style.RESET_ALL} {len(deleted)} deleted, {len(failed)} failed.\n")
            else:
                print_status("Could not find JSON results in PowerShell output. Raw output:", "warning")
                print(completed.stdout)
                
        except json.JSONDecodeError:
            # If JSON parsing fails, just show the raw output
            print_status("Could not parse JSON results. Raw PowerShell output:", "error")
            print(completed.stdout)
            
    except subprocess.TimeoutExpired:
        print_status(f"PowerShell command timed out after {SCRIPT_TIMEOUT} seconds.", "error")
    except Exception as e:
        print_status(f"Unexpected error running delete command: {e}", "error")

def main():
    print(BANNER)
    print(f"{Fore.CYAN}This utility helps you find and remove temporary Visio files.{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Type 'help' at any prompt for more information.{Style.RESET_ALL}\n")

    # Validate environment before starting
    if not validate_powershell_available():
        print_status("PowerShell is not available on this system.", "error")
        print_status("This tool requires PowerShell to run. Please install PowerShell and try again.", "error")
        sys.exit(1)
        
    # Print PowerShell detection info
    if IS_POWERSHELL:
        # Use simpler styling for PowerShell terminals
        print_status("PowerShell environment detected. Using simplified styling for better compatibility.", "info")
    
    if not validate_scripts_exist():
        print_status("Required PowerShell scripts are missing.", "error")
        sys.exit(1)
    
    try:
        while True:
            target_directory = get_directory_to_scan()

            if target_directory is None:
                print_status("Exiting program.", "info")
                break

            print_status(f"Scanning {Style.BRIGHT}{target_directory}{Style.NORMAL} for Visio temporary files...", "working")
            found_temp_files = find_temp_files(target_directory, TEMP_PATTERNS)
            
            if not found_temp_files:
                print_status("No matching temporary Visio files found in the specified location.", "info")
            else:
                files_to_delete = select_files_for_deletion(found_temp_files, target_directory)
                if files_to_delete:
                    delete_files(files_to_delete)
            
            # Make sure no color formatting is used in PowerShell
            if IS_POWERSHELL:
                continue_choice = questionary.select(
                    "What would you like to do next?",
                    choices=[
                        Choice(title="Scan another location", value="scan"),
                        Choice(title="Exit program", value="exit")
                    ],
                    qmark="?"
                ).ask()
            else:
                continue_choice = questionary.select(
                    "What would you like to do next?",
                    choices=[
                        Choice(title="Scan another location", value="scan"),
                        Choice(title=f"{Fore.YELLOW}Exit program{Style.RESET_ALL}", value="exit")
                    ],
                    style=questionary_style,
                    qmark=f"{Fore.CYAN}?{Style.RESET_ALL}"
                ).ask()
            
            if continue_choice != "scan":
                print_status("Thanks for using Visio Temporary File Remover!", "success")
                break
    finally:
        # Re-initialize colorama with proper settings if needed
        init(autoreset=True, convert=True, strip=False, wrap=True)
        # Ensure PowerShell compatibility
        if IS_POWERSHELL:
            # For PowerShell, use strip=True to avoid raw ANSI codes
            init(autoreset=True, convert=True, strip=True, wrap=True)
        elif platform.system() == 'Windows':
            init(autoreset=True, convert=True, strip=False, wrap=True)

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
        try:
            import colorama
            colorama.deinit() # type: ignore
            # Re-init with safe settings for PowerShell
            if IS_POWERSHELL:
                init(autoreset=True, convert=True, strip=True, wrap=True)
        except Exception:
            pass # Ignore any errors when deinitializing
