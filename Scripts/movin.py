import argparse, sys, os, shutil
from datetime import datetime, timedelta
from Functions.helpers import Union, Path, Alert, GetFileSize
from Colors.ConsoleColors import ConsoleColors as CC

PROGRAM = "movin"

def main() :
    parser = argparse.ArgumentParser(formatter_class= argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("source", type=str, help="Source Folder")
    parser.add_argument("destination", type=str, help="Where to move to")
    parser.add_argument("-l", "--list", action="store_true", help="List file only")
    parser.add_argument("-r", "--replace", action="store_true", help="Replace destination file")
    parser.add_argument("-fl", "--flatten", action="store_true", help="Do not preserve directory structure")
    parser.add_argument("-re", "--recursive", action="store_true", help="Enable Recursive Search")
    parser.add_argument("-ls", "--listsize", action="store_true", help="Display file size when moving file")
    parser.add_argument("-t", "--time", default=5, type=int, help="How much time difference is allowed (-1 to ignore)")
    parser.add_argument("-s", "--size", default=-1, type=float, help="Minimum file size to move in MB (-1 to ignore)")

    args = parser.parse_args()
    SOURCE = args.source
    DEST = args.destination
    LISTSIZE = args.listsize
    AGE_MINUTES = args.time
    MIN_SIZE = args.size
    TOTAL = 0
    del parser #Unload Parser

    if args.recursive:
        files = (
            os.path.join(root, name)
            for root, _, names in os.walk(SOURCE)
            for name in names
        )
    else:
        files = (
            os.path.join(SOURCE, name)
            for name in os.listdir(SOURCE)
        )
    for src_path in files:
        if not os.path.isfile(src_path):
            continue

        if not Valid_Age(src_path, AGE_MINUTES):
            continue

        if not Valid_Size(src_path, MIN_SIZE):
            continue

        if not Is_Ready(src_path):
            continue

        name = os.path.basename(src_path)

        if LISTSIZE:
            print(f"\033[38;5;46m[{PROGRAM}] {name} ({GetFileSize(src_path)})\033[0m")
        else:
            print(f"\033[38;5;46m[{PROGRAM}] {name}\033[0m")

        Move_File(src_path, SOURCE, DEST, args.replace, args.list, args.flatten)
        TOTAL += 1
    
    print(f"\033[38;5;226m[{PROGRAM}] Moved {TOTAL} files\033[0m")

def Is_Ready(path : Union[str, Path]) -> bool :
    try :
        with open(path, "rb") :
            return True
    except Exception as e :
        print(f'[{PROGRAM}] {path} {e}')
        return False
def Valid_Age(path : Union[str, Path], age : int) -> bool :
    #Ignore Flag
    if age < 0 :
        return True
    
    path = Path(path)
    #Skip downloading files
    if path.suffix.lower() in (".tmp", ".crdownload", ".part"):
        return False
    
    # Age check
    mtime = datetime.fromtimestamp(path.stat().st_mtime)
    age_delta = datetime.now() - mtime
    threshold = timedelta(minutes=age)
    mtime = datetime.fromtimestamp(os.path.getmtime(path))
    return age_delta <= threshold
def Valid_Size(path : Union[str, Path], size : float) -> bool :
    #Ignore Flag
    if size < 0 :
        return True
    
    path = Path(path)
    #Skip downloading files
    if path.suffix.lower() in (".tmp", ".crdownload", ".part"):
        return False
    return path.stat().st_size > int(size * 1024 * 1024) #Bytes (convert MB to bytes)
def Move_File(src, source_root, dest, replace=False, listfile=False, flatten = False):
    if flatten:
        dest_path = os.path.join(dest, os.path.basename(src))
    else:
        relative = os.path.relpath(src, source_root)
        dest_path = os.path.join(dest, relative)

    # Create destination directories
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    base, ext = os.path.splitext(dest_path)
    counter = 1

    while os.path.exists(dest_path):
        CC.SetColor(CC.CYAN)
        print(f'[{PROGRAM}] Already Exists : {dest_path}')

        if replace:
            os.remove(dest_path)
            print(f'[{PROGRAM}] Replacing : {dest_path}')
            break

        dest_path = f"{base}_{counter}{ext}"
        print(f'[{PROGRAM}] Attempting : {dest_path}')
        CC.SetColor(CC.RESET)

        counter += 1

    if not listfile:
        shutil.move(src, dest_path)
        return True

    return False

if __name__ == "__main__" :
    try :
        main()
        sys.exit(0)
    except KeyboardInterrupt :
        sys.exit(1)
    except Exception as e :
        print(f"[{PROGRAM}] An error has occored\n{e}{CC.RESET}")
        sys.exit(-1)
    finally :
        print(f"{CC.YELLOW}[{PROGRAM}] All done...{CC.RESET}")
        Alert()