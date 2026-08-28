from Functions.helpers import IMG_CORRECTOR, ImgCorrect, ImgCheck
from pathlib import Path
from typing import Optional, Union

def VertifyImage(File : Union[Path, str], Log : bool = True) -> Path :
    File = Path(File)
    if File.is_file() :
        res = _file_check(File, Log)
        return res if res is not None else File
    return File

def LocateImages(Paths : list[str], Recursive : bool, Log : bool = True) -> list[Path] :
    '''Convert user input into a list of images'''
    results : list[Path] = []

    for path in _normalize_paths(Paths, Recursive) :
        if path.is_file() : #It's a file
            res = _file_check(path, Log)
            if res is not None :
                results.append(res)

        elif path.is_dir() : #It's directory
            dirs = path.rglob("*.*") if Recursive else path.glob("*.*")
            for _ in dirs :
                res = _file_check(_, Log)
                if res is not None :
                    results.append(res)

        else : #Everything Else
            if Log :
                print(f"\033[38;5;226m{path} does not exist or is not accessible\033[0m")

    return results

def _normalize_paths(paths: list[str], recursive: bool) -> list[Path]:
    normalized = list(dict.fromkeys(Path(p).resolve() for p in paths))

    if not recursive:
        return normalized

    return [
        path
        for path in normalized
        if not any(
            other != path and other in path.parents
            for other in normalized
        )
    ]

def _file_check(path: Path, Log: bool) -> Optional[Path]:
    """Validate and correct an image file."""
    try:
        check = ImgCheck(path)
        if check == "unknown":
            return None
        
        res = ImgCorrect(path, check)
        if (res != path) and Log:
            print(f"\033[38;5;196m{path.name} is actually {res.name}\033[0m")
        return res
    except Exception as e:
        if Log:
            print(f'\033[38;5;226m{path} failed to process : {e}\033[0m')
        return None
