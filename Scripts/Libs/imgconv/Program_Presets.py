from enum import Enum

class ProgramPresets (Enum):
    Default = 1,
    Lossless = 2,
    Transcode = 3
    @classmethod
    def Presets(cls) -> list[str] :
        return [x.name.lower() for x in cls]