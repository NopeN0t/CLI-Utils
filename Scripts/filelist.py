from Functions.helpers import Alert, ConvertTime, InputPath, SizeToStr
import os, time, sys, argparse

PROGRAM = "FileList"

def main() :
    #Parse Input Path
    parser = argparse.ArgumentParser(formatter_class= argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-i", "--input", default="", type=str, help="Input path")
    parser.add_argument("-r", "--reverse", action="store_true", help="Sort from biggest to lowest instead")
    args = parser.parse_args()
        
    BASE_DIR = args.input
    if BASE_DIR == "" : #Manual Input
        BASE_DIR = InputPath("Enter Folder to probe : ")

    if not os.path.isdir(BASE_DIR) :
        BASE_DIR = BASE_DIR.replace(os.path.basename(BASE_DIR), "") #Remove Filename part
    BASE_DIR = os.path.abspath(InputPath(BASE_DIR,True).removesuffix('"')) #Force Absloute Path

    FILES = {}
    SIZES = {}

    for root,folder,names in os.walk(BASE_DIR) :
        print(f"\033[38;5;50m   Processing {root}\033[0m")
        for name in names :
            f_path = os.path.join(root, name)
            ext = name.lower().split('.')[-1] #extract ext
            size = os.path.getsize(f_path)
            if ext not in FILES :
                FILES[ext] = 1
                SIZES[ext] = size
            else :
                FILES[ext] += 1
                SIZES[ext] += size

    print(f"\033[38;5;46mDone...\033[0m")
    total_f = 0
    total_s = 0
    SIZES_SORT = {}
    for key in sorted(SIZES, key=SIZES.get, reverse=args.reverse):
        SIZES_SORT[key] = SIZES[key]

    for key in SIZES_SORT :  
        print(f"    {key} : {SizeToStr(SIZES_SORT[key])} ({FILES[key]} files)")
        total_f += FILES[key]
        total_s += SIZES_SORT[key]
    print(f"\033[38;5;46mTotal {total_f} files {SizeToStr(total_s)}\033[0m")
        

if __name__ == "__main__" :
    try :
        START = time.perf_counter()
        main()
        sys.exit(0)
    except KeyboardInterrupt :
        sys.exit(-1)
    except Exception as e:
        print(f"[{PROGRAM}] An error has occored\n{e}\033[0m")
        sys.exit(1)
    finally :
        print(f"\033[38;5;226m[{PROGRAM}] Time Taken (Menuing Counts) Time taken {ConvertTime(START, time.perf_counter())}\033[0m")
        Alert()