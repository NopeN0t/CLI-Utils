from typing import Union, Optional, Any
from datetime import timedelta
from pathlib import Path
import sys, os
#File format that's image check/corrector supports
IMG_CORRECTOR = ['png', 'jpg', 'jp2', 'jxl', 'gif', 'bmp', 'ico',
               'psd', 'tiff', 'webp', 'heic', 'heif', 'avif', 'svg']
#File helpers
def SizeToStr(size : float) -> str:
    """ Convert bytes to KB, or MB or GB returns -1 if something went wrong"""
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return "%3.1f %s" % (size, x)
        size /= 1024.0
    return "-1"

def GetFileSize(filepath : Union[str, Path]) -> str :
    return SizeToStr(os.path.getsize(filepath))
def ImgCheck(file : Union[str, Path]) :
    '''
    Check Magic Code Of Image File
    
    :param file: image's path
    :type file: Union[str, Path]
    '''
    file = Path(file)
    SIGNATURES = {
        "png" : [b"\x89PNG\r\n\x1A\n"],
        "jpg" : [b"\xFF\xD8\xFF"],
        "jp2" : [b"\x00\x00\x00\x0CjP  \r\n\x87\n"],
        "jxl" : [b"\xFF\x0A", b"\x00\x00\x00\x0C\x4A\x58\x4C\x20\x0D\x0A\x87\x0A"],
        "gif": [b"GIF87a", b"GIF89a"],
        "bmp" : [b"BM"],
        "ico" : [b"\x00\x00\x01\x00"],
        "psd" : [b"8BPS"],
        "tiff" : [b"II*\x00", b"MM\x00*"],
    }
    if not file.exists() or file.stat().st_size < 12 : #File doesn't exist or too small (Minimum usable image is ~30bytes)
        return "unknown"
    
    with open(file, "rb") as f: #Extract file header
        sig = f.read(64)

    #Common Signatures
    for fmt, sig_list in SIGNATURES.items() :
        if any(sig.startswith(s) for s in sig_list) :
            return fmt

    #RIFF type header
    if sig[0:4] == b"RIFF" and sig[8:12] == b"WEBP":
        return "webp"
    
    #AVIF / HEIF container
    if sig[4:8] == b"ftyp":
        brand = sig[8:12]
        if brand in [b"heic", b"heix", b"hevc", b"hevx"]:
            return "heic"
        elif brand in [b"avif", b"avis"]:
            return "avif"
        elif brand in [b"mif1", b"msf1"]:
            return "heif"
        elif brand == b"jxl" :
            return "jxl"

    #Text Based
    if b"<svg" in sig.lower():
        return "svg"

    return "unknown"
def ImgCorrect(file : Union[str, Path], img_type : Optional[str] = None) -> Path:
    '''
    Check and correct image ext
    
    :param file: image's path
    :type file: Union[str, Path]
    :param img_type: Image Format (Skips Checking)
    :type img_type: Optional[str]
    :return: Input path with/without extendtion changes
    :rtype: Path
    '''
    EXT = Path(file).suffix.lower().lstrip('.')
    if img_type == None :
        img_type = ImgCheck(file)
    if img_type != EXT and img_type != 'unknown':
        base = os.path.splitext(file)[0]
        new_path = base + "." + img_type
        os.rename(file,new_path) #This Overwrite Files (If it does you probably want to anyways)
        file = new_path
    return Path(file)

#Converters
def ConvertTime(start : float, end : float) -> str :
    '''
    Convert time to a humen friendly format
    
    :param time: Hard to read version of time
    :type time: float
    :return: More readable version of time
    :rtype: str
    '''
    return str(timedelta(seconds=round((end - start), 4)))

#Input helpers
def InputPath(info : str, process_text : bool = False) -> str :
    """Allow user to input paths wrapped in quotes."""
    if process_text :
        data = info
    else : 
        data = input(info).strip()
    if len(data) >= 2 and data[0] == data[-1] and data[0] in ("'", '"') :
        data = data[1:-1]
    return data.strip()
def Selector(Options : list[Any], fn : list[Any]) -> Optional[Any] :
    '''A warpper to select functions'''
    for c, ops in enumerate(Options) :
        print(f"{c} : {ops}")
    select = int(input("\033[38;5;46mSelect Option : \033[0m").strip())
    for c, ops in enumerate(fn) :
        if c == select :
            return ops
    print(f"\033[38;5;46mInvalid Choice\033[0m")
    return None

#User information
def log(silent : bool, text : str, endl = True) -> None :
    '''Print wrapper that have option to not print'''
    if not silent :
        if endl :
            print(text)
        else :
            print(text, end="")
def Alert() :
    try:
        if sys.platform.startswith("win"):
            import winsound
            winsound.MessageBeep()
        else:
            print("\a", end="", flush=True)
    except Exception:
        print("\a", end="", flush=True)
