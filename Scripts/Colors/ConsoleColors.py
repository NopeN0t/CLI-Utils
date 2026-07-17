class ConsoleColors :
    # Reset color code (always reset to default)
    RESET = "\033[0m"

    # Standard colors
    BLACK = "\033[38;5;16m"
    RED = "\033[38;5;196m"
    GREEN = "\033[38;5;40m"
    YELLOW = "\033[38;5;226m"
    BLUE = "\033[38;5;12m"
    PURPLE = "\033[38;5;128m"
    CYAN = "\033[38;5;50m"

    WARNING_MSG = "WARNING"
    ERROR_MSG = "ERROR"
    FATAL_MSG = "FATAL"

    # Warning, Error, Fatal
    WARNING = f"{RESET}[{YELLOW}{WARNING_MSG}{RESET}] "
    ERROR = f"{RESET}[{RED}{ERROR_MSG}{RESET}] "
    FATAL = f"{RESET}[{RED}{FATAL_MSG}{RESET}] "

    # Info and Highlight
    INFO = "\033[38;5;40m"  # Green, but could be anything
    HIGHLIGHT = f"{YELLOW}\033[1m"  # Yellow with bold
    
    def SetColor(COLOR) : # type: ignore
        '''This is no difference from inserting color into regular print'''
        print(COLOR, end='')