# CLI Utils 🛠️

A comprehensive CLI utility suite for media processing, file management, and system operations on Windows.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)

## 📋 Table of Contents

- [Features](#-features)
- [Requirements](#-requirements)
- [Installation](#-installation)
- [Usage](#-usage)
- [Scripts](#-scripts)
- [External Programs](#-external-programs)
- [License](#-license)
- [Credits](#-credits)
- [Notes](#notes)

## ✨ Features

### Video Processing
- **Compression** - Optimize video files with adjustable CRF/bitrate
- **Comparison** - Analyze and compare video quality
- **Cover Art** - Embed, extract, or remove cover art from videos
- **FFmpeg Integration** - Leverage powerful FFmpeg capabilities

### Image Optimization
- **Lossless Compression** - Optimize PNG, JPG, and WEBP files
- **Multiple Optimizers** - oxipng, ect, jpegoptim, cwebp
- **Batch Processing** - Process multiple files simultaneously
- **Metadata Handling** - Preserve or manipulate EXIF data

### PDF Creation
- **Image to PDF** - Convert images to PDF documents
- **Metadata Embedding** - Add metadata to PDF files
- **Cross-platform Support** - Works with various image formats

### Archive Management
- **7-Zip Integration** - Extract and compress archive files
- **File Listing** - List and analyze file types and sizes

### System Utilities
- **File Operations** - Move, copy, and manage files
- **Path Management** - Handle file paths efficiently
- **Console Enhancement** - Colored console output

## 📋 Requirements

### Python Dependencies
```bash
pip install pillow>=12.3.0 pymupdf>=1.28.2 tqdm>=4.70.1 yt-dlp
```

### External Programs (Required)
| Program | Purpose | Install Command |
|---------|---------|-----------------|
| `ffmpeg` | Video encoding/decoding | `winget install ffmpeg` |
| `7-Zip` | Archive extraction | `winget install 7zip` |
| `exiftool` | Metadata extraction | `winget install exiftool` |

### Optional Programs (Enhanced Features)
- Some script still requried them though

| Program | Purpose |
|---------|---------|
| `oxipng.exe` | PNG optimization |
| `jpegoptim.exe` | JPEG optimization |
| `cwebp.exe` | WEBP conversion |
| `cjxl.exe` | JPEG-XL conversion |
| `ect.exe` | PNG optimization |

## 🚀 Installation

### Step 1: Install Python
Ensure Python 3.8+ is installed on your system.

### Step 2: Install External Programs
```powershell
winget install ffmpeg
winget install 7zip
winget install exiftool
```

### Step 3: Install Python Dependencies
```powershell
pip install -r Notes/python_requirements.txt
```

### Step 4: Add to PATH (Optional)
```powershell
AddToPath_CLI Utils.bat
```

## 📖 Usage

### Quick Start
1. Clone the repository
2. Activate virtual environment
3. Install dependencies
4. Run scripts from the Scripts folder

### Example Commands
```powershell
# Image optimization
python Scripts/imgopt.py -i "C:\Images"

# Video compression
python Scripts/ffcomp.py -i "C:\Videos"

# Archive extraction
python Scripts/archive-extractor.py -i "archive.zip" -o "extracted"

# PDF creation
python Scripts/mkpdf.py -i "images" -o "document.pdf"
```

## 📁 Scripts

| Script | Description |
|--------|-------------|
| `imgopt.py` | Image optimization (PNG, JPG, WEBP) |
| `ffcomp.py` | Video compression and encoding |
| `ffcompare.py` | Video quality comparison |
| `ffcover.py` | Cover art management |
| `archive-extractor.py` | Archive file extraction |
| `deb.py` | File management utilities |
| `filelist.py` | File listing and analysis |
| `imgconv.py` | Image format conversion |
| `movin.py` | File movement operations |
| `mkpdf.py` | PDF creation from images |

## 🔧 External Programs

See [`Notes/Refs.txt`](Notes/Refs.txt) for a complete list of all required and optional programs.

### Installation Guide
```powershell
# Install all required programs
winget install ffmpeg
winget install 7zip
winget install exiftool

# Optional: Image optimizers
winget install oxipng

# Verify installations
ffmpeg -version
7z -v
exiftool --version
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Third-Party Dependencies
- **pillow** - BSD 3-Clause License
- **pymupdf** - BSD 3-Clause License
- **tqdm** - MIT License

All external programs (ffmpeg, 7-Zip, exiftool) are open source and MIT-friendly.

## 🙏 Credits

### Based On
- FFmpeg - Video processing library
- Pillow - Python imaging library
- PyMuPDF - PDF manipulation
- tqdm - Progress bar library

### Tools
- winget - Windows Package Manager
- 7-Zip - Archive utility
- EXIFTool - Metadata tool
- oxipng - PNG optimizer
- cwebp - WebP encoder

## Notes
- All executables are not included
- I provided a luncher that can be used for lunching python scripts in Scripts/Code Base/luncher.cpp
### How to use luncher
- Building 
```powershell
g++ ./luncher.cpp -o luncher.exe 
```
- Place it inside root folder and rename it to match the script's name
- Run it

## 📄 Documentation

- [References](Notes/Refs.txt) - Complete list of required programs
- [Requirements](Notes/python_requirements.txt) - Python dependencies
- [README.md](README.md) - This file

---