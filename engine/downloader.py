import os
import sys
import time
import uuid
import threading
import yt_dlp
from engine.cookies import get_cookie_file_path
from engine.ffmpeg_helper import get_ffmpeg_path
from engine.history import add_history_item

# Global active downloads registry
ACTIVE_DOWNLOADS = {}
DOWNLOAD_LOCK = threading.Lock()

def parse_time_to_seconds(time_str):
    """Converts HH:MM:SS or MM:SS or seconds string to float seconds."""
    if not time_str or not time_str.strip():
        return None
    time_str = time_str.strip()
    try:
        parts = time_str.split(':')
        if len(parts) == 3:
            return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
        elif len(parts) == 2:
            return float(parts[0]) * 60 + float(parts[1])
        else:
            return float(time_str)
    except Exception:
        return None

def format_speed(bytes_per_sec):
    if not bytes_per_sec:
        return "0.0 MB/s"
    mb = bytes_per_sec / (1024 * 1024)
    if mb >= 1.0:
        return f"{mb:.1f} MB/s"
    kb = bytes_per_sec / 1024
    return f"{kb:.1f} KB/s"

def format_bytes(b):
    if not b:
        return "0 MB"
    mb = b / (1024 * 1024)
    if mb >= 1024:
        return f"{mb / 1024:.2f} GB"
    return f"{mb:.1f} MB"

def format_eta(seconds):
    if not seconds:
        return "--:--"
    m = int(seconds) // 60
    s = int(seconds) % 60
    return f"{m:02d}:{s:02d}"

