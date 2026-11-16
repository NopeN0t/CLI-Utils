import argparse, sys, os, shutil, time
from Functions.helpers import Alert, SizeToStr
from Colors.ConsoleColors import ConsoleColors as CC
from typing import Dict, Any

PROGRAM = "movin"
NOW = time.time()
SKIP_EXT = (".tmp", ".crdownload", ".part")


def Get_Arguments() -> Dict[str, Any]:
    parser = argparse.ArgumentParser(
        description="Moves files between folders",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("source", metavar="SOURCE", help="Source Folder")
    parser.add_argument("destination", metavar="DEST", help="Where to move to")

    parser.add_argument("-l", "--dry-run", action="store_true", help="List file only")
    parser.add_argument(
        "-r", "--replace", action="store_true", help="Replace destination file"
    )
    parser.add_argument(
        "-fl",
        "--flatten",
        action="store_true",
        help="Do not preserve directory structure",
    )
    parser.add_argument(
        "-re", "--recursive", action="store_true", help="Enable Recursive Search"
    )
    parser.add_argument(
        "-ls",
        "--list-size",
        action="store_true",
        help="Display file size when moving file",
    )
    parser.add_argument(
        "-t",
        "--max-age",
        metavar="MINUTES",
        default=5,
        type=int,
        help="Maximum file age in minutes (-1 to ignore)",
    )
    parser.add_argument(
        "-s",
        "--size",
        metavar="MB",
        default=-1,
        type=float,
        help="Minimum file size in MB (-1 to ignore)",
    )

    return vars(parser.parse_args())


def Scan_Files(source, recursive=False):
    with os.scandir(source) as entries:
        for entry in entries:
            try:
                if entry.is_file(follow_symlinks=False):
                    # if os.path.splitext(entry.name)[1].lower() in SKIP_EXT:
                    if entry.name.lower().endswith(SKIP_EXT): # This is faster but riskier
                        continue
                    yield entry, entry.stat(follow_symlinks=False)

                elif recursive and entry.is_dir(follow_symlinks=False):
                    yield from Scan_Files(entry.path, True)

            except OSError:
                continue


def Valid_File(st: os.stat_result, age_seconds: int, size_bytes: float) -> bool:
    # Modify date check
    if age_seconds >= 0 and NOW - st.st_mtime > age_seconds:
        return False

    # File size check
    if size_bytes >= 0 and st.st_size <= size_bytes:
        return False

    return True


def Move_File(
    src: str,
    source_root: str,
    dest: str,
    name: str,
    replace=False,
    listfile=False,
    flatten=False,
    created=None,
) -> bool:
    if created is None:
        created = set()

    if flatten:
        dest_path = os.path.join(dest, name)
    else:
        relative = os.path.relpath(src, source_root)
        dest_path = os.path.join(dest, relative)

    if not listfile :
        # Create destination directories
        dest_dir = os.path.dirname(dest_path)
        if dest_dir not in created:
            os.makedirs(dest_dir, exist_ok=True)
            created.add(dest_dir)

    base, ext = None 
    counter = 1

    while os.path.exists(dest_path): # This spams filesystem when moving between 2 large folder
        CC.SetColor(CC.CYAN)
        print(f"[{PROGRAM}] Already Exists : {dest_path}")

        if replace:
            if not listfile :
                os.remove(dest_path)
            print(f"[{PROGRAM}] Replacing : {dest_path}")
            break

        if base is None :
            base, ext = os.path.splitext(dest_path)
        
        dest_path = f"{base}_{counter}{ext}"
        print(f"[{PROGRAM}] Attempting : {dest_path}")
        CC.SetColor(CC.RESET)

        counter += 1

    if not listfile:
        try:
            shutil.move(src, dest_path)
        except OSError:
            print(f"[{PROGRAM}] Failed to move {dest_path}")
            return False
    return True


def main():
    ARGS = Get_Arguments()
    SOURCE: str = ARGS["source"]
    DEST: str = ARGS["destination"]
    LISTSIZE: bool = ARGS["list_size"]
    AGE_MINUTES: int = ARGS["max_age"]
    MIN_SIZE: float = ARGS["size"]
    TOTAL: int = 0
    PROCESSED: int = 0

    age_max = AGE_MINUTES * 60
    size_min = MIN_SIZE * 1048576

    created = set()  # Directories already created at destination
    for entry, st in Scan_Files(SOURCE, ARGS["recursive"]):
        if not Valid_File(st, age_max, size_min):
            continue

        size_str = f" ({SizeToStr(st.st_size)})" if LISTSIZE else ""
        print(f"\033[38;5;46m[{PROGRAM}] {entry.name}{size_str}\033[0m")

        if Move_File(
            entry.path,
            SOURCE,
            DEST,
            entry.name,
            ARGS["replace"],
            ARGS["dry_run"],
            ARGS["flatten"] or not ARGS["recursive"], # Non recursive is equal to flatten
            created,
        ):
            PROCESSED += 1
        TOTAL += 1

    print(f"\033[38;5;226m[{PROGRAM}] Moved {PROCESSED}/{TOTAL} files\033[0m")


if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except KeyboardInterrupt:
        sys.exit(1)
    except Exception as e:
        print(f"[{PROGRAM}] An error has occored\n{e}{CC.RESET}")
        sys.exit(-1)
    finally:
        print(f"{CC.YELLOW}[{PROGRAM}] All done...{CC.RESET}")
        Alert()
