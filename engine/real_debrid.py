import json
import urllib.request
import urllib.parse
from datetime import datetime
from engine.cookies import get_app_dir

RD_API_BASE = "https://api.real-debrid.com/rest/1.0"

# Common file hoster domains supported by Real-Debrid
RD_KNOWN_HOSTS = [
    'rapidgator.net', 'rg.to', '1fichier.com', 'mega.nz', 'mega.co.nz',
    'turbobit.net', 'uploaded.net', 'ul.to', 'filefactory.com', 'nitroflare.com',
    'katfile.com', 'ddownload.com', 'mediafire.com', 'uptobox.com',
    'dropapk.to', 'bayfiles.com', 'anonfiles.com', 'hexupload.net',
    'clicknupload.cc', 'clicknupload.org', 'send.cm', 'streamtape.com'
]

def get_settings_file_path():
    import os
    return os.path.join(get_app_dir(), 'settings.json')

def get_rd_token() -> str:
    path = get_settings_file_path()
    try:
        import os
        if os.path.isfile(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('rd_api_token', '').strip()
    except Exception:
        pass
    return ""

def save_rd_token(token: str) -> dict:
    import os
    path = get_settings_file_path()
    try:
        data = {}
        if os.path.isfile(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        data['rd_api_token'] = token.strip()
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return verify_rd_token(token)
    except Exception as e:
        return {"success": False, "error": str(e)}

def remove_rd_token() -> dict:
    save_rd_token("")
    return {"success": True, "message": "Real-Debrid bağlantısı kaldırıldı"}

def make_rd_request(endpoint: str, method: str = 'GET', data: dict = None, token: str = None) -> dict:
    if not token:
        token = get_rd_token()
    if not token:
        return {"success": False, "error": "Real-Debrid API token bulunamadı"}

    url = f"{RD_API_BASE}/{endpoint.lstrip('/')}"
    headers = {
        'Authorization': f'Bearer {token}',
        'User-Agent': 'MerVid-Studio/1.0.0'
    }

    try:
        encoded_data = None
        if data is not None:
            encoded_data = urllib.parse.urlencode(data).encode('utf-8')

        req = urllib.request.Request(url, data=encoded_data, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode('utf-8')
            return {"success": True, "data": json.loads(content) if content else {}}
    except urllib.error.HTTPError as e:
        error_body = ""
        try:
            error_body = e.read().decode('utf-8')
            err_json = json.loads(error_body)
            error_msg = err_json.get('error', str(e))
        except Exception:
            error_msg = f"HTTP {e.code}: {e.reason}"
        return {"success": False, "error": error_msg}
    except Exception as e:
        return {"success": False, "error": str(e)}

def verify_rd_token(token: str = None) -> dict:
    """Checks token validity and returns user premium status."""
    res = make_rd_request('/user', method='GET', token=token)
    if not res.get('success'):
        return {
            "has_token": False,
            "status": "Geçersiz",
            "message": res.get('error', 'Token doğrulanamadı'),
            "user": None
        }

    u = res.get('data', {})
    is_premium = u.get('type') == 'premium'
    expiration = u.get('expiration')
    
    exp_str = ""
    if expiration:
        try:
            dt = datetime.fromisoformat(expiration.replace('Z', '+00:00'))
            exp_str = dt.strftime('%d.%m.%Y')
        except Exception:
            exp_str = str(expiration)[:10]

    return {
        "has_token": True,
        "success": True,
        "is_premium": is_premium,
        "username": u.get('username'),
        "email": u.get('email'),
        "points": u.get('points', 0),
        "expiration": exp_str,
        "status": f"Premium Aktif ({exp_str})" if is_premium else "Ücretsiz Hesap (Kısıtlı)",
        "message": f"Kullanıcı: {u.get('username')} • Bitiş: {exp_str}" if is_premium else "Premium abonelik bulunamadı"
    }

def is_rd_supported_url(url: str) -> bool:
    """Checks if the URL is a magnet or belongs to known hosters."""
    url_lower = url.lower().strip()
    if url_lower.startswith('magnet:?'):
        return True
    return any(host in url_lower for host in RD_KNOWN_HOSTS)

def unrestrict_link(url: str, password: str = None) -> dict:
    """Unrestricts a file host link via Real-Debrid API and returns direct high-speed link."""
    payload = {'link': url.strip()}
    if password:
        payload['password'] = password
    
    res = make_rd_request('/unrestrict/link', method='POST', data=payload)
    if not res.get('success'):
        return {"success": False, "error": res.get('error', 'Link kilidi açılamadı')}

    d = res.get('data', {})
    filesize = d.get('filesize', 0)
    
    # Format filesize
    mb = filesize / (1024 * 1024)
    size_str = f"{mb / 1024:.2f} GB" if mb >= 1024 else f"{mb:.1f} MB"

    return {
        "success": True,
        "is_debrid": True,
        "id": d.get('id'),
        "title": d.get('filename', 'Dosya'),
        "download_url": d.get('download'),
        "direct_link": d.get('download'),
        "original_link": d.get('link'),
        "host": d.get('host', 'Debrid').upper(),
        "filesize": filesize,
        "filesize_formatted": size_str,
        "mime_type": d.get('mimeType'),
        "streamable": bool(d.get('streamable'))
    }

def unrestrict_magnet(magnet_url: str) -> dict:
    """Adds a magnet link to Real-Debrid, selects all files, and gets instant download links."""
    add_res = make_rd_request('/torrents/addMagnet', method='POST', data={'magnet': magnet_url.strip()})
    if not add_res.get('success'):
        return {"success": False, "error": add_res.get('error', 'Magnet eklenemedi')}

    torrent_id = add_res.get('data', {}).get('id')
    if not torrent_id:
        return {"success": False, "error": "Geçersiz torrent ID"}

    # Select all files
    make_rd_request(f'/torrents/selectFiles/{torrent_id}', method='POST', data={'files': 'all'})

    # Fetch torrent info
    info_res = make_rd_request(f'/torrents/info/{torrent_id}', method='GET')
    if not info_res.get('success'):
        return {"success": False, "error": "Torrent bilgisi alınamadı"}

    t_data = info_res.get('data', {})
    status = t_data.get('status')
    links = t_data.get('links', [])

    if status == 'downloaded' and links:
        # Torrent is cached on Real-Debrid! Instant high-speed direct download!
        first_link = links[0]
        unrestricted = unrestrict_link(first_link)
        if unrestricted.get('success'):
            unrestricted['title'] = t_data.get('filename') or unrestricted.get('title')
            unrestricted['host'] = 'TORRENT (INSTANT RD CACHE)'
            return unrestricted

    return {
        "success": False,
        "error": f"Torrent durumu: {status}. Anlık önbellekte bulunamadı veya indirilmesi gerekiyor."
    }
