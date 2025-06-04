# Product Context: Visio Temp File Remover

## Project Purpose

### Problem & Solution
The Visio Temp File Remover addresses a specific operational challenge faced by teams and individuals who work with Microsoft Visio. During Visio editing sessions, the application creates temporary backup files (identifiable by patterns like `~$$*.vsdx`) in the working directory. These files serve as automatic backups but are rarely needed after the editing session concludes.

The accumulation of these files creates several problems:
1. Cluttered file repositories that make finding the actual Visio files difficult
2. Wasted storage space, especially in network shares with many users
3. Confusion when browsing directories or when multiple editors work in the same location
4. Potential for these temporary files to be accidentally committed to version control

This tool provides a streamlined way to identify and remove these temporary files, offering both command-line and web-based solutions to accommodate different user preferences and scenarios.

### Historical Context
The project originated as two separate tools:
1. A Python CLI tool for individual users and automation scripts
2. A Node.js web application for team use and less technical users

These tools had similar purposes but were maintained separately, leading to duplicate effort and inconsistent behavior. The current project unifies these implementations by creating shared PowerShell scripts for core file operations, with the Python and Node.js components serving as interface layers.

## User Experience Goals

### CLI Interface
The CLI interface prioritizes:
- **Efficiency**: Quick operation with minimal steps
- **Scriptability**: Ability to be incorporated into automation workflows
- **Control**: Fine-grained selection of which files to remove
- **Safety**: Clear confirmation before file deletion
- **Visibility**: Clear feedback on what files were found and deleted

### Web Interface
The web interface focuses on:
- **Accessibility**: Easy to use for non-technical users, with improved visual clarity and responsive design for various screen sizes.
- **Clarity**: Visual representation of files for easier identification, enhanced by a polished and intuitive user interface with consistent styling and dark mode support.
- **Safety**: Clear confirmation before file deletion.
- **Collaboration**: Suitable for teams working in shared directories.
- **Simplicity**: Minimal setup and configuration required.

## User Workflows

### Primary Use Cases
1. **Routine Cleanup**: Users periodically removing accumulated temp files
2. **Pre-Sharing Cleanup**: Tidying directories before sharing with colleagues
3. **Space Recovery**: Freeing disk space by removing unnecessary files
4. **Directory Preparation**: Cleaning workspace before beginning new work

### Typical User Workflow
1. User specifies a directory to scan for temporary Visio files
2. System scans the directory and identifies matching files
3. User reviews the list of found files and selects which to delete
4. System removes selected files with appropriate validation
5. System confirms successful deletions and reports any failures

## Business Context

### Value Proposition
- **Time Savings**: Reduces time spent manually identifying and deleting temp files
- **Reduced Errors**: Minimizes risk of accidentally deleting important files
- **Storage Efficiency**: Recovers wasted disk space, particularly valuable for network shares
- **Cleaner Repositories**: Maintains tidy directories for better productivity
- **Dual Interface**: Accommodates both technical users (CLI) and non-technical users (web)

### Target Environments
- Corporate engineering departments
- Technical documentation teams
- Diagram-heavy project teams
- System integration consulting firms
- Individual power users of Visio

## Integration and Dependencies

The solution has been designed to operate with minimal dependencies:
- Requires Windows environment with PowerShell
- CLI requires Python with minimal dependencies
- Web UI requires Node.js and basic web browser support
- Both interfaces share configuration for consistency
- Core file operations handled by PowerShell scripts for security and performance 