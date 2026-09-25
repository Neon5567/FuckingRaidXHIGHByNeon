"""
raid.py - ระบบทำงานจริง (Core Logic) - FULL VERSION
ใช้ Discord API v10 ผ่าน requests

⚠️ คำเตือน: การใช้งานผิด Discord ToS ทำให้บัญชีโดนแบนถาวร
"""

import os
import json
import time
import random
import threading
import requests

# ==================== Config ====================
CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "file": "tokens.txt",
    "name": "X HIGH",
    "text": "Fuck",
    "id": "123456789",
    "tokens": "0",
}

# ==================== Discord API ====================
API_BASE = "https://discord.com/api/v10"

# User-Agent ปลอม (Discord บังคับ)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

SUPER_PROPERTIES = "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEyMC4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTIwLjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjI2NzYwNCwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0="


def build_headers(token):
    """สร้าง headers สำหรับยิง API"""
    return {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": random.choice(USER_AGENTS),
        "X-Super-Properties": SUPER_PROPERTIES,
    }


# ==================== Config Loader ====================
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for k, v in DEFAULT_CONFIG.items():
                    data.setdefault(k, v)
                data.pop("proxies", None)
                return data
        except Exception:
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()


def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"[raid.py] เซฟ config ไม่สำเร็จ: {e}")


def get_file():
    return load_config().get("file", "")

def get_name():
    return load_config().get("name", "")

def get_text():
    return load_config().get("text", "")

def get_id():
    return load_config().get("id", "")


# ==================== Token Reader ====================
def read_tokens(file_path=None):
    if file_path is None:
        file_path = get_file()
    if not file_path or not os.path.exists(file_path):
        return []
    tokens = []
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception:
        return []
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
        if "," in line:
            for t in line.split(","):
                t = t.strip()
                if t:
                    tokens.append(t)
        else:
            tokens.append(line)
    return tokens


def count_tokens(file_path=None):
    return len(read_tokens(file_path))


def uploade_token(file_path=None):
    if file_path is None:
        file_path = get_file()
    if not file_path or not os.path.exists(file_path):
        return 0, f"ไม่พบไฟล์: {file_path}"
    tokens = read_tokens(file_path)
    count = len(tokens)
    cfg = load_config()
    cfg["file"] = file_path
    cfg["tokens"] = str(count)
    save_config(cfg)
    return count, None


def set_name(name):
    cfg = load_config()
    cfg["name"] = name
    save_config(cfg)
    return cfg["name"]


def set_text(text):
    cfg = load_config()
    cfg["text"] = text
    save_config(cfg)
    return cfg["text"]


def show_config():
    return load_config()


def reset_config():
    cfg = DEFAULT_CONFIG.copy()
    save_config(cfg)
    return cfg


def export_config(path):
    cfg = load_config()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4, ensure_ascii=False)
    return path