class DownloadTask:
    def __init__(self, download_id, options, progress_callback=None):
        self.download_id = download_id
        self.options = options
        self.progress_callback = progress_callback
        self.cancelled = False
        self.thread = None
        self.final_filepath = None
        is_debrid = options.get('is_debrid') or bool(options.get('download_url'))
        title = options.get('title', 'Initializing...')
        ext = os.path.splitext(title)[1].replace('.', '').upper() if '.' in title else 'DIRECT'

        self.status_data = {
            "id": download_id,
            "url": options.get('url'),
            "title": title,
            "thumbnail": options.get('thumbnail'),
            "mode": "DEBRID" if is_debrid else options.get('mode', 'video'),
            "resolution": options.get('resolution', 'best'),
            "format": ext if is_debrid else options.get('format', 'mp4'),
            "status": "queued", # queued, downloading, muxing, completed, error, cancelled
            "percent": 0.0,
            "speed": "0.0 MB/s",
            "eta": "--:--",
            "downloaded": "0 MB",
            "total": "0 MB",
            "filepath": None,
            "error": None
        }

    def update_status(self, **kwargs):
        self.status_data.update(kwargs)
        if self.progress_callback:
            try:
                self.progress_callback(self.status_data.copy())
            except Exception:
                pass

    def cancel(self):
        self.cancelled = True
        self.update_status(status="cancelled", error="Cancelled by user")

    def _progress_hook(self, d):
        if self.cancelled:
            raise yt_dlp.utils.DownloadCancelled("Download cancelled by user")

        status = d.get('status')
        if status == 'downloading':
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            speed = d.get('speed', 0)
            eta = d.get('eta', 0)

            percent = 0.0
            if total > 0:
                percent = round((downloaded / total) * 100, 1)

            self.update_status(
                status="downloading",
                percent=percent,
                speed=format_speed(speed),
                eta=format_eta(eta),
                downloaded=format_bytes(downloaded),
                total=format_bytes(total)
            )
        elif status == 'finished':
            self.update_status(
                status="muxing",
                percent=99.0,
                speed="Processing...",
                eta="Almost done"
            )

    def _postprocessor_hook(self, d):
        if self.cancelled:
            raise yt_dlp.utils.DownloadCancelled("Download cancelled by user")
        pp = d.get('postprocessor')
        if pp:
            self.update_status(status="muxing", speed=f"Muxing ({pp})...")

    def run(self):
        try:
            self.update_status(status="downloading", speed="Starting stream...")
            url = self.options['url']
            mode = self.options.get('mode', 'video')
            format_ext = self.options.get('format', 'mp4' if mode == 'video' else 'mp3')
            quality = self.options.get('resolution', 'best')
            save_path = self.options.get('save_path') or os.path.join(os.path.expanduser('~'), 'Downloads', 'MerVid_Downloads')
            os.makedirs(save_path, exist_ok=True)

            # Direct HTTP / Real-Debrid High-Speed Stream
            direct_url = self.options.get('download_url')
            if direct_url:
                import urllib.request
                import time
                import re

                title = self.options.get('title', 'downloaded_file')
                clean_title = re.sub(r'[\\/*?:"<>|]', '_', title).strip()
                target_file = os.path.join(save_path, clean_title)

                req = urllib.request.Request(direct_url, headers={'User-Agent': 'MerVid-Studio/1.0.0'})
                with urllib.request.urlopen(req, timeout=30) as resp:
                    total = int(resp.headers.get('Content-Length') or 0)
                    downloaded = 0
                    start_time = time.time()
                    last_update = start_time

                    with open(target_file, 'wb') as f:
                        while True:
                            if self.cancelled:
                                raise yt_dlp.utils.DownloadCancelled("İptal edildi")
                            chunk = resp.read(1024 * 512)
                            if not chunk:
                                break
                            f.write(chunk)
                            downloaded += len(chunk)
                            now = time.time()
                            if now - last_update >= 0.5:
                                elapsed = now - start_time
                                speed = downloaded / elapsed if elapsed > 0 else 0
                                eta = (total - downloaded) / speed if speed > 0 and total > downloaded else 0
                                percent = round((downloaded / total) * 100, 1) if total > 0 else 0.0
                                self.update_status(
                                    status="downloading",
                                    percent=percent,
                                    speed=format_speed(speed),
                                    eta=format_eta(eta),
                                    downloaded=format_bytes(downloaded),
                                    total=format_bytes(total)
                                )
                                last_update = now

                self.final_filepath = target_file
                self.update_status(
                    status="completed",
                    percent=100.0,
                    speed="Bitti",
                    eta="00:00",
                    filepath=target_file,
                    title=clean_title
                )
                add_history_item({
                    "id": self.download_id,
                    "title": clean_title,
                    "url": self.options.get('url'),
                    "thumbnail": self.options.get('thumbnail'),
                    "filepath": target_file,
                    "filesize": format_bytes(total),
                    "mode": "Debrid",
                    "resolution": "Premium",
                    "format": "Direct"
                })
                return

            ffmpeg_path = get_ffmpeg_path()
            outtmpl = os.path.join(save_path, '%(title)s.%(ext)s')

            ydl_opts = {
                'outtmpl': outtmpl,
                'progress_hooks': [self._progress_hook],
                'postprocessor_hooks': [self._postprocessor_hook],
                'quiet': True,
                'no_warnings': True,
                'nocheckcertificate': True,
            }

            if ffmpeg_path:
                ydl_opts['ffmpeg_location'] = ffmpeg_path

            # Multi-threading / Fragment concurrency
            threads = int(self.options.get('threads', 8))
            ydl_opts['concurrent_fragment_downloads'] = threads

            # Cookie Vault integration
            if self.options.get('use_cookies', True):
                cookie_file = get_cookie_file_path()
                if os.path.isfile(cookie_file) and os.path.getsize(cookie_file) > 0:
                    ydl_opts['cookiefile'] = cookie_file

            # SponsorBlock
            if self.options.get('sponsorblock', False):
                ydl_opts['sponsorblock_remove'] = ['sponsor', 'intro', 'outro', 'selfpromo', 'preview', 'music_offtopic']

            # Banner / Thumbnail Download (.jpg)
            if self.options.get('save_banner', False):
                ydl_opts['writethumbnail'] = True
                if 'postprocessors' not in ydl_opts:
                    ydl_opts['postprocessors'] = []
                ydl_opts['postprocessors'].append({
                    'key': 'FFmpegThumbnailsConvertor',
                    'format': 'jpg'
                })

            # Embed thumbnail as media cover art
            if self.options.get('embed_thumbnail', False):
                ydl_opts['writethumbnail'] = True
                if 'postprocessors' not in ydl_opts:
                    ydl_opts['postprocessors'] = []
                ydl_opts['postprocessors'].append({
                    'key': 'FFmpegEmbedThumbnail',
                    'already_have_thumbnail': False
                })

            # Timeline Trimming
            start_sec = parse_time_to_seconds(self.options.get('start_time'))
            end_sec = parse_time_to_seconds(self.options.get('end_time'))
            if start_sec is not None or end_sec is not None:
                start = start_sec if start_sec is not None else 0
                end = end_sec if end_sec is not None else float('inf')
                ydl_opts['download_ranges'] = yt_dlp.utils.download_range_func(None, [(start, end)])
                ydl_opts['force_keyframes_at_cuts'] = True

            # Subtitles
            if self.options.get('embed_subtitles', False):
                lang = self.options.get('subtitle_lang', 'all')
                ydl_opts['writesubtitles'] = True
                ydl_opts['writeautomaticsub'] = True
                if lang == 'all':
                    ydl_opts['subtitleslangs'] = ['en', 'tr', '.*']
                else:
                    ydl_opts['subtitleslangs'] = [lang, 'en']
                
                # embed subs
                ydl_opts['postprocessors'] = ydl_opts.get('postprocessors', [])
                ydl_opts['postprocessors'].append({
                    'key': 'FFmpegEmbedSubtitle',
                    'already_have_subtitle': False
                })

            # Format Configuration
            if mode == 'audio':
                # Lossless or high bitrate audio extraction
                ydl_opts['format'] = 'bestaudio/best'
                audio_pp = {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': format_ext,
                }
                if format_ext == 'mp3':
                    audio_pp['preferredquality'] = self.options.get('audio_quality', '320')
                
                if 'postprocessors' not in ydl_opts:
                    ydl_opts['postprocessors'] = []
                ydl_opts['postprocessors'].insert(0, audio_pp)
            else:
                # Video Mode: 4K / 1080p / High-res muxing
                if quality == 'best':
                    format_str = f"bestvideo+bestaudio/best"
                else:
                    try:
                        h = int(quality)
                        format_str = f"bestvideo[height<={h}]+bestaudio/best[height<={h}]/best"
                    except ValueError:
                        format_str = "bestvideo+bestaudio/best"

                ydl_opts['format'] = format_str
                ydl_opts['merge_output_format'] = format_ext

            # Execute Download
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                extract_res = ydl.extract_info(url, download=True)
                
                # Determine final file path
                title = extract_res.get('title') if extract_res else self.options.get('title', 'video')
                final_filename = ydl.prepare_filename(extract_res)
                # If audio extraction was done, ext might have changed
                if mode == 'audio':
                    base, _ = os.path.splitext(final_filename)
                    final_filename = f"{base}.{format_ext}"
                elif format_ext:
                    base, _ = os.path.splitext(final_filename)
                    final_filename = f"{base}.{format_ext}"

                if not os.path.isfile(final_filename):
                    # Check directory for matching title
                    for f in os.listdir(save_path):
                        if f.startswith(title[:20]):
                            final_filename = os.path.join(save_path, f)
                            break

                self.final_filepath = final_filename
                filesize = os.path.getsize(final_filename) if os.path.isfile(final_filename) else 0

                self.update_status(
                    status="completed",
                    percent=100.0,
                    speed="Finished",
                    eta="00:00",
                    filepath=final_filename,
                    title=title
                )

                # Add to history
                add_history_item({
                    "id": self.download_id,
                    "title": title,
                    "url": url,
                    "thumbnail": self.options.get('thumbnail'),
                    "filepath": final_filename,
                    "filesize": format_bytes(filesize),
                    "mode": mode,
                    "resolution": quality if mode == 'video' else 'Audio',
                    "format": format_ext
                })

        except yt_dlp.utils.DownloadCancelled:
            self.update_status(status="cancelled", error="Cancelled by user")
        except Exception as e:
            self.update_status(status="error", error=str(e))
        finally:
            with DOWNLOAD_LOCK:
                if self.download_id in ACTIVE_DOWNLOADS:
                    pass  # keep for UI inspection until cleared

