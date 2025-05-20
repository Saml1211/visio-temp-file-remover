# Visio Temp File Remover - Project Brief

## Project Overview
The Visio Temp File Remover is a utility designed to find and delete temporary files created by Microsoft Visio. The project integrates two previously separate tools—a Python CLI application and a Node.js web application—into a unified codebase that shares common PowerShell scripts for core file operations.

## Problem Statement
Microsoft Visio creates temporary backup files (with patterns like `~$$*.vsdx`) during editing, which can accumulate in work directories. These files:
- Consume unnecessary disk space
- Create confusion when browsing directories
- May cause version control issues when accidentally committed

Users need a reliable, secure way to identify and remove these temporary files from specified directories, with both command-line and web-based interfaces available.

## Core Requirements

### Functional Requirements
1. **File Discovery**: Scan directories to locate Visio temporary files matching specific patterns
2. **File Selection**: Allow users to review and select which files to delete
3. **File Deletion**: Safely remove selected files with proper validation and error handling
4. **Dual Interface**: Provide both a command-line interface and a web interface
5. **Shared Core Logic**: Use common PowerShell scripts for file operations across interfaces

### Non-Functional Requirements
1. **Security**: Prevent command injection and unauthorized access to system directories
2. **Reliability**: Handle errors gracefully, validate inputs, and provide clear feedback
3. **Maintainability**: Follow consistent code patterns and provide documentation
4. **Performance**: Efficiently scan large directories with minimal resource usage
5. **Configurability**: Support different environments and directory paths

## Target Users
- Engineering teams working with Visio diagrams
- System administrators managing shared Visio template directories
- Individual Visio users seeking to clean up their working directories

## Constraints
- Windows-only application due to PowerShell dependency
- Requires appropriate permissions to scan and modify target directories
- Must maintain compatibility with existing usage patterns and expectations

## Success Criteria
1. Successfully identifies all Visio temporary files in target directories
2. Reliably deletes selected files without affecting other files
3. Provides clear feedback on operations through both interfaces
4. Maintains security with proper input validation and error handling
5. Offers an intuitive experience in both CLI and web interfaces 