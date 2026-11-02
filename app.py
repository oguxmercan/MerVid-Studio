import os
import sys
import json
import subprocess
import webview
from engine.extractor import extract_media_info
from engine.downloader import start_download_task, cancel_download_task, get_all_downloads_status, download_banner_directly
from engine.cookies import get_cookie_status, save_cookie_file, save_cookie_text, clear_cookie, get_app_dir
from engine.history import load_history, clear_all_history
from engine.ffmpeg_helper import get_ffmpeg_path

def get_settings_file_path():
    return os.path.join(get_app_dir(), 'settings.json')

def load_settings():
    default_save = os.path.join(os.path.expanduser('~'), 'Downloads', 'MerVid_Downloads')
    defaults = {
        "save_path": default_save,
        "default_video_format": "mp4",
        "default_audio_format": "mp3",
        "concurrent_threads": 8,
        "sponsorblock_enabled": True
    }
    path = get_settings_file_path()
    if os.path.isfile(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                defaults.update(data)
        except Exception:
            pass
    return defaults

def save_app_settings(settings_dict):
    current = load_settings()
    current.update(settings_dict)
    path = get_settings_file_path()
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(current, f, indent=2)
    except Exception as e:
        print("Error saving settings:", e)
    return current

class DownloaderApi:
    def __init__(self):
        self._window = None

    def set_window(self, window):
        self._window = window

    def inspect_url(self, url: str) -> dict:
        return extract_media_info(url)

    def start_download(self, payload: dict) -> dict:
        try:
            download_id = start_download_task(payload)
            return {"success": True, "download_id": download_id}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def cancel_download(self, download_id: str) -> bool:
        return cancel_download_task(download_id)

    def get_active_downloads(self) -> list:
        return get_all_downloads_status()

    def get_history(self) -> list:
        return load_history()

    def clear_history(self) -> list:
        return clear_all_history()

    def get_cookie_status(self) -> dict:
        return get_cookie_status()

    def save_cookie_text(self, text: str) -> dict:
        return save_cookie_text(text)

    def clear_cookie(self) -> dict:
        return clear_cookie()

    def get_rd_status(self) -> dict:
        from engine.real_debrid import verify_rd_token
        return verify_rd_token()

    def save_rd_token(self, token: str) -> dict:
        from engine.real_debrid import save_rd_token
        return save_rd_token(token)

    def remove_rd_token(self) -> dict:
        from engine.real_debrid import remove_rd_token
        return remove_rd_token()

    def download_banner(self, thumbnail_url: str, title: str, save_path: str = None) -> dict:
        if not save_path:
            settings = load_settings()
            save_path = settings.get('save_path')
        return download_banner_directly(thumbnail_url, title, save_path)

    def get_settings(self) -> dict:
        settings = load_settings()
        settings['ffmpeg_path'] = get_ffmpeg_path()
        return settings

    def save_settings(self, settings: dict) -> dict:
        return save_app_settings(settings)

    def select_folder(self) -> str:
        if not self._window:
            return ""
        result = self._window.create_file_dialog(webview.FOLDER_DIALOG)
        if result and len(result) > 0:
            return result[0]
        return ""

    def select_cookie_file(self) -> dict:
        if not self._window:
            return {"success": False, "error": "Window not ready"}
        result = self._window.create_file_dialog(
            webview.OPEN_DIALOG,
            file_types=('Cookie Text Files (*.txt)', '*.txt')
        )
        if result and len(result) > 0:
            return save_cookie_file(result[0])
        return {"success": False, "error": "No file selected"}

    def open_file(self, filepath: str) -> bool:
        if filepath and os.path.isfile(filepath):
            try:
                os.startfile(filepath)
                return True
            except Exception:
                try:
                    subprocess.Popen(['explorer', filepath])
                    return True
                except Exception:
                    return False
        return False

    def open_folder(self, filepath: str) -> bool:
        if not filepath:
            return False
        target_dir = filepath if os.path.isdir(filepath) else os.path.dirname(filepath)
        if os.path.exists(target_dir):
            try:
                if os.path.isfile(filepath):
                    subprocess.Popen(['explorer', '/select,', os.path.normpath(filepath)])
                else:
                    os.startfile(target_dir)
                return True
            except Exception:
                return False
        return False

    def open_url(self, url: str) -> bool:
        if url:
            import webbrowser
            try:
                webbrowser.open(url)
                return True
            except Exception:
                return False
        return False

def resolve_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, relative_path)

def main():
    api = DownloaderApi()
    ui_html_path = resolve_resource_path(os.path.join('ui', 'index.html'))

    window = webview.create_window(
        title="MerVid Studio",
        url=ui_html_path,
        js_api=api,
        width=1060,
        height=720,
        min_size=(880, 620),
        background_color="#111113"
    )
    api.set_window(window)
    webview.start(debug=False)

if __name__ == '__main__':
    main()