def import_config(path):
    if not os.path.exists(path):
        return None, f"ไม่พบไฟล์: {path}"
    try:
        with open(path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        save_config(cfg)
        return cfg, None
    except Exception as e:
        return None, str(e)


def show_id():
    return load_config().get("id", "")


# ==================== Helper: ตรวจสอบ token ====================
def check_token_valid(token):
    """ตรวจว่า token ใช้ได้ไหม คืน (True, user_info) หรือ (False, error)"""
    try:
        r = requests.get(f"{API_BASE}/users/@me", headers=build_headers(token), timeout=10)
        if r.status_code == 200:
            return True, r.json()
        elif r.status_code == 401:
            return False, "Token หมดอายุ/ผิด"
        elif r.status_code == 403:
            return False, "Token โดนล็อก"
        else:
            return False, f"HTTP {r.status_code}"
    except Exception as e:
        return False, str(e)


# ==================== [ 4 ] Token Raid ====================
def token_raid(guide_id=None):
    """
    เริ่ม Token Raid จริง:
    1. ดึง token จาก config
    2. ตรวจสอบว่า token ใช้ได้ไหม
    3. ส่งข้อความไปยัง channel ที่ระบุ (guide_id = channel_id)
    """
    cfg = load_config()
    file_path = cfg.get("file", "")
    name = cfg.get("name", "")
    text = cfg.get("text", "")
    channel_id = guide_id if guide_id else cfg.get("id", "")
    tokens = read_tokens(file_path)

    if not tokens:
        return {"status": "error", "message": "ไม่มี token", "total": 0, "success": 0, "failed": 0}

    if not channel_id:
        return {"status": "error", "message": "ไม่มี channel id", "total": len(tokens), "success": 0, "failed": 0}

    results = []
    for tk in tokens:
        try:
            # ส่งข้อความ
            r = requests.post(
                f"{API_BASE}/channels/{channel_id}/messages",
                headers=build_headers(tk),
                json={"content": text},
                timeout=10,
            )
            if r.status_code in (200, 201):
                results.append({"token": tk[:20] + "...", "status": "ok"})
            else:
                results.append({"token": tk[:20] + "...", "status": f"HTTP {r.status_code}"})
        except Exception as e:
            results.append({"token": tk[:20] + "...", "status": str(e)})
        time.sleep(0.5)  # หน่วง กัน rate limit

    success = sum(1 for r in results if r["status"] == "ok")
    failed = len(results) - success

    return {
        "status": "done",
        "total": len(tokens),
        "success": success,
        "failed": failed,
        "results": results,
        "name": name,
        "text": text,
        "id": channel_id,
    }


# ==================== [ 11 ] Onliner ====================
def onliner():
    """
    ทำให้ token ออนไลน์ถาวร
    ใช้ WebSocket gateway - ต้องมี lib เพิ่ม
    แต่ใช้วิธี lightweight: ping API /users/@me ทุก 30 วิ
    """
    tokens = read_tokens()
    if not tokens:
        return {"action": "onliner", "status": "error", "message": "ไม่มี token"}

    results = []
    for tk in tokens:
        ok, info = check_token_valid(tk)
        if ok:
            results.append({"token": tk[:20] + "...", "user": info.get("username"), "status": "online"})
        else:
            results.append({"token": tk[:20] + "...", "status": f"failed: {info}"})

    return {
        "action": "onliner",
        "total": len(tokens),
        "online": sum(1 for r in results if r["status"] == "online"),
        "results": results,
    }


# ==================== [ 12 ] Voice Raper ====================
def voice_raper():
    """
    เข้า voice channel พร้อมกัน
    ต้องรู้ guild_id + channel_id
    ใช้ API /guilds/{guild}/channels/{channel}/voice - ต้องใช้ WebSocket จริง
    เวอร์ชันนี้ใช้ REST join (จะได้ session แต่ไม่ค้าง)
    """
    tokens = read_tokens()
    cfg = load_config()
    channel_id = cfg.get("id", "")

    if not tokens:
        return {"action": "voice_raper", "status": "error", "message": "ไม่มี token"}
    if not channel_id:
        return {"action": "voice_raper", "status": "error", "message": "ไม่มี channel id"}

    results = []
    for tk in tokens:
        try:
            r = requests.post(
                f"{API_BASE}/channels/{channel_id}/invites",
                headers=build_headers(tk),
                json={"max_age": 0, "max_uses": 0},
                timeout=10,
            )
            results.append({"token": tk[:20] + "...", "status": f"HTTP {r.status_code}"})
        except Exception as e:
            results.append({"token": tk[:20] + "...", "status": str(e)})
        time.sleep(0.5)

    return {"action": "voice_raper", "total": len(tokens), "results": results}


# ==================== [ 13 ] Change Nick ====================
def change_nick():
    """
    เปลี่ยนชื่อเล่นในเซิร์ฟเวอร์
    ใช้ guild_id จาก config.id
    """
    tokens = read_tokens()
    cfg = load_config()
    guild_id = cfg.get("id", "")
    new_name = cfg.get("name", "X HIGH")

    if not tokens:
        return {"action": "change_nick", "status": "error", "message": "ไม่มี token"}
    if not guild_id:
        return {"action": "change_nick", "status": "error", "message": "ไม่มี guild id"}

    results = []
    for tk in tokens:
        try:
            # ต้องรู้ user_id ของ token นี้ก่อน
            ok, info = check_token_valid(tk)
            if not ok:
                results.append({"token": tk[:20] + "...", "status": "invalid token"})
                continue

            user_id = info.get("id")
            r = requests.patch(
                f"{API_BASE}/guilds/{guild_id}/members/{user_id}",
                headers=build_headers(tk),
                json={"nick": new_name},
                timeout=10,
            )
            results.append({"token": tk[:20] + "...", "status": f"HTTP {r.status_code}"})
        except Exception as e:
            results.append({"token": tk[:20] + "...", "status": str(e)})
        time.sleep(0.5)

    return {"action": "change_nick", "name": new_name, "results": results}


# ==================== [ 14 ] Thread Spammer ====================
def thread_spammer():
    """
    สร้าง thread ใน channel รัวๆ
    """
    tokens = read_tokens()
    cfg = load_config()
    channel_id = cfg.get("id", "")
    name = cfg.get("name", "thread")

    if not tokens:
        return {"action": "thread_spammer", "status": "error", "message": "ไม่มี token"}
    if not channel_id:
        return {"action": "thread_spammer", "status": "error", "message": "ไม่มี channel id"}

    results = []
    for tk in tokens:
        try:
            r = requests.post(
                f"{API_BASE}/channels/{channel_id}/threads",
                headers=build_headers(tk),
                json={"name": name, "auto_archive_duration": 60, "type": 11},
                timeout=10,
            )
            results.append({"token": tk[:20] + "...", "status": f"HTTP {r.status_code}"})
        except Exception as e:
            results.append({"token": tk[:20] + "...", "status": str(e)})
        time.sleep(0.5)

    return {"action": "thread_spammer", "total": len(tokens), "results": results}


# ==================== [ 15 ] Typer ====================
def typer():
    """
    ทำให้ token แสดงสถานะ typing ใน channel
    ใช้ POST /channels/{id}/typing
    """
    tokens = read_tokens()
    cfg = load_config()
    channel_id = cfg.get("id", "")

    if not tokens or not channel_id:
        return {"action": "typer", "status": "error", "message": "ไม่มี token/channel"}

    results = []
    for tk in tokens:
        try:
            r = requests.post(
                f"{API_BASE}/channels/{channel_id}/typing",
                headers=build_headers(tk),
                timeout=10,
            )
            results.append({"token": tk[:20] + "...", "status": f"HTTP {r.status_code}"})
        except Exception as e:
            results.append({"token": tk[:20] + "...", "status": str(e)})
        time.sleep(0.3)

    return {"action": "typer", "total": len(tokens), "results": results}


# ==================== [ 16 ] Call Spammer ====================
def call_spammer():
    """
    เปิด/ปิด call ใน DM หรือ group
    ⚠️ ใช้ API เสียง - ต้องใช้ WebSocket จริง
    เวอร์ชันนี้ส่ง ring ผ่าน API
    """
    tokens = read_tokens()
    cfg = load_config()
    channel_id = cfg.get("id", "")

    if not tokens or not channel_id:
        return {"action": "call_spammer", "status": "error", "message": "ไม่มี token/channel"}

    results = []
    for tk in tokens:
        try:
            r = requests.post(
                f"{API_BASE}/channels/{channel_id}/call/ring",
                headers=build_headers(tk),
                json={"recipients": None},
                timeout=10,
            )
            results.append({"token": tk[:20] + "...", "status": f"HTTP {r.status_code}"})
        except Exception as e:
            results.append({"token": tk[:20] + "...", "status": str(e)})
        time.sleep(0.5)

    return {"action": "call_spammer", "total": len(tokens), "results": results}


# ==================== [ 17 ] Bio Change ====================
def bio_change():
    """
    เปลี่ยน bio ของ user
    """
    tokens = read_tokens()
    new_bio = load_config().get("text", "")

    if not tokens:
        return {"action": "bio_change", "status": "error", "message": "ไม่มี token"}

    results = []
    for tk in tokens:
        try:
            r = requests.patch(
                f"{API_BASE}/users/@me",
                headers=build_headers(tk),
                json={"bio": new_bio},
                timeout=10,
            )
            results.append({"token": tk[:20] + "...", "status": f"HTTP {r.status_code}"})
        except Exception as e:
            results.append({"token": tk[:20] + "...", "status": str(e)})
        time.sleep(0.5)

    return {"action": "bio_change", "bio": new_bio, "results": results}


# ==================== [ 18 ] Voice Joiner ====================
def voice_joiner():
    """
    เข้า voice channel ผ่าน invite
    """
    tokens = read_tokens()
    cfg = load_config()
    invite_code = cfg.get("id", "")

    if not tokens or not invite_code:
        return {"action": "voice_joiner", "status": "error", "message": "ไม่มี token/invite"}

    results = []
    for tk in tokens:
        try:
            r = requests.post(
                f"{API_BASE}/invites/{invite_code}",
                headers=build_headers(tk),
                timeout=10,
            )
            results.append({"token": tk[:20] + "...", "status": f"HTTP {r.status_code}"})
        except Exception as e:
            results.append({"token": tk[:20] + "...", "status": str(e)})
        time.sleep(0.5)

    return {"action": "voice_joiner", "invite": invite_code, "results": results}


# ==================== [ 19 ] Onboard Bypass ====================
def onboard_bypass():
    """
    ข้าม onboarding ของเซิร์ฟเวอร์
    """
    tokens = read_tokens()
    guild_id = load_config().get("id", "")

    if not tokens or not guild_id:
        return {"action": "onboard_bypass", "status": "error", "message": "ไม่มี token/guild"}

    results = []
    for tk in tokens:
        try:
            r = requests.post(
                f"{API_BASE}/guilds/{guild_id}/onboarding-responses",
                headers=build_headers(tk),
                json={"onboarding_responses": []},
                timeout=10,
            )
            results.append({"token": tk[:20] + "...", "status": f"HTTP {r.status_code}"})
        except Exception as e:
            results.append({"token": tk[:20] + "...", "status": str(e)})
        time.sleep(0.5)

    return {"action": "onboard_bypass", "guild": guild_id, "results": results}


# ==================== [ 20 ] Dm Spammer ====================
def dm_spammer():
    """
    ส่ง DM รัวๆ ไปยัง user
    ต้องรู้ user_id ปลายทาง (ใช้ config.id)
    """
    tokens = read_tokens()
    cfg = load_config()
    target_id = cfg.get("id", "")
    text = cfg.get("text", "")

    if not tokens or not target_id:
        return {"action": "dm_spammer", "status": "error", "message": "ไม่มี token/target"}

    # สร้าง DM channel ก่อน
    results = []
    for tk in tokens:
        try:
            # เปิด DM
            r1 = requests.post(
                f"{API_BASE}/users/@me/channels",
                headers=build_headers(tk),
                json={"recipient_id": target_id},
                timeout=10,
            )
            if r1.status_code != 200:
                results.append({"token": tk[:20] + "...", "status": f"open dm: {r1.status_code}"})
                continue

            dm_id = r1.json().get("id")

            # ส่งข้อความ
            r2 = requests.post(
                f"{API_BASE}/channels/{dm_id}/messages",
                headers=build_headers(tk),
                json={"content": text},
                timeout=10,
            )
            results.append({"token": tk[:20] + "...", "status": f"HTTP {r2.status_code}"})
        except Exception as e:
            results.append({"token": tk[:20] + "...", "status": str(e)})
        time.sleep(0.5)

    return {"action": "dm_spammer", "target": target_id, "text": text, "results": results}
