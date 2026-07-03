#Project : MK_PDF
#Argument Sector
#Debug Args
# import sys
# sys.argv = ["DEBUG", "./Images"]
import argparse, sys
praser = argparse.ArgumentParser(formatter_class = argparse.ArgumentDefaultsHelpFormatter)
praser.add_argument("folder_path", help = "Folder Where The Program Process")
praser.add_argument("-d" , "--dpi", default = 300, help= "The resloution of image")
praser.add_argument("-rv", "--reverse", action = "store_true", help = "Reverse The process (PDF -> PNG)")
praser.add_argument("-r", "--remove", action = "store_true", help = "Remove Images Files After Running")
cfg = vars(praser.parse_args())
cfg['dpi'] = int(cfg['dpi'])

from pathlib import Path
from PIL import Image
import pymupdf
import os
import re

def natural_sort_key(path):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(r'(\d+)', path.name)]

def Make_PDF(path : Path, remove : bool, DPI = 300) -> bool :
    try :
        ImagePaths : Path = list(path.glob("*"))
        ValidPaths : Path = []
  
        #Locate Actual Image
        print("Locating Valid Images")
        for ImgFile in ImagePaths :
            try :
                with Image.open(ImgFile) as img :
                    img.verify()
                    ValidPaths.append(ImgFile)
            except (IOError,SyntaxError) :
                pass
        ValidPaths.sort(key = natural_sort_key)

        #Result name
        print("Making PDF")
        index : int = 0
        save_to : Path = Path(f"{path}/Res_{index}.pdf")
  
        while True :
            if not os.path.exists(save_to) :
                break
            else :
                index += 1
                save_to = Path(f"{path}/Res_{index}.pdf")

        #Actually Making PDF
        Imgs = [Image.open(f) for f in ValidPaths]
        Imgs[0].save(save_to, resoution = DPI, save_all = True, append_images = (Imgs[1:]))
        Imgs.clear()
  
        if remove :
            print("Deleting Images")
            for path in ValidPaths :
                os.remove(path)
        return True
    except Exception as e :
        print(e.args)
        return False

def Extract_PDF(path : Path, remove : bool, DPI = None) -> bool :
    try :
        PDF_Files : Path = [path for path in list(path.glob("*")) if path.suffix.lower() == ".pdf"]
        #Handle Multiple Files
        if len(PDF_Files) == 0 :
            print("No PDF found")
            return False
        elif len(PDF_Files) > 1 :
            print("Multiple File Detected")
            for count, path in enumerate(PDF_Files) :
                print(f"{count}. '{path}'")
            while True :
                usi = input().lower()
                if int(usi) >= 0 and int(usi) < len(PDF_Files) :
                    select = int(usi)
                    break
        
        #Extract Data
        with pymupdf.open(PDF_Files[select]) as doc :
            Page_Size = []
            for count, page in enumerate(doc) :
                page.get_pixmap(dpi=DPI).save(Path(f"{path.parent}/Page_{count}.png"))

        #Delete Original File
        if remove :
            for file in PDF_Files :
                os.remove(file)
        return True
    except Exception as e :
        print(e.args)
        return False
    
if __name__ == "__main__" :
    StartPath = Path(cfg['folder_path'])
    if not Path.exists(StartPath) :
        print("Invalid Path")
        exit(1)
    if cfg['reverse'] :
        if Extract_PDF(StartPath, cfg['remove'], cfg['dpi']) :
            print("Done...")
        else :
            print("An error has occored...")
    else :
        if Make_PDF(StartPath, cfg['remove'], cfg['dpi']) :
            print("Done...")
        else :
            print("An error has occored...")
    try:
        if sys.platform.startswith("win"):
            import winsound
            winsound.MessageBeep()
        else:
            print("\a", end="", flush=True)
    except Exception:
        print("\a", end="", flush=True)