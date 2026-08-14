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

def ffmpeg_Check(terminate : bool = True) -> bool :
    '''Check if ffmpeg exists in user's PC'''

    if not __ProgramExists("ffmpeg", ["ffmpeg", "-version"]) :
        print("\033[31m[Error] ffmpeg.exe not found\n" 
        "\033[38;5;50m   on windows run \"winget install ffmpeg\"\n" 
        "   on debian based linux run \"sudo apt-get install ffmpeg\"\n" 
        "   then reboot the terminal to update the global enviroment\033[0m")
        if terminate :
            sys.exit(1)
        return False
    return True

def exiftool_Check(terminate : bool = True) -> bool :
    '''Check if exiftool exists in user's PC'''

    if not __ProgramExists("exiftool", ["exiftool", "-ver"]) :
        print("\033[31m[Error] exiftool.exe not found\033[0m")
        if terminate :
            sys.exit(1)
        return False
    return True

def Custom_Checker(process : str, params : list, terminate : bool = True, NotFoundmsg : str = "") -> bool :
    '''
    Custom Checker with open control
    
    :param process: program name
    :type process: str
    :param params: parameters to given process
    :type params: str
    :param terminate: Exit program if failed
    :type terminate: bool
    :param NotFoundmsg: Message to show when failed to find the process
    :type NotFoundmsg: str
    :return: Check result (True if success otherwise False)
    :rtype: bool
    '''

    if not __ProgramExists(process, params) :
        print(NotFoundmsg)
        if terminate :
            sys.exit(1)
        return False
    return True

def Custom_Checker_Short(process : str, params : list) -> bool :
    '''
        Custom Checker with open control (Short Ver)
        
        :param process: program name
        :type process: str
        :param params: parameters to given process
        :type params: str
        :return: Check result (True if success otherwise False)
        :rtype: bool
    '''
    return __ProgramExists(process, params)
    
