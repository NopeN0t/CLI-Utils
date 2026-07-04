import os, subprocess, sys, argparse, time
from Functions.helpers import Union, Path, SizeToStr, ConvertTime, Alert, InputPath, ImgCorrect, ImgCheck, IMG_CORRECTOR
from multiprocessing import Pool, cpu_count
from tqdm import tqdm
PROGRAM = "imgopt"
WORKERS = cpu_count() - 2 if cpu_count() > 2 else 1 #Left threads unused to prevent global OS lag
#External Programs
#fffunctions.py
#oxipng.exe
#ect.exe
#jpegoptim.exe 
#cwebp.exe (libwebp)

def ect_optimize(file : Union[str, Path]) :
    return run(["ect", "-9", "--disable-jpg", "-quiet", "-keep", file])
def oxipng_optimize(file : Union[str, Path]) :
    return run(["oxipng", "-o", "max", "--strip", "none", "--fix", "--quiet", "-p", file])
def jpeg_optimize(file : Union[str, Path]) :
    return run(["jpegoptim", "--strip-none", "--all-progressive", "-q", "-p", file])
def run(args) :
    try :
        subprocess.run(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except KeyboardInterrupt :
        pass
    except Exception as e:
        print(f"[{PROGRAM}] An error has occored\n{e}\033[0m")
    finally :
        return args[-1]

def webp_type(path : Union[str, Path]) :
    with open(path, "rb") as f:
        header = f.read(32)

    if header[0:4] != b"RIFF" or header[8:12] != b"WEBP":
        return "not_webp"

    chunk = header[12:16]

    if chunk == b"VP8 ":
        return "lossy"
    elif chunk == b"VP8L":
        return "lossless"
    elif chunk == b"VP8X":
        return "extended"  # may be animated or metadata
    else:
        return "unknown"
def ActualType(path : Union[str, Path]) :
    with open(path, "rb") as f:
        sig = f.read(12)

    if sig.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    elif sig.startswith(b"\xff\xd8"):
        return "jpg"
    elif sig[0:4] == b"RIFF" and sig[8:12] == b"WEBP":
        return "webp"
    
    return "unknown"
def Print_Stat(text : str, base : int, opt : int) -> None :
    print(f"\033[38;5;50m[{PROGRAM}] {text} : {SizeToStr(opt)} / {SizeToStr(base)} ({SizeToStr(base - opt)} : {round((opt / base)*100, 4)}%)\033[0m")

def main() :
    #THIS PROGRAM ONLY OPTIMIZE LOSSLESSLY
    #Current implementation of image processer is lower than it needed to be
    #due to overhead of parsing argument on every loop
    #but this make user experince better? I guess

    #Parse Input Path
    parser = argparse.ArgumentParser(formatter_class= argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-i", "--input", default="", type=str, help="Input path")
    parser.add_argument("-d", "--detect", action="store_true", help="Only detect files")
    parser.add_argument("-png", "--nopng", action="store_true", help="Ignore PNG")
    parser.add_argument("-jpg", "--nojpg", action="store_true", help="Ignore JPG")
    parser.add_argument("-webp", "--nowebp", action="store_true", help="Ignore WEBP")
    parser.add_argument("-nc", "--nocheck", action="store_true", help="Skip extension checking process")
    args = parser.parse_args()
    
    FOLDER = args.input
    if FOLDER == "" :
        FOLDER = InputPath("Enter folder to optimize : ")
    FOLDER = os.path.abspath(InputPath(FOLDER,True).removesuffix('"'))

    if not os.path.isdir(FOLDER) :
        FOLDER = FOLDER.replace(os.path.basename(FOLDER), "")
    del parser #Unload Parser
    
    #File Preps
    FILES = {"png" : [], "jpg" : [], "webp" : [], "total" : 0}
    BASE_SIZE = {"png" : 0, "jpg" : 0, "webp" : 0, "total" : 0}
    OPT_SIZE = {"png" : 0, "jpg" : 0, "webp" : 0, "total" : 0}
    IMG_READY = ['png', 'jpg', 'jpeg', 'webp'] #This program Supports

    for root, _, names in os.walk(FOLDER):
        for n in names:
            EXT = n.lower().split('.')[-1] #extract ext
            if EXT not in IMG_CORRECTOR : #Skip file that Correcter doesn't support
                continue

            f_path = os.path.join(root, n)
            size = os.path.getsize(f_path)
            valid = False
            
            if not args.nocheck : #Check and Correct extendtion
                AT = ImgCheck(f_path)
                if AT != EXT and AT != 'unknown' :
                    print(f"\033[38;5;196m{n} is actually {AT}\033[0m")
                    f_path = ImgCorrect(f_path, AT)
                    EXT = AT

            if EXT not in IMG_READY : #Skip image that's this program doesn't support
                continue

            if EXT == "png" and not args.nopng:
                FILES['png'].append(f_path)
                BASE_SIZE["png"] += size
                valid = True
            elif (EXT == "jpg" or EXT == "jpeg") and not args.nojpg :
                FILES["jpg"].append(f_path)
                BASE_SIZE["jpg"] += size
                valid = True
            elif EXT == "webp" and not args.nowebp:
                if webp_type(f_path) == 'lossless' :
                    FILES["webp"].append(f_path)
                    BASE_SIZE["webp"] += size
                    valid = True

            if valid :
                FILES["total"] += 1
                BASE_SIZE["total"] += size
                if args.detect :
                    print(f_path)

    print(f"\033[38;5;226m[{PROGRAM}] Files found : {FILES['total']} ({SizeToStr(BASE_SIZE['total'])})\n"
          f"[{PROGRAM}] PNG {len(FILES['png'])} ({SizeToStr(BASE_SIZE['png'])}) : JPG {len(FILES['jpg'])} ({SizeToStr(BASE_SIZE['jpg'])}) : WEBP (lossless) {len(FILES['webp'])} ({SizeToStr(BASE_SIZE['webp'])})\033[0m")
    if args.detect :
        return
    
    if len(FILES["png"]) > 0 :
        #PNG phase 1
        print(f"\033[38;5;46m[{PROGRAM}] Processing PNGs Phase 1\033[0m\n"
              f"\033[31mn>> oxipng -o max --strip none --fix -p *.png\033[0m")

        with Pool(2) as pool :
            for _ in tqdm(pool.imap_unordered(oxipng_optimize, FILES["png"]), "PNG Phase 1", len(FILES["png"]), unit="files") :
                OPT_SIZE["png"] += os.path.getsize(_)

        Print_Stat("PNG Phase 1 Completed", BASE_SIZE["png"], OPT_SIZE["png"])

        #PNG phase 2
        tmp = OPT_SIZE["png"]
        OPT_SIZE["png"] = 0
        print(f"\033[38;5;46m[{PROGRAM}] Processing PNGs Phase 2\033[0m\n"
              f"\033[31mn>> ect -9 --disable-jpg -keep [files]\033[0m")
    
        with Pool(WORKERS) as pool:
            for _ in tqdm(pool.imap_unordered(ect_optimize, FILES["png"]), "PNG Phase 2", len(FILES["png"]), unit="files"):
                OPT_SIZE["png"] += os.path.getsize(_)

        Print_Stat("PNG Phase 2 Completed", tmp, OPT_SIZE["png"])
        
    if len(FILES["jpg"]) > 0 :
        #JPG phase 1
        print(f"\033[38;5;46m[{PROGRAM}] Processing JPGs\033[0m\n"
              f"\033[31mn>> jpegoptim --strip-none --all-progressive -p *.jpg\033[0m")
        with Pool(WORKERS) as pool :
            for _ in tqdm(pool.imap_unordered(jpeg_optimize, FILES["jpg"]), "JPG Phase 1", len(FILES["jpg"]), unit="files") :
                OPT_SIZE["jpg"] += os.path.getsize(_)

        Print_Stat("JPG Phase 1 Completed", BASE_SIZE["jpg"], OPT_SIZE["jpg"])

    if len(FILES["webp"]) > 0 :
        #WEBP phase 1
        print(f"\033[38;5;46m[{PROGRAM}] Processing WEBPs\033[0m\n"
              f"\033[31mn>> cwebp -lossless -z 9 -m 6 -metadata all [input.webp] -o [output.webp]\033[0m")
        
        for _ in tqdm(FILES["webp"], "WEBP Phase 1", len(FILES["webp"]), unit="files") :
            tmp = _ + ".tmp.webp"
            subprocess.run(["cwebp", "-lossless", "-z", "9", "-m", "6", "-metadata all", _, "-o", tmp],stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if os.path.exists(tmp):
                if os.path.getsize(tmp) < os.path.getsize(_):
                    os.replace(tmp, _)  # atomic replace
                else:
                    os.remove(tmp)
            OPT_SIZE["webp"] += os.path.getsize(_)

        Print_Stat("WEBP Phase 1 Completed", BASE_SIZE["webp"], OPT_SIZE["webp"])
    
    OPT_SIZE["total"] += OPT_SIZE["jpg"] + OPT_SIZE["png"] + OPT_SIZE["webp"]
    print(f"\033[38;5;226m[{PROGRAM}] Total Files : {FILES['total']}\n"
          f"[{PROGRAM}] PNG {len(FILES['png'])} : JPG {len(FILES['jpg'])} : WEBP (lossless) {len(FILES['webp'])}\n"
          f"[{PROGRAM}] Space Saved : {SizeToStr(OPT_SIZE['total'])} / {SizeToStr(BASE_SIZE['total'])} "
          f"({SizeToStr(BASE_SIZE['total'] - OPT_SIZE['total'])} : {round((OPT_SIZE['total'] / BASE_SIZE['total'])*100, 4)}%)\033[0m")

if __name__ == "__main__":
    try :
        START = time.perf_counter()
        main()
        sys.exit(0)
    except KeyboardInterrupt :
        sys.exit(-1)
    except Exception as e:
        print(f"[{PROGRAM}] An error has occored\n{e}\033[0m")
        sys.exit(-1)
    finally :
        print(f"\033[38;5;226m[{PROGRAM}] Time Taken (Menuing Counts) Time taken {ConvertTime(START, time.perf_counter())}\033[0m")
        Alert()