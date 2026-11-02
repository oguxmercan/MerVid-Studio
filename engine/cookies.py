import os
import sys
import re
from datetime import datetime

def get_app_dir():
    """Returns local app data directory for storing configs and cookies."""
    app_dir = os.path.join(os.path.expanduser('~'), '.mervid_studio')
    os.makedirs(app_dir, exist_ok=True)
    return app_dir

def get_cookie_file_path():
    return os.path.join(get_app_dir(), 'cookies.txt')

def save_cookie_text(content: str) -> dict:
    """Saves Netscape cookie text into the Cookie Vault file."""
    try:
        path = get_cookie_file_path()
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content.strip() + '\n')
        return {"success": True, "message": "Cookies saved successfully", "info": get_cookie_status()}
    except Exception as e:
        return {"success": False, "error": str(e)}

def save_cookie_file(source_path: str) -> dict:
    """Copies user-selected cookies.txt file into the Cookie Vault."""
    try:
        if not os.path.isfile(source_path):
            return {"success": False, "error": "Selected file does not exist"}
        with open(source_path, 'r', encoding='utf-8', errors='ignore') as src:
            content = src.read()
        return save_cookie_text(content)
    except Exception as e:
        return {"success": False, "error": str(e)}

def clear_cookie() -> dict:
    """Removes the saved cookie file."""
    path = get_cookie_file_path()
    if os.path.isfile(path):
        try:
            os.remove(path)
            return {"success": True, "message": "Cookie vault cleared"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    return {"success": True, "message": "No cookies to clear"}

def get_cookie_status() -> dict:
    """Analyzes the current cookies.txt and returns status."""
    path = get_cookie_file_path()
    if not os.path.isfile(path) or os.path.getsize(path) == 0:
        return {
            "has_cookie": False,
            "status": "Inactive",
            "message": "No cookies loaded. Import cookies.txt for private or member-only videos.",
            "domains": [],
            "count": 0,
            "file_path": None
        }

    domains = set()
    count = 0
    now = datetime.now().timestamp()
    has_valid_expiry = False
    latest_expiry = 0

    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') and not line.startswith('#HttpOnly_'):
                    continue
                parts = re.split(r'\t+|\s+', line)
                if len(parts) >= 7:
                    count += 1
                    domain = parts[0].replace('#HttpOnly_', '')
                    domains.add(domain)
                    try:
                        exp = float(parts[4])
                        if exp > latest_expiry:
                            latest_expiry = exp
                        if exp > now:
                            has_valid_expiry = True
                    except (ValueError, IndexError):
                        pass

        exp_str = ""
        if latest_expiry > 0:
            exp_date = datetime.fromtimestamp(latest_expiry)
            if latest_expiry > now:
                exp_str = f"Active until {exp_date.strftime('%d %b %Y')}"
            else:
                exp_str = f"Expired on {exp_date.strftime('%d %b %Y')}"
        else:
            exp_str = "Session active"

        return {
            "has_cookie": True,
            "status": "Active" if (has_valid_expiry or latest_expiry == 0) else "Expired",
            "message": exp_str,
            "domains": sorted(list(domains))[:10],
            "total_domains": len(domains),
            "count": count,
            "file_path": path
        }
    except Exception as e:
        return {
            "has_cookie": True,
            "status": "Error",
            "message": f"Error parsing cookies: {str(e)}",
            "domains": [],
            "count": 0,
            "file_path": path
        }
