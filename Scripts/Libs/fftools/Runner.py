import subprocess as sp
import shlex
from pathlib import Path
from typing import Union

from .Preset import FFMPEG, FFPROBE, LogLevel

def RunFFmpeg(
    inputs: Union[Path, str, list[Union[Path, str]]], 
    output: Union[Path, str, list[Union[Path, str]]],
    args: list[str], 
    loglevel: LogLevel = LogLevel.FATAL,
    show_status: bool = True,
    show_command: bool = False,
    capture_output: bool = False,
    check: bool = True,
) -> sp.CompletedProcess:
    '''Run FFmpeg command via subprocess.run()'''
    # Normalize inputs
    input_paths = inputs if isinstance(inputs, list) else [inputs]
    input_flags = [item for inp in input_paths for item in ("-i", str(inp))]
    
    # Normalize outputs (handle multiple outputs)
    output_list = output if isinstance(output, list) else [output]
    out_flags = [str(out) for out in output_list]
    
    cmd = [
        *FFMPEG,
        "-v", str(loglevel.value),
        * (["-stats"] if show_status else []),
        *input_flags,
        *args,
        *out_flags
    ]
    
    if show_command:
        print(f"\033[31m\n>> {shlex.join(cmd)}\n\033[0m")
    return sp.run(
        cmd, 
        text=True, 
        capture_output=capture_output, 
        check=check,
        encoding='UTF-8' # Ran into some japanese text and things breaks
    )

def RunFFprobe(
    inputs: Union[Path, str, list[Union[Path, str]]],
    args: list[str] | None = None,
    loglevel: LogLevel = LogLevel.INFO,
    show_command: bool = False,
    capture_output: bool = True,
    check: bool = True
) -> sp.CompletedProcess:
    '''Run FFprobe command via subprocess.run().'''

    input_paths = inputs if isinstance(inputs, list) else [inputs]
    input_flags = [str(inp) for inp in input_paths]

    cmd = [
        *FFPROBE,
        "-v", str(loglevel.value),
        *(args or []),
        *input_flags
    ]

    if show_command:
        print(f"\033[31m\n>> {shlex.join(cmd)}\n\033[0m")

    return sp.run(
        cmd,
        text=True,
        capture_output=capture_output,
        check=check,
        encoding='UTF-8' # Ran into some japanese text and things breaks
    )



if __name__ == "__main__":
    # Example Usage
    from .Preset import GetVideoPreset, BuildVideoPreset, VideoPreset, VideoModifier
    
    vp = GetVideoPreset(VideoPreset.AV1_VERY_FAST, VideoModifier.VFR)
    args = BuildVideoPreset(vp)
    
    result = RunFFmpeg(
        inputs=Path("./X.mp4"),
        output=Path("./y.mp4"),
        args=args,
        show_command=True,
        capture_output=False 
    )
    #Cover module
    # RunFFmpeg(
    # inputs=[file_path, image_path],  # Automatically becomes -i file_path -i image_path
    # output=Path(OUTPUT),
    # args=[COVER_PRESETS_ADD["MP3"]], # Pass remaining flags
    # loglevel=LogLevel.ERROR,
    # capture_output=False 
    # )

    #Weird Module (Is1Frame from V_Optimizer)
    # RunFFmpeg(
    #     inputs=filepath,
    #     output="-",
    #     args=["-vf", "mpdecimate", "-f", "null"],
    #     loglevel=LogLevel.FATAL,
    #     capture_output=True 
    # )

    #Ideal usage
    #def func(input,output,videopreset : Preset, audiopreset : Preset, loglevel : LogLevel =  LogLevel.FATAL) #Video modifiers is handle outside of this
    #   ...
    #   *Builds args somewhere or BuildArguments(...)
    #   RunFFmpeg(input ,output ,args ,loglevel ,True)