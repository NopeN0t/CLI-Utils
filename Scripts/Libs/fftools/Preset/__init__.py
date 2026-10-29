# fftools/Preset/__init__.py
from .PresetInfo import Preset, OptionValue
from .Presets import VideoPreset, VideoModifier, AudioPreset
from .Presets import GetVideoPreset, GetAudioPreset, BuildVideoPreset, BuildAudioPreset, prompt_custom_preset
from .PresetData import (
    VIDEO_PRESETS, AUDIO_PRESETS,
    COVER_FORMATS, AddCover, RemoveCover,
    FFMPEG, FFPROBE, LogLevel, RATE_KEYS, MAX_CRF
)

__all__ = [
    # Dataclasses & Types
    "Preset", "OptionValue",
    
    # Enums
    "VideoPreset", "VideoModifier", "AudioPreset",
    
    # Core Functions
    "GetVideoPreset", "GetAudioPreset",
    "BuildVideoPreset", "BuildAudioPreset", "prompt_custom_preset",
    
    # Preset Collections
    "VIDEO_PRESETS", "AUDIO_PRESETS",

    #Cover Module
    "COVER_FORMATS", "AddCover", "RemoveCover",
   
    # FFmpeg Values
    "FFMPEG", "FFPROBE", "RATE_KEYS", "MAX_CRF", "LogLevel"
]
