from pathlib import Path
import ctypes
import os
import subprocess
import sys
from dataclasses import dataclass

@dataclass
class RunResult :
    exitcode : int
    stdout : str
    stderr : str

def _SetFsDates (Source : Path, Target : Path) -> None :
    """
    Copies filesystem dates from Source to Target
    """
    st = Source.stat()

    if sys.platform == "win32" :
        # Windows (NTFS) : creation, last-access and last-write dates are all settable
        class _FILETIME (ctypes.Structure) :
            _fields_ = (("dwLowDateTime", ctypes.c_uint32), ("dwHighDateTime", ctypes.c_uint32))

        def _ToFileTime (ns_since_epoch : int) -> _FILETIME :
            total = (ns_since_epoch + 11_644_473_600_000_000_000) // 100 # 100ns units since 1601-01-01 (FILETIME epoch)
            return _FILETIME(total & 0xFFFFFFFF, total >> 32 & 0xFFFFFFFF)

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.CreateFileW.restype = ctypes.c_void_p
        kernel32.SetFileTime.argtypes = [ctypes.c_void_p,
                                         ctypes.POINTER(_FILETIME),
                                         ctypes.POINTER(_FILETIME),
                                         ctypes.POINTER(_FILETIME)]

        INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value
        # GENERIC_READ | GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE, OPEN_EXISTING
        handle = kernel32.CreateFileW(str(Target), 0xC0000000, 0x7, None, 3, 0, None)
        try :
            if handle not in (None, INVALID_HANDLE_VALUE) :
                kernel32.SetFileTime(
                    handle,
                    _ToFileTime(int(round(st.st_ctime * 1e9))), # st_ctime IS the creation date on Windows
                    _ToFileTime(st.st_atime_ns),
                    _ToFileTime(st.st_mtime_ns),
                )
        finally :
            if handle not in (None, INVALID_HANDLE_VALUE) :
                kernel32.CloseHandle(handle)
    else :
        # Other OS's : only access and modification dates are settable,
        # creation date is managed by the filesystem itself
        os.utime(Target, ns=(st.st_atime_ns, st.st_mtime_ns))

def MetaDupe_Image (Source : Path, Target : Path) -> RunResult:
    """
    Dupelicates all avaliable metadata from an image to another
    """
    COMMAND = [
        "exiftool", 
        "-TagsFromFile", Source, 
        "-all:all<all:all", 
        "-P", "-m", 
        "-overwrite_original", Target
    ]

    res = subprocess.run(
        COMMAND,
        capture_output=True,
        text=True,
    )

    try :
        _SetFsDates(Source, Target)
    except OSError :
        pass

    return RunResult(
        res.returncode, 
        res.stdout, 
        res.stderr
    )
