import os, sys, shutil, argparse, time
from typing import Union
from pathlib import Path

from Libs.fftools.Optimizers import V_Optimizer
from Libs.fftools.Preset import (
    VideoPreset, VideoModifier, GetVideoPreset, BuildVideoPreset,
    AudioPreset, GetAudioPreset, BuildAudioPreset,
    Preset, prompt_custom_preset, ApplyVideoModifiers
)
from Libs.fftools.Media import CoverManager
from Libs.fftools import RunFFmpeg, ffmpeg_Check, ConvertTime, VAnalyzer, LogLevel

from Functions.helpers import GetFileSize, SizeToStr, Alert, InputPath

CM : CoverManager

# ==========================
# Functions
# ==========================

def process_video(
        file_path, a_preset : Preset, v_preset : Preset, 
        optimize : str, args, target : float = 95
) -> str:
    global CM
    BASE_PATH = os.path.dirname(file_path)
    FILE_NAME = os.path.splitext(os.path.basename(file_path))[0]
    COVER_PATH = f"{BASE_PATH}/{FILE_NAME}_cover.jpg"
    TMP = f"{BASE_PATH}/{FILE_NAME}_out.mp4"
    OUTPUT = f"{BASE_PATH}/{FILE_NAME}_final.mp4"
    optimize = optimize.lower()
    
    #Extract video cover (returns none if doesn't exists)
    IDX = CM.extract_cover(file_path, COVER_PATH)

    #encode
    OPT = V_Optimizer(v_preset, a_preset, target)
    print(f"\033[38;5;50m[ffcomp] Encoding video... (Source frames {VAnalyzer(file_path).frames})\033[0m")
    
    try : 
        if optimize == "c" : #Crf optimize (can fallback to bitrate optimize)
            OPT.CRF_Optimize(file_path, TMP, args.crf_base)
        elif optimize == "b" : #Bitrate optimize (not recommend on ANY case)
            OPT.Bitrate_Optimize(file_path, TMP)
        else : #Regular encode
            RunFFmpeg(
                inputs=file_path,
                output=TMP,
                args=[
                    "-map", "0",
                    *(["-map", f"-0:{IDX}"] if IDX is not None else []), # Cover art detection
                    "-c:s", "copy", "-c:d", "copy",
                    *BuildAudioPreset(a_preset),
                    *BuildVideoPreset(v_preset)
                ],
                loglevel=LogLevel.ERROR,
                show_status=True,
                show_command=args.verbose
            )
    except KeyboardInterrupt :
        print("[ffcomp] Ctrl + C Recived")
        for _ in (TMP, OUTPUT, COVER_PATH, "1Frame_Base.mp4") :
            if os.path.exists(_) :
                os.remove(_)
        raise KeyboardInterrupt
    except Exception as e:
        print("\033[38;5;128m[ffcomp] Encoding Failed\033[0m")
        print(e.args)
    
    #reattach cover art
    if os.path.exists(COVER_PATH) :
        try :
            print("\033[38;5;50m[ffcomp] Adding Cover picture\033[0m")
            CM.add_cover(TMP, COVER_PATH, OUTPUT)
            os.remove(COVER_PATH)
            os.remove(TMP)
        except Exception as e :
            print(f"\033[38;5;128m[ffcomp] Failed to add cover picture {e}\033[0m")
    else :
        os.rename(TMP,OUTPUT)
    return OUTPUT
def Is_Bigger(INPUT_PATH : Union[str, Path], RESULT_PATH : Union[str, Path]) -> bool :
    print(f"\033[38;5;202m[ffcomp] Original file size {GetFileSize(INPUT_PATH)}")
    print(f"[ffcomp] Result file size {GetFileSize(RESULT_PATH)}\033[0m")
    if os.path.getsize(INPUT_PATH) < os.path.getsize(RESULT_PATH) :
        print("\033[38;5;128m[ffcomp] Result is bigger using old file\033[0m")
        os.remove(RESULT_PATH)
        return True
    return False

