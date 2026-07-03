import argparse, sys, os, shutil
from datetime import datetime, timedelta
from helpers import Union, Path, Alert, GetFileSize
PROGRAM = "movin"

def main() :
    parser = argparse.ArgumentParser(formatter_class= argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("source", type=str, help="Source Folder")
    parser.add_argument("destination", type=str, help="Where to move to")
    parser.add_argument("-r", "--replace", action="store_true", help="Replace destination file")
    parser.add_argument("-ls", "--listsize", action="store_true", help="Display file size when moving file")
    parser.add_argument("-t", "--time", default=5, type=int, help="How much time difference is allowed (-1 to ignore)")
    parser.add_argument("-s", "--size", default=-1, type=float, help="Minimum file size to move in MB (-1 to ignore)")

    args = parser.parse_args()
    LISTSIZE = args.listsize
    AGE_MINUTES = args.time
    MIN_SIZE = args.size
    REPLACE = args.replace
    TOTAL = 0
    del parser #Unload Parser

    for name in os.listdir(args.source) :
        src_path = os.path.join(args.source, name)
    
        if not os.path.isfile(src_path) :
            continue
        if not Should_Process(src_path, AGE_MINUTES) or not Valid_Size(src_path, MIN_SIZE):
            continue
        if not Is_Ready(src_path) :
            continue

        if LISTSIZE :
            print(f'\033[38;5;46m[{PROGRAM}] {name} ({GetFileSize((src_path))})\033[0m')
        else :
            print(f'\033[38;5;46m[{PROGRAM}] {name}\033[0m')
    
        dest_path = os.path.join(args.destination, name)

        # Handle name collisions
        base, ext = os.path.splitext(name)
        counter = 1
        while os.path.exists(dest_path) :
            print(f'\033[38;5;50m[{PROGRAM}] Already Exists : {name} \033[0m')
            if REPLACE :
                os.remove(dest_path)
                print(f'\033[38;5;50m[{PROGRAM}] Replacing : {name}\033[0m')
                break
            dest_path = os.path.join(args.destination, f"{base}_{counter}{ext}")
            print(f'\033[38;5;50m[{PROGRAM}] Attempting : {dest_path}\033[0m')
            counter += 1

        shutil.move(src_path, dest_path)
        TOTAL += 1
    print(f"\033[38;5;226m[{PROGRAM}] Moved {TOTAL} files\033[0m")

def Is_Ready(path : Union[str, Path]) -> bool :
    try :
        with open(path, "rb") :
            return True
    except Exception as e :
        print(f'[{PROGRAM}] {path} {e}')
        return False
def Should_Process(path : Union[str, Path], age : int) -> bool :
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

if __name__ == "__main__" :
    try :
        main()
        sys.exit(0)
    except KeyboardInterrupt :
        sys.exit(1)
    except Exception as e :
        print(f"[{PROGRAM}] An error has occored\n{e}\033[0m")
        sys.exit(-1)
    finally :
        print(f"\033[38;5;226m[{PROGRAM}] All done...\033[0m")
        Alert()