print(
    "NOTE: This script uses 'questionary' for interactive prompts."
    "\nIt also uses 'colorama' for colored output."
    "\nIf you see an ImportError, run:"
    "\n  pip install questionary colorama\n"
)

import os
import subprocess
import glob
import platform
import sys
from pathlib import Path

import questionary
from questionary import Choice
from colorama import Fore, Style
import colorama
colorama.init()

# Editable: Patterns for Visio temp/backup files
TEMP_PATTERNS = [
    '~$$*.vssx',
    '~$$*.vsdx',
    '~$$*.vstx',
    '~$$*.vsdm',
    '~$$*.vsd',
]

DEFAULT_DIR = r'Z:\ENGINEERING TEMPLATES\VISIO SHAPES 2025'

def get_directory_to_scan():
    """
    Prompts the user to choose a directory for scanning.
    Returns a Path object if a directory is selected, or None if the user cancels/exits.
    """
    while True:
        default_path_obj = Path(DEFAULT_DIR)
        default_path_valid = default_path_obj.is_dir()

        choices = []
        if default_path_valid:
            choices.append(Choice(title=f"Default: {DEFAULT_DIR}", value="default"))
        choices.append(Choice(title="Enter custom directory path", value="custom"))
        choices.append(Choice(title="Exit program", value="exit"))

        selection_prompt_message = "Select an option for the directory to scan:"
        if not default_path_valid and DEFAULT_DIR: # Also check if DEFAULT_DIR is set
            selection_prompt_message = (
                f"{Fore.YELLOW}Configured default directory '{DEFAULT_DIR}' is invalid or not accessible.{Style.RESET_ALL}\n"
                "Select an option:"
            )
        elif not DEFAULT_DIR: # DEFAULT_DIR is empty
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
            if default_path_valid:
                print(f"{Fore.GREEN}Using default directory: {DEFAULT_DIR}{Style.RESET_ALL}")
                return default_path_obj.resolve()
            else:
                # This case should ideally not be hit if choice isn't offered, but defensive
                print(f"{Fore.RED}Error: Default directory was selected but is invalid. Please report this issue.{Style.RESET_ALL}")
                # Potentially offer to enter custom path or exit
                if questionary.confirm("Try entering a custom path instead? (No to exit)").ask():
                    action = "custom" # Fall through to custom path logic
                else:
                    return None
                # continue # Re-prompt selection (or fall through to custom if modified)
        
        if action == "custom": # Handles fall-through from invalid default if user agrees
            path_str = questionary.text(
                "Enter the directory path to scan:",
                validate=lambda text: True if text and Path(text.strip('"').strip("'")).is_dir()
                                   else ("Path is not a valid directory or does not exist."
                                         if text else "Input cannot be empty. Press ESC to cancel."),
            ).ask()

            if path_str is None: # User pressed Esc during text input
                print(f"{Fore.YELLOW}Custom path entry cancelled. Returning to options.{Style.RESET_ALL}")
                continue # Go back to "Select an option"
            else:
                chosen_path = Path(path_str.strip('"').strip("'")).resolve()
                print(f"{Fore.GREEN}Selected directory: {chosen_path}{Style.RESET_ALL}")
                return chosen_path
        elif action == "exit" or action is None: # User chose Exit or Esc'd select prompt
            return None
        # If action was 'default' but invalid, and user chose not to enter custom, loop continues if not returned None.
        # Adding an explicit continue here if for some reason action isn't covered, to prevent dead states.
        elif action != "custom": # e.g. if default path invalid and user chose no to custom
            continue


