import os, sys, shutil, argparse
import time
from typing import Union
from pathlib import Path
from Libs.fftools.Legacy import Extract_Cover, Add_Cover, V_Optimizer, VAnalyzer, run, FFMPEG, VIDEO_PRESETS, AUDIO_PRESETS
from Functions.helpers import GetFileSize, SizeToStr, Alert, InputPath, ConvertTime
from Functions.Checkers import ffmpeg_Check

# ==========================
# Functions
# ==========================

def process_video(file_path, a_preset, v_preset, optimize : str, args, target : float = 95) -> str:
    BASE_PATH = os.path.dirname(file_path)
    FILE_NAME = os.path.splitext(os.path.basename(file_path))[0]
    COVER_PATH = f"{BASE_PATH}/{FILE_NAME}_cover.jpg"
    TMP = f"{BASE_PATH}/{FILE_NAME}_out.mp4"
    OUTPUT = f"{BASE_PATH}/{FILE_NAME}_final.mp4"
    optimize = optimize.lower()
    
    #Extract video cover (returns none if doesn't exists)
    IDX = Extract_Cover(file_path, COVER_PATH, False, args.verbose)

    #encode
    OPT = V_Optimizer(v_preset, a_preset, target)
    print(f"\033[38;5;50m[ffcomp] Encoding video... (Source frames {VAnalyzer(file_path).frames})\033[0m")
    try : 
        if optimize == "c" : #Crf optimize (can fallback to bitrate optimize)
            OPT.CRF_Optimize(file_path, TMP, args.crf_base)
        elif optimize == "b" : #Bitrate optimize (not recommend on ANY case)
            OPT.Bitrate_Optimize(file_path, TMP)
        else : #Regular encode
            v_codec = VIDEO_PRESETS[v_preset]["codec"]
            v_param = VIDEO_PRESETS[v_preset]["params"]
            a_codec = AUDIO_PRESETS[a_preset]["codec"]
            a_param = AUDIO_PRESETS[a_preset]["params"]
            if IDX is None : #No cover art is found
                run(f'{FFMPEG} -v error -stats -i "{file_path}" -map 0 -c:s copy '
                    f'-c:d copy -c:a {a_codec} {a_param} -c:v {v_codec} {v_param} "{TMP}"',args.verbose)
            else : #Cover art exists
                run(f'{FFMPEG} -v error -stats -i "{file_path}" -map 0 -map -0:{IDX} -c:s copy '
                    f'-c:d copy -c:a {a_codec} {a_param} -c:v {v_codec} {v_param} "{TMP}"',args.verbose)
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
            Add_Cover(TMP, COVER_PATH, OUTPUT, args.verbose)
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
    parser.add_argument("-v", "--verbose", action="store_false", help="Show ffmpeg command while running")
    parser.add_argument("-cb", "--crf_base", default=42, type=int, help="Set Starting CRF (CRF Optimizer)")
    parser.add_argument("-vp", "--video_preset", default=-1, type=int, help="Select Video Preset")
    parser.add_argument("-ap", "--audio_preset", default=-1, type=int, help="Select Audio Preset")
    parser.add_argument("-o", "--optimize", default="", type=str, help="Optimization Mode (b : bitrate, c : crf, n : none)")
    parser.add_argument("-t", "--target", default=-1, type=int, help="Optimize Target (vmaf score)")
    parser.add_argument("-i", "--input", default="", type=str, help="Input path")
    args = parser.parse_args()
    del parser #Unload Parser
    
    v_select = args.video_preset
    if v_select == -1 :
        for c,preset in enumerate(VIDEO_PRESETS) :
            print(f"{c} : {preset}")
        v_select = int(input("\033[38;5;46mSlect video preset:\033[0m").strip())
    if v_select >= 0 and v_select < len(VIDEO_PRESETS) :
        for c,preset in enumerate(VIDEO_PRESETS) :
            if c == int(v_select) :
                v_preset = preset
                if preset == "custom" :
                    custom_codec = input("\033[38;5;46mEnter ffmpeg encoder:\033[0m") 
                    custom = input("\033[38;5;46mEnter ffmpeg params:\033[0m")
                    VIDEO_PRESETS["custom"] = {"codec" : custom_codec, "params" : custom}
    else :
        print("\033[38;5;46mInvalid Choice\033[0m")
        return
    
    a_select = args.audio_preset
    if a_select == -1 :
        for c,preset in enumerate(AUDIO_PRESETS) :
            print(f"{c} : {preset}")
        a_select = int(input("\033[38;5;46mSlect audio preset:\033[0m").strip())
    if a_select >= 0 and a_select < len(AUDIO_PRESETS) :
        for c,preset in enumerate(AUDIO_PRESETS) :
            if c == int(a_select) :
                a_preset = preset
                if preset == "custom" :
                    custom_codec = input("\033[38;5;46mEnter ffmpeg encoder:\033[0m") 
                    custom = input("\033[38;5;46mEnter ffmpeg params:\033[0m")
                    AUDIO_PRESETS["custom"] = {"codec" : custom_codec, "params" : custom}
    else :
        print("\033[38;5;46mInvalid Choice\033[0m")
        return
    
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