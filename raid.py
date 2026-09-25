"""
raid.py - ระบบทำงานจริง (Core Logic)
รับ Token แบบตรงๆ (manual input) ไม่ต้องใช้ไฟล์
"""

import os
import json
import time
import random
import requests

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "name": "X HIGH",
    "text": "Fuck",
    "id": "123456789",
    "tokens": [],       # เก็บ token เป็น list
}

API_BASE = "https://discord.com/api/v10"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

SUPER_PROPERTIES = "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEyMC4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTIwLjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjI2NzYwNCwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0="


def build_headers(token):
    return {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": random.choice(USER_AGENTS),
        "X-Super-Properties": SUPER_PROPERTIES,
    }


# ==================== Config ====================
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for k, v in DEFAULT_CONFIG.items():
                    data.setdefault(k, v)
                # ถ้า tokens เก่าเป็น string ให้แปลง
                if isinstance(data.get("tokens"), str):
                    data["tokens"] = []
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


# ==================== Get / Set ====================
def get_name():
    return load_config().get("name", "")


def get_text():
    return load_config().get("text", "")


def get_id():
    return load_config().get("id", "")


def get_tokens():
    """คืน list ของ token"""
    return load_config().get("tokens", [])


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


def set_id(gid):
    cfg = load_config()
    cfg["id"] = gid
    save_config(cfg)
    return cfg["id"]


# ==================== Token Management ====================
def add_token(token):
    """เพิ่ม token (ทีละตัว)"""
    cfg = load_config()
    tokens = cfg.get("tokens", [])
    if token in tokens:
        return False, "token นี้มีอยู่แล้ว"
    tokens.append(token)
    cfg["tokens"] = tokens
    save_config(cfg)
    return True, len(tokens)


def add_tokens_bulk(text):
    """
    เพิ่ม token หลายตัวจาก text
    รองรับ , และ ขึ้นบรรทัดใหม่
    """
    cfg = load_config()
    tokens = cfg.get("tokens", [])
    added = 0
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(",") if "," in line else [line]
        for t in parts:
            t = t.strip()
            if t and t not in tokens:
                tokens.append(t)
                added += 1
    cfg["tokens"] = tokens
    save_config(cfg)
    return added, len(tokens)


def remove_token(token):
    cfg = load_config()
    tokens = cfg.get("tokens", [])
    if token in tokens:
        tokens.remove(token)
        cfg["tokens"] = tokens
        save_config(cfg)
        return True, len(tokens)
    return False, len(tokens)


def clear_tokens():
    cfg = load_config()
    cfg["tokens"] = []
    save_config(cfg)
    return 0


def count_tokens():
    return len(get_tokens())


def list_tokens():
    return get_tokens()


# ==================== ตรวจสอบ token ====================
def check_token_valid(token):
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
    cfg = load_config()
    name = cfg.get("name", "")
    text = cfg.get("text", "")
    channel_id = guide_id if guide_id else cfg.get("id", "")
    tokens = cfg.get("tokens", [])

    if not tokens:
        return {"status": "error", "message": "ไม่มี token", "total": 0, "success": 0, "failed": 0}

    if not channel_id:
        return {"status": "error", "message": "ไม่มี channel id", "total": len(tokens), "success": 0, "failed": 0}

    results = []
    for tk in tokens:
        try:
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
        time.sleep(0.5)

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
    tokens = get_tokens()
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
    tokens = get_tokens()
    channel_id = get_id()
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
    tokens = get_tokens()
    guild_id = get_id()
    new_name = get_name()
    if not tokens:
        return {"action": "change_nick", "status": "error", "message": "ไม่มี token"}
    if not guild_id:
        return {"action": "change_nick", "status": "error", "message": "ไม่มี guild id"}

    results = []
    for tk in tokens:
        try:
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
    tokens = get_tokens()
    channel_id = get_id()
    name = get_name()
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
    tokens = get_tokens()
    channel_id = get_id()
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
    tokens = get_tokens()
    channel_id = get_id()
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
    tokens = get_tokens()
    new_bio = get_text()
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
    tokens = get_tokens()
    invite_code = get_id()
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
    tokens = get_tokens()
    guild_id = get_id()
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
    tokens = get_tokens()
    target_id = get_id()
    text = get_text()
    if not tokens or not target_id:
        return {"action": "dm_spammer", "status": "error", "message": "ไม่มี token/target"}

    results = []
    for tk in tokens:
        try:
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
