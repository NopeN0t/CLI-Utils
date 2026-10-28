import mimetypes, struct, base64, json, os
from typing import Union, Optional
from pathlib import Path
from ..Functions import log
from ..Runner import RunFFprobe, RunFFmpeg, LogLevel
from ..Preset import COVER_FORMATS, AddCover, RemoveCover

class CoverManager:
    '''Cover management for audio/video files'''
    
    def __init__(self, show_command: bool = False, verbose: bool = False):
        self.show_command = show_command
        self.verbose = verbose
    
    def _get_output_path(self, file_path: Union[str, Path], output: Optional[Union[str, Path]] = None) -> Path:
        '''Derive output path from input file'''
        FILENAME = os.path.splitext(os.path.basename(file_path))
        if output is None:
            return Path(f'{os.path.dirname(file_path)}/{FILENAME[0]}_res{FILENAME[1]}')
        return Path(str(output))
    
    def _metadata_block_cover(self, cover_path: str) -> None:
        '''Generate Metadata block for cover art'''
        cover = Path(cover_path)

        mime, _ = mimetypes.guess_type(cover)
        if mime not in ("image/jpeg", "image/png"):
            raise ValueError("Cover must be JPEG or PNG")

        img_data = cover.read_bytes()

        picture_type = 3  # front cover
        description = b"Cover (front)"
        width = height = depth = colors = 0

        block = b"".join([
            struct.pack(">I", picture_type),
            struct.pack(">I", len(mime)), mime.encode(),
            struct.pack(">I", len(description)), description,
            struct.pack(">IIII", width, height, depth, colors),
            struct.pack(">I", len(img_data)),
            img_data
        ])

        with open("./tmp.ffmeta", "w", encoding="ascii") as f :
            f.write(";FFMETADATA1\n")
            f.write(f"METADATA_BLOCK_PICTURE={base64.b64encode(block).decode("ascii")}\n")

    def extract_cover(self, file_path: Union[str, Path], cover_path: Union[str, Path]) -> Optional[int]:
        '''
        Extract embedded cover art from file
        
        :param file_path: Input file path
        :param cover_path: Destination for extracted cover
        :return: Cover stream index (None if not found)
        '''
        log(self.verbose, "\033[38;5;50m[CoverExtract] Extracting cover art...\033[0m")
        
        probe = RunFFprobe(
            inputs=file_path,
            args=["-print_format", "json", "-show_streams"],
            loglevel=LogLevel.QUIET,
            show_command=self.show_command,
            capture_output=True
        )
        
        data = json.loads(probe.stdout)
        cover_path = Path(cover_path) if isinstance(cover_path, str) else cover_path

        # Method 1: Extract from dedicated cover streams
        for s in data["streams"]:
            if s["codec_type"] == "video" and s["codec_name"] in ("png", "mjpeg", "jpeg"):
                if s["codec_name"] == "png":
                    cover_path = cover_path.with_suffix(".png")
                elif s["codec_name"] in ("mjpeg", "jpeg"):
                    cover_path = cover_path.with_suffix(".jpg")

                RunFFmpeg(
                    inputs=file_path,
                    output=cover_path,
                    args=["-map", f"0:{s['index']}", "-c:v", "copy"],
                    loglevel=LogLevel.QUIET,
                    show_status=False,
                    show_command=self.show_command
                )
                log(self.verbose, "\033[38;5;50m[CoverExtract] Done\033[0m")
                return s["index"]
        
        # Method 2: Extract from attached picture metadata
        try:
            RunFFmpeg(
                inputs=file_path,
                output=cover_path.with_suffix(".png"),
                args=["-map", "0:v:m:attached_pic"],
                loglevel=LogLevel.QUIET,
                show_status=False,
                show_command=self.show_command
            )
            log(self.verbose, "\033[38;5;214m[CoverExtract] Done with unusak method\033[0m")
            return None
        except:
            log(self.verbose, "\033[38;5;128m[CoverExtract] No cover art found, Skipping\033[0m")
            return None
    
    def remove_cover(self, file_path: Union[str, Path], output: Optional[Union[str, Path]] = None) -> Path:
        '''
        Remove embedded cover art from file
        
        :param file_path: Input file path
        :param output: Output path (None to derive from input)
        :return: Output path
        '''
        if not str(file_path).lower().endswith(COVER_FORMATS):
            raise NotImplementedError("[RemoveCover] Unsupported file format")
        
        OUTPUT = self._get_output_path(file_path, output)
        SUFFIX = os.path.splitext(str(file_path))[1].removeprefix('.')
        
        if SUFFIX in ("mp3", "flac", "mp4"):
            RunFFmpeg(
                inputs=file_path,
                output=OUTPUT,
                args=[*RemoveCover[SUFFIX.upper()].value],
                loglevel=LogLevel.ERROR,
                show_status=False,
                show_command=self.show_command
            )
        elif SUFFIX in ("ogg", "opus"):
            with open("./tmp.ffmeta", "w", encoding="ascii") as f : #Generate empty metadata
                f.write(";FFMETADATA1\n")
            RunFFmpeg(
                inputs=[file_path, "./tmp.ffmeta"],
                output=OUTPUT,
                args=[*RemoveCover["OGG_OPUS"].value],
                loglevel=LogLevel.ERROR,
                show_status=False,
                show_command=self.show_command
            )
            os.remove("./tmp.ffmeta")
        
        return OUTPUT
    
    def add_cover(self, file_path: Union[str, Path], image_path: Union[str, Path], 
                  output: Optional[Union[str, Path]] = None) -> Path:
        '''
        Add front cover to file
        
        :param file_path: Input file path
        :param image_path: Cover image path
        :param output: Output path (None to derive from input)
        :return: Output path
        '''
        if not str(file_path).lower().endswith(COVER_FORMATS):
            raise NotImplementedError("[AddCover] Unsupported file format")
        
        # Convert to JPG if needed
        if (
            os.path.getsize(image_path) > 4 * 1024 * 1024 # 4MiB
        ):
            tmppath = image_path.replace(os.path.basename(image_path), "cover.jpg")
            RunFFmpeg(
                inputs=image_path,
                output=tmppath,
                args=["-q:v", "1"],
                loglevel=LogLevel.ERROR,
                show_status=False,
                show_command=self.show_command
            )
            image_path = tmppath
        
        OUTPUT = self._get_output_path(file_path, output)
        SUFFIX = os.path.splitext(str(file_path))[1].removeprefix('.')
        
        if SUFFIX in ("mp3", "flac", "mp4"):
            RunFFmpeg(
                inputs=[file_path, image_path],
                output=OUTPUT,
                args=[*AddCover[SUFFIX.upper()].value],
                loglevel=LogLevel.ERROR,
                show_status=False,
                show_command=self.show_command
            )
        elif SUFFIX in ("ogg", "opus"):
            try:
                self._metadata_block_cover(image_path)
                RunFFmpeg(
                    inputs=[file_path, './tmp.ffmeta'],
                    output=OUTPUT,
                    args=['-map', '0:a', '-map_metadata', '1', '-c', 'copy'],
                    loglevel=LogLevel.ERROR,
                    show_status=False,
                    show_command=self.show_command
                )
                os.remove("./tmp.ffmeta")
            except:
                log(self.verbose, "\033[38;5;128m[Add_Cover] Embedding failed, falling back to external cover\033[0m")
                RunFFmpeg(
                    inputs=file_path,
                    output=OUTPUT,
                    args=[*AddCover["OGG_OPUS"].value],
                    loglevel=LogLevel.ERROR,
                    show_status=False,
                    show_command=self.show_command
                )
        
        return OUTPUT
