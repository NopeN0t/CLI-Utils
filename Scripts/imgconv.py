#Existing Libs
from Colors.ConsoleColors import ConsoleColors as CC
from multiprocessing import Pool, cpu_count
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from pathlib import Path
import sys, time

#Custom Libs
from Functions.helpers import Alert, ConvertTime, SizeToStr, GetFileSize, ImgCorrect
from Projects.imgconv.Program_Check import Supports, exiftool_Check
from Projects.imgconv.Encoder_Presets import Encoder_Presets
from Projects.imgconv.Program_Presets import ProgramPresets
from Functions.Image_Locator import LocateImages

PROGRAM = "imgconv"
def log(msg : str, Color = CC.RESET) -> None :
    print(f"{Color}[{PROGRAM}] {msg}{CC.RESET}")

def _getArgStr(args : list) -> str :
    res = ""
    for _ in args :
         res += (_ + " ")
    return res

def process_file() -> Path :
     pass

def Main() :    
    parser = ArgumentParser(formatter_class= ArgumentDefaultsHelpFormatter)
    parser.add_argument("input_paths", nargs="+", type=str, help="File/Path to process")
    parser.add_argument("-r", "--recursive", action="store_true", help="Enable Recursive Search")
    parser.add_argument("-f", "--format", required=True, choices=Supports.formats(), help="Supported Formats (Encoder must exists)")
    parser.add_argument("-p", "--preset", type=ProgramPresets, choices=ProgramPresets.Presets(), default=ProgramPresets.Default, help="Preset for encoder")
    parser.add_argument("-k", "--keep", action="store_true", help="Keep converted files")
    parser.add_argument("-t", "--threads", type=int, 
                        default=cpu_count() - 2 if cpu_count() > 2 else 1, #Left threads unused to prevent global OS lag
                        help="Maximum number of parallelism, Default = Max threads - 2")
    args = parser.parse_args()
    del parser

    if not Supports.check_format(args.format) or not exiftool_Check(False) :
         raise FileNotFoundError(f"{CC.FATAL}Tool not found")

    # Ensure preset is correct
    preset_str = args.preset if isinstance(args.preset, str) else args.preset.name.lower()
        
    # Setup Process
    ARGS = Encoder_Presets.get_args(Encoder_Presets.get_preset(args.format, preset_str))
    PATHS = LocateImages(args.input_paths, args.recursive)
    BAS_SIZE = 0
    RES_SIZE = 0
    log(f"Images found : {len(PATHS)}", CC.INFO)
    log(f"Converting to {args.format} using {preset_str} preset", CC.INFO)

    log(f"n>> {_getArgStr(ARGS)}", CC.RED)
    
    # with Pool(args.threads) as pool :
    #     for _ in pool.imap_unordered(, PATHS) :
    #         RES_SIZE += 
    
    
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