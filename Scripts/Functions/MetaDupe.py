from pathlib import Path
import subprocess
from dataclasses import dataclass

@dataclass
class RunResult :
    exitcode : int
    stdout : str
    stderr : str

def MetaDupe_Image (Source : Path, Target : Path) -> RunResult:
    """
    Dupelicates all avaliable metadata from an image to another
    """
    COMMAND = [
        "exiftool", 
        "-TagsFromFile", Source, 
        "-all:all<all:all", 
        "-P", "-m", 
        "-overwrite_original", Target
    ]

    res = subprocess.run(
        COMMAND,
        capture_output=True,
        text=True,
    )

    return RunResult(
        res.returncode, 
        res.stdout, 
        res.stderr
    )
