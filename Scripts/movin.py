import argparse, sys, os, shutil, time, stat
from Functions.helpers import Alert, SizeToStr
from Colors.ConsoleColors import ConsoleColors as CC

PROGRAM = "movin"
SKIP_EXT = (".tmp", ".crdownload", ".part")

def main() :
    parser = argparse.ArgumentParser(formatter_class= argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("source", help="Source Folder")
    parser.add_argument("destination", help="Where to move to")
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
    created = set() #Directories already created at destination
    for src_path in files:
        try :
            st = os.stat(src_path)
        except OSError :
            continue
        if not stat.S_ISREG(st.st_mode):
            continue

        name = os.path.basename(src_path)

        if not Valid_File(name, st, AGE_MINUTES, MIN_SIZE):
            continue

        if not Is_Ready(src_path):
            continue

        size_str = f" ({SizeToStr(st.st_size)})" if LISTSIZE else ""
        print(f"\033[38;5;46m[{PROGRAM}] {name}{size_str}\033[0m")

        Move_File(src_path, SOURCE, DEST, args.replace, args.list, args.flatten, created)
        TOTAL += 1

    print(f"\033[38;5;226m[{PROGRAM}] Moved {TOTAL} files\033[0m")

def Valid_File(name : str, st : os.stat_result, age : int, size : float) -> bool :
    #Ignore Flag
    if age < 0 and size < 0 :
        return True

    #Skip downloading files
    if os.path.splitext(name)[1].lower() in SKIP_EXT:
        return False

    # Age check
    if age >= 0 and (time.time() - st.st_mtime) > age * 60 :
        return False

    # Size check
    return size < 0 or st.st_size > int(size * 1024 * 1024) #Bytes (convert MB to bytes)
def Is_Ready(path : str) -> bool :
    try :
        with open(path, "rb") :
            return True
    except Exception as e :
        print(f'[{PROGRAM}] {path} {e}')
        return False
def Move_File(src, source_root, dest, replace=False, listfile=False, flatten = False, created=None) :
    if created is None:
        created = set()
    if flatten:
        dest_path = os.path.join(dest, os.path.basename(src))
    else:
        relative = os.path.relpath(src, source_root)
        dest_path = os.path.join(dest, relative)

    # Create destination directories
    dest_dir = os.path.dirname(dest_path)
    if dest_dir not in created :
        os.makedirs(dest_dir, exist_ok=True)
        created.add(dest_dir)

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
