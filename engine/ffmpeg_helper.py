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
        meipass_ffmpeg = os.path.join(sys._MEIPASS, 'ffmpeg.exe')
        if os.path.isfile(meipass_ffmpeg):
            return meipass_ffmpeg
        meipass_bin = os.path.join(sys._MEIPASS, 'binaries', 'ffmpeg.exe')
        if os.path.isfile(meipass_bin):
            return meipass_bin

    # 2. Check local application directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    local_ffmpeg = os.path.join(base_dir, 'ffmpeg.exe')
    if os.path.isfile(local_ffmpeg):
        return local_ffmpeg
    local_bin = os.path.join(base_dir, 'binaries', 'ffmpeg.exe')
    if os.path.isfile(local_bin):
        return local_bin

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
