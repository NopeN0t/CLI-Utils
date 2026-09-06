#Existing Libs
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from multiprocessing import Pool, cpu_count
from pathlib import Path
import subprocess
import sys
import time

#Custom Libs
from Functions.helpers import Alert, ConvertTime, SizeToStr
from Projects.imgconv.Program_Check import Supports, exiftool_Check
from Projects.imgconv.Encoder_Presets import Encoder_Presets, EncoderPreset
from Projects.imgconv.Program_Presets import ProgramPresets
from Colors.ConsoleColors import ConsoleColors as CC
from Functions.Image_Locator import LocateImages #This does image checking too
from Functions.MetaDupe import MetaDupe_Image

PROGRAM = "imgconv"

def log(msg : str, Color = CC.RESET) -> None :
    print(f"{Color}[{PROGRAM}] {msg}{CC.RESET}")

def process_file(task : tuple[Path, EncoderPreset, str, bool]) -> tuple[Path, int, int] :
    path, preset, fmt, keep = task
    before = path.stat().st_size
    after = -1

    try :
        output = path.with_suffix(f".{fmt}")
        log(f"  Processing {path}")

        subprocess.run(
             preset.command(path,output),
             check=True,
             stdin=subprocess.DEVNULL,
             stdout=subprocess.DEVNULL,
             stderr=subprocess.PIPE
        )

        if MetaDupe_Image(path,output).exitcode != 0 :
             log(f"Failed to duplicate metadata of {path}", CC.BLUE)

        after = output.stat().st_size
        
        if not keep and output.exists() :
            path.unlink()

    except Exception as e :
        log(f"Failed processing {path} {e}", CC.RED)

    return (output, before, after)

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
    global args
    args = parser.parse_args()
    del parser

    if not Supports.check_format(args.format) or not exiftool_Check(False) :
         raise FileNotFoundError(f"{CC.FATAL}Tool not found")

    # Ensure preset is correct
    preset_str = args.preset if isinstance(args.preset, str) else args.preset.name.lower()
        
    # Setup Process
    PRESET = Encoder_Presets.get_preset(args.format, preset_str)
    PATHS = LocateImages(args.input_paths, args.recursive)
    BAS_SIZE = 0
    RES_SIZE = 0
    PROCESESD = 0
    log(f"Images found : {len(PATHS)}", CC.INFO)
    log(f"Converting to {args.format} using {preset_str} preset", CC.INFO)

    tasks = [
         (path, PRESET, args.format, args.keep)
         for path in PATHS
    ]

    log(f"n>> {PRESET.encoder} {" ".join(PRESET.params)}", CC.RED)

    with Pool(args.threads) as pool :
        for _ in pool.imap_unordered(process_file, tasks) :
            if(_[2] != -1) :
                BAS_SIZE += _[1]
                RES_SIZE += _[2]
                PROCESESD += 1
    log(f"Processed {PROCESESD}/{len(PATHS)} images",CC.YELLOW)
    log(f"Space Saved : {SizeToStr(RES_SIZE)}/{SizeToStr(BAS_SIZE)} ({SizeToStr(BAS_SIZE - RES_SIZE)} : {round((RES_SIZE / BAS_SIZE)*100, 4)}%)", CC.YELLOW)



if __name__ == "__main__":
    try :
        START = time.perf_counter()
        Main()
        sys.exit(0)
    except KeyboardInterrupt :
        sys.exit(-1)
    except Exception as e:
        log(f"An error has occored\n{e}")
        sys.exit(-1)
    finally :
        log(f"Time Taken (Menuing Counts) Time taken {ConvertTime(START, time.perf_counter())}", CC.YELLOW)
        Alert()