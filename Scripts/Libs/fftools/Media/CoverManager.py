import mimetypes, struct, base64, json, os
from typing import Union, Optional
from pathlib import Path
from ..Functions import log
from ..Runner import RunFFprobe, RunFFmpeg, LogLevel
from ..Preset import COVER_FORMATS, AddCover, RemoveCover

# On Cleanup Pass
# root, ext = os.path.splitext(file_path)
# OUTPUT = output if output is not None else os.path.join(root, f"_res{ext}")

class CoverManager():
    '''Cover Shenanigans'''
    def __init__(self, show_command : bool = False, verbose : bool = False):
        self.show_command = show_command
        self.verbose = verbose
    def __Metadata_block_cover(self, cover_path: str) -> None:
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

    def Extract_Cover(
            self,
            file_path : Union[str, Path], 
            cover_path : Union[str, Path]
    ) -> Optional[int] :
        '''
        Extract cover from a file to provided path

        :param file_path: Input file
        :type file_path: Path
        :param cover_path: Where to save cover to
        :type cover_path: Path
        :return: Return track id of cover (None if not found)
        :rtype: int
        '''
        #extract cover art (if exists)
        log(self.verbose, "\033[38;5;50m[CoverExtract] Extracting cover art...\033[0m")

        #Get streams
        probe = RunFFprobe(
            inputs=file_path,
            args=["-print_format", "json", "-show_streams"],
            loglevel=LogLevel.QUIET,
            show_command=self.show_command,
            capture_output=True
        )
        data = json.loads(probe.stdout)

        for s in data["streams"]:
            #locate png mjpeg jpeg streams (likely to be cover)
            if s["codec_type"] == "video" and s["codec_name"] in ("png", "mjpeg", "jpeg"):
                #Extract the cover
                RunFFmpeg(
                    inputs=file_path,
                    output=cover_path,
                    args=["-map", f"0:{s["index"]}", "-frames:v", "1"],
                    loglevel=LogLevel.QUIET,
                    show_command=self.show_command
                )

                log(self.verbose, "\033[38;5;50m[CoverExtract] Done\033[0m")
                return s["index"] #Return cover stream id

        #Backup method
        try :
            #Extract from metadata
            RunFFmpeg(
                inputs=file_path,
                output=cover_path,
                args=["-map", "0:v:m:attached_pic"],
                loglevel=LogLevel.QUIET,
                show_command=self.show_command
            )
            log(self.verbose, "\033[38;5;50m[CoverExtract] Done\033[0m")
            return None #No id since there's isn't one
        except :
            log(self.verbose, "\033[38;5;50m[CoverExtract] No cover art found, Skipping\033[0m")
            return None 
    def Remove_Cover(
            self,
            file_path : Union[str, Path], 
            output : Optional[Union[str, Path]] = None
    ) -> Path :
        '''
        Remove cover from the file

        :param file_path: Input file
        :type file_path: Path
        :param output: Where to save (Optional) 
        :type output: Path
        :return: Where output is generated
        :rtype: Path
        '''
        if not str(file_path).lower().endswith(COVER_FORMATS) :
            raise NotImplementedError("[RemoveCover] this file format is not supported")

        # ignore if it aready is
        OUTPUT = output
        FILENAME = os.path.splitext(os.path.basename(file_path))

        if output == None : #If output path is not provided derived one from input
            OUTPUT = f'{os.path.dirname(file_path)}/{FILENAME[0]}_res{FILENAME[1]}'
        SUFFIX = FILENAME[1]

        if SUFFIX == ".mp3" : #Process mp3
            RunFFmpeg(
                inputs=file_path,
                output=OUTPUT,
                args=[*RemoveCover.MP3.value],
                loglevel=LogLevel.ERROR,
                show_command=self.show_command
            )

        elif SUFFIX == ".flac" : #Process flac
            RunFFmpeg(
                inputs=file_path,
                output=OUTPUT,
                args=[*RemoveCover.FLAC.value],
                loglevel=LogLevel.ERROR,
                show_command=self.show_command
            )

        elif SUFFIX == ".ogg" or SUFFIX == ".opus": #Process ogg / opus
            with open("./tmp.ffmeta", "w", encoding="ascii") as f : #Generate empty metadata
                f.write(";FFMETADATA1\n")
            RunFFmpeg(
                inputs=[file_path, './tmp.ffmeta'],
                output=OUTPUT,
                args=[*RemoveCover.OGG_OPUS.value],
                loglevel=LogLevel.ERROR,
                show_command=self.show_command
            )
            os.remove("./tmp.ffmeta")

        elif SUFFIX == ".mp4" : #Process mp4
            RunFFmpeg(
                inputs=file_path,
                output=OUTPUT,
                args=[*RemoveCover.MP4.value],
                loglevel=LogLevel.ERROR,
                show_command=self.show_command
            )

        return Path(str(OUTPUT))
    def Add_Cover(
            self, 
            file_path : Union[str, Path], 
            image_path : Union[str, Path], 
            output : Optional[Union[str, Path]] = None, 
    ) -> Path :
        '''
        Add front cover to the file

        :param file_path: Input file
        :type file_path: Path
        :param image_path: Cover path
        :type image_path: Path
        :param output: Where to save (Optional) 
        :type output: Path
        :return: Where output is generated
        :rtype: Path
        '''
        if not str(file_path).lower().endswith(COVER_FORMATS) :
            raise NotImplementedError("[AddCover] this file format is not supported")

        #Make an jpg cover (Some options embed cover to the file)
        if not os.path.basename(image_path).lower().endswith(".jpg") :
            tmppath = image_path.replace(os.path.basename(image_path), "cover.jpg") # type: ignore Some format requried the file to be named cover.jpg
            RunFFmpeg(
                inputs=image_path,
                output=tmppath,
                args=['-q;v', '1'],
                loglevel=LogLevel.ERROR,
                show_command=self.show_command
            ) #convert image (this make image on base_path not res)
            image_path = tmppath #Re-route image_path
        # ignore if it aready is
        OUTPUT = output
        FILENAME = os.path.splitext(os.path.basename(file_path))
        if output == None : #If output path is not provided devrive one from input
            OUTPUT = f'{os.path.dirname(file_path)}/{FILENAME[0]}_res{FILENAME[1]}'
        SUFFIX = FILENAME[1]

        if SUFFIX == ".mp3" : #Process mp3
            RunFFmpeg(
                inputs=[file_path, image_path],
                output=OUTPUT,
                args=[*AddCover.MP3.value],
                loglevel=LogLevel.ERROR,
                show_command=self.show_command
            )

        elif SUFFIX == ".flac" : #Process flac
            RunFFmpeg(
                inputs=[file_path, image_path],
                output=OUTPUT,
                args=[*AddCover.FLAC.value],
                loglevel=LogLevel.ERROR,
                show_command=self.show_command
            )

        elif SUFFIX == ".ogg" or SUFFIX == ".opus": #Process ogg / opus
            try : #Embed the cover into the file
                self.__Metadata_block_cover(str(image_path))
                RunFFmpeg(
                    inputs=[file_path, './tmp.ffmeta'],
                    output=OUTPUT,
                    args=['-map', '0:a', '-map_metadata', '1', '-c', 'copy'],
                    loglevel=LogLevel.ERROR,
                    show_command=self.show_command
                )
                os.remove("./tmp.ffmeta")

            except :
                log(self.verbose, "\033[38;5;128m[Add_Cover] Embeding failed falling back to external cover\033[0m")
                RunFFmpeg(
                    inputs=file_path,
                    output=OUTPUT,
                    args=[*AddCover.OGG_OPUS.value],
                    loglevel=LogLevel.ERROR,
                    show_command=self.show_command
                ) #Non embed version
        elif SUFFIX == ".mp4" :
            RunFFmpeg(
                inputs=[file_path, image_path],
                output=OUTPUT,
                args=[*AddCover.MP4.value],
                loglevel=LogLevel.ERROR,
                show_command=self.show_command
            )
        return Path(str(OUTPUT))
