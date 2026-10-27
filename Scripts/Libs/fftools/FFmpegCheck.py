'''Self contained version of Checkers'''
import shutil, subprocess, sys, platform


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
        system = platform.system().lower()
        
        if system == "windows":
            install_cmd = 'run "winget install ffmpeg"'
        elif system == "darwin":  # macOS
            install_cmd = 'run "brew install ffmpeg"'
        elif system == "linux":
            install_cmd = 'run "sudo apt-get install ffmpeg" (or your package manager)'
        else:
            install_cmd = 'install ffmpeg via your package manager'

        error_msg = (
            f"\033[31m[Error] ffmpeg not found\n"
            f"\033[38;5;50m   on {system} {install_cmd}\n"
            f"   then reboot the terminal to update the PATH\033[0m"
        )
        
        print(error_msg)

        if terminate :
            sys.exit(1)
        return False
    return True
