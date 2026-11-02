import os
import re
import yt_dlp
from engine.cookies import get_cookie_file_path
from engine.ffmpeg_helper import get_ffmpeg_path

def format_duration(seconds):
    if not seconds:
        return "Unknown"
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"

def format_number(num):
    if not num:
        return "0"
    num = int(num)
    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    if num >= 1_000:
        return f"{num / 1_000:.1f}K"
    return str(num)

def extract_media_info(url: str, use_cookies: bool = True) -> dict:
    """
    Extracts complete media metadata from any video/audio URL.
    Returns structured data for single video or playlist.
    """
    url = url.strip()
    if not url:
        return {"success": False, "error": "URL cannot be empty"}

    # Real-Debrid Filehoster & Magnet Check
    from engine.real_debrid import is_rd_supported_url, unrestrict_link, unrestrict_magnet, get_rd_token
    if is_rd_supported_url(url):
        rd_token = get_rd_token()
        if not rd_token:
            return {
                "success": False,
                "error": "Bu dosya barındırıcısı (Rapidgator, 1fichier, vb.) veya Torrent için Ayarlar'dan Real-Debrid API Token eklemelisiniz."
            }
        
        if url.lower().startswith('magnet:?'):
            rd_res = unrestrict_magnet(url)
        else:
            rd_res = unrestrict_link(url)

        if rd_res.get('success'):
            return {
                "success": True,
                "is_playlist": False,
                "is_debrid": True,
                "id": str(rd_res.get('id', 'rd_file')),
                "url": url,
                "download_url": rd_res.get('download_url'),
                "title": rd_res.get('title'),
                "duration": 0,
                "duration_string": rd_res.get('filesize_formatted', 'Dosya'),
                "thumbnail": "",
                "uploader": f"{rd_res.get('host')} [Real-Debrid Premium]",
                "views": rd_res.get('filesize_formatted', 'Premium'),
                "resolutions": [
                    {"height": 0, "label": f"Orijinal Dosya ({rd_res.get('filesize_formatted')})", "value": "direct"}
                ],
                "subtitles": []
            }
        else:
            return rd_res

    ffmpeg_path = get_ffmpeg_path()
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'extract_flat': 'in_playlist',
    }

    if ffmpeg_path:
        ydl_opts['ffmpeg_location'] = ffmpeg_path

    cookie_file = get_cookie_file_path()
    if use_cookies and os.path.isfile(cookie_file) and os.path.getsize(cookie_file) > 0:
        ydl_opts['cookiefile'] = cookie_file

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as e:
        err_msg = str(e)
        # Clean up common yt-dlp error prefixes
        err_msg = re.sub(r'ERROR:\s*', '', err_msg)
        return {"success": False, "error": err_msg}

    if not info:
        return {"success": False, "error": "Could not extract information from URL"}

    # Check if this is a playlist / channel / collection
    if 'entries' in info and info.get('_type') == 'playlist':
        entries = []
        for idx, entry in enumerate(info.get('entries') or []):
            if not entry:
                continue
            entry_url = entry.get('url') or entry.get('webpage_url')
            if not entry_url and entry.get('id'):
                entry_url = f"https://www.youtube.com/watch?v={entry.get('id')}"
            
            entries.append({
                "index": idx + 1,
                "id": entry.get('id', str(idx)),
                "title": entry.get('title', f"Track #{idx + 1}"),
                "duration": entry.get('duration'),
                "duration_string": format_duration(entry.get('duration')),
                "thumbnail": entry.get('thumbnail') or (entry.get('thumbnails')[-1].get('url') if entry.get('thumbnails') else None),
                "url": entry_url,
                "uploader": entry.get('uploader') or entry.get('channel') or "Unknown"
            })

        return {
            "success": True,
            "is_playlist": True,
            "title": info.get('title', 'Playlist'),
            "uploader": info.get('uploader') or info.get('channel') or "Various Creators",
            "total_items": len(entries),
            "thumbnail": entries[0]['thumbnail'] if entries else None,
            "url": url,
            "items": entries
        }

    # Single video / audio extraction
    title = info.get('title', 'Unknown Title')
    duration = info.get('duration', 0)
    
    # Extract highest resolution thumbnail / banner
    thumbnail = info.get('thumbnail')
    thumbnails = info.get('thumbnails', [])
    best_thumbnail = thumbnail
    if thumbnails:
        valid_thumbs = [t for t in thumbnails if t.get('url')]
        if valid_thumbs:
            sorted_thumbs = sorted(
                valid_thumbs,
                key=lambda t: (t.get('preference', 0) or 0, t.get('width', 0) or 0, t.get('height', 0) or 0),
                reverse=True
            )
            best_thumbnail = sorted_thumbs[0].get('url') or thumbnail

    # If YouTube, check maxresdefault option
    video_id = info.get('id')
    if info.get('extractor_key') == 'Youtube' and video_id:
        best_thumbnail = f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg"

    uploader = info.get('uploader') or info.get('channel') or "Unknown Creator"
    views = format_number(info.get('view_count'))
    description = info.get('description', '')[:250]

    # Parse available video resolutions and qualities
    formats = info.get('formats', [])
    resolution_map = {}
    has_audio_stream = False

    for f in formats:
        height = f.get('height')
        width = f.get('width')
        vcodec = f.get('vcodec', 'none')
        acodec = f.get('acodec', 'none')
        fps = f.get('fps')

        if acodec != 'none':
            has_audio_stream = True

        if vcodec != 'none' and height:
            label = f"{height}p"
            quality_num = height
            extra = []
            if fps and fps >= 50:
                extra.append(f"{int(fps)}fps")
            if 'hdr' in (f.get('dynamic_range') or '').lower():
                extra.append("HDR")
            
            extra_str = f" ({', '.join(extra)})" if extra else ""
            display_label = f"{label}{extra_str}"
            
            # Map common names
            tier_name = label
            if height >= 2160:
                tier_name = f"4K Ultra HD ({label})"
            elif height >= 1440:
                tier_name = f"2K Quad HD ({label})"
            elif height >= 1080:
                tier_name = f"1080p Full HD"
            elif height >= 720:
                tier_name = f"720p HD"
            else:
                tier_name = f"{label} SD"

            if display_label not in resolution_map or quality_num > resolution_map[display_label]['height']:
                resolution_map[display_label] = {
                    "height": height,
                    "label": display_label,
                    "tier_name": tier_name,
                    "format_id": f.get('format_id'),
                    "ext": f.get('ext', 'mp4'),
                    "filesize": f.get('filesize') or f.get('filesize_approx')
                }

    # Sort resolutions high to low
    sorted_resolutions = sorted(
        resolution_map.values(),
        key=lambda x: x['height'],
        reverse=True
    )

    # Standard preset resolutions
    preset_resolutions = [
        {"height": 2160, "label": "4K Ultra HD (2160p)", "value": "2160"},
        {"height": 1440, "label": "2K Quad HD (1440p)", "value": "1440"},
        {"height": 1080, "label": "1080p Full HD", "value": "1080"},
        {"height": 720, "label": "720p HD", "value": "720"},
        {"height": 480, "label": "480p SD", "value": "480"},
        {"height": 0, "label": "Best Available (Source Max)", "value": "best"}
    ]

    # Available subtitles
    subtitles = []
    all_subs = info.get('subtitles', {})
    auto_subs = info.get('automatic_captions', {})
    sub_langs = set(list(all_subs.keys()) + list(auto_subs.keys()))
    common_langs = [('en', 'English'), ('tr', 'Turkish / Türkçe'), ('es', 'Spanish'), ('de', 'German'), ('fr', 'French'), ('ar', 'Arabic'), ('ja', 'Japanese'), ('ru', 'Russian')]
    
    for code, name in common_langs:
        if code in sub_langs:
            subtitles.append({"code": code, "name": name})
    
    if not subtitles and sub_langs:
        for code in list(sub_langs)[:5]:
            subtitles.append({"code": code, "name": code.upper()})

    return {
        "success": True,
        "is_playlist": False,
        "id": info.get('id'),
        "url": url,
        "title": title,
        "duration": duration,
        "duration_string": format_duration(duration),
        "thumbnail": thumbnail or best_thumbnail,
        "banner_url": best_thumbnail or thumbnail,
        "uploader": uploader,
        "views": views,
        "description": description,
        "resolutions": sorted_resolutions if sorted_resolutions else preset_resolutions,
        "subtitles": subtitles,
        "has_audio": has_audio_stream
    }
