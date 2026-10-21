from pathlib import Path
from typing import Union
import subprocess
import json

class VAnalizer() :
    '''A fully self contained Video Analizer'''
    def __init__(self, file_path: Union[str, Path]):
        file_path = str(file_path)

        cmd = [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries",
            "stream=codec_name,profile,level,width,height,pix_fmt,"
            "bit_rate,r_frame_rate,avg_frame_rate,nb_frames,"
            "duration,display_aspect_ratio,sample_aspect_ratio,"
            "color_space,color_transfer,color_primaries,has_b_frames",
            "-show_format",  # <-- Critical for MKV/WebM
            "-of", "json",
            file_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        stream = data["streams"][0]
        fmt = data.get("format", {})

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

        # --- Core Video Properties ---
        self.codec = stream.get("codec_name")
        self.profile = stream.get("profile")
        self.level = stream.get("level")
        self.width = safe_int(stream.get("width"))
        self.height = safe_int(stream.get("height"))
        self.pix_fmt = stream.get("pix_fmt")

        self.fps = round(parse_ratio(stream.get("r_frame_rate", "0/1")), 4)
        self.avg_fps = round(parse_ratio(stream.get("avg_frame_rate", "0/1")), 4)

        # --- Robust Duration Extraction ---
        # Try stream first (MP4), fallback to format (MKV/WebM)
        self.duration = safe_float(stream.get("duration"))
        if self.duration == 0.0:
            self.duration = safe_float(fmt.get("duration"))

        # --- Robust Frame Count Extraction ---
        self.frames = safe_int(stream.get("nb_frames"))
        if self.frames == 0 and self.duration > 0:
            # avg_fps is calculated from actual timestamps, making it more accurate for frame estimation
            fps_to_use = self.avg_fps if self.avg_fps > 0 else self.fps
            if fps_to_use > 0:
                self.frames = max(1, round(self.duration * fps_to_use))

        # Bitrate: stream -> format fallback
        self.bitrate = safe_float(stream.get("bit_rate"))
        if self.bitrate == 0.0:
            self.bitrate = safe_float(fmt.get("bit_rate"))
        self.bitrate /= 1000.0  # kbps

        # --- Aspect Ratios & Color ---
        self.dar = stream.get("display_aspect_ratio")
        self.sar = stream.get("sample_aspect_ratio")
        self.color_space = stream.get("color_space")
        self.color_transfer = stream.get("color_transfer")
        self.color_primaries = stream.get("color_primaries")
        self.has_b_frames = safe_int(stream.get("has_b_frames"))  

    def __repr__(self):
        return (
            f"VAnalyzer(codec={self.codec}, duration={self.duration}, "
            f"resolution={self.width}x{self.height}, "
            f"fps={self.fps}, avg_fps={self.avg_fps}, frames={self.frames}, "
            f"bitrate={self.bitrate:.2f} kbps)"
        )

class AAnalizer() :
    pass