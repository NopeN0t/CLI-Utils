import shutil
import sys, os
from Functions.helpers import Union, Optional, Path, InputPath, Selector, Alert
from Projects.fftools.ffpresets import COVER_FORMATS
from Projects.fftools.fffunctions import AudioHelper, Add_Cover, Extract_Cover, Remove_Cover, ffmpeg_Check

def process(Mode : int, hide_command : bool = True) -> bool:
    F_INPUT, F_OUTPUT, IMAGE = GetPaths(True) if Mode == 1 else GetPaths()

    if os.path.isdir(F_INPUT) : #Batch mode
        AudioHelper.UncompressedToFLAC(F_INPUT) #Focre convert all uncompressed files to flac before searching
        if os.path.exists(F_OUTPUT) :#make result folder
            shutil.rmtree(F_OUTPUT)
        os.mkdir(F_OUTPUT)

        FILES = os.listdir(F_INPUT)
        F_TOTAL = F_COUNT = 0
        for file in FILES: #Iterate on each file
            if file.lower().endswith(COVER_FORMATS) : #Check for supported format
                F_TOTAL += 1
                #Save file inside RES folder
                out = os.path.join(F_OUTPUT, os.path.basename(os.path.splitext(file)[0] + ".png")) if Mode == 2 else os.path.join(F_OUTPUT, os.path.basename(file)) 
                if Wrapper(Mode, os.path.join(F_INPUT,file), out, IMAGE, hide_command) :
                    if Mode != 2 : #Delete Source Original File (Except Extract Mode)
                        os.remove(file)
                    F_COUNT += 1
        shutil.move(IMAGE, F_OUTPUT) #Move Cover to Res folder
        print(f"[ffCover] Processed {F_COUNT} / {F_TOTAL} files")
    else :
        TMP = os.path.splitext(F_INPUT)
        F_OUTPUT = f"{TMP[0]}_final{TMP[1]}" if Mode != 2 else f"{TMP[0]}.png" #Inplace Output
        Wrapper(Mode,F_INPUT, F_OUTPUT, IMAGE, hide_command) #Actually Process The thing
        if Mode != 2 : #Delete Original File (Except Extract Mode)
            os.remove(F_INPUT)
            os.rename(F_OUTPUT, F_INPUT)
            
    if os.path.exists(os.path.join(os.path.dirname(F_INPUT), "Cover.jpg")) : #Delete Cover.jpg
        os.remove(os.path.join(os.path.dirname(F_INPUT), "Cover.jpg"))
def Wrapper(Mode : int, F_INPUT : Union[str, Path], F_OUTPUT : Union[str, Path], IMAGE : Optional[Union[str, Path]] = None, hide_command : bool = True) -> bool :
    print(f"\033[38;5;220m[ffCover] Processing {F_INPUT}\033[0m")
    try :
        if Mode == 1 : #Add Cover
            Add_Cover(F_INPUT, IMAGE, F_OUTPUT, hide_command)
        elif Mode == 2 : #Extract Cover
            Extract_Cover(F_INPUT, F_OUTPUT, False, hide_command)
        elif Mode == 3 : #Remove Cover
            Remove_Cover(F_INPUT, F_OUTPUT, hide_command)
        else :
            raise ValueError("Invalid Process Mode")
        return True
    except Exception as e :
        print(f"\033[38;5;128m[ffCover] Something went wrong : {e}\033[0m")
        return False
def GetPaths(Include_Image : bool = False) -> list[str] :
    F_INPUT = InputPath("\033[38;5;46mEnter Inputpath : \033[0m")
    F_OUTPUT = os.path.join(F_INPUT.replace(os.path.basename(F_INPUT),""), "res")
    IMAGE = None
    if Include_Image :
        IMAGE = InputPath ("\033[38;5;46mEnter Coverpath : \033[0m")
    
    #File check
    if not os.path.exists(F_INPUT) :
        print("\033[38;5;128m[ffCover] Input path not found\033[0m")
        sys.exit(1)
    elif Include_Image :
        if not os.path.exists(IMAGE) :
            print("\033[38;5;128m[ffCover] Image path not found\033[0m")
            sys.exit(1)

    return [F_INPUT,F_OUTPUT,IMAGE]

def main() :
    hide_command = True
    #arguments (very crude handling)
    if len(sys.argv) > 1 :
        if sys.argv[1] == "-v" : #verbose (show ffmpeg command)
            print("[ffCover] Running on verbose mode")
            hide_command = False
    
    MODE = ["Insert", "Extract", "Remove"]
    OPTIONS = [1, 2, 3]

    mode = Selector(MODE, OPTIONS)
    if mode != None :
        process(mode, hide_command)
    
    print("[ffCover] All done...")
    sys.exit(0)

if __name__ == "__main__" :
    try :
        ffmpeg_Check()
        main()
    except KeyboardInterrupt :
        sys.exit(1)
    except Exception as e :
        print(f"An error has occored\n{e}")
        sys.exit(-1)
    finally :
        Alert()