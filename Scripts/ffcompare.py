from Projects.fftools.fffunctions import Comparator, VAnalizer
from Functions.helpers import Alert, InputPath
import sys, argparse
if __name__ == "__main__" :
    try :
        parser = argparse.ArgumentParser(formatter_class= argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument("-b", "--base", default=None, type=str, help="Base file path")
        parser.add_argument("-c", "--compare", default=None, type=str, help="Compare Target")
        parser.add_argument("-v", "--verbose", action="store_true", help="Show more info")
        args = parser.parse_args()
        del parser #Unload Parser
        
        Base = None
        Comp = None
        if args.base == None :
            Base = InputPath("\033[38;5;46mEnter Base file path:\033[0m")
        else :
            Base = InputPath(args.base, True) 
            
        if args.compare == None :
            Comp = InputPath("\033[38;5;46mEnter file path to compare:\033[0m")
        else :
            Comp = InputPath(args.compare, True)

        COMPARE = Comparator(False, True)

        if (args.verbose) :
            base_analize = VAnalizer(Base)
            comp_analize = VAnalizer(Comp)
            print(f"\033[38;5;50m[ffcompare] Base Frames {base_analize.frames}\033[0m")
            print(f"\033[38;5;50m[ffcompare] Base Bitrate {round(base_analize.bitrate, 2)}k\033[0m")
            print(f"\033[38;5;50m[ffcompare] Comp Frames {comp_analize.frames}\033[0m")
            print(f"\033[38;5;50m[ffcompare] Comp Bitrate {round(comp_analize.bitrate, 2)}k\033[0m")
        
        try :
            print("\033[38;5;50m[ffcompare] Calculating vmaf score\033[0m")
            print(f"vmaf score is {COMPARE.get_vmaf(Base, Comp)}")
        except Exception as e :
            print(f"ERROR {e}")

        try :
            print("\033[38;5;50m[ffcompare] Calculating psnr score\033[0m")
            print(f"psnr score is {COMPARE.get_psnr(Base, Comp)}")
        except Exception as e :
            print(f"ERROR {e}")

        try :
            print("\033[38;5;50m[ffcompare] Calculating ssim score\033[0m")
            print(f"ssim score is {COMPARE.get_ssim(Base, Comp)}")
        except Exception as e :
            print(f"ERROR {e}")
        
        if (args.verbose) :
            print("\033[38;5;46mvmaf score : How people feels\033[0m")
            print("    100-95 Visually lossless\n    94-90  Very hard to spot\n    <90    Lossy")
            print("\033[38;5;46mpsnr score : Pixel error introduced (every +5 is big quality gap)\033[0m")
            print("    >40   Visually lossless\n    35-39 Very hard to spot\n    30-34 Minor Artifact\n    <30   Lossy")
            print("\033[38;5;46mssim score : structure preservation\033[0m")
            print("     >0.990      Visually lossless\n     0.970-0.989 Very hard to spot\n     0.950-0.969 Noticeable\n     <0.95       Lossy")
        
        sys.exit(0)
    
    except KeyboardInterrupt :
        sys.exit(1)
    except Exception as e :
        print(f"[ffcomp] An error has occored\n{e}\033[0m")
        sys.exit(-1)
    finally :
        Alert()