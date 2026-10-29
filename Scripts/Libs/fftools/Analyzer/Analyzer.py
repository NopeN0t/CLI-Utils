from pathlib import Path
from typing import Union
import subprocess
import json
import re

class _ParseHelper() :
    @staticmethod
    def parse_ratio(value: str) -> float:
        if not value or value == "0/0":
            return 0.0
        num, den = value.split("/")
        return float(num) / float(den)

    @staticmethod
    def safe_int(value):
        try:
            return int(value) if value else 0
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def safe_float(value):
        try:
            return float(value) if value else 0.0
        except (TypeError, ValueError):
            return 0.0

class VAnalyzer() :
    '''A fully self contained Video Analyzer'''
    def __init__(self, file_path: Union[str, Path], track : int = 0):
        if isinstance(file_path, str) :
            file_path = Path(file_path)

        cmd = [
            "ffprobe", "-v", "error", 
            "-select_streams", f"v:{track}",
            "-show_entries",
            "stream=codec_name,profile,level,width,height,pix_fmt,"
            "bit_rate,r_frame_rate,avg_frame_rate,nb_frames,"
            "duration,display_aspect_ratio,sample_aspect_ratio,"
            "color_space,color_transfer,color_primaries,has_b_frames",
            "-show_format",  # <-- Critical for MKV/WebM
            "-of", "json",
            file_path
        ]

        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, encoding='utf-8', check=True
        )
        data = json.loads(result.stdout)
        stream = data["streams"][0]
        fmt = data.get("format", {})

        # --- Core Video Properties ---
        _ph = _ParseHelper()
        self.codec = stream.get("codec_name")
        self.profile = stream.get("profile")
        self.level = stream.get("level")
        self.width = _ph.safe_int(stream.get("width"))
        self.height = _ph.safe_int(stream.get("height"))
        self.pix_fmt = _ph.safe_int(stream.get("pix_fmt"))

        self.fps = round(_ph.parse_ratio(stream.get("r_frame_rate", "0/1")), 4)
        self.avg_fps = round(_ph.parse_ratio(stream.get("avg_frame_rate", "0/1")), 4)

        # --- Robust Duration Extraction ---
        # Try stream first (MP4), fallback to format (MKV/WebM)
        self.duration = _ph.safe_float(stream.get("duration"))
        if self.duration == 0.0:
            self.duration = _ph.safe_float(fmt.get("duration"))

        # --- Robust Frame Count Extraction ---
        self.frames = _ph.safe_int(stream.get("nb_frames"))
        if self.frames == 0 and self.duration > 0:
            # avg_fps is calculated from actual timestamps, making it more accurate for frame estimation
            fps_to_use = self.avg_fps if self.avg_fps > 0 else self.fps
            if fps_to_use > 0:
                self.frames = max(1, round(self.duration * fps_to_use))

        # Bitrate: stream -> format fallback
        self.bitrate = _ph.safe_float(stream.get("bit_rate"))
        if self.bitrate == 0.0:
            self.bitrate = _ph.safe_float(fmt.get("bit_rate"))
        self.bitrate /= 1000.0  # kbps

        # --- Aspect Ratios & Color ---
        self.dar = stream.get("display_aspect_ratio")
        self.sar = stream.get("sample_aspect_ratio")
        self.color_space = stream.get("color_space")
        self.color_transfer = stream.get("color_transfer")
        self.color_primaries = stream.get("color_primaries")
        self.has_b_frames = _ph.safe_int(stream.get("has_b_frames"))  
    def __repr__(self):
        return (
            f"VAnalyzer(codec={self.codec}, duration={self.duration}, "
            f"resolution={self.width}x{self.height}, "
            f"fps={self.fps}, avg_fps={self.avg_fps}, frames={self.frames}, "
            f"bitrate={self.bitrate:.2f} kbps)"
        )

