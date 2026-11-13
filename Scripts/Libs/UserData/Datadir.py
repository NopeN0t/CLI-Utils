from pathlib import Path

def _find_project_root(start: Path) -> Path:
    current = start
    while current.parent != current:
        if current.name == "Scripts":
            return current.parent
        current = current.parent
    raise RuntimeError("Could not locate project root ('Scripts' folder not found)")

_PROJECT_ROOT = _find_project_root(Path(__file__).resolve().parent)

def GetUserDataDir(name : str) -> Path :
    '''Get folder path with given name'''
    p = Path(name)

    if p.is_absolute() or ".." in p.parts :
        raise ValueError(f"Unsafe name {name!r}") #Show exact string
    
    dir = _PROJECT_ROOT / "Scripts" / "UserData" / name
    dir.mkdir(parents=True, exist_ok=True)
    return dir