from .PresetInfo import Preset
from enum import IntEnum

VIDEO_PRESETS = {
    "av1_placebo" : Preset(
        codec="libaom-av1",
        base_params={ "g" : 600 },
        encoder_params={
            "cpu-used": 6, "auto-alt-ref" : 1,
            "arnr-maxframes" : 7, "arnr-strength" : 4, "lag-in-frames" : 48,
            "enable-tx64" : 1, "tile-columns" : 1, "row-mt" : 1
        },
        rate_controls={ "b:v" : 0, "crf" : 32 }
    ),
    "av1_veryslow" : Preset(
        codec="libaom-av1",
        base_params={ "g" : 600},
        encoder_params={
            "cpu-used": 6, "auto-alt-ref" : 1,
            "arnr-maxframes" : 7, "arnr-strength" : 4, "lag-in-frames" : 24,
            "enable-tx64" : 1, "tile-columns" : 1, "row-mt" : 1
        },
        rate_controls={ "b:v" : 0, "crf" : 32 }
    ),
    "av1_slow" : Preset(
        codec="libaom-av1",
        base_params={ "g" : 600},
        encoder_params={
            "cpu-used" : 6, "tile-columns" : 2, 
            "row-mt" : 1, "lag-in-frames" : 16
        },
        rate_controls={ "b:v" : 0, "crf" : 32 }
    ),
    "av1_medium" : Preset(
        codec="libsvtav1",
        base_params={ "g" : 600},
        encoder_params={ "preset" : 5, "tile-columns" : 2, "tile-rows" : 1 },
        rate_controls={ "b:v" : 0, "crf" : 34 }
    ),
    "av1_fast" : Preset(
        codec="libsvtav1",
        base_params={ "g" : 600},
        encoder_params={ "preset" : 6, "tile-columns" : 2, "tile-rows" : 1 },
        rate_controls={ "b:v" : 0, "crf" : 34 }
    ),
    "av1_veryfast" : Preset(
        codec="libsvtav1",
        base_params={ "g" : 600},
        encoder_params={ "preset" : 8, "tile-columns" : 2, "tile-rows" : 1 },
        rate_controls={ "b:v" : 0, "crf" : 34 }
    ),
    "vp9_slow" : Preset(
        codec="libvpx-vp9",
        encoder_params={ "speed" : 2, "tile-columns" : 3, "row-mt" : 1, "lag-in-frames" : 4 },
        rate_controls={ "crf" : 32 }
    ),
    "vp9_lossless" : Preset(
        codec="libvpx-vp9",
        encoder_params={ "speed" : 4, "tile-columns" : 3, "row-mt" : 1, "lossless" : 1 }
    ),
    "copy" : Preset(
        codec="copy"
    ),
}
AUDIO_PRESETS = {
    "flac" : Preset(
        codec="flac",
        encoder_params={ "compression_level" : 12 }
    ),
    "opus_96k" : Preset(
        codec="libopus",
        encoder_params={ "vbr" : "on", "compression_level" : 10, "application" : "audio" },
        rate_controls={ "b:a" : "96k"}
    ),
    "opus_128k" : Preset(
        codec="libopus",
        encoder_params={ "vbr" : "on", "compression_level" : 10, "application" : "audio" },
        rate_controls={ "b:a" : "128k"}
    ),
    "opus_192k" : Preset(
        codec="libopus",
        encoder_params={ "vbr" : "on", "compression_level" : 10, "application" : "audio" },
        rate_controls={ "b:a" : "192k"}
    ),
    "opus_256k" : Preset(
        codec="libopus",
        encoder_params={ "vbr" : "on", "compression_level" : 10, "application" : "audio" },
        rate_controls={ "b:a" : "256k"}
    ),
    "opus_512k" : Preset(
        codec="libopus",
        encoder_params={ "vbr" : "on", "compression_level" : 10, "application" : "audio" },
        rate_controls={ "b:a" : "512k"}
    ),
    "copy" : Preset(
        codec="copy"
    )
}

COVER_FORMATS = ("mp3", "mp4", "flac", "ogg", "opus")
COVER_PRESETS_ADD = {
    #The preset that embed picture into the file may produce larger albums/collections
    #You can mixup files that have embeded cover and noting will break
    "FLAC" : '-map_metadata 0 -map 0:a -map 1:v -c:v copy -c:a copy -disposition:v attached_pic', #Embed
    "MP3" : '-map_metadata 0 -map 0:a -map 1:v -c:v copy -c:a copy -metadata:s:v comment="Cover (front)" -id3v2_version 3', #Embed
    "MP4" : '-map_metadata 0 -map 0 -map 1 -c copy -disposition:v:1 attached_pic', #Embed
    "OGG/OPUS" : '-c copy -metadata "METADATA_BLOCK_PICTURE=&(base64 -w 0 cover.jpg)"', #This requried cover.jpg to exist in same folder (fallback)
}
COVER_PRESETS_REMOVE = {
    "FLAC" : '-map 0:a -c copy -map_metadata 0',
    "MP3" : '-map 0:a -c copy -map_metadata 0',
    "MP4" : '-map 0:a -c copy -map_metadata 0',
    "OGG/OPUS" : '-map 0:a -map_metadata 1 -c copy'
}

FFMPEG = ["ffmpeg", "-hide_banner", "-y"]
FFPROBE = ["ffprobe", "-hide_banner"]
class LogLevel(IntEnum) :
    QUIET = -8
    PANIC = 0
    FATAL = 8
    ERROR = 16
    WARNING = 24
    INFO = 32
    VERBOSE = 40
    DEBUG = 48
    TRACE = 56

##Legacy Datas
RATE_KEYS = [
    "-crf", "-b:v", "-minrate", "-maxrate",
    "-qp", "-qmin", "-qmax", "-bufsize"
]
