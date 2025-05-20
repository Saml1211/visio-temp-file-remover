# System Patterns: Visio Temp File Remover

## Architecture Overview

The Visio Temp File Remover follows a layered architecture with shared core logic:

```
┌───────────────────┐  ┌───────────────────┐
│  Python CLI Tool  │  │  Node.js Web App  │
│   (Interface)     │  │   (Interface)     │
└─────────┬─────────┘  └─────────┬─────────┘
          │                      │
          │                      │
          ▼                      ▼
┌─────────────────────────────────────────┐
│       Shared Configuration (JSON)        │
└─────────────────────┬───────────────────┘
                      │
                      │
                      ▼
┌─────────────────────────────────────────┐
│      PowerShell Script Backend          │
│  (Core File Operations & Business Logic) │
└─────────────────────────────────────────┘
```

This architecture separates the user interfaces (CLI and web) from the core business logic, which is implemented in PowerShell scripts. Both interfaces use the same configuration and scripts, ensuring consistent behavior.

## Design Patterns

### 1. Layered Architecture
- **Interface Layer**: Python CLI and Node.js web app handle user interaction
- **Business Logic Layer**: PowerShell scripts perform file operations
- **Configuration Layer**: Shared JSON files for consistent settings

### 2. Command Pattern
Both interfaces implement a command pattern to execute operations:
- **Commands**: Scan for files, Delete files
- **Invoker**: CLI and web app interfaces
- **Receiver**: PowerShell scripts

### 3. Facade Pattern
The PowerShell scripts present a simplified interface for complex file operations:
- `Scan-VisioTempFiles.ps1`: Encapsulates directory scanning and file pattern matching
- `Remove-VisioTempFiles.ps1`: Handles file deletion with validation and error handling

### 4. Strategy Pattern
The system uses different strategies for user interaction based on the interface:
- CLI: Interactive questionary-based selection
- Web: Checkbox-based selection in HTML interface

## Component Relationships

### Configuration Sharing
Both the CLI tool and web app read from the same configuration files:
- `config.json`: Base configuration
- `config.[environment].json`: Environment-specific overrides

This ensures consistent behavior and simplifies maintenance.

### Process Execution Model
```
┌───────────────┐     ┌─────────────┐     ┌───────────────┐
│ UI Component  │────►│ Subprocess  │────►│ PowerShell    │
│ (Python/Node) │     │ Execution   │     │ Scripts       │
└───────┬───────┘     └─────────────┘     └───────┬───────┘
        │                                          │
        │             ┌─────────────┐              │
        └────────────►│ JSON Parse  │◄─────────────┘
                      │ Results     │
                      └─────────────┘
```

Both interfaces execute PowerShell scripts as subprocesses, passing parameters and receiving JSON output for consistent data interchange.

## Key Technical Decisions

### PowerShell for Core Operations
- **Rationale**: PowerShell provides powerful file system operations and is available on all Windows systems
- **Advantage**: Superior performance for file operations compared to Python/Node.js
- **Trade-off**: Windows-only support, additional process execution overhead

### Shared Configuration Files
- **Rationale**: Maintain consistency between interfaces
- **Implementation**: JSON format for easy parsing in both Python and Node.js
- **Extension**: Support for environment-specific configuration variants

### JSON-Based Interprocess Communication
- **Rationale**: Structured data format compatible with all components
- **Implementation**: PowerShell scripts output JSON, which is parsed by the interfaces
- **Benefit**: Type-safe data transfer with object serialization/deserialization

### Security Focus
- **Implementation**: Input validation at multiple levels:
  - Interface-level validation
  - Script-level validation
  - Pattern restriction for file matching
  - Protected path verification to prevent system file deletion

## Scalability Considerations

The architecture supports scalability in several dimensions:

### 1. Directory Size Scaling
- Efficient PowerShell file scanning with filtering
- Pagination capabilities in web UI for large file lists
- Timeout handling to prevent hanging on very large directories

### 2. Functional Expansion
- New file operations can be added as additional PowerShell scripts
- Interfaces can be extended independently while maintaining shared core

### 3. Multi-User Support
- Web interface designed for multiple concurrent users
- Resource usage monitoring for high-load scenarios 