def start_download_task(options: dict, progress_callback=None) -> str:
    """Spawns a new background download task and returns its unique ID."""
    download_id = str(uuid.uuid4())[:8]
    task = DownloadTask(download_id, options, progress_callback)
    
    with DOWNLOAD_LOCK:
        ACTIVE_DOWNLOADS[download_id] = task
        
    thread = threading.Thread(target=task.run, daemon=True)
    task.thread = thread
    thread.start()
    return download_id

def cancel_download_task(download_id: str) -> bool:
    with DOWNLOAD_LOCK:
        task = ACTIVE_DOWNLOADS.get(download_id)
        if task:
            task.cancel()
            return True
    return False

def get_all_downloads_status() -> list:
    with DOWNLOAD_LOCK:
        return [task.status_data.copy() for task in ACTIVE_DOWNLOADS.values()]

def download_banner_directly(thumbnail_url: str, title: str, save_path: str = None) -> dict:
    """Downloads the banner/thumbnail image directly to disk."""
    import urllib.request
    import re
    try:
        if not save_path:
            save_path = os.path.join(os.path.expanduser('~'), 'Downloads', 'MerVid_Downloads')
        os.makedirs(save_path, exist_ok=True)

        clean_title = re.sub(r'[\\/*?:"<>|]', '_', title)[:80].strip()
        filename = f"{clean_title}_banner.jpg"
        filepath = os.path.join(save_path, filename)

        req = urllib.request.Request(
            thumbnail_url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read()
            with open(filepath, 'wb') as f:
                f.write(content)

        return {"success": True, "filepath": filepath, "filename": filename}
    except Exception as e:
        return {"success": False, "error": str(e)}

