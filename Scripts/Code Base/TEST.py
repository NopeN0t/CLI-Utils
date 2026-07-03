import tempfile
import base64
import struct
import mimetypes
from pathlib import Path

def build_ffmetadata_with_picture(cover_path: str) -> Path:
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

    b64 = base64.b64encode(block).decode("ascii")

    tmp = tempfile.NamedTemporaryFile(
        mode="w",
        delete=False,
        suffix=".ffmeta",
        encoding="utf-8"
    )

    tmp.write(";FFMETADATA1\n")
    tmp.write(f"METADATA_BLOCK_PICTURE={b64}\n")
    tmp.close()

    return Path(tmp.name)


import subprocess

def embed_cover_opus(input_file, cover_file, output_file):
    meta = build_ffmetadata_with_picture(cover_file)

    try:
        subprocess.run([
            "ffmpeg", "-y",
            "-i", input_file,
            "-i", meta,
            "-map_metadata", "1",
            "-c", "copy",
            output_file
        ], check=True)
    finally:
        meta.unlink(missing_ok=True)

embed_cover_opus("R:\\x.ogg", "R:/cover.jpg", "R:/x2.ogg")