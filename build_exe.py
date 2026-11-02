import os
import sys
import shutil
import subprocess

def build():
    print("=== Building MerVid Studio Windows Executable ===")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)

    # Ensure binaries/ffmpeg.exe exists
    bin_dir = os.path.join(base_dir, 'binaries')
    ffmpeg_exe = os.path.join(bin_dir, 'ffmpeg.exe')
    if not os.path.isfile(ffmpeg_exe):
        try:
            import imageio_ffmpeg
            src = imageio_ffmpeg.get_ffmpeg_exe()
            os.makedirs(bin_dir, exist_ok=True)
            shutil.copyfile(src, ffmpeg_exe)
            print("Bundled ffmpeg into binaries/")
        except Exception as e:
            print("Warning: ffmpeg not bundled automatically:", e)

    # Ensure app_icon.ico exists
    ico_path = os.path.join(base_dir, 'app_icon.ico')
    png_path = os.path.join(base_dir, 'ui', 'mervid-studio.png')
    if not os.path.isfile(ico_path) and os.path.isfile(png_path):
        try:
            from PIL import Image
            img = Image.open(png_path).convert('RGBA')
            sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
            img.save(ico_path, format='ICO', sizes=sizes)
            print("Generated app_icon.ico from ui/mervid-studio.png")
        except Exception as e:
            print("Warning: could not generate app_icon.ico:", e)

    # PyInstaller arguments
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=MerVid-Studio",
        "-y",
        "--noconsole",
        "--clean",
        "--icon=app_icon.ico",
        "--add-data=ui;ui",
        "--add-data=binaries;binaries",
        "--hidden-import=webview",
        "--hidden-import=webview.platforms.winforms",
        "--hidden-import=webview.platforms.edgechromium",
        "--hidden-import=clr",
        "--hidden-import=pythonnet",
        "--hidden-import=yt_dlp",
        "--hidden-import=yt_dlp.extractor",
        "--hidden-import=yt_dlp.postprocessor",
        "--onedir",
        "app.py"
    ]

    print("Running PyInstaller command:")
    print(" ".join(cmd))
    
    ret = subprocess.call(cmd)
    if ret == 0:
        dist_exe = os.path.join(base_dir, "dist", "MerVid-Studio", "MerVid-Studio.exe")
        print("\n=======================================================")
        print(" BUILD SUCCESSFUL!")
        print(f" Executable: {dist_exe}")
        print("=======================================================\n")
    else:
        print("\n Build failed with code", ret)
    return ret

if __name__ == '__main__':
    sys.exit(build())
