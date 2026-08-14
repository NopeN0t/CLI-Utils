from Colors.ConsoleColors import ConsoleColors as CC
from Functions.helpers import Alert, ConvertTime, SizeToStr, GetFileSize, ImgCorrect
from multiprocessing import pool, cpu_count
import argparse
import sys, time
from Projects.imgconv.Program_Check import Supports, exiftool_Check

PROGRAM = "imgconv"
WORKERS = cpu_count() - 2 if cpu_count() > 2 else 1 #Left threads unused to prevent global OS lag

def log(msg : str, Color = CC.RESET) -> None :
    print(f"{Color}[{PROGRAM}] {msg}{CC.RESET}")

def Main() :    
    parser = argparse.ArgumentParser(formatter_class= argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-i", "--input", default="", type=str, help="Input path")
    parser.add_argument("-f", "--format", choices=["jxl", "webp"])

    
    print(sys.argv)
    print(Supports.JXL.value)
    print(Supports.formats())
    print(exiftool_Check(False))
    pass

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