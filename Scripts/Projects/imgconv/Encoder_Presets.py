from dataclasses import dataclass
from pathlib import Path
from enum import Enum

@dataclass
class EncoderPreset:
    encoder: str
    params: tuple[str, ...]

    def command(self, input_path: Path, output_path: Path) -> list[str]:
        if self.encoder == "cwebp":
            return [
                self.encoder,
                *self.params,
                str(input_path),
                "-o",
                str(output_path),
            ]

        if self.encoder == "cjxl":
            return [
                self.encoder,
                str(input_path),
                str(output_path),
                *self.params,
            ]

        raise ValueError(f"Unknown encoder: {self.encoder}")

class Encoder_Presets(Enum):
    JXL_Default = EncoderPreset(
        "cjxl",
        ("-e", "10", "-d", "0.9", "--container=1", "--lossless_jpeg=0")
    )
    JXL_Lossless = EncoderPreset(
        "cjxl",
        ("-e", "10", "-d", "0", "--container=1", "--lossless_jpeg=0")
    )
    JXL_Transcode = EncoderPreset(
        "cjxl",
        ("-e", "10", "-d", "0", "--container=1", "--lossless_jpeg=1")
    )
    WEBP_Default = EncoderPreset(
        "cwebp",
        ("-q", "85", "-m", "6", "-mt", "-metadata", "all")
    )
    WEBP_Lossless = EncoderPreset(
        "cwebp",
        ("-z", "9", "-m", "6", "-mt", "-metadata", "all")
    )
    WEBP_Transcode = EncoderPreset(
        "cwebp",
        ("-z", "9", "-m", "6", "-mt", "-metadata", "all")
    )

    @classmethod
    def get_preset(cls, format_name: str, preset_name: str) -> EncoderPreset:
        """
        Selects the correct preset based on format and preset name strings.
        Args:
            format_name: e.g., 'jxl', 'webp'
            preset_name: e.g., 'default', 'lossless'
        """
        # Convert to TitleCase to match Enum keys (e.g., 'jxl' -> 'JXL', 'default' -> 'Default')
        key = f"{format_name.upper()}_{preset_name.capitalize()}"
        
        # Retrieve the enum member
        try:
            return cls[key].value
        except KeyError:
            raise ValueError(f"Preset not found: {key}")

    @classmethod
    def get_args(cls, preset : EncoderPreset) -> list :
        """
        Converts Preset to list of argument for easier uses.
        """
        tmp = [preset.encoder]
        for _ in preset.params :
            tmp.append(_)
        return tmp
