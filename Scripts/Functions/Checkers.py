import shutil, subprocess, sys

def __ProgramExists(process : str, params : list) -> bool :
    '''
        Check if a program exists in PC
        
        :param process: Process name
        :type process: str
        :param params: Param to test if it exists ([program] --version)
        :type params: list
    '''
    if shutil.which(process) is None :
        return False
    try :
        subprocess.run(
            params,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except :
        return False

    return True

def ffmpeg_Check(terminate : bool = True) -> None :
    '''Check if ffmpeg exists in user's PC'''

    if not __ProgramExists("ffmpeg", ["ffmpeg", "-version"]) :
        print("\033[31m[Fatal] ffmpeg.exe not found\n" 
        "\033[38;5;50m   on windows run \"winget install ffmpeg\"\n" 
        "   on debian based linux run \"sudo apt-get install ffmpeg\"\n" 
        "   then reboot the terminal to update the global enviroment\033[0m")
        if terminate :
            sys.exit(1)

def exiftool_Check(terminate : bool = True) -> None :
    '''Check if exiftool exists in user's PC'''

    if not __ProgramExists("exiftool", ["exiftool", "-ver"]) :
        print("\033[31m[Fatal] exiftool.exe not found\n"
        "\033[38;5;50m   Make sure exiftool.exe is installed and in PATH\n"
        "   then reboot the terminal to update the global enviroment\033[0m")
        if terminate :
            sys.exit(1)
