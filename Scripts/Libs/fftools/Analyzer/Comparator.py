from typing import Union
from pathlib import Path
from ..Runner import RunFFmpeg, LogLevel
import json
import re
import os

class Comparator() :
    '''Collection of analyzers'''
    def __init__(self, fast : bool = False, show_command : bool = False, feedback : bool = False):
        '''
        A collection of analyzers for video
        
        :param fast: Enable fast mode (less precise)
        :type fast: bool (False)
        :param show_command: Show what command it's running
        :type show_command: bool (False)
        :param feedback: Show progress bar
        :type feedback: bool (True)
        '''
        self.sample = 2 if fast else 10
        self.show_command = show_command
        self.feedback = feedback
        self.null_device = "NUL" if os.name == "nt" else "/dev/null"
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
        RunFFmpeg(
            inputs=[encoded, original],
            output=self.null_device,
            args=[
                "-lavfi", 
                f'[0:v:0]scale=iw:ih:flags=bicubic,format=yuv420p[dist];'
                f'[1:v:0]scale=iw:ih:flags=bicubic,format=yuv420p[ref];'
                f'[dist][ref]libvmaf=log_fmt=json:log_path=vmaf.json:'
                f'n_threads={os.cpu_count()}:n_subsample={self.sample}',
                "-f", "null"
            ],
            loglevel=LogLevel.FATAL,
            show_command=self.show_command,
            capture_output=self.feedback
        )

        score = 0
        with open("vmaf.json") as f :
            data = json.load(f)
            score = data["pooled_metrics"]["vmaf"]["mean"]
        os.remove("vmaf.json")

        if score < 65 and not recursive : #Low score (can be caused by order of input)
            print("\033[38;5;226m[vmaf] possible mismatch detected\033[0m")
            
            swapped = self.get_vmaf(encoded, original, True) #RECURSIVE
            
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
        RunFFmpeg(
            inputs=[original, encoded],
            output=self.null_device,
            args=[
                "-lavfi",
                f"[0:v:0][1:v:0]psnr=stats_file={statfile}",
                "-f", "null"
            ],
            loglevel=LogLevel.FATAL,
            show_command=self.show_command,
            capture_output=self.feedback
        )
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
        RunFFmpeg(
            inputs=[original, encoded],
            output=self.null_device,
            args=[
                "-lavfi",
                f"[0:v:0][1:v:0]ssim=stats_file={statfile}",
                "-f", "null"
            ],
            loglevel=LogLevel.FATAL,
            show_command=self.show_command,
            capture_output=self.feedback
        )
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
