#Universal Imports
from typing import Union, Optional
from Projects.fftools.ffpresets import *
from Functions.helpers import log, ConvertTime
from Functions.Checkers import ffmpeg_Check
from pathlib import Path
import os, json

# ====================================================
#                   Helper functions
# ====================================================
import re, time, subprocess
def strip_all_rate_controls(params: str) -> str:
    '''Remove all rate controls from an ffmpeg command'''
    for key in RATE_KEYS:
        params = re.sub(fr'{key}\s+\S+', '', params)
    params = re.sub(r'\s+', ' ', params).strip()
    return params
def run(command : str, silent : bool = True, capture_output : bool = False, text : bool = True) -> subprocess.CompletedProcess[str] :
    '''Run an terminal command other overload will be added as needed'''
    #Echo the command
    if not silent :
        log(silent, f"\033[31mn>> {command}\n\033[0m")
    #Run subprocess (params will be added as needed)
    return subprocess.run(command, shell=True, check=True, capture_output=capture_output, text=text)

# ====================================================
#                  helper / Analizer
# ====================================================
class Comparator() :
    '''Collection of analizer'''
    def __init__(self, fast : bool = False, hide_command : bool = False, feedback : bool = True):
        '''
        A collection of analizer for video
        
        :param fast: Enable fast mode (less precise)
        :type fast: bool (False)
        :param hide_command: Don't show what command it's running
        :type hide_command: bool (False)
        :param feedback: Show progress bar
        :type feedback: bool (True)
        '''
        self.fast = fast
        self.hide_command = hide_command
        self.feedback = feedback
    def get_vmaf(self, original : Union[str, Path], encoded : Union[str, Path], recursive : bool = False) -> float :
        '''
        Calculate vmaf
        
        :param original: Base file
        :type original: Path
        :param encoded: Target file
        :type encoded: Path
        '''
        #This is very bad implementation
        #[0:v:0][1:v:0] is to prevent error on file with multiple video source
        if not self.fast :
            run(
                f'{FFMPEG} -v fatal -stats '
                f'-i "{encoded}" -hwaccel auto -i "{original}" '
                f'-lavfi "[0:v:0]scale=iw:ih:flags=bicubic,format=yuv420p[dist];'
                f'[1:v:0]scale=iw:ih:flags=bicubic,format=yuv420p[ref];'
                f'[dist][ref]libvmaf=log_fmt=json:log_path=vmaf.json:'
                f'n_threads={os.cpu_count()}:n_subsample=2" '
                f'-f null -',
                self.hide_command,
                not self.feedback
            )
        else :
            run(
                f'{FFMPEG} -v fatal -stats '
                f'-i "{encoded}" -hwaccel auto -i "{original}" '
                f'-lavfi "[0:v:0]scale=iw:ih:flags=bicubic,format=yuv420p[dist];'
                f'[1:v:0]scale=iw:ih:flags=bicubic,format=yuv420p[ref];'
                f'[dist][ref]libvmaf=log_fmt=json:log_path=vmaf.json:'
                f'n_threads={os.cpu_count()}:n_subsample=10" '
                f'-f null -',
                self.hide_command,
                not self.feedback
            )      
        score = 0
        with open("vmaf.json") as f :
            data = json.load(f)
            score = data["pooled_metrics"]["vmaf"]["mean"]
        os.remove("vmaf.json")

        if score < 65 and not recursive : #Low score (can caused by order of input)
            print("\033[38;5;226m[vmaf] possible missmatch detected\033[0m")
            swapped = self.get_vmaf(encoded, original, True) #RECURSIVEEEE
            print(f"\033[38;5;226m[vmaf] base : {score}, swapped : {swapped}\033[0m")
            return max(score,swapped) #Uses higher one
        return score
    def get_psnr(self, original : Union[str, Path], encoded : Union[str, Path]) -> float:
        '''
        Calculate PSNR score
        
        :param original: Base file
        :type original: Path
        :param encoded: Target file
        :type encoded: Path
        '''
        statfile = "psnr.log"
        run(f'{FFMPEG} -v fatal -stats -i "{original}" -i "{encoded}" -lavfi [0:v:0][1:v:0]psnr=stats_file={statfile} -f null -', self.hide_command, not self.feedback)
        values = []
        with open(statfile, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                match = re.search(r"psnr_avg:([0-9.]+|inf)", line)
                if match:
                    val = match.group(1)
                    if val != "inf":
                        values.append(float(val))
        os.remove(statfile)
        
        if not values:
            return 0.0
        return round(sum(values) / len(values), 6)
    def get_ssim(self, original : Union[str, Path], encoded : Union[str, Path]) -> float:
        '''
        Calculate SSIM score
        
        :param original: Base file
        :type original: Path
        :param encoded: Target file
        :type encoded: Path
        '''
        statfile = "ssim.log"
        run(f'{FFMPEG} -v fatal -stats -i "{original}" -i "{encoded}" -lavfi [0:v:0][1:v:0]ssim=stats_file={statfile} -f null -', self.hide_command, not self.feedback)
        ssim = 0.0
        with open(statfile, "r", encoding="UTF-8", errors="ignore") as f :
            for line in f :
                if "All:" in line :
                    match = re.search(r"All:([0-9.]+)", line)
                    if match:
                        ssim = float(match.group(1))
                    break
        os.remove(statfile)
        return ssim

class VAnalizer() :
    '''A fully self contained Video Analizer'''
    def __init__(self, file_path: Union[str, Path]):
        '''
        A fully self contained Video Analizer
    
        :param file_path: input path
        :type file_path: Union[str, Path]
        '''
        file_path = str(file_path)

        cmd = [
            "ffprobe",
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries",
            "stream=codec_name,profile,level,width,height,pix_fmt,"
            "bit_rate,r_frame_rate,avg_frame_rate,nb_frames,"
            "duration,display_aspect_ratio,sample_aspect_ratio,"
            "color_space,color_transfer,color_primaries,has_b_frames",
            "-of", "json",
            file_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)["streams"][0]

        def parse_ratio(value: str) -> float:
            if not value or value == "0/0":
                return 0.0
            num, den = value.split("/")
            return float(num) / float(den)

        def safe_int(value):
            try:
                return int(value)
            except (TypeError, ValueError):
                return 0

        def safe_float(value):
            try:
                return float(value)
            except (TypeError, ValueError):
                return 0.0

        # core video properties
        self.codec = data.get("codec_name")
        self.profile = data.get("profile")
        self.level = data.get("level")

        self.width = safe_int(data.get("width"))
        self.height = safe_int(data.get("height"))

        self.pix_fmt = data.get("pix_fmt")

        self.fps = round(parse_ratio(data.get("r_frame_rate", "0/1")), 4)
        self.avg_fps = round(parse_ratio(data.get("avg_frame_rate", "0/1")), 4)

        self.frames = safe_int(data.get("nb_frames"))
        self.bitrate = safe_float(data.get("bit_rate")) / 1000.0

        self.duration = safe_float(data.get("duration"))

        # aspect ratios
        self.dar = data.get("display_aspect_ratio")
        self.sar = data.get("sample_aspect_ratio")

        # color info
        self.color_space = data.get("color_space")
        self.color_transfer = data.get("color_transfer")
        self.color_primaries = data.get("color_primaries")

        # encoding structure
        self.has_b_frames = safe_int(data.get("has_b_frames"))
    def __repr__(self):
        return (
            f"VAnalyzer(codec={self.codec}, "
            f"resolution={self.width}x{self.height}, "
            f"fps={self.fps}, avg_fps={self.avg_fps}, frames={self.frames}, "
            f"bitrate={self.bitrate:.2f} kbps)"
        )

# ====================================================
#                   Cover Related
# ====================================================
import mimetypes, struct, base64

def Extract_Cover(file_path : Union[str, Path], cover_path : Union[str, Path], silent : bool = False, hide_command : bool = False) -> Union[int, None] :
    '''
    Extract cover from a file to provided path

    :param file_path: Input file
    :type file_path: Path
    :param cover_path: Where to save cover to
    :type cover_path: Path
    :param silent: Show/Hide message
    :type silent: bool
    :param hide_command: Prevent command from displaing in console
    :type hide_command: bool
    :return: Return track id of cover (None if not found)
    :rtype: int
    '''
    #extract cover art (if exists)
    log(silent, "\033[38;5;50m[CoverExtract] Extracting cover art...\033[0m")

    #Get streams
    probe = run(f'ffprobe -v quiet -print_format json -show_streams "{file_path}"', hide_command, True, True)
    data = json.loads(probe.stdout)

    for s in data["streams"]:
        #locate png mjpeg jpeg streams (likely to be cover)
        if s["codec_type"] == "video" and s["codec_name"] in ("png", "mjpeg", "jpeg"):
            #Extract the cover
            run(f'{FFMPEG} -v quiet -i "{file_path}" -map 0:{s["index"]} -frames:v 1 "{cover_path}"', hide_command)
            # log(silent, "\033[38;5;50m[CoverExtract] Done\033[0m")
            return s["index"] #Return cover stream id

    #Backup method
    try :
        #Extract from metadata
        run(f'{FFMPEG} -v quiet -i "{file_path}" -map 0:v:m:attached_pic "{cover_path}"',hide_command)
        # log(silent, "\033[38;5;50m[CoverExtract] Done\033[0m")
        return None #No id since it doesn't use one
    except :
        log(silent, "\033[38;5;50m[CoverExtract] No cover art found, Skipping\033[0m")
        return None 

def Remove_Cover(file_path : Union[str, Path], output : Optional[Union[str, Path]] = None, hide_command = False) -> Path :
    '''
    Remove cover from the file
    
    :param file_path: Input file
    :type file_path: Path
    :param output: Where to save (Optional) 
    :type output: Path
    :param hide_command: Prevent command from displaing in console
    :type hide_command: bool
    :return: Where output is generated
    :rtype: Path
    '''
    if not str(file_path).lower().endswith(COVER_FORMATS) :
        raise NotImplementedError("[RemoveCover] this file format is not supported")
    
    # ignore if it aready is
    OUTPUT = output
    FILENAME = os.path.splitext(os.path.basename(file_path))
    if output == None : #If output path is not provided devrive one from input
        OUTPUT = f'{os.path.dirname(file_path)}/{FILENAME[0]}_res{FILENAME[1]}'
    SUFFIX = FILENAME[1]

    if SUFFIX == ".mp3" : #Process mp3
        run(f'{FFMPEG} -v error -i "{file_path}" {COVER_PRESETS_REMOVE["MP3"]} "{OUTPUT}"',hide_command)
    elif SUFFIX == ".flac" : #Process flac
        run(f'{FFMPEG} -v error -i "{file_path}" {COVER_PRESETS_REMOVE["FLAC"]} "{OUTPUT}"',hide_command)
    elif SUFFIX == ".ogg" or SUFFIX == ".opus": #Process ogg / opus
        with open("./tmp.ffmeta", "w", encoding="ascii") as f : #Generate empty metadata
            f.write(";FFMETADATA1\n")
        run(f'{FFMPEG} -v error -i "{file_path}" -i "./tmp.ffmeta" {COVER_PRESETS_REMOVE['OGG/OPUS']} "{OUTPUT}"', hide_command)
        os.remove("./tmp.ffmeta")
    elif SUFFIX == ".mp4" : #Process mp4
        run(f'{FFMPEG} -v error -i "{file_path}" {COVER_PRESETS_REMOVE['MP4']} "{OUTPUT}"',hide_command)
    return Path(str(OUTPUT))

def Add_Cover(file_path : Union[str, Path], image_path : Union[str, Path], output : Optional[Union[str, Path]] = None, hide_command = False) -> Path :
    '''
    Add front cover to the file
    
    :param file_path: Input file
    :type file_path: Path
    :param image_path: Cover path
    :type image_path: Path
    :param output: Where to save (Optional) 
    :type output: Path
    :param hide_command: Prevent command from displaing in console
    :type hide_command: bool
    :return: Where output is generated
    :rtype: Path
    '''
    if not str(file_path).lower().endswith(COVER_FORMATS) :
        raise NotImplementedError("[AddCover] this file format is not supported")
    
    #Make an jpg cover (Some options embed cover to the file)
    if not os.path.basename(image_path).lower().endswith(".jpg") :
        tmppath = image_path.replace(os.path.basename(image_path), "cover.jpg") # type: ignore Some format requried the file to be named cover.jpg
        run(f'{FFMPEG} -v error -i "{image_path}" -q:v 1 "{tmppath}"', hide_command) #convert image (this make image on base_path not res)
        image_path = tmppath #Re-route image_path
    # ignore if it aready is
    OUTPUT = output
    FILENAME = os.path.splitext(os.path.basename(file_path))
    if output == None : #If output path is not provided devrive one from input
        OUTPUT = f'{os.path.dirname(file_path)}/{FILENAME[0]}_res{FILENAME[1]}'
    SUFFIX = FILENAME[1]

    if SUFFIX == ".mp3" : #Process mp3
        run(f'{FFMPEG} -v error -i "{file_path}" -i "{image_path}" {COVER_PRESETS_ADD["MP3"]} "{OUTPUT}"',hide_command)
    elif SUFFIX == ".flac" : #Process flac
        run(f'{FFMPEG} -v error -i "{file_path}" -i "{image_path}" {COVER_PRESETS_ADD["FLAC"]} "{OUTPUT}"',hide_command)
    elif SUFFIX == ".ogg" or SUFFIX == ".opus": #Process ogg / opus
        try : #Embed the cover into the file
            Metadata_block_cover(str(image_path))
            run(f'{FFMPEG} -v error -i "{file_path}" -i "./tmp.ffmeta" -map 0:a -map_metadata 1 -c copy "{OUTPUT}"', hide_command)
            os.remove("./tmp.ffmeta")
        except :
            log(False, "\033[38;5;128m[Add_Cover] Embeding failed falling back to external cover\033[0m")
            run(f'{FFMPEG} -v error -i "{file_path}" {COVER_PRESETS_ADD["OGG/OPUS"]} "{OUTPUT}"', hide_command) #Non embed version
    elif SUFFIX == ".mp4" :
        run(f'{FFMPEG} -v error -i "{file_path}" -i "{image_path}" {COVER_PRESETS_ADD['MP4']} "{OUTPUT}"',hide_command)
    return Path(str(OUTPUT))
def Metadata_block_cover(cover_path: str) -> None:
    '''Generate Metadata block for cover art'''
    cover = Path(cover_path)

    mime, _ = mimetypes.guess_type(cover)
    if mime not in ("image/jpeg", "image/png"):
        raise ValueError("Cover must be JPEG or PNG")

    img_data = cover.read_bytes()

    picture_type = 3  # front cover
    description = b"Cover (front)"
    width = height = depth = colors = 0

    block = b"".join([
        struct.pack(">I", picture_type),
        struct.pack(">I", len(mime)), mime.encode(),
        struct.pack(">I", len(description)), description,
        struct.pack(">IIII", width, height, depth, colors),
        struct.pack(">I", len(img_data)),
        img_data
    ])

    with open("./tmp.ffmeta", "w", encoding="ascii") as f :
        f.write(";FFMETADATA1\n")
        f.write(f"METADATA_BLOCK_PICTURE={base64.b64encode(block).decode("ascii")}\n")

# ====================================================
#                     Optimizer
# ====================================================
import math
#Next idea : Completely Static Video Detection and Optimization
class V_Optimizer : 
    '''Video Optimizer'''
    def __init__(self, v_preset, a_preset, target : float = 93):
        '''
        Video Optimizer
        
        :param v_preset: Video preset name from VIDEO_PRESETS
        :param a_preset: Audio preset name from AUDIO_PRESETS
        :param target: VMAF target
        :type target: float
        :param silent: Display message to console
        :type silent: bool
        '''
        self.target = target
        
        #simplify and remove rate controls from preset
        self.v_codec = VIDEO_PRESETS[v_preset]["codec"]
        self.v_param = strip_all_rate_controls(VIDEO_PRESETS[v_preset]["params"])
        self.a_codec = AUDIO_PRESETS[a_preset]["codec"]
        self.a_param = AUDIO_PRESETS[a_preset]["params"]

    def __GetMax_CRF(self) -> int :
        '''
        Returns max crf of an libary
        
        :return: Maximum crf
        :rtype: int
        '''
        Sets = {
            63 : ["libaom-av1", "libsvtav1", "libvpx-vp9"],
            51 : ["libx264", "libx265"]
        } 
        if self.v_codec in Sets[63] :
            return 46 #Safe range (This keep simple fade+statc from breaking)
        elif self.v_codec in Sets[51] :
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
        result = run(f'{FFMPEG} -v fatal -stats -i "{in_path}" -vf mpdecimate -f null -', True, True)
        #Extract frame counts from video
        m = re.findall(r'frame=\s*(\d+)', result.stderr)
        frames = int(m[-1]) if m else 0
        print(f"\033[38;5;46m[Optimizer] Unique Frames {frames}\033[0m")
        if frames <= 2 :
            print(f"\033[38;5;50m[Optimizer] True Static Video Detected, Optimizing For Static Video\033[0m")
            run(f'{FFMPEG} -v fatal -i "{in_path}" -map_metadata 0 -c copy "1Frame_Base.mp4"') #This remove things like cover
            run(f'{FFMPEG} -v fatal -stats -i "1Frame_Base.mp4" -map_metadata 0 -map 0 -vf mpdecimate -fps_mode vfr'
                f' -c:s copy -c:d copy -c:a {self.a_codec} {self.a_param} -c:v libaom-av1 -cpu-used 1 -pix_fmt yuv420p10le -still-picture 1 -crf 38 -b:v 0 '
                f'"{out_path}"', True)
            os.remove("1Frame_Base.mp4")
            return True
        return False

    def CRF_Optimize(self, in_path : Union[str, Path], out_path : Union[str, Path], crf_base : int = 42, crf_floor : int = 0, margin : float = 1.0) -> None :
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
        if self.Is1Frame(in_path, out_path) : #If video Is just a static image
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

        #make a copy of video (this should remove thigs like cover bad for big files)
        run(f'{FFMPEG} -v fatal -i "{in_path}" -map_metadata 0 -c copy "{TMP_FOLDER}/base.mp4"')
        file_c = f'{TMP_FOLDER}/base.mp4'
        SOURCE_SIZE = os.path.getsize(file_c)

        crf = CRF_BASE
        previous_crf = None
        previous_score = None
        Comp = Comparator(False, True)
        while True :
            out = f'{TMP_FOLDER}/{crf}.mp4'
            print(f"\033[38;5;50m[Optimizer] Attempting crf {crf} ({ConvertTime(START, time.perf_counter())})\033[0m")

            #Encode
            run(f'{FFMPEG} -v fatal -stats -i "{file_c}" -map_metadata 0 -map 0'
                f' -c:s copy -c:d copy -c:a {self.a_codec} {self.a_param} -c:v {self.v_codec} {self.v_param} -crf {crf} -b:v 0 '
                f'"{out}"', True)

            #Generate score
            score = Comp.get_vmaf(file_c, out)
            print(f"  Score : {score}")

            #If result is bigger than source abort even if it pass vmaf
            if os.path.getsize(out) > SOURCE_SIZE :
                print("\033[38;5;46m[Optimizer] Output Is Larger Than Source Aborting...\033[0m")
                out = in_path
                if score >= VMAF_TARGET - VMAF_MARGIN : #Switch to bitrate opimize if close enough
                    print("\033[38;5;46m[Optimizer] Condition met, Switching to Bitrate Optimize\033[0m")
                    self.Bitrate_Optimize(in_path, out_path)
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
                print("\033[38;5;46m[Optimizer] Crf floor reached skipping...\033[0m")
                break
            elif crf == CRF_MAX : #Maximum CRF allowed
                print("\033[38;5;46m[Optimizer] Crf celing reached skipping...\033[0m")
                break

        print(f"\033[38;5;46m[Optimizer] Using CRF {crf}\n[Optimizer] Time taken {ConvertTime(START, time.perf_counter())}\033[0m")
        run(f'{FFMPEG} -v fatal -i "{TMP_FOLDER}/{crf}.mp4" -map_metadata 0 -c copy "{out_path}"')
    def Bitrate_Optimize(self, in_path : Union[str, Path], out_path : Union[str, Path]) -> None :
        '''
        Optimize bitrate for an video may not works well on static video(this sacrifices a lot of time)
        
        :param in_path: Input path
        :type in_path: Path
        :param out_path: Output path
        :type out_path: Path
        '''
        if self.Is1Frame(in_path, out_path) : #If video Is just a static image
            return
        TMP = f'{os.path.dirname(in_path)}//_TMP' #Temppath
        
        MIN_RATE = 50 #kbits
        MAX_RATE = round(VAnalizer(in_path).bitrate)
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
        run(f'{FFMPEG} -v fatal -i "{in_path}" -map_metadata 0 -c copy "{TMP}/base.mp4"')
        file_c = f'{TMP}/base.mp4'
        
        #Start binary seasch
        Comp = Comparator(False, True)
        for i in range(ROUNDS) :
            mid = round((MIN_RATE + MAX_RATE) / 2)
            out = f'{TMP}/{mid}.mp4' #easier bitrate viewing on windows
            print(f"\033[38;5;50m[{i + 1}/{ROUNDS}] Attempting {mid}k Best:{BEST_RATE}k ({ConvertTime(START, time.perf_counter())})\033[0m")

            #Encode
            ######################################################################################################
            run(f'{FFMPEG} -v fatal -stats -i "{file_c}" -map_metadata 0 -map 0'
                f' -c:s copy -c:d copy -an -c:v {self.v_codec} {self.v_param} -b:v {mid}k -pass 1 -f null nul', True)

            run(f'{FFMPEG} -v fatal -stats -i "{file_c}" -map_metadata 0 -map 0'
                f' -c:s copy -c:d copy -c:a {self.a_codec} {self.a_param} -c:v {self.v_codec} {self.v_param} -b:v {mid}k -pass 2 "{out}"', True)

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
            run(f'{FFMPEG} -v fatal -i "{TMP}/base.mp4" -map_metadata 0 -c copy "{out_path}"')
        else :
            run(f'{FFMPEG} -v fatal -i "{TMP}/{BEST_RATE}.mp4" -map_metadata 0 -c copy "{out_path}"')

# ====================================================
#                 Audio Shenanigans
# ====================================================
class AudioHelper() :
    def __init__(self):
        pass
    def UncompressedToFLAC(self, input : Union[str, Path], replace : bool = True, silent : bool = False) -> None:
        '''
        Convert uncompressed audio files to flac files\n
        This always process every file in given directory\n
        Even when input is a file

        :param input: Input file / Directory
        :type input: Union[str, Path]
        :param replace: Remove wav file
        :type replace: bool
        :param silent: Show feedback on console
        :type silent: bool
        '''
        FORMATS = (".wav", ".aiff")
        START = time.perf_counter()
        FOLDER = os.path.dirname(input)

        processed = 0
        log(silent, f"\033[38;5;46m[To_FLAC] Converting {FOLDER}\033[0m\n    [Config] Overwrite = {replace}")

        for file in os.listdir(FOLDER) : #Get all file in dir
            file = os.path.join(FOLDER, file) #Rebuild path
            if file.lower().endswith(FORMATS) : #Valid format
                run(f'{FFMPEG} -v fatal -i "{file}" -c:a flac -compression_level 12 "{os.path.splitext(file)[0] + ".flac"}"')
                if replace : #Delete source file
                    os.remove(file)
                processed += 1 
                log(silent, f"\033[38;5;220m    Converted {file} ({ConvertTime(START, time.perf_counter())})\033[0m")
        log(silent, f"\033[38;5;46m    Processed {processed} files ({ConvertTime(START, time.perf_counter())})\033[0m")

# ====================================================
#                   Debug only
# ====================================================
if __name__ == "__main__" :
    print("fffunctions debug code")
    from Scripts.Functions.helpers import InputPath

    f = InputPath("Input Path : ")
    v_info = VAnalizer(f)
    print(v_info)
    print(f"Frames {v_info.frames}")
    print(f"Bitrate {v_info.bitrate}kbps")
    print(f"FPS {v_info.fps}")
    print(f"AVG_FPS {v_info.avg_fps}")
    # o = V_Optimizer("av1_veryslow+", "copy")
    # print(o.Is1Frame(f, "tmp.mp4"))
    # UncompressedToFLAC("R:\\A.wav", False) # "R:\\" will do the same thing
    #This split video on EVERY KEYFRAME
    #ffmpeg -i ./A.mp4 -f segment -c copy segment_%03d.mkv

    #shutil.copyfile(f"{SPLIT_RAW}/{seg}", out)