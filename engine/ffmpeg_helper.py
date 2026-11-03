import os
import sys
import shutil

def get_ffmpeg_path():
    """
    Finds the ffmpeg executable.
    Checks:
    1. PyInstaller bundled path (_MEIPASS)
    2. Local application directory
    3. imageio-ffmpeg bundled binary
    4. System PATH
    """
    # 1. Check PyInstaller _MEIPASS
    if hasattr(sys, '_MEIPASS'):
        for name in ['ffmpeg.exe', 'ffmpeg']:
            p1 = os.path.join(sys._MEIPASS, name)
            if os.path.isfile(p1):
                return p1
            p2 = os.path.join(sys._MEIPASS, 'binaries', name)
            if os.path.isfile(p2):
                return p2

    # 2. Check local application directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for name in ['ffmpeg.exe', 'ffmpeg']:
        p1 = os.path.join(base_dir, name)
        if os.path.isfile(p1):
            return p1
        p2 = os.path.join(base_dir, 'binaries', name)
        if os.path.isfile(p2):
            return p2

    # 3. Check imageio_ffmpeg
    try:
        import imageio_ffmpeg
        ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
        if ffmpeg_bin and os.path.isfile(ffmpeg_bin):
            return ffmpeg_bin
    except Exception:
        pass

    # 4. Check system PATH
    sys_ffmpeg = shutil.which('ffmpeg')
    if sys_ffmpeg:
        return sys_ffmpeg

    return None

def is_ffmpeg_available():
    return get_ffmpeg_path() is not None
