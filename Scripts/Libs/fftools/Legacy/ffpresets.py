# ====================================================
#      Presets and currently implimented feature
# ====================================================
VIDEO_PRESETS = {
    #crf must type with exactly 1 space between f and number otherwise something breaks
    #-frame-parallel 1 is on by default apparently
    #-lag-in-frames affect both size and speed (lower = faster bigger file)
    #-threads can be ignore if using av1 vp9 libx264/265
    #-vf \"fps=min(source_fps\,48)\" this limits fps to 48
    
    
    #-----------------------Debug presets-----------------------
    #libaom-av1 -cpu-used 7 -b:v 0 -crf 32 -auto-alt-ref 1 -arnr-maxframes 3 -arnr-strength 2 -tile-columns 2 -row-mt 1 -lag-in-frames 12 -g 600 -keyint_min 10 -pix_fmt yuv420p10le
    "av1_veryslow+ 48fps max VFR 420 10bit" :{ # Smallest file Extreme edition
        "codec": "libaom-av1",
        "params": f"-cpu-used 6 -b:v 0 -crf 32 -auto-alt-ref 1 -arnr-maxframes 7 -arnr-strength 4 -lag-in-frames 48 -enable-tx64 1 -tile-columns 1 -row-mt 1 -g 600 -pix_fmt yuv420p10le -vf \"fps=min(source_fps\\,48),mpdecimate=hi=128:lo=32:frac=0.00005\" -fps_mode vfr"
    }, 
    "av1_veryslow+ 48fps max 420 10bit" :{ # Smallest file Semi Extreme edition
        "codec": "libaom-av1",
        "params": f"-cpu-used 6 -b:v 0 -crf 32 -auto-alt-ref 1 -arnr-maxframes 7 -arnr-strength 4 -lag-in-frames 48 -enable-tx64 1 -tile-columns 1 -row-mt 1 -g 600 -pix_fmt yuv420p10le -vf \"fps=min(source_fps\\,48)\""
    }, 
     "av1_veryslow+ VFR 420 10bit" :{ # Smallest file no dupe edition
        "codec": "libaom-av1",
        "params": f"-cpu-used 6 -b:v 0 -crf 32 -auto-alt-ref 1 -arnr-maxframes 7 -arnr-strength 4 -lag-in-frames 48 -enable-tx64 1 -tile-columns 1 -row-mt 1 -g 600 -pix_fmt yuv420p10le -vf \"mpdecimate=hi=128:lo=32:frac=0.00005\" -fps_mode vfr"
    },    
    "av1_veryslow+ 420 10bit" :{ # Smallest file (cpu 6 so the speed is actually usable)
        "codec": "libaom-av1",
        "params": f"-cpu-used 6 -b:v 0 -crf 32 -auto-alt-ref 1 -arnr-maxframes 7 -arnr-strength 4 -lag-in-frames 48 -enable-tx64 1 -tile-columns 1 -row-mt 1 -g 600 -pix_fmt yuv420p10le"
    }, 
    "av1_veryslow 420 10bit": {   # Almost smallest file (the command looks weird but it's for speed so It's actually usable)
        "codec": "libaom-av1",
        "params": f"-cpu-used 6 -b:v 0 -crf 32 -auto-alt-ref 1 -arnr-maxframes 7 -arnr-strength 4 -lag-in-frames 24 -tile-columns 2 -row-mt 1 -g 600 -pix_fmt yuv420p10le"
    },
    "av1_slow": {       # Relaxed veryslow preset
        "codec": "libaom-av1",
        "params": f"-cpu-used 6 -b:v 0 -crf 32 -tile-columns 2 -row-mt 1 -lag-in-frames 16 -g 600"
    },
    "av1_medium": {     # SVT faster actually uses 100% cpu but bigger file than AOM in almost all cases
        "codec": "libsvtav1",
        "params": f"-preset 5 -b:v 0 -crf 34 -tile-columns 2 -tile-rows 1 -g 600"
    },
    "av1_fast": {       # SVT faster, slightly larger; good for watch builds
        "codec": "libsvtav1",
        "params": f"-preset 6 -b:v 0 -crf 34 -tile-columns 2 -tile-rows 1 -g 600"
    },
    "av1_veryfast": {   # SVT throughput preset — very fast, noticeably larger, best for previews
        "codec": "libsvtav1",
        "params": f"-preset 8 -b:v 0 -crf 34 -tile-columns 2 -tile-rows 1 -g 600"
    },
    "vp9_slow" : { #this actually worse than av1_veryfast at speed and size but it seeks a bit faster on playback
        "codec" : "libvpx-vp9",
        "params" : f"-crf 32 -speed 2 -tile-columns 3 -row-mt 1 -lag-in-frames 4"
    },
    "vp9_lossless" : {
        "codec" : "libvpx-vp9",
        "params" : f"-speed 4 -tile-columns 3 -row-mt 1 -lossless 1"
    },
    "copy" : {
        "codec" : "",
        "params" : "copy"
    },
    "custom" : {
        "codec" : "",
        "params" : ""
    }
}
AUDIO_PRESETS = {
    "flac" : {
        "codec" : "flac",
        "params" : "-compression_level 12"
    },
    "opus_96k" : {
        "codec" : "libopus",
        "params" : "-vbr on -compression_level 10 -application audio -b:a 96k"
    },
    "opus_128k (Transparent)" : {
        "codec" : "libopus",
        "params" : "-vbr on -compression_level 10 -application audio -b:a 128k"
    },
    "opus_192k" : {
        "codec" : "libopus",
        "params" : "-vbr on -compression_level 10 -application audio -b:a 256k"
    },
    "opus_256k" : {
        "codec" : "libopus",
        "params" : "-vbr on -compression_level 10 -application audio -b:a 510k"
    },
    "copy" : {
        "codec" : "",
        "params" : "copy"
    },
    "custom" : {
        "codec" : "",
        "params" : ""
    }
}
COVER_FORMATS = ("mp3", "mp4", "flac", "ogg", "opus")
COVER_PRESETS_ADD = {
    #The preset that embed picture into the file may produce larger albums/collections
    #You can mixup files that have embeded cover and noting will break
    "FLAC" : '-map_metadata 0 -map 0:a -map 1:v -c:v copy -c:a copy -disposition:v attached_pic', #Embed
    "MP3" : '-map_metadata 0 -map 0:a -map 1:v -c:v copy -c:a copy -metadata:s:v comment="Cover (front)" -id3v2_version 3', #Embed
    "MP4" : '-map_metadata 0 -map 0 -map 1 -c copy -disposition:v:1 attached_pic', #Embed
    "OGG/OPUS" : '-c copy -metadata "METADATA_BLOCK_PICTURE=&(base64 -w 0 cover.jpg)"', #This requried cover.jpg to exist in same folder (fallback)
}
COVER_PRESETS_REMOVE = {
    "FLAC" : '-map 0:a -c copy -map_metadata 0',
    "MP3" : '-map 0:a -c copy -map_metadata 0',
    "MP4" : '-map 0:a -c copy -map_metadata 0',
    "OGG/OPUS" : '-map 0:a -map_metadata 1 -c copy'
}

FFMPEG = "ffmpeg -hide_banner -y"
RATE_KEYS = [
    "-crf", "-b:v", "-minrate", "-maxrate",
    "-qp", "-qmin", "-qmax", "-bufsize"
]
