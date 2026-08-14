#!/usr/bin/env python3

from pathlib import Path
import argparse
import shutil
import subprocess
import sys

PROGRAM = "ArchiveExtractor"

SUPPORTED_EXTENSIONS = {
    ".zip",
    ".rar",
    ".7z",
    ".tar",
    ".gz",
    ".bz2",
    ".xz",
    ".iso",
}


def find_7zip() -> str:
    """
    Locate 7z executable.
    """

    candidates = [
        shutil.which("7z"),
        r"C:\Program Files\7-Zip\7z.exe",
        r"C:\Program Files (x86)\7-Zip\7z.exe",
    ]

    for exe in candidates:
        if exe and Path(exe).exists():
            return exe

    raise FileNotFoundError("7z.exe not found. Please install 7-Zip.")


def find_archives(root: Path):
    for file in root.rglob("*"):
        if file.is_file() and file.suffix.lower() in SUPPORTED_EXTENSIONS:
            yield file


def extract_archive(sevenzip: str, archive: Path, destination: Path):
    destination.mkdir(parents=True, exist_ok=True)

    cmd = [
        sevenzip,
        "x",
        "-y",
        f"-o{destination}",
        str(archive),
    ]

    result = subprocess.run(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        print(f"ERROR: {archive}")
        print(result.stderr)
        return False

    return True


def main():

    parser = argparse.ArgumentParser(
        description="Extract archives while preserving folder structure."
    )

    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="Source folder",
    )

    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="Destination folder",
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Re-extract existing folders",
    )

    args = parser.parse_args()

    source = Path(args.input).resolve()
    destination_root = Path(args.output).resolve()

    if not source.exists():
        sys.exit("Input folder does not exist.")

    destination_root.mkdir(parents=True, exist_ok=True)

    sevenzip = find_7zip()

    archives = list(find_archives(source))

    total = len(archives)

    if total == 0:
        print("No archives found.")
        return

    print(f"Found {total} archives.\n")

    extracted = 0
    skipped = 0
    failed = 0

    for index, archive in enumerate(archives, start=1):

        relative_parent = archive.parent.relative_to(source)

        target = (
            destination_root /
            relative_parent /
            archive.stem
        )

        print(f"[{index}/{total}] {archive.relative_to(source)}")

        if target.exists() and any(target.iterdir()) and not args.overwrite:
            print("    Skipped (already extracted)")
            skipped += 1
            continue

        if extract_archive(sevenzip, archive, target):
            extracted += 1
        else:
            failed += 1

    print("\nDone.")
    print(f"Extracted : {extracted}")
    print(f"Skipped   : {skipped}")
    print(f"Failed    : {failed}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelled.")