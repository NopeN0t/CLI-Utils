from .PresetData import VIDEO_PRESETS, AUDIO_PRESETS
from .PresetInfo import Preset, OptionValue
from enum import IntFlag, StrEnum
from typing import List
import copy
import shlex

class VideoPreset(StrEnum):
    AV1_PLACEBO = "av1_placebo"
    AV1_VERY_SLOW = "av1_veryslow"
    AV1_SLOW = "av1_slow"
    AV1_MEDIUM = "av1_medium"
    AV1_FAST = "av1_fast"
    AV1_VERY_FAST = "av1_veryfast"
    VP9_SLOW = "vp9_slow"
    VP9_LOSSLESS = "vp9_lossless"
    COPY = "copy"

class VideoModifier(IntFlag):
    NONE = 0
    FPS_48 = 1
    VFR = 2
    BIT_10 = 4

class AudioPreset(StrEnum):
    FLAC = "flac"
    OPUS_96K = "opus_96k"
    OPUS_128K = "opus_128k"
    OPUS_192K = "opus_192k"
    OPUS_256K = "opus_256k"
    OPUS_512K = "opus_512k"
    COPY = "copy"

def GetVideoPreset(vp: VideoPreset, modifier: VideoModifier = VideoModifier.NONE) -> Preset:
    base = copy.deepcopy(VIDEO_PRESETS[vp.value])

    if modifier & VideoModifier.FPS_48:
        base.filters["fps"] = "min(source_fps\\,48)" #I Don't know why but it must be like this to works
        base.base_params["fps_mode"] = "vfr"
        
    if modifier & VideoModifier.VFR:
        base.filters["mpdecimate"] = "hi=128:lo=32:frac=0.00005"
        
    if modifier & VideoModifier.BIT_10:
        base.base_params["pix_fmt"] = "yuv420p10le"

    return base

def GetAudioPreset(ap: AudioPreset) -> Preset:
    return copy.deepcopy(AUDIO_PRESETS[ap.value])


def _format_arg(key: str, value: OptionValue) -> List[str]:
    res = [f"-{key}"]
    if value is not None:
        res.append(str(value) if not isinstance(value, bool) else ("1" if value else "0"))
    return res

def BuildVideoPreset(preset: Preset) -> List[str]:
    res = ["-c:v", preset.codec]
    
    for d in (preset.base_params, preset.encoder_params, preset.rate_controls):
        for k, v in d.items():
            res.extend(_format_arg(k, v))

    if preset.filters:
        res.extend(["-vf", ",".join(f"{k}={v}" for k, v in preset.filters.items())])

    if preset.custom_params:
        res.extend(shlex.split(preset.custom_params))  # ← Safe string → list conversion
    
    return res

def BuildAudioPreset(preset: Preset) -> List[str]:  
    res: List[str] = []

    if not preset.codec:
        return ["copy"]
    res.extend(["-c:a", preset.codec])
    
    # Audio rarely uses filters/rate-controls in this structure
    for d in (preset.base_params, preset.encoder_params, preset.rate_controls):
        for k, v in d.items():
            res.extend(_format_arg(k, v))

    if preset.custom_params:
        res.extend(shlex.split(preset.custom_params))

    return res

def prompt_custom_preset(preset_type: str) -> Preset:
    """Interactive fallback for custom codec + params"""
    GREEN = "\033[38;5;46m"
    YELLOW = "\033[38;5;226m"
    RESET = "\033[0m"
    codec = input(f"{GREEN}Enter {YELLOW}{preset_type}{GREEN} encoder (empty for 'copy'): {RESET}").strip()
    params = input(f"{GREEN}Enter {YELLOW}{preset_type}{GREEN} FFmpeg params: {RESET}").strip() if codec else "" #Skip this if codec is empty
    
    return Preset(
        codec=codec if codec else "copy",
        base_params={},
        encoder_params={},
        rate_controls={},
        filters={},
        custom_params=params
    )


# Example usage workflow:
if __name__ == "__main__":
    sel = input("\033[38;5;50mType C for custom input\n\033[0m")
    if sel.lower() == "c" :
        vp = prompt_custom_preset("VideoPreset")
        ap = prompt_custom_preset("AudioPreset")
        args = BuildVideoPreset(vp) + BuildAudioPreset(ap)
        
    else :
        vp = GetVideoPreset(VideoPreset.AV1_PLACEBO, VideoModifier.FPS_48 | VideoModifier.VFR | VideoModifier.BIT_10)
        ap = GetAudioPreset(AudioPreset.COPY)
        args = BuildVideoPreset(vp) + BuildAudioPreset(ap)

        # import subprocess
        # subprocess.run([
        #     "ffmpeg", "-hide_banner", "-y", "-v", "error", "-stats",
        #     "-i", ".\\X.mp4", "-map", "0", "-map", "-0:3",
        #     "-c:s", "copy", "-c:d", "copy",
        # ] + args + ["./X_out.mp4"])

    print(args)    

'''
#CLI Parser idea (pseudocode-ish)
#parser = argparse.ArgumentParser(formatter_class= argparse.ArgumentDefaultsHelpFormatter)
#parser.add_argument("-vp", "--video-preset", type=VideoPreset, options=VideoPreset.GetPreset(), help="Base video preset")
#parser.add_argument("--fps-48", action="store_true", help="Cap FPS to 48")
#parser.add_argument("--vfr", action="store_true", help="Use Variable Frame Rate (mpdecimate)")
#parser.add_argument("--bit-10", action="store_true", help="Use 10-bit pixel format (yuv420p10le)")

#CLI Input Idea
#prompt_custom_preset()
'''