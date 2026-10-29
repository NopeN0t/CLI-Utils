from .. import ConvertTime, log, RunFFmpeg, LogLevel
from typing import Union
from pathlib import Path
import time, os

def Raw2FLAC(input : Union[str, Path], replace : bool = True, silent : bool = False) -> None:
    '''
    Convert uncompressed audio files to flac files\n
    This always process every file in given directory\n
    Even when input is a file

    :param input: Input file / Directory
    :type input: Union[str, Path]
    :param replace: Remove wav file
    :type replace: bool
    :param silent: Show feedback on console
    :type silent: bool
    '''
    FORMATS = (".wav", ".aiff")
    START = time.perf_counter()
    FOLDER = os.path.dirname(input)

    processed = 0
    log(silent, f"\033[38;5;46m[To_FLAC] Converting {FOLDER}\033[0m\n    [Config] Overwrite = {replace}")

    for file in os.listdir(FOLDER) : #Get all file in dir
        file = os.path.join(FOLDER, file) #Rebuild path
        
        if file.lower().endswith(FORMATS) : #Valid format
            RunFFmpeg(
                inputs=file,
                output=f"{os.path.splitext(file)[0] + ".flac"}",
                args=["-c:a", "flac", "-compression_level", "12"],
                loglevel=LogLevel.FATAL,
                show_status=False,
                show_command=False
            )
    
            if replace : #Delete source file
                os.remove(file)
    
            processed += 1 
            log(silent, f"\033[38;5;220m    Converted {file} ({ConvertTime(START, time.perf_counter())})\033[0m")
    
    log(silent, f"\033[38;5;46m    Processed {processed} files ({ConvertTime(START, time.perf_counter())})\033[0m")