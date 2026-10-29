from ..Preset import Preset, RATE_KEYS, MAX_CRF, BuildAudioPreset, BuildVideoPreset
from ..Analyzer import VAnalyzer, Comparator
from .. import RunFFmpeg, LogLevel, ConvertTime

from typing import Union
from pathlib import Path
import re, os
import math, time

class V_Optimizer : 
    '''Video Optimizer'''
    def __init__(self, Vpreset : Preset, Apreset : Preset, target : float = 93):
        '''
        Video Optimizer
        
        :param v_preset: Video preset
        :param a_preset: Audio preset
        :param target: VMAF target
        :type target: float
        '''
        
        #simplify and remove rate controls from preset
        self.null_device = "NUL" if os.name == "nt" else "/dev/null"
        self.Vpreset = self.__StripRateControls(Vpreset)
        self.Vpreset.rate_controls["b:v"] = 0
        self.Apreset = Apreset
        self.target = target

    def __StripRateControls(self, Vp : Preset) -> Preset:
        for _ in RATE_KEYS :
            if _ in Vp.rate_controls :
                Vp.rate_controls.pop(_)
        return Vp
    def __GetMax_CRF(self) -> int :
        '''
        Returns maximum usable crf of an libary
        
        :return: Maximum crf
        :rtype: int
        '''
        if self.Vpreset.codec in MAX_CRF[63] :
            return 46 #Safe range (This keep simple fade+statc from breaking)
        elif self.Vpreset.codec in MAX_CRF[51] :
            return 36 #Safe range 
        else :
            return 42 #Assume this on all other formats
    
    def Is1Frame(self, in_path : Union[str, Path], out_path : Union[str, Path]) -> bool :
        '''
        Check if video is actually static the kind that 1 frame will do\n
        This supposed to be a private Function but whateaver
        
        :param in_path: Input path
        :type in_path: Union[str, Path]
        :return: Check result
        :rtype: bool
        '''
        print(f"\033[38;5;46m[Optimizer] Checking For Static Video\033[0m")

        #Check Static
        result = RunFFmpeg(
            inputs=in_path,
            output=self.null_device,
            args=['-vf', 'mpdecimate', "-f", "null"],
            loglevel=LogLevel.FATAL,
            show_status=True,
            show_command=False,
            capture_output=True
        )

        #Extract frame counts from video
        m = re.findall(r'frame=\s*(\d+)', result.stderr)
        frames = int(m[-1]) if m else 0

        print(f"\033[38;5;46m[Optimizer] Unique Frames {frames}\033[0m")

        if frames <= 2 :
            print(f"\033[38;5;50m[Optimizer] True Static Video Detected, Optimizing For Static Video\033[0m")
            
            RunFFmpeg(
                inputs=input,
                output="1Frame_Base.mp4",
                args=["-map_metadata", "0", "-c", "copy"],
                loglevel=LogLevel.FATAL
            ) #This remove things like cover
            
            RunFFmpeg(
                inputs="1Frame_Base.mp4",
                output=Path(out_path) if isinstance(out_path, str) else out_path,
                args=[
                    "-map_metadata", "0", "-map", "0", 
                    "-vf", "mpdecimate", "-fps_mode", "vfr",
                    "-c:s", "copy", "-c:d", "copy",
                    *BuildAudioPreset(self.Apreset),
                    "-c:v", "libaom-av1", "-cpu-used", "1",
                    "-pix_fmt", "yuv420p10le", "-still-picture", "1",
                    "-crf", "38", "-b:v", "0"
                ],
                loglevel=LogLevel.FATAL,
                show_status=True,
                show_command=False
            )
            os.remove("1Frame_Base.mp4")
            return True
        return False

    def CRF_Optimize(
            self, in_path : Union[str, Path], out_path : Union[str, Path], 
            crf_base : int = 42, crf_floor : int = 0, 
            margin : float = 1.0
    ) -> None :
        '''
        Optimize crf for an video (this sacrifices a lot of time)

        :param in_path: Input path
        :type in_path: Path
        :param out_path: Output path
        :type out_path: Path
        :param crf_base: Starting CRF
        :type crf_base: int
        :param crf_floor: Minimum CRF (0 = repeat until abort condition met)
        :type crf_floor: int
        :param margin: Margin to trigger bitrate optimize
        :type margin: float
        '''
        if self.Is1Frame(in_path, out_path) : # Check for fully static video. Take forever for long videos
            return
        
        #Doesn't use binary seach because this should be faster on avarage
        def decay(current_crf, current_score, target, previous_crf = None, previous_score = None) :
            distance = target - current_score  
            pred_crf = None
            dist_crf = 0
            
            if previous_score is not None and previous_crf is not None:
                  # Calculate VMAF gain per CRF step
                  vmaf_gain = current_score - previous_score
                  crf_change = previous_crf - current_crf
                  
                  if crf_change > 0 and vmaf_gain > 0:  # Valid data
                      vmaf_per_crf = vmaf_gain / crf_change
                      
                      # Predict how many CRF steps we need
                      if vmaf_per_crf > 0.1:  # Reasonable gain rate
                          predicted_steps = distance / vmaf_per_crf
                          step = int(max(2, min(6, predicted_steps)))
                          pred_crf = current_crf - step

            # Fallback to distance-based decay
            if distance > 12 :
                dist_crf = current_crf - 8
            elif distance > 8:
                dist_crf = current_crf - 6
            elif distance > 4:
                dist_crf = current_crf - 4 
            elif distance > 1:
                dist_crf = current_crf - 3
            else:
                dist_crf = current_crf - 1
            candidate = dist_crf if pred_crf is None else max(pred_crf,dist_crf)
            return max(CRF_FLOOR, candidate) #Uses higher decay between 2 method

        #Redefine variable so it's more readable
        TMP_FOLDER = f'{os.path.dirname(in_path)}//_TMP' #Temppath
        
        CRF_BASE = crf_base             #Starting CRF
        CRF_FLOOR = crf_floor           #Minimum CRF
        CRF_MAX = self.__GetMax_CRF()   #Maximum safe CRF

        VMAF_TARGET = self.target       #Target quality
        VMAF_MARGIN = margin            #Error margin (Bitrate fallback)

        START = time.perf_counter()     #timer
        
        #Main process
        print(f"\033[38;5;46m[Optimizer] Optimizing {os.path.basename(in_path)}\033[0m")

        #Make TMP folder
        if not os.path.exists(TMP_FOLDER) :
            os.mkdir(TMP_FOLDER)

        #make a copy of video (this should remove thigs like cover. Bad for big files)
        RunFFmpeg(
            inputs=in_path,
            output=f"{TMP_FOLDER}/base.mp4",
            args=["-map_metadata", "0", "-c", "copy"],
            loglevel=LogLevel.FATAL,
            show_status=False,
            show_command=False
        )

        file_c = f'{TMP_FOLDER}/base.mp4'
        SOURCE_SIZE = os.path.getsize(file_c)

        crf = CRF_BASE
        previous_crf = None
        previous_score = None
        Comp = Comparator(fast=False, show_command=False)
        while True :
            out = f'{TMP_FOLDER}/{crf}.mp4'
            print(f"\033[38;5;50m[Optimizer] Attempting crf {crf} ({ConvertTime(START, time.perf_counter())})\033[0m")

            #Encode
            self.Vpreset.rate_controls["crf"] = crf
            RunFFmpeg(
                inputs=file_c,
                output=out,
                args=[
                    '-map_metadata', "0", "-map", "0",
                    "-c:s", "copy", "-c:d", "copy",
                    *BuildAudioPreset(self.Apreset),
                    *BuildVideoPreset(self.Vpreset)
                ],
                loglevel=LogLevel.FATAL,
                show_command=False
            )

            #Generate score
            score = Comp.get_vmaf(original=file_c, encoded=out, recursive=True)
            print(f"  Score : {score}")

            #If result is bigger than source abort even if it pass vmaf
            if os.path.getsize(out) > SOURCE_SIZE :
                print("\033[38;5;46m[Optimizer] Output Is Larger Than Source Aborting...\033[0m")
                out = in_path
                if score >= VMAF_TARGET - VMAF_MARGIN : #Switch to bitrate opimize if close enough
                    print("\033[38;5;46m[Optimizer] Condition met, Switching to Bitrate Optimize\033[0m")
                    self.Bitrate_Optimize(in_path, out_path, Fallback=True)
                    return
                break

            #Exit conditions
            if score >= VMAF_TARGET :
                if crf == CRF_BASE : #If it pass on very first attempt
                    if crf == CRF_MAX : #Prevent infinite loop at CRF_MAX
                        break
                    crf = min(crf + 10, CRF_MAX)
                    CRF_BASE = crf #Ajust CRF_BASE accordingly (this allow 32 -> 42 -> 52)
                    continue #Skip ajustment part
                else :
                    break #Regular exit conditions
                 
            #Ajustments
            new_crf = max(CRF_FLOOR, decay(crf, score, VMAF_TARGET, previous_crf, previous_score))
            previous_crf = crf
            previous_score = score
            crf = new_crf

            #Terminator (If somehow it managed to reach)
            if crf == CRF_FLOOR : #Minimum CRF allowed
                print("\033[38;5;46m[Optimizer] CRF floor reached skipping...\033[0m")
                break
            elif crf == CRF_MAX : #Maximum CRF allowed
                print("\033[38;5;46m[Optimizer] CRF celing reached skipping...\033[0m")
                break

        print(f"\033[38;5;46m[Optimizer] Using CRF {crf}\n[Optimizer] Time taken {ConvertTime(START, time.perf_counter())}\033[0m")
        RunFFmpeg(
            inputs=f"{TMP_FOLDER}/{crf}.mp4",
            output=out_path,
            args=["-map_metadata", "0", "-c", "copy"],
            loglevel=LogLevel.FATAL,
            show_status=False,
            show_command=False
        )
    def Bitrate_Optimize(self, in_path : Union[str, Path], out_path : Union[str, Path], Fallback : bool = False) -> None :
        '''
        Optimize bitrate for an video may not works well on static video(this sacrifices a lot of time)
        
        :param in_path: Input path
        :type in_path: Path
        :param out_path: Output path
        :type out_path: Path
        '''
        if not Fallback and self.Is1Frame(in_path, out_path) : #If video Is just a static image
            return
        TMP = f'{os.path.dirname(in_path)}//_TMP' #Temppath
        
        MIN_RATE = 50 #kbits
        MAX_RATE = round(VAnalyzer(in_path).bitrate)
        BEST_RATE = MAX_RATE
        BASE_RATE = MAX_RATE
        VMAF_TARGET = self.target

        #Total rounds of binary search               #Precision
        ROUNDS = math.ceil( math.log2( (MAX_RATE - MIN_RATE) / 50 ) )
        START = time.perf_counter() #Timer

        print(f"\033[38;5;46m[Optimizer] Optimizing Bitrate for {os.path.basename(in_path)}\033[0m")
        if not os.path.exists(TMP) :
            os.mkdir(TMP)

        #make a copy of video (this should remove thigs like cover)
        RunFFmpeg(
            inputs=in_path,
            output=f"{TMP}/base.mp4",
            args=["-map_metadata", "0", "-c", "copy"],
            loglevel=LogLevel.FATAL,
            show_status=False,
            show_command=False
        )
        file_c = f'{TMP}/base.mp4'
        
        #Start binary seasch
        Comp = Comparator(False, True)
        for i in range(ROUNDS) :
            mid = round((MIN_RATE + MAX_RATE) / 2)
            out = f'{TMP}/{mid}.mp4' #easier bitrate viewing on windows
            print(f"\033[38;5;50m[{i + 1}/{ROUNDS}] Attempting {mid}k Best:{BEST_RATE}k ({ConvertTime(START, time.perf_counter())})\033[0m")

            #Encode
            ######################################################################################################
            self.Vpreset.rate_controls["b:v"] = f"{mid}k"
            RunFFmpeg(
                inputs=file_c,
                output=self.null_device,
                args=[
                    "-map_metadata", "0", "-map", "0",
                    "-c:s", "copy", "-c:d", "copy", "-an",
                    *BuildVideoPreset(self.Vpreset),
                    "-pass", "1", "-f", "null"
                ],
                loglevel=LogLevel.FATAL,
                show_status=True,
                show_command=False
            )

            RunFFmpeg(
                inputs=file_c,
                output=out,
                args=[
                    "-map_metadata", "0", "-map", "0",
                    "-c:s", "copy", "-c:d", "copy",
                    *BuildAudioPreset(self.Apreset),
                    *BuildVideoPreset(self.Vpreset),
                    "-pass", "2"
                ],
                loglevel=LogLevel.FATAL,
                show_status=True,
                show_command=False
            )

            #calculate score
            score = Comp.get_vmaf(file_c, out)
            print(f'vmaf score : {score}')

            #Binary search thing
            if score >= VMAF_TARGET :
                MAX_RATE = mid
                BEST_RATE = mid
            else :
                MIN_RATE = mid

        print(f"\033[38;5;46m[Optimizer] Using bitrate {BEST_RATE}\n[Optimizer]Time taken {ConvertTime(START, time.perf_counter())}\033[0m")
        
        if BEST_RATE == BASE_RATE :
            RunFFmpeg(
               inputs=f"{TMP}/base.mp4",
               output=out_path,
               args=["-map_metadata", "0", "-c", "copy"],
               loglevel=LogLevel.FATAL,
               show_status=False,
               show_command=False
           )
        else :
            RunFFmpeg(
                inputs=f"{TMP}/{BEST_RATE}.mp4",
                output=out_path,
                args=["-map_metadata", "0", "-c", "copy"],
                loglevel=LogLevel.FATAL,
                show_status=False,
                show_command=False,
            )