def find_temp_files(directory, patterns):
    """Find files matching Visio temp patterns in directory (platform aware)."""
    files = set()
    dir_str = str(directory)
    try:
        if platform.system().lower() == "windows":
            if not patterns:
                print(f"{Fore.RED}No patterns defined to search for.{Style.RESET_ALL}")
                return []

            # Build the -like clauses for the Where-Object
            like_clauses = []
            for pat in patterns:
                # Escape single quotes in pattern for PowerShell, though current patterns don't need it.
                # PowerShell uses single quotes for literal strings. If a pattern had one, it'd need doubling: ' -> ''
                ps_pattern = pat.replace("'", "''")
                like_clauses.append(f"($_.Name -like '{ps_pattern}')")
            
            if not like_clauses:
                print(f"{Fore.RED}No valid PowerShell -like clauses generated from patterns.{Style.RESET_ALL}")
                return []

            where_clause = " -or ".join(like_clauses)

            # Command string
            ps_cmd = (
                f"Get-ChildItem -Path '{dir_str}' -Recurse -Force -File "
                f"| Where-Object {{ {where_clause} }} "
                f"| Select-Object -ExpandProperty FullName"
            )
            print(f"{Fore.YELLOW}Running PowerShell command: {ps_cmd}{Style.RESET_ALL}")
            completed = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_cmd],
                capture_output=True,
                text=True,
                check=False,
            )
            if completed.returncode != 0:
                print(f"{Fore.RED}PowerShell error!{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}STDOUT:\n{completed.stdout}{Style.RESET_ALL}")
                print(f"{Fore.RED}STDERR:\n{completed.stderr}{Style.RESET_ALL}")
                return []

            # Python-side filtering
            candidate_files = completed.stdout.splitlines()
            for line in candidate_files:
                if not line.strip():
                    continue
                
                p = Path(line.strip())
                file_name = p.name

                # Find the index of the last dot to separate base name and extension
                try:
                    dot_index = file_name.rindex('.')
                    base_name_part = file_name[:dot_index]
                    # file_ext_part = file_name[dot_index:] # Not strictly needed for this logic
                except ValueError:
                    # No dot found, or filename might be like ".bashrc"
                    # This file structure is not expected for Visio temp files
                    continue

                # Check if base_name_part starts with '~$$'
                if base_name_part.startswith("~$$"):
                    files.add(p)
        else:
            # Fallback glob (not as robust for hidden files)
            for pat in patterns:
                for fname in glob.glob(str(directory / "**" / pat), recursive=True):
                    files.add(Path(fname))
    except Exception as e:
        print(
            f"{Fore.RED}Error during file scan: {e}{Style.RESET_ALL}"
        )
        return []
    return sorted(files)

def select_files_for_deletion(file_list, base_directory):
    """Prompt user to select files to delete."""
    if not file_list:
        print(
            f"{Fore.GREEN}No Visio temp files found in the selected directory.{Style.RESET_ALL}"
        )
        return []
    choices = []
    for f in file_list:
        try:
            rel_parent = f.parent.relative_to(base_directory)
        except ValueError:
            rel_parent = f.parent
        display = f"{f.name} (in {rel_parent})"
        choices.append(Choice(title=display, value=str(f)))
    selected = questionary.checkbox(
        "Select files to delete:",
        choices=choices,
        validate=lambda vals: True if vals else "Select at least one file or ESC to cancel."
    ).ask()
    return selected or []

def delete_files(selected_paths):
    """Delete selected files with user confirmation and reporting."""
    if not selected_paths:
        return
    confirm = questionary.confirm(
        f"Are you sure you want to delete {len(selected_paths)} selected file(s)?"
    ).ask()
    if not confirm:
        print(f"{Fore.YELLOW}Deletion cancelled by user.{Style.RESET_ALL}")
        return
    deleted = []
    failed = []
    for path_str in selected_paths:
        try:
            os.remove(path_str)
            deleted.append(path_str)
        except Exception as e:
            failed.append((path_str, str(e)))
    if deleted:
        print(f"{Fore.GREEN}Successfully deleted the following file(s):{Style.RESET_ALL}")
        for f in deleted:
            print(f"  - {f}")
    if failed:
        print(f"\n{Fore.RED}Failed to delete the following file(s):{Style.RESET_ALL}")
        for f, reason in failed:
            print(f"  - {f}: {reason}")
    print(
        f"\n{Style.BRIGHT}Summary:{Style.RESET_ALL} {len(deleted)} deleted, {len(failed)} failed.\n"
    )

def main():
    print(
        f"{Fore.CYAN}Welcome to the Visio Temporary File Remover Wizard!{Style.RESET_ALL}"
    )
    while True:
        directory_to_scan = get_directory_to_scan()

        if directory_to_scan is None: # User chose to exit from get_directory_to_scan
            print(f"{Fore.CYAN}Exiting program.{Style.RESET_ALL}")
            break

        print(f"{Fore.BLUE}Scanning {Style.BRIGHT}{directory_to_scan}{Style.NORMAL} for temporary Visio files...{Style.RESET_ALL}")
        files = find_temp_files(directory_to_scan, TEMP_PATTERNS)
        to_delete = select_files_for_deletion(files, directory_to_scan)
        if to_delete:
            delete_files(to_delete)
        
        again_q = questionary.confirm("Would you like to scan another location?", default=True, qmark="?")
        again = again_q.ask()
        if not again:
            print(f"{Fore.CYAN}Exiting program.{Style.RESET_ALL}")
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Program interrupted by user. Exiting.{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}An unexpected error occurred: {e}{Style.RESET_ALL}")
        # Consider logging the traceback here for debugging
        # import traceback
        # traceback.print_exc()
    finally:
        colorama.deinit() 