class AAnalyzer() :
    '''A fully self contained Audio Analyzer'''
    def __init__(self, file_path: Union[str, Path], track : int = 0):
        if isinstance(file_path, str) :
            file_path = Path(file_path)

        # ========= Metadata =========
        cmd_meta = [
            "ffprobe", "-v", "error",
            "-select_streams", f"a:{track}",
            "-show_entries",
            "stream=codec_name,sample_rate,channels,channel_layout,sample_fmt,"
            "bit_rate,size,duration,flags,nb_frames",
            "-show_format",
            "-of", "json",
            file_path,
        ]
        result = subprocess.run(
            cmd_meta, 
            capture_output=True, 
            text=True, encoding='utf-8', check=True
        )
        data = json.loads(result.stdout)
        self._stream = data.get("streams", [{}])[0]
        self._fmt = data.get("format", {})

        # ========= Packet =========
        cmd_packets = [
            "ffprobe", "-v", "error",
            "-select_streams", f"a:{track}",
            "-show_entries", "packet=size,pts_time,duration_time",
            "-of", "json",
            str(file_path),
        ]
        result_packets = subprocess.run(
            cmd_packets,
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, encoding='utf-8', check=True,
        )
        packets = json.loads(result_packets.stdout).get("packets", [])
        self._packet_count = len(packets)
        self._total_bytes = sum(int(p.get("size", 0) or 0) for p in packets)
        
        # Parse ffprobe JSON values (all numeric fields come back as strings)
        self._ph = _ParseHelper()
        self._accurate_end = (
            max(self._ph.safe_float(p.get("pts_time")) + self._ph.safe_float(p.get("duration_time")) for p in packets)
            if packets else 0.0
        )


        # ========= Core audio attributes =========
        self.codec = self._stream.get("codec_name")
        self.sample_rate = self._ph.safe_int(self._stream.get("sample_rate"))
        self.channels = self._ph.safe_int(self._stream.get("channels"))
        self.channel_layout = self._stream.get("channel_layout")
        self.sample_fmt = self._stream.get("sample_fmt")

        # Bit depth from sample_fmt string (e.g. "s16" → 16, "fltp" → 0)
        m = re.search(r"(\d+)", self.sample_fmt or "")
        self.bits_per_sample = self._ph.safe_int(m.group(1)) if m else 0

        # Duration: stream → format → accurate packet end
        self.duration = self._ph.safe_float(self._stream.get("duration"))
        if self.duration == 0.0:
            self.duration = self._ph.safe_float(self._fmt.get("duration"))
        if self.duration == 0.0:
            self.duration = self._accurate_end

        # Bitrate (kbps): bit_rate → stream.size/duration → packet sum → PCM math → format total
        self.bitrate_kbps = self._compute_bitrate_kbps()

        # Frames / packets
        self.frames = self._ph.safe_int(self._stream.get("nb_frames"))
        if self.frames == 0:
            self.frames = self._packet_count

    def __repr__(self):
        return (
            f"AAnalyzer(codec={self.codec}, duration={self.duration}, "
            f"rate={self.sample_rate}Hz, ch={self.channels}, "
            f"frames={self.frames}, bitrate={self.bitrate_kbps:.2f} kbps)"
        )
    def _compute_bitrate_kbps(self):
        """Multi-tier fallback for bitrate — works on every container."""

        # 1. Direct stream bitrate (MP4 esds, MP3 frame headers, etc.)
        br = self._stream.get("bit_rate")
        if br:
            return self._ph.safe_float(br) / 1000.0

        # 2. Stream size / duration (when size is available)
        sz = self._stream.get("size")
        if sz and self.duration > 0:
            return (self._ph.safe_float(sz) * 8.0) / (self.duration * 1000.0)

        # 3. Universal exact: total packet bytes / duration
        if self._total_bytes > 0 and self.duration > 0:
            return (self._total_bytes * 8.0) / (self.duration * 1000.0)

        # 4. PCM math: sample_rate × channels × bits_per_sample
        if self.sample_fmt and self.bits_per_sample > 0 and self.sample_rate > 0:
            return (self.sample_rate * self.channels * self.bits_per_sample) / 1000.0

        # 5. Container total bitrate (last resort)
        fmt_br = self._fmt.get("bit_rate")
        if fmt_br:
            return self._ph.safe_float(fmt_br) / 1000.0

        return 0.0