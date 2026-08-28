# CLI Utils

A collection of command-line utility tools with Python automation scripts.

## 📋 Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Directory Structure](#directory-structure)
- [Usage](#usage)
- [Scripts](#scripts)
- [Notes](#notes)
- [Contributing](#contributing)
- [License](#license)

---

## 📋 Overview

**CLI Utils** is a utility collection that provides:
- **Executable callers** (`.exe` files) - Spawn processes and pass parameters
- **Python automation scripts** - Manage, invoke, and orchestrate the executables
- **Path integration** - The project root directory is added to `%PATH%` for easy access

### 🎯 Key Features

| Feature | Description |
|---------|-------------|
| **Executable Callers** | `.exe` files that wrap Python scripts |
| **Python Automation** | Python scripts in `/Scripts/` for orchestration |
| **Path Integration** | Project root added to `%PATH%` environment variable |
| **Multi-format Support** | Supports batch (`.bat`) and PowerShell (`.ps1`) automation |

---

## 📥 Installation

### Prerequisites

- Python 3.x (for scripts)
- Visual Studio C++ Redistributable (for `.exe` dependencies)
- Windows 10/11 (Windows-specific tools)

### Setup

1. **Clone/Extract** the project
2. **Verify dependencies**: Ensure all `.exe` files are present
3. **Add to PATH**: The project root is automatically added to `%PATH%`

---

## 📁 Directory Structure

```
CLI Utils/
├── .gitignore              # Git ignore rules
├── .vscode/                # VS Code configuration
├── Notes/                   # Text files and references
│   └── Refs.txt            # Documentation references
├── Scripts/                 # Python automation scripts
│   ├── archive-extractor.py
│   ├── CLI Utils.code-workspace
│   ├── Code Base/          # Source code (optional)
│   ├── Colors/             # Console utilities
│   ├── deb.py
│   ├── ffcomp.py
│   ├── ffcompare.py
│   ├── ffcover.py
│   ├── filelist.py
│   ├── Functions/          # Helper functions
│   │   ├── Checkers.py
│   │   ├── fffunctions.py
│   │   ├── ffpresets.py
│   │   └── helpers.py
│   ├── imgconv.py
│   ├── mkpdf.py
│   ├── movin.py
│   ├── Projects/           # Project-specific scripts
│   │   └── imgconv/
│   │       ├── Path_Builder.py
│   │       └── Program_Check.py
│   ├── Runner.aes          # Encryption utility
│   └── [various .py files] # Automation scripts
├── [exe files]              # Executable callers (see Usage)
└── [batch/ps1 scripts]      # Windows automation
```

### 📂 Directory Purpose

| Directory | Purpose |
|-----------|---------|
| `Scripts/` | **Active Python scripts** (not source code) |
| `Notes/` | Documentation, references, and text files |
| Root | `.exe` files and PATH integration |

---

## 🚀 Usage

### Executable Callers

Each `.exe` file acts as a **caller** that:
- Spawns a Python process
- Passes parameters to the corresponding Python script
- Executes the automation task

### Execution Pattern

```bash
# Basic usage
python "./Scripts/[exe name]" [Parameters]

# Example
python "./Scripts/filelist.py" --list --output results.txt

# Or directly invoke the exe file
filelist.exe --list --output results.txt
```

### Common Executables

| Executable | Description |
|------------|-------------|
| `ffcomp.exe` | FFmpeg compression |
| `ffcompare.exe` | FFmpeg comparison |
| `ffcover.exe` | FFmpeg cover extraction |
| `imgconv.exe` | Image conversion |
| `imgopt.exe` | Image optimization |
| `mkpdf.exe` | PDF generation |
| `movin.exe` | File movement |
| `zopfli.exe` | Compression |
| `zopflipng.exe` | PNG compression |
| `oxipng.exe` | PNG optimization |
| `cjxl.exe` | JPEG-XL conversion |
| `aomenc.exe` | AV1 encoding |
| `PathDump.exe` | Path dumping |
| `filelist.exe` | File listing |
| `random.exe` | Random utilities |
| `deb.exe` | Deb package creation |
| `SvtAv1EncApp.exe` | SVT-AV1 encoding |

---

## 🐍 Scripts

### Script Organization

#### `/Scripts/Functions/`
Contains helper functions and utilities:
- `Checkers.py` - Validation and checking utilities
- `fffunctions.py` - FFmpeg-specific functions
- `ffpresets.py` - FFmpeg preset configurations
- `helpers.py` - General helper functions

#### `/Scripts/Colors/`
Console color utilities:
- `ConsoleColors.py` - ANSI color formatting

#### `/Scripts/Projects/`
Project-specific implementations:
- `imgconv/` - Image conversion project

#### `/Scripts/Code Base/`
Optional source code (not active scripts):
- `762MB Bomb.cpp` - Performance test
- `luncher.cpp` - Launcher source
- `TEST.py` - Test suite

---

## 📝 Notes

Located in `/Notes/`:
- **Refs.txt** - Reference documentation and links
- Additional text files for project references

---

## 🔧 Automation Scripts

### Batch Files (`.bat`)
- `AddToPath_CLI Utils.bat` - Adds project to PATH
- `tomp4.bat` - Convert to MP4
- `restartexplorer.bat` - Restart Explorer

### PowerShell Scripts (`.ps1`)
- `ytdl.ps1` - YouTube downloader
- `ytmdl.ps1` - YouTube Media Downloader

---

## 🛠️ Development

### Python Dependencies

Check `Scripts/` directory for specific requirements. Most scripts use:
- Standard Python library
- Additional dependencies as needed

### Testing

Test scripts individually:
```bash
# Test a single script
python "./Scripts/filelist.py" --help

# Run with specific parameters
python "./Scripts/imgconv.py" --input image.jpg --output output.jpg
```

### Debugging

1. Check Python logs in `Scripts/`
2. Use `python -v` for verbose output
3. Enable debugging in VS Code (`.vscode/` folder)

---

## 🤝 Contributing

### Guidelines

1. **Add scripts to `/Scripts/`** (not root)
2. **Create matching `.exe` callers** in root
3. **Document in `/Notes/`** or README
4. **Update PATH integration** if needed

### Pull Request Requirements

- ✅ Update `README.md`
- ✅ Add to `/Notes/` if documentation exists
- ✅ Test all functionality
- ✅ Ensure Python dependencies are documented

---

## 📄 License

This project is licensed under the MIT License.  
See `/Notes/Refs.txt` for license details.

---

## 📧 Support

For issues or questions:
1. Check `/Notes/Refs.txt` for documentation
2. Review Python script error messages
3. Use PowerShell/Command Prompt for debugging

---

## 📚 References

- **Python Documentation**: https://docs.python.org/
- **FFmpeg**: https://ffmpeg.org/
- **VS Code**: https://code.visualstudio.com/

---

**Last Updated**: 2024  
**Project Status**: Active Development
