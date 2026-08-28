from Colors.ConsoleColors import ConsoleColors as CC
from Functions.helpers import Alert, ConvertTime, SizeToStr, GetFileSize, ImgCorrect
from multiprocessing import pool, cpu_count
import argparse
import sys, time
from Projects.imgconv.Program_Check import Supports, exiftool_Check
from Functions.Image_Locator import LocateImages

PROGRAM = "imgconv"
def log(msg : str, Color = CC.RESET) -> None :
    print(f"{Color}[{PROGRAM}] {msg}{CC.RESET}")

def Main() :    
    parser = argparse.ArgumentParser(formatter_class= argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("input_paths", nargs="+", type=str, help="File/Path to process")
    parser.add_argument("-r", "--recursive", action="store_true", help="Enable Recursive Search")
    parser.add_argument("-f", "--format", required=True, choices=Supports.formats(), help="Supported Formats (Encoder must exists)")
    parser.add_argument("-k", "--keep", action="store_true", help="Keep converted files")
    parser.add_argument("-t", "--threads", type=int, 
                        default=cpu_count() - 2 if cpu_count() > 2 else 1, #Left threads unused to prevent global OS lag
                        help="Maximum number of parallelism, Default = Max threads - 2")
    args = parser.parse_args()
    del parser

    if not Supports.check_format(args.format) or not exiftool_Check(False) :
         raise FileNotFoundError(f"{CC.FATAL}Tool not found")

    PATHS = LocateImages(args.input_paths, args.recursive)
    print(PATHS)
    
if __name__ == "__main__":
    # try :
        START = time.perf_counter()
        Main()
        sys.exit(0)
    # except KeyboardInterrupt :
    #     sys.exit(-1)
    # except Exception as e:
    #     log(f"An error has occored\n{e}")
    #     sys.exit(-1)
    # finally :
    #     log(f"Time Taken (Menuing Counts) Time taken {ConvertTime(START, time.perf_counter())}", CC.YELLOW)
    #     Alert()