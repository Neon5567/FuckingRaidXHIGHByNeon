import os
import sys
import time
import json
import re
import shutil
import raid

# เปิด ANSI บน Windows
if os.name == 'nt':
    os.system('')

RESET = "\033[0m"

def rgb(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def term_width(default=100):
    try:
        return shutil.get_terminal_size((default, 30)).columns
    except Exception:
        return default

def visible_len(s):
    return len(re.sub(r'\033\[[0-9;]*m', '', s))

def center(text, width=None):
    if width is None:
        width = term_width()
    pad = max(0, (width - visible_len(text)) // 2)
    return " " * pad + text

def gradient_text(text, start=(120, 0, 0), end=(255, 40, 40)):
    if not text:
        return ""
    buf = ""
    n = len(text)
    for i, ch in enumerate(text):
        t = i / (n - 1) if n > 1 else 0
        r = int(start[0] + (end[0] - start[0]) * t)
        g = int(start[1] + (end[1] - start[1]) * t)
        b = int(start[2] + (end[2] - start[2]) * t)
        buf += rgb(r, g, b) + ch
    return buf + RESET

def gradient_block(lines, start=(120, 0, 0), end=(255, 40, 40)):
    if not lines:
        return []
    width = max(len(l) for l in lines)
    color_map = []
    for i in range(width):
        t = i / (width - 1) if width > 1 else 0
        r = int(start[0] + (end[0] - start[0]) * t)
        g = int(start[1] + (end[1] - start[1]) * t)
        b = int(start[2] + (end[2] - start[2]) * t)
        color_map.append(rgb(r, g, b))
    out = []
    for line in lines:
        buf = ""
        for i, ch in enumerate(line):
            buf += color_map[i] + ch
        buf += RESET
        out.append(buf)
    return out

def solid(text, r, g, b):
    return rgb(r, g, b) + text + RESET

ART = [
    "██╗  ██╗    ██╗  ██╗██╗ ██████╗ ██╗  ██╗",
    "╚██╗██╔╝    ██║  ██║██║██╔════╝ ██║  ██║",
    " ╚███╔╝     ███████║██║██║  ███╗███████║",
    " ██╔██╗     ██╔══██║██║██║   ██║██╔══██║",
    "██╔╝ ██╗    ██║  ██║██║╚██████╔╝██║  ██║",
    "╚═╝  ╚═╝    ╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝  ╚═╝",
]

NYA_ART = [
    "  [ Nya~ ]",
    "   /\\_/\\ ",
    "  ( o.o ) ",
    "   > ^ <  ",
]

MENU = [
    ("1",  "Uploade Token"),
    ("2",  "Set Name"),
    ("3",  "Set Text"),
    ("4",  "Token Raid"),
    ("5",  "Show Config"),
    ("6",  "Reset Config"),
    ("7",  "Export Config"),
    ("8",  "Import Config"),
    ("9",  "Check Token"),
    ("10", "Show ID"),
    ("11", "Onliner"),
    ("12", "Voice Raper"),
    ("13", "Change Nick"),
    ("14", "Thread Spammer"),
    ("15", "Typer"),
    ("16", "Call Spammer"),
    ("17", "Bio Change"),
    ("18", "Voice Joiner"),
    ("19", "Onboard Bypass"),
    ("20", "Dm Spammer"),
    ("21", "Exit"),
]

def render_menu_grid():
    rows = []
    cols = 4
    per_col = (len(MENU) + cols - 1) // cols
    for i in range(per_col):
        row_items = []
        for c in range(cols):
            idx = i + c * per_col
            if idx < len(MENU):
                key, label = MENU[idx]
                key_str = solid(f"[ {key} ]", 255, 80, 80)
                label_str = solid(label, 200, 200, 200)
                item = f"{key_str} {label_str}"
                row_items.append(item)
        rows.append(row_items)
    return rows

def render_menu_box():
    rows = render_menu_grid()
    col_widths = [0] * 4
    for row in rows:
        for i, item in enumerate(row):
            w = visible_len(item)
            if w > col_widths[i]:
                col_widths[i] = w
    padded_rows = []
    for row in rows:
        padded = []
        for i, item in enumerate(row):
            pad = col_widths[i] - visible_len(item)
            padded.append(item + " " * pad)
        padded_rows.append("  ".join(padded))
    inner_width = max(visible_len(r) for r in padded_rows) + 2
    red = lambda s: solid(s, 180, 0, 0)
    title_text = "X HIGH GANG By : Neon"
    title_colored = gradient_text(title_text, start=(180, 0, 0), end=(255, 60, 60))
    title_pad = max(0, (inner_width - len(title_text)) // 2)
    title_pad_right = max(0, inner_width - len(title_text) - title_pad)
    lines = []
    lines.append(red("╭" + "─" * inner_width + "╮"))
    lines.append(red("│") + " " * title_pad + title_colored + " " * title_pad_right + red("│"))
    lines.append(red("├" + "─" * inner_width + "┤"))
    for r in padded_rows:
        pad = inner_width - visible_len(r) - 1
        lines.append(red("│") + " " + r + " " * pad + red("│"))
    lines.append(red("╰" + "─" * inner_width + "╯"))
    return lines

def show_ui(cfg):
    clear()
    w = term_width()
    print()
    art_colored = gradient_block(ART, start=(120, 0, 0), end=(255, 40, 40))
    for line in art_colored:
        print(center(line, w))
    print()
    tokens = solid(f"<{cfg.get('tokens','0')}>", 255, 60, 60)
    status_left = solid("Loaded ", 180, 180, 180) + tokens + solid(" tokens", 180, 180, 180)
    nya_colored = [solid(l, 200, 50, 50) for l in NYA_ART]
    left_pad = max(0, (w - visible_len(status_left) - 20) // 2)
    print(" " * left_pad + status_left + "    " + nya_colored[0])
    for i in range(1, len(nya_colored)):
        print(" " * (left_pad + visible_len(status_left) + 4) + nya_colored[i])
    print()
    for l in render_menu_box():
        print(center(l, w))
    print()

def prompt(text):
    return input(gradient_text(text, start=(200, 0, 0), end=(255, 120, 120)))

def success(text):
    print(solid("  [+] ", 0, 220, 0) + solid(text, 220, 220, 220))

def error(text):
    print(solid("  [-] ", 255, 0, 0) + solid(text, 220, 220, 220))

def info(text):
    print(solid("  [i] ", 100, 180, 255) + solid(text, 220, 220, 220))

def wait(sec=1.2):
    time.sleep(sec)


def handle_result(r, title):
    """แสดงผลลัพธ์จาก raid.py ให้สวยงาม"""
    if not isinstance(r, dict):
        info(str(r))
        return
    if r.get("status") == "error":
        error(r.get("message", "ผิดพลาด"))
        return
    # แสดงสรุป
    parts = []
    for k in ("total", "success", "failed", "online", "invite", "guild", "name", "bio", "target"):
        if k in r and r[k] is not None:
            parts.append(f"{k}={r[k]}")
    if parts:
        success(" | ".join(parts))
    # แสดงตัวอย่าง 5 รายการแรก
    for x in r.get("results", [])[:5]:
        if isinstance(x, dict):
            tk = x.get("token", "")
            st = x.get("status", "")
            info(f"{tk} -> {st}")
        else:
            info(str(x))
    if len(r.get("results", [])) > 5:
        info(f"... และอีก {len(r['results']) - 5} รายการ")


def main():
    cfg = raid.load_config()
    file_path = cfg.get("file", "")
    if file_path and os.path.exists(file_path):
        count, err = raid.uploade_token(file_path)
        if not err:
            cfg = raid.load_config()

    while True:
        show_ui(cfg)
        choice = prompt("  > Choose : ").strip()

        # ==================== [ 1 ] ====================
        if choice == "1":
            print()
            print(solid("  --- [ 1 ] Uploade Token ---", 255, 60, 60))
            v = prompt("  Choose File : ").strip()
            if v:
                count, err = raid.uploade_token(v)
                if err:
                    error(err)
                else:
                    success(f"โหลดแล้ว: {v}")
                    info(f"พบ {count} token")
                cfg = raid.load_config()
            else:
                error("ไม่ได้กรอก")
            wait()

        # ==================== [ 2 ] ====================
        elif choice == "2":
            print()
            print(solid("  --- [ 2 ] Set Name ---", 255, 60, 60))
            v = prompt("  Name : ").strip()
            if v:
                raid.set_name(v)
                cfg = raid.load_config()
                success(f"ชื่อ: {cfg['name']}")
            else:
                error("ไม่ได้กรอก")
            wait()

        # ==================== [ 3 ] ====================
        elif choice == "3":
            print()
            print(solid("  --- [ 3 ] Set Text ---", 255, 60, 60))
            v = prompt("  Text : ").strip()
            if v:
                raid.set_text(v)
                cfg = raid.load_config()
                success(f"ข้อความ: {cfg['text']}")
            else:
                error("ไม่ได้กรอก")
            wait()

        # ==================== [ 4 ] ====================
        elif choice == "4":
            print()
            print(solid("  --- [ 4 ] Token Raid ---", 255, 60, 60))
            v = prompt("  Guide ID (Channel ID) : ").strip()
            r = raid.token_raid(v if v else None)
            handle_result(r, "Token Raid")
            wait(2)

        # ==================== [ 5 ] ====================
        elif choice == "5":
            print()
            print(solid("  --- [ 5 ] Current Config ---", 255, 60, 60))
            for k, v in raid.show_config().items():
                print(solid(f"  {k:<10}", 255, 100, 100) + solid(f": {v}", 220, 220, 220))
            print()
            prompt("  กด Enter...")

        # ==================== [ 6 ] ====================
        elif choice == "6":
            print()
            print(solid("  --- [ 6 ] Reset Config ---", 255, 60, 60))
            raid.reset_config()
            cfg = raid.load_config()
            success("รีเซ็ต config แล้ว")
            wait()

        # ==================== [ 7 ] ====================
        elif choice == "7":
            print()
            print(solid("  --- [ 7 ] Export Config ---", 255, 60, 60))
            v = prompt("  Save as : ").strip()
            if v:
                try:
                    raid.export_config(v)
                    success(f"บันทึกเป็น: {v}")
                except Exception as e:
                    error(f"ผิดพลาด: {e}")
            else:
                error("ไม่ได้กรอก")
            wait()

        # ==================== [ 8 ] ====================
        elif choice == "8":
            print()
            print(solid("  --- [ 8 ] Import Config ---", 255, 60, 60))
            v = prompt("  Load from : ").strip()
            result, err = raid.import_config(v)
            if err:
                error(err)
            else:
                cfg = raid.load_config()
                success(f"โหลดจาก: {v}")
            wait()

        # ==================== [ 9 ] ====================
        elif choice == "9":
            print()
            print(solid("  --- [ 9 ] Check Token ---", 255, 60, 60))
            count = raid.count_tokens()
            if count == 0:
                error("ไม่พบ token หรือไฟล์หาย")
            else:
                success(f"พบ {count} token")
            cfg = raid.load_config()
            wait(2)

        # ==================== [ 10 ] ====================
        elif choice == "10":
            print()
            print(solid("  --- [ 10 ] Show ID ---", 255, 60, 60))
            print(solid(f"  Guide ID : {raid.show_id()}", 220, 220, 220))
            print()
            prompt("  กด Enter...")

        # ==================== [ 11 ] Onliner ====================
        elif choice == "11":
            print()
            print(solid("  --- [ 11 ] Onliner ---", 255, 60, 60))
            r = raid.onliner()
            handle_result(r, "Onliner")
            wait(2)

        # ==================== [ 12 ] Voice Raper ====================
        elif choice == "12":
            print()
            print(solid("  --- [ 12 ] Voice Raper ---", 255, 60, 60))
            r = raid.voice_raper()
            handle_result(r, "Voice Raper")
            wait(2)

        # ==================== [ 13 ] Change Nick ====================
        elif choice == "13":
            print()
            print(solid("  --- [ 13 ] Change Nick ---", 255, 60, 60))
            r = raid.change_nick()
            handle_result(r, "Change Nick")
            wait(2)

        # ==================== [ 14 ] Thread Spammer ====================
        elif choice == "14":
            print()
            print(solid("  --- [ 14 ] Thread Spammer ---", 255, 60, 60))
            r = raid.thread_spammer()
            handle_result(r, "Thread Spammer")
            wait(2)

        # ==================== [ 15 ] Typer ====================
        elif choice == "15":
            print()
            print(solid("  --- [ 15 ] Typer ---", 255, 60, 60))
            r = raid.typer()
            handle_result(r, "Typer")
            wait(2)

        # ==================== [ 16 ] Call Spammer ====================
        elif choice == "16":
            print()
            print(solid("  --- [ 16 ] Call Spammer ---", 255, 60, 60))
            r = raid.call_spammer()
            handle_result(r, "Call Spammer")
            wait(2)

        # ==================== [ 17 ] Bio Change ====================
        elif choice == "17":
            print()
            print(solid("  --- [ 17 ] Bio Change ---", 255, 60, 60))
            r = raid.bio_change()
            handle_result(r, "Bio Change")
            wait(2)

        # ==================== [ 18 ] Voice Joiner ====================
        elif choice == "18":
            print()
            print(solid("  --- [ 18 ] Voice Joiner ---", 255, 60, 60))
            r = raid.voice_joiner()
            handle_result(r, "Voice Joiner")
            wait(2)

        # ==================== [ 19 ] Onboard Bypass ====================
        elif choice == "19":
            print()
            print(solid("  --- [ 19 ] Onboard Bypass ---", 255, 60, 60))
            r = raid.onboard_bypass()
            handle_result(r, "Onboard Bypass")
            wait(2)

        # ==================== [ 20 ] Dm Spammer ====================
        elif choice == "20":
            print()
            print(solid("  --- [ 20 ] Dm Spammer ---", 255, 60, 60))
            r = raid.dm_spammer()
            handle_result(r, "Dm Spammer")
            wait(2)

        # ==================== [ 21 ] Exit ====================
        elif choice == "21":
            print()
            print(solid("  ปิดโปรแกรม...", 255, 80, 80))
            wait(0.8)
            break

        # ==================== Default ====================
        else:
            error("ยังไม่ได้ทำ หรือพิมพ์ผิด")
            wait()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print(solid("\n  ปิดโปรแกรม", 255, 80, 80))
        sys.exit(0)