# ==========================
# Main Code
# ==========================
def Main():
    #arguments
    parser = argparse.ArgumentParser(formatter_class= argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-v", "--verbose", action="store_true", help="Show ffmpeg command while running")
    parser.add_argument("-i", "--input", default="", type=str, help="Input path")
    
    parser.add_argument("-vp", "--video_preset", type=str, choices=VideoPreset.Presets(), help="Video Preset")
    parser.add_argument("-fps", "--fps48", action="store_true", help="Cap FPS to 48")
    parser.add_argument("-vfr", "--vfr", action="store_true", help="Use Variable Frame Rate (mpdecimate)")
    parser.add_argument("-bit", "--bit10", action="store_true", help="Use 10-bit pixel format (yuv420p10le)")

    parser.add_argument("-ap", "--audio_preset", type=str, choices=AudioPreset.Presets(), help="Audio Preset")
    
    parser.add_argument("-o", "--optimize", default="", type=str, help="Optimization Mode (b : bitrate, c : crf, n : none)")
    parser.add_argument("-cb", "--crf_base", default=42, type=int, help="Set Starting CRF (CRF Optimizer)")
    parser.add_argument("-t", "--target", default=-1, type=int, help="Optimize Target (vmaf score)")
    
    args = parser.parse_args()
    del parser #Unload Parser
    
    global CM
    CM = CoverManager(show_command=False, verbose=args.verbose)

    # ========== VIDEO PRESET ==========
    v_select = args.video_preset
    modifier = VideoModifier.NONE
    
    # Preset selection
    if v_select is None:
        VPS = VideoPreset.Presets()
    
        for c, preset in enumerate(VPS):
            print(f"{c} : {preset}")
    
        print(f"{len(VPS)} : custom")
    
        try:
            choice = int(input("\033[38;5;46mSelect video preset:\033[0m ").strip())
        except ValueError:
            print("\033[38;5;46mInvalid Choice\033[0m")
            return
    
        if choice == len(VPS):
            v_preset = prompt_custom_preset("Video Preset")
            v_select = None
        elif 0 <= choice < len(VPS):
            v_select = VPS[choice]
        else:
            print("\033[38;5;46mInvalid Choice\033[0m")
            return
    
    # Collect CLI modifiers
    if args.fps48:
        modifier |= VideoModifier.FPS_48
    
    if args.vfr:
        modifier |= VideoModifier.VFR
    
    if args.bit10:
        modifier |= VideoModifier.BIT_10
    
    # Prompt for modifiers only when preset was not provided through CLI
    if args.video_preset is None and v_select is not None:
        if not args.fps48 and input("Enable 48 FPS? [y/N]: ").strip().lower() == "y":
            modifier |= VideoModifier.FPS_48
    
        if not args.vfr and input("Enable VFR (drop similar frames)? [y/N]: ").strip().lower() == "y":
            modifier |= VideoModifier.VFR
    
        if not args.bit10 and input("Enable 10-bit? [y/N]: ").strip().lower() == "y":
            modifier |= VideoModifier.BIT_10

    # Build preset
    if v_select is not None:
        if isinstance(v_select, str):
            v_select = VideoPreset[v_select.upper()]
    
    v_preset = GetVideoPreset(v_select, modifier)

    # ========== AUDIO PRESET ==========
    a_select = args.audio_preset

    # Preset selection
    if a_select is None:
        APS = AudioPreset.Presets()
    
        for c, preset in enumerate(APS):
            print(f"{c} : {preset}")
    
        print(f"{len(APS)} : custom")
    
        try:
            choice = int(input("\033[38;5;46mSelect audio preset:\033[0m ").strip())
        except ValueError:
            print("\033[38;5;46mInvalid Choice\033[0m")
            return
    
        if choice == len(APS):
            a_preset = prompt_custom_preset("Audio Preset")
            a_select = None
        elif 0 <= choice < len(APS):
            a_select = APS[choice]
        else:
            print("\033[38;5;46mInvalid Choice\033[0m")
            return

    # Build preset
    if a_select is not None:
        if isinstance(a_select, str):
            a_select = AudioPreset[a_select.upper()]

    a_preset = GetAudioPreset(a_select)

    #Mode Select
    optimize = (args.optimize).strip().lower()
    target = args.target
    if optimize == "" :
        optimize = input("\033[38;5;46mOptimize Bitrate/CRF/None? (b/c/n)\n\033[31mNOTE: May take very long time!!\n\033[0m").strip().lower()
    if optimize in ("b", "bitrate") :
        optimize = "b"
    elif optimize in ("c", "crf") :
        optimize = "c"
    else :
        optimize = "n"
    if optimize != "n" and target < 0 :
        target = float(input("\033[38;5;46mEnter optimize target (vmaf score)\n   95-100 : Visually lossless\n    90-94 Very hard to spot\n   <90 lossy\nInput : \033[0m"))

    INPUT_PATH = args.input
    if INPUT_PATH == "" :
        INPUT_PATH = InputPath("\033[38;5;46mEnter Input path :\033[0m")
    else :
        INPUT_PATH = InputPath(INPUT_PATH, True)
    if os.path.isdir(INPUT_PATH) : #Batch mode
        RES_PATH = os.path.join(INPUT_PATH, "res")
        F_COUNT = F_TOTAL = 0

        SRC = []
        RES = []
        if os.path.exists(RES_PATH) : #make result folder delete if exists
            shutil.rmtree(RES_PATH)
        os.mkdir(RES_PATH)
        try :
            for file in os.listdir(INPUT_PATH):
                if file.lower().endswith((".mp4", ".mkv", ".mov")) :
                    print(f"\033[38;5;46m[ffcomp] Processing {file}\033[0m")
                    F_TOTAL += 1
                    filepath = os.path.join(INPUT_PATH,file)
                    res = process_video(filepath, a_preset, v_preset, optimize, args, target)
                    SRC.append(os.path.getsize(filepath))
                    
                    
                    if Is_Bigger(filepath, res) :
                        RES.append(os.path.getsize(filepath)) #Uses Old file
                        shutil.copyfile(os.path.join(INPUT_PATH,file), os.path.join(RES_PATH,file))
                    else :
                        RES.append(os.path.getsize(res))#Uses New file
                        shutil.move(res, RES_PATH)
                        os.rename(os.path.join(RES_PATH,os.path.basename(res)), os.path.join(RES_PATH,file.replace("_final","",1)))
                        F_COUNT += 1
        except KeyboardInterrupt :
            raise KeyboardInterrupt
        finally :
            print(f"\033[38;5;46m[ffcomp] Processed {F_COUNT} / {F_TOTAL}\033[0m")
            print(f"\033[38;5;46m[ffcomp] File Size {SizeToStr(sum(RES))} / {SizeToStr(sum(SRC))} ({SizeToStr(sum(SRC) - sum(RES))} : {round((sum(RES)/sum(SRC))*100, 2)}%)\033[0m")
    else : #Single file mode
        res = process_video(INPUT_PATH, a_preset, v_preset, optimize, args, target)
        Is_Bigger(INPUT_PATH, res)

if __name__ == "__main__" :
    START = time.perf_counter()
    try :
        ffmpeg_Check(True)
        Main()
        sys.exit(0)
    except KeyboardInterrupt :
        sys.exit(1)
    except Exception as e :
        print(f"[ffcomp] An error has occored\n{e}\033[0m")
        sys.exit(-1)
    finally :
        print(f"\033[38;5;226m[ffcomp] Time Taken (Menuing Counts) Time taken {ConvertTime(START, time.perf_counter())}\033[0m")
        Alert()