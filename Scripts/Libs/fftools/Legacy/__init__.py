# fftools/Legacy/__init__.py
from .ffpresets import (
    VIDEO_PRESETS, AUDIO_PRESETS,
    COVER_FORMATS, COVER_PRESETS_ADD, COVER_PRESETS_REMOVE,
    FFMPEG, RATE_KEYS
)
from .fffunctions import (
    run, strip_all_rate_controls,
    Comparator, VAnalizer,
    Extract_Cover, Remove_Cover, Add_Cover, Metadata_block_cover,
    V_Optimizer, AudioHelper
)

__all__ = [
    #Presets
    "VIDEO_PRESETS", "AUDIO_PRESETS",
    "COVER_FORMATS", "COVER_PRESETS_ADD", "COVER_PRESETS_REMOVE",

    #FFmpeg Defaults
    "FFMPEG", "RATE_KEYS",

    #Helpers
    "run", "strip_all_rate_controls",

    #Analyzers
    "Comparator", "VAnalizer",

    #Cover
    "Extract_Cover", "Remove_Cover", "Add_Cover", "Metadata_block_cover",

    #Optimizer
    "V_Optimizer",

    #Audio
    "AudioHelper"
]
