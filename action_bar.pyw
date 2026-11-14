"""螢幕快捷鍵列。

預設貼在滑鼠所在螢幕的上緣，半透明，內建常用 Windows 快捷鍵。
左鍵送出快捷鍵。Ctrl+Alt+Shift+H 顯示或隱藏。
拖 ≡ 可放到任意位置。按「鼠」會改到游標右邊直排，右邊放不下就改到左邊。
按「上」貼回螢幕上緣。工具列上的群組名稱可切換應用程式。
按「選」管理快捷鍵。一般群組列出全部快捷鍵。同一組合在不同群組可以有不同名稱。
頁籤「已勾選」只列出有打勾的鍵。可儲存或載入目前的勾選。勾選後立刻套用。
按 — 縮到工作列旁的小圖示。按 × 結束程式。按齒輪可開關左鍵連點貼上、右鍵連點複製。
快捷列最上方第一列是 PgUp、PgDn、Home、End、上、下，第二列是 Bksp、Del、Tab、Enter、左、右。滑鼠停在常用鍵上時，名稱以黑底白字顯示，直到滑鼠離開。

快捷鍵寫法：ctrl+c、win+shift+s、ctrl+alt+shift+h。只含減號時也可寫 ctrl-c。
"""

from __future__ import annotations

import json
import math
import os
import sys
import time
import traceback
import uuid
import ctypes
from ctypes import wintypes
from pathlib import Path


def enable_dpi() -> None:
    try:
        shcore = ctypes.WinDLL("shcore", use_last_error=True)
        shcore.SetProcessDpiAwareness.argtypes = [ctypes.c_int]
        shcore.SetProcessDpiAwareness.restype = ctypes.HRESULT
        shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


enable_dpi()

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk


APP_DIR = Path(__file__).resolve().parent
CONFIG_PATH = APP_DIR / "config.json"
SHORTCUTS_PATH = APP_DIR / "shortcuts.json"
LOG_PATH = APP_DIR / "error.log"
MUTEX_NAME = "Local\\TopActionBar.SingleInstance"

BAR = "#1b1c20"
BORDER = "#8ab4f8"
BTN = "#3c4048"
TOOL = "#2c2f36"
TEXT = "#f8f9fa"
HINT = "#d0d3d8"
PRESS = "#1a73e8"
BAD = "#c5221f"
FONT = ("Microsoft JhengHei UI", 10, "bold")
FONT_HINT = ("Microsoft JhengHei UI", 8)
FONT_TOOL = ("Segoe UI Symbol", 12)
FONT_UI = ("Microsoft JhengHei UI", 10)

MOD_ORDER = ("win", "ctrl", "alt", "shift")
MOD_VK = {"win": 0x5B, "ctrl": 0x11, "alt": 0x12, "shift": 0x10}
MOD_FLAG = {"alt": 0x0001, "ctrl": 0x0002, "shift": 0x0004, "win": 0x0008}
HOTKEY_ID = 1

WM_MOUSEACTIVATE = 0x0021
WM_HOTKEY = 0x0312
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
WM_LBUTTONDBLCLK = 0x0203
WM_MOUSEMOVE = 0x0200
WM_RBUTTONDOWN = 0x0204
WM_RBUTTONUP = 0x0205
WM_TIMER = 0x0113
TIMER_RIGHT_CLICK = 2
INPUT_MOUSE = 0
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_VIRTUALDESK = 0x4000
RIGHT_MARK = 0x52434C4B
SM_XVIRTUALSCREEN = 76
SM_YVIRTUALSCREEN = 77
SM_CXVIRTUALSCREEN = 78
SM_CYVIRTUALSCREEN = 79
WM_COPY = 0x0301
WM_CANCELMODE = 0x001F
WM_CLOSE = 0x0010
WM_APP_DBL = 0x8002
WH_MOUSE_LL = 14
LLMHF_INJECTED = 0x00000001
SM_CXDOUBLECLK = 36
SM_CYDOUBLECLK = 37
SMTO_ABORTIFHUNG = 0x0002
GA_ROOT = 2
WM_CONTEXTMENU = 0x007B
WM_TRAY = 0x8001
NIM_ADD = 0
NIM_DELETE = 2
NIM_SETVERSION = 4
NIF_MESSAGE = 0x01
NIF_ICON = 0x02
NIF_TIP = 0x04
NIF_SHOWTIP = 0x80
NIN_SELECT = 0x0400
MA_NOACTIVATE = 3
GWL_EXSTYLE = -20
GWLP_WNDPROC = -4
WS_EX_NOACTIVATE = 0x08000000
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_TRANSPARENT = 0x00000020
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_NOACTIVATE = 0x0010
SWP_SHOWWINDOW = 0x0040
SWP_FRAMECHANGED = 0x0020
HWND_TOPMOST = -1
INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_EXTENDEDKEY = 0x0001
MAPVK_VK_TO_VSC_EX = 4
GW_OWNER = 4
ERROR_ALREADY_EXISTS = 183
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
TOKEN_QUERY = 0x0008
TOKEN_ELEVATION = 20

user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)
shell32 = ctypes.WinDLL("shell32", use_last_error=True)

ULONG_PTR = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong
LRESULT = ctypes.c_ssize_t
WNDPROC = ctypes.WINFUNCTYPE(LRESULT, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)
HOOKPROC = ctypes.WINFUNCTYPE(LRESULT, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)
WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
MUTEX_HANDLE: wintypes.HANDLE | None = None

# id, group, label, hotkey. 預設全部出現，可在「選」裡關掉。
CATALOG: tuple[tuple[str, str, str, str], ...] = (
    ("copy", "編輯", "複製", "ctrl+c"),
    ("paste", "編輯", "貼上", "ctrl+v"),
    ("cut", "編輯", "剪下", "ctrl+x"),
    ("undo", "編輯", "復原", "ctrl+z"),
    ("redo", "編輯", "重做", "ctrl+y"),
    ("selectall", "編輯", "全選", "ctrl+a"),
    ("save", "編輯", "存檔", "ctrl+s"),
    ("find", "編輯", "尋找", "ctrl+f"),
    ("replace", "編輯", "取代", "ctrl+h"),
    ("print", "編輯", "列印", "ctrl+p"),
    ("bold", "編輯", "粗體", "ctrl+b"),
    ("italic", "編輯", "斜體", "ctrl+i"),
    ("underline", "編輯", "底線", "ctrl+u"),
    ("rename", "檔案總管", "重新命名", "f2"),
    ("delete", "檔案總管", "刪除", "delete"),
    ("delete-perm", "檔案總管", "永久刪除", "shift+delete"),
    ("properties", "檔案總管", "內容", "alt+enter"),
    ("context", "檔案總管", "右鍵選單", "shift+f10"),
    ("up", "檔案總管", "上一層", "alt+up"),
    ("back", "檔案總管", "返回", "alt+left"),
    ("forward", "檔案總管", "向前", "alt+right"),
    ("refresh", "檔案總管", "重新整理", "f5"),
    ("new-folder", "檔案總管", "新增資料夾", "ctrl+shift+n"),
    ("address", "檔案總管", "位址列", "alt+d"),
    ("close", "視窗", "關閉視窗", "alt+f4"),
    ("switch", "視窗", "切換視窗", "alt+tab"),
    ("switch-back", "視窗", "反向切換", "alt+shift+tab"),
    ("cycle", "視窗", "循環視窗", "alt+esc"),
    ("maximize", "視窗", "最大化", "win+up"),
    ("restore", "視窗", "還原", "win+down"),
    ("snap-left", "視窗", "靠左", "win+left"),
    ("snap-right", "視窗", "靠右", "win+right"),
    ("taskview", "視窗", "工作檢視", "win+tab"),
    ("desktop", "視窗", "顯示桌面", "win+d"),
    ("min-all", "視窗", "全部縮小", "win+m"),
    ("restore-all", "視窗", "還原縮小", "win+shift+m"),
    ("close-tab", "視窗", "關閉分頁", "ctrl+w"),
    ("close-doc", "視窗", "關閉文件", "ctrl+f4"),
    ("new-tab", "視窗", "新分頁", "ctrl+t"),
    ("reopen-tab", "視窗", "重開分頁", "ctrl+shift+t"),
    ("fullscreen", "視窗", "全螢幕", "f11"),
    ("window-menu", "視窗", "視窗選單", "alt+space"),
    ("help", "視窗", "說明", "f1"),
    ("lock", "系統", "鎖定", "win+l"),
    ("run", "系統", "執行", "win+r"),
    ("settings", "系統", "設定", "win+i"),
    ("explorer", "系統", "檔案總管", "win+e"),
    ("search", "系統", "搜尋", "win+s"),
    ("quick", "系統", "快速設定", "win+a"),
    ("notify", "系統", "通知", "win+n"),
    ("widgets", "系統", "小工具", "win+w"),
    ("clipboard", "系統", "剪貼簿", "win+v"),
    ("emoji", "系統", "表情", "win+."),
    ("snip", "系統", "截圖", "win+shift+s"),
    ("shot", "系統", "整張截圖", "printscreen"),
    ("shot-win", "系統", "視窗截圖", "alt+printscreen"),
    ("shot-f5", "系統", "擷圖", "ctrl+f5"),
    ("project", "系統", "投影", "win+p"),
    ("voice", "系統", "語音輸入", "win+h"),
    ("zoom-in", "系統", "放大鏡", "win+plus"),
    ("zoom-out", "系統", "縮小鏡", "win+minus"),
    ("taskmgr", "系統", "工作管理員", "ctrl+shift+esc"),
    ("lang", "系統", "切換輸入法", "win+space"),
    ("gamebar", "系統", "遊戲列", "win+g"),
    ("record", "系統", "錄製", "win+alt+r"),
    ("desk-new", "虛擬桌面", "新增桌面", "win+ctrl+d"),
    ("desk-close", "虛擬桌面", "關閉桌面", "win+ctrl+f4"),
    ("desk-left", "虛擬桌面", "左邊桌面", "win+ctrl+left"),
    ("desk-right", "虛擬桌面", "右邊桌面", "win+ctrl+right"),
    ("url", "瀏覽器", "網址列", "ctrl+l"),
    ("tab-next", "瀏覽器", "下一分頁", "ctrl+tab"),
    ("tab-prev", "瀏覽器", "上一分頁", "ctrl+shift+tab"),
    ("hard-refresh", "瀏覽器", "強制重新整理", "ctrl+f5"),
    ("page-in", "瀏覽器", "頁面放大", "ctrl+plus"),
    ("page-out", "瀏覽器", "頁面縮小", "ctrl+minus"),
    ("page-100", "瀏覽器", "實際大小", "ctrl+0"),
    ("play", "媒體", "播放", "playpause"),
    ("next-track", "媒體", "下一首", "nexttrack"),
    ("prev-track", "媒體", "上一首", "prevtrack"),
    ("stop", "媒體", "停止", "mediastop"),
    ("vol-up", "媒體", "音量加", "volumeup"),
    ("vol-down", "媒體", "音量減", "volumedown"),
    ("mute", "媒體", "靜音", "volumemute"),
)
CATALOG_IDS = {item[0] for item in CATALOG}


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long),
    ]


class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("pt", POINT),
        ("mouseData", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class GUITHREADINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("hwndActive", wintypes.HWND),
        ("hwndFocus", wintypes.HWND),
        ("hwndCapture", wintypes.HWND),
        ("hwndMenuOwner", wintypes.HWND),
        ("hwndMoveSize", wintypes.HWND),
        ("hwndCaret", wintypes.HWND),
        ("rcCaret", RECT),
    ]


class MONITORINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("rcMonitor", RECT),
        ("rcWork", RECT),
        ("dwFlags", wintypes.DWORD),
    ]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    ]


class GUID(ctypes.Structure):
    _fields_ = [
        ("Data1", wintypes.DWORD),
        ("Data2", wintypes.WORD),
        ("Data3", wintypes.WORD),
        ("Data4", wintypes.BYTE * 8),
    ]


class ICONINFO(ctypes.Structure):
    _fields_ = [
        ("fIcon", wintypes.BOOL),
        ("xHotspot", wintypes.DWORD),
        ("yHotspot", wintypes.DWORD),
        ("hbmMask", wintypes.HBITMAP),
        ("hbmColor", wintypes.HBITMAP),
    ]


class NOTIFYICONDATAW(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("hWnd", wintypes.HWND),
        ("uID", wintypes.UINT),
        ("uFlags", wintypes.UINT),
        ("uCallbackMessage", wintypes.UINT),
        ("hIcon", wintypes.HICON),
        ("szTip", wintypes.WCHAR * 128),
        ("dwState", wintypes.DWORD),
        ("dwStateMask", wintypes.DWORD),
        ("szInfo", wintypes.WCHAR * 256),
        ("uVersion", wintypes.UINT),
        ("szInfoTitle", wintypes.WCHAR * 64),
        ("dwInfoFlags", wintypes.DWORD),
        ("guidItem", GUID),
        ("hBalloonIcon", wintypes.HICON),
    ]


class INPUT(ctypes.Structure):
    class _U(ctypes.Union):
        _fields_ = [("ki", KEYBDINPUT), ("mi", MOUSEINPUT), ("hi", HARDWAREINPUT)]

    _anonymous_ = ("u",)
    _fields_ = [("type", wintypes.DWORD), ("u", _U)]


def setup_win32() -> None:
    user32.GetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int]
    user32.GetWindowLongW.restype = ctypes.c_long
    user32.SetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_long]
    user32.SetWindowLongW.restype = ctypes.c_long
    user32.GetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int]
    user32.GetWindowLongPtrW.restype = ctypes.c_void_p
    user32.SetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_void_p]
    user32.SetWindowLongPtrW.restype = ctypes.c_void_p
    user32.CallWindowProcW.argtypes = [
        ctypes.c_void_p,
        wintypes.HWND,
        wintypes.UINT,
        wintypes.WPARAM,
        wintypes.LPARAM,
    ]
    user32.CallWindowProcW.restype = LRESULT
    user32.SetWindowPos.argtypes = [
        wintypes.HWND,
        wintypes.HWND,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        wintypes.UINT,
    ]
    user32.SetWindowPos.restype = wintypes.BOOL
    user32.SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int]
    user32.SendInput.restype = wintypes.UINT
    user32.MapVirtualKeyW.argtypes = [wintypes.UINT, wintypes.UINT]
    user32.MapVirtualKeyW.restype = wintypes.UINT
    user32.GetAsyncKeyState.argtypes = [ctypes.c_int]
    user32.GetAsyncKeyState.restype = wintypes.SHORT
    user32.GetForegroundWindow.restype = wintypes.HWND
    user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
    user32.GetWindowThreadProcessId.restype = wintypes.DWORD
    user32.AttachThreadInput.argtypes = [wintypes.DWORD, wintypes.DWORD, wintypes.BOOL]
    user32.AttachThreadInput.restype = wintypes.BOOL
    user32.SetForegroundWindow.argtypes = [wintypes.HWND]
    user32.SetForegroundWindow.restype = wintypes.BOOL
    user32.BringWindowToTop.argtypes = [wintypes.HWND]
    user32.BringWindowToTop.restype = wintypes.BOOL
    user32.RegisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int, wintypes.UINT, wintypes.UINT]
    user32.RegisterHotKey.restype = wintypes.BOOL
    user32.UnregisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int]
    user32.UnregisterHotKey.restype = wintypes.BOOL
    user32.GetCursorPos.argtypes = [ctypes.POINTER(POINT)]
    user32.GetCursorPos.restype = wintypes.BOOL
    user32.MonitorFromPoint.argtypes = [POINT, wintypes.DWORD]
    user32.MonitorFromPoint.restype = ctypes.c_void_p
    user32.GetMonitorInfoW.argtypes = [ctypes.c_void_p, ctypes.POINTER(MONITORINFO)]
    user32.GetMonitorInfoW.restype = wintypes.BOOL
    user32.GetParent.argtypes = [wintypes.HWND]
    user32.GetParent.restype = wintypes.HWND
    user32.GetAncestor.argtypes = [wintypes.HWND, wintypes.UINT]
    user32.GetAncestor.restype = wintypes.HWND
    user32.GetWindow.argtypes = [wintypes.HWND, wintypes.UINT]
    user32.GetWindow.restype = wintypes.HWND
    user32.GetSystemMetrics.argtypes = [ctypes.c_int]
    user32.GetSystemMetrics.restype = ctypes.c_int
    kernel32.CreateMutexW.argtypes = [ctypes.c_void_p, wintypes.BOOL, wintypes.LPCWSTR]
    kernel32.CreateMutexW.restype = wintypes.HANDLE
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL
    kernel32.GetCurrentThreadId.restype = wintypes.DWORD
    kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel32.OpenProcess.restype = wintypes.HANDLE
    kernel32.GetCurrentProcess.restype = wintypes.HANDLE
    advapi32.OpenProcessToken.argtypes = [wintypes.HANDLE, wintypes.DWORD, ctypes.POINTER(wintypes.HANDLE)]
    advapi32.OpenProcessToken.restype = wintypes.BOOL
    advapi32.GetTokenInformation.argtypes = [
        wintypes.HANDLE,
        ctypes.c_int,
        ctypes.c_void_p,
        wintypes.DWORD,
        ctypes.POINTER(wintypes.DWORD),
    ]
    advapi32.GetTokenInformation.restype = wintypes.BOOL
    shell32.Shell_NotifyIconW.argtypes = [wintypes.DWORD, ctypes.POINTER(NOTIFYICONDATAW)]
    shell32.Shell_NotifyIconW.restype = wintypes.BOOL
    user32.LoadIconW.argtypes = [wintypes.HINSTANCE, wintypes.LPCWSTR]
    user32.LoadIconW.restype = wintypes.HICON
    user32.SetWindowsHookExW.argtypes = [ctypes.c_int, HOOKPROC, wintypes.HINSTANCE, wintypes.DWORD]
    user32.SetWindowsHookExW.restype = ctypes.c_void_p
    user32.UnhookWindowsHookEx.argtypes = [ctypes.c_void_p]
    user32.UnhookWindowsHookEx.restype = wintypes.BOOL
    user32.CallNextHookEx.argtypes = [ctypes.c_void_p, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM]
    user32.CallNextHookEx.restype = LRESULT
    user32.GetDoubleClickTime.restype = wintypes.UINT
    user32.WindowFromPoint.argtypes = [POINT]
    user32.WindowFromPoint.restype = wintypes.HWND
    user32.GetGUIThreadInfo.argtypes = [wintypes.DWORD, ctypes.POINTER(GUITHREADINFO)]
    user32.GetGUIThreadInfo.restype = wintypes.BOOL
    user32.SendMessageTimeoutW.argtypes = [
        wintypes.HWND,
        wintypes.UINT,
        wintypes.WPARAM,
        wintypes.LPARAM,
        wintypes.UINT,
        wintypes.UINT,
        ctypes.POINTER(ctypes.c_size_t),
    ]
    user32.SendMessageTimeoutW.restype = ctypes.c_void_p
    user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
    user32.PostMessageW.restype = wintypes.BOOL
    user32.FindWindowW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
    user32.FindWindowW.restype = wintypes.HWND
    user32.SetFocus.argtypes = [wintypes.HWND]
    user32.SetFocus.restype = wintypes.HWND
    user32.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    user32.GetClassNameW.restype = ctypes.c_int
    user32.EnumWindows.argtypes = [WNDENUMPROC, wintypes.LPARAM]
    user32.EnumWindows.restype = wintypes.BOOL
    user32.IsWindow.argtypes = [wintypes.HWND]
    user32.IsWindow.restype = wintypes.BOOL
    user32.SetTimer.argtypes = [wintypes.HWND, ULONG_PTR, wintypes.UINT, ctypes.c_void_p]
    user32.SetTimer.restype = ULONG_PTR
    user32.KillTimer.argtypes = [wintypes.HWND, ULONG_PTR]
    user32.KillTimer.restype = wintypes.BOOL
    kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
    kernel32.GetModuleHandleW.restype = wintypes.HMODULE


setup_win32()


def log_exc() -> None:
    try:
        with LOG_PATH.open("a", encoding="utf-8") as handle:
            handle.write("\n---\n")
            handle.write(traceback.format_exc())
    except Exception:
        pass


def hwnd_int(value) -> int:
    if not value:
        return 0
    if isinstance(value, int):
        return value
    return int(ctypes.cast(value, ctypes.c_void_p).value or 0)


def native_hwnd(tk_id: int) -> int:
    ancestor = hwnd_int(user32.GetAncestor(int(tk_id), 2))
    return ancestor or int(tk_id)


def topmost_handle() -> wintypes.HWND:
    return wintypes.HWND(HWND_TOPMOST)


KEY_VK: dict[str, int] = {}
for _index, _char in enumerate("abcdefghijklmnopqrstuvwxyz"):
    KEY_VK[_char] = 0x41 + _index
for _digit in range(10):
    KEY_VK[str(_digit)] = 0x30 + _digit
    KEY_VK[f"num{_digit}"] = 0x60 + _digit
for _fn in range(1, 25):
    KEY_VK[f"f{_fn}"] = 0x6F + _fn

KEY_VK.update(
    {
        "esc": 0x1B,
        "tab": 0x09,
        "enter": 0x0D,
        "space": 0x20,
        "backspace": 0x08,
        "delete": 0x2E,
        "insert": 0x2D,
        "home": 0x24,
        "end": 0x23,
        "pageup": 0x21,
        "pagedown": 0x22,
        "left": 0x25,
        "up": 0x26,
        "right": 0x27,
        "down": 0x28,
        "printscreen": 0x2C,
        "pause": 0x13,
        "capslock": 0x14,
        "numlock": 0x90,
        "scrolllock": 0x91,
        "apps": 0x5D,
        "plus": 0xBB,
        "minus": 0xBD,
        "comma": 0xBC,
        "period": 0xBE,
        "slash": 0xBF,
        "backquote": 0xC0,
        "semicolon": 0xBA,
        "quote": 0xDE,
        "bracketleft": 0xDB,
        "bracketright": 0xDD,
        "backslash": 0xDC,
        "multiply": 0x6A,
        "add": 0x6B,
        "subtract": 0x6D,
        "decimal": 0x6E,
        "divide": 0x6F,
        "volumeup": 0xAF,
        "volumedown": 0xAE,
        "volumemute": 0xAD,
        "playpause": 0xB3,
        "nexttrack": 0xB0,
        "prevtrack": 0xB1,
        "mediastop": 0xB2,
    }
)

ALIASES = {
    "control": "ctrl",
    "ctl": "ctrl",
    "lctrl": "ctrl",
    "rctrl": "ctrl",
    "option": "alt",
    "lalt": "alt",
    "ralt": "alt",
    "lshift": "shift",
    "rshift": "shift",
    "windows": "win",
    "window": "win",
    "super": "win",
    "cmd": "win",
    "meta": "win",
    "lwin": "win",
    "rwin": "win",
    "escape": "esc",
    "return": "enter",
    "spacebar": "space",
    "del": "delete",
    "ins": "insert",
    "pgup": "pageup",
    "pgdn": "pagedown",
    "prior": "pageup",
    "arrowleft": "left",
    "arrowright": "right",
    "arrowup": "up",
    "arrowdown": "down",
    "prtsc": "printscreen",
    "prtscn": "printscreen",
    "snapshot": "printscreen",
    "volup": "volumeup",
    "voldown": "volumedown",
    "mute": "volumemute",
    "play": "playpause",
    "equal": "plus",
    "oem_plus": "plus",
    "=": "plus",
    "oem_minus": "minus",
    ",": "comma",
    ".": "period",
    "/": "slash",
    "`": "backquote",
    ";": "semicolon",
    "'": "quote",
    "[": "bracketleft",
    "]": "bracketright",
    "\\": "backslash",
    "bs": "backspace",
    "bksp": "backspace",
}

DISPLAY_KEY = {
    "esc": "Esc",
    "pageup": "PgUp",
    "pagedown": "PgDn",
    "printscreen": "PrtSc",
    "backspace": "Bksp",
    "delete": "Del",
    "insert": "Ins",
    "space": "Space",
    "enter": "Enter",
    "tab": "Tab",
    "left": "Left",
    "right": "Right",
    "up": "Up",
    "down": "Down",
    "plus": "Plus",
    "minus": "Minus",
    "volumeup": "Vol+",
    "volumedown": "Vol-",
    "volumemute": "Mute",
    "playpause": "Play",
    "nexttrack": "Next",
    "prevtrack": "Prev",
    "mediastop": "Stop",
    "period": ".",
    "apps": "Menu",
}


def default_config() -> dict:
    return {
        "mode": "top",
        "orientation": "horizontal",
        "side": "right",
        "x": None,
        "y": None,
        "opacity": 0.72,
        "toggle_hotkey": "ctrl+alt+shift+h",
        "auto_hide_seconds": 0,
        "dblclick_left_paste": True,
        "dblclick_right_copy": True,
        "hidden": False,
        "disabled": [],
        "custom": [],
    }


def parse_hotkey(text: str) -> tuple[list[str], str]:
    raw = str(text).strip().lower().replace("＋", "+").replace(" ", "")
    if "-" in raw and "+" not in raw:
        raw = raw.replace("-", "+")
    parts = [part for part in raw.split("+") if part]
    if not parts:
        raise ValueError("empty")
    mods: list[str] = []
    key = None
    for part in parts:
        canon = ALIASES.get(part, part)
        if canon in MOD_ORDER:
            if canon not in mods:
                mods.append(canon)
            continue
        if key is not None or canon not in KEY_VK:
            raise ValueError(canon)
        key = canon
    if key is None:
        raise ValueError("no-key")
    return [name for name in MOD_ORDER if name in mods], key


def canonical_hotkey(text: str) -> str:
    mods, key = parse_hotkey(text)
    return "+".join([*mods, key])


def display_key(key: str) -> str:
    if key in DISPLAY_KEY:
        return DISPLAY_KEY[key]
    if len(key) == 1:
        return key.upper()
    if key.startswith("f") and key[1:].isdigit():
        return key.upper()
    return key[:1].upper() + key[1:]


def format_hotkey(text: str) -> str:
    mods, key = parse_hotkey(text)
    names = {"win": "Win", "ctrl": "Ctrl", "alt": "Alt", "shift": "Shift"}
    return "+".join([*(names[name] for name in mods), display_key(key)])


def key_event(vk: int, keyup: bool) -> INPUT:
    scan_ex = user32.MapVirtualKeyW(vk, MAPVK_VK_TO_VSC_EX)
    flags = KEYEVENTF_EXTENDEDKEY if scan_ex & 0xFF00 else 0
    if keyup:
        flags |= KEYEVENTF_KEYUP
    event = INPUT()
    event.type = INPUT_KEYBOARD
    event.ki.wVk = vk
    event.ki.wScan = scan_ex & 0xFF
    event.ki.dwFlags = flags
    event.ki.time = 0
    event.ki.dwExtraInfo = 0
    return event


def send_hotkey(mods: list[str], key: str) -> bool:
    mod_vks = [MOD_VK[name] for name in mods]
    key_vk = KEY_VK[key]
    events = [key_event(vk, False) for vk in mod_vks]
    events.append(key_event(key_vk, False))
    events.append(key_event(key_vk, True))
    events.extend(key_event(vk, True) for vk in reversed(mod_vks))
    array = (INPUT * len(events))(*events)
    sent = user32.SendInput(len(events), array, ctypes.sizeof(INPUT))
    if sent == len(events):
        return True
    if 0 < sent < len(events) and mod_vks:
        ups = [key_event(vk, True) for vk in reversed(mod_vks)]
        cleanup = (INPUT * len(ups))(*ups)
        user32.SendInput(len(ups), cleanup, ctypes.sizeof(INPUT))
    return False


def make_tray_icon():
    gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)
    user32.GetDC.argtypes = [wintypes.HWND]
    user32.GetDC.restype = wintypes.HDC
    user32.ReleaseDC.argtypes = [wintypes.HWND, wintypes.HDC]
    user32.ReleaseDC.restype = ctypes.c_int
    user32.CreateIconIndirect.argtypes = [ctypes.POINTER(ICONINFO)]
    user32.CreateIconIndirect.restype = wintypes.HICON
    gdi32.CreateCompatibleDC.argtypes = [wintypes.HDC]
    gdi32.CreateCompatibleDC.restype = wintypes.HDC
    gdi32.CreateCompatibleBitmap.argtypes = [wintypes.HDC, ctypes.c_int, ctypes.c_int]
    gdi32.CreateCompatibleBitmap.restype = wintypes.HBITMAP
    gdi32.CreateBitmap.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_uint, ctypes.c_uint, ctypes.c_void_p]
    gdi32.CreateBitmap.restype = wintypes.HBITMAP
    gdi32.SelectObject.argtypes = [wintypes.HDC, wintypes.HGDIOBJ]
    gdi32.SelectObject.restype = wintypes.HGDIOBJ
    gdi32.CreateSolidBrush.argtypes = [wintypes.COLORREF]
    gdi32.CreateSolidBrush.restype = wintypes.HBRUSH
    user32.FillRect.argtypes = [wintypes.HDC, ctypes.POINTER(wintypes.RECT), wintypes.HBRUSH]
    user32.FillRect.restype = ctypes.c_int
    gdi32.DeleteObject.argtypes = [wintypes.HGDIOBJ]
    gdi32.DeleteObject.restype = wintypes.BOOL
    gdi32.DeleteDC.argtypes = [wintypes.HDC]
    gdi32.DeleteDC.restype = wintypes.BOOL
    width = height = 32
    screen = user32.GetDC(None)
    if not screen:
        return 0
    memory = gdi32.CreateCompatibleDC(screen)
    color = gdi32.CreateCompatibleBitmap(screen, width, height)
    previous = gdi32.SelectObject(memory, color)
    blue = gdi32.CreateSolidBrush(0x00E8731A)
    white = gdi32.CreateSolidBrush(0x00FFFFFF)
    user32.FillRect(memory, ctypes.byref(wintypes.RECT(0, 0, width, height)), blue)
    for top in (7, 13, 19, 25):
        user32.FillRect(memory, ctypes.byref(wintypes.RECT(5, top, 27, top + 4)), white)
    gdi32.SelectObject(memory, previous)
    mask_bits = (ctypes.c_ubyte * ((width * height) // 8))()
    mask = gdi32.CreateBitmap(width, height, 1, 1, ctypes.addressof(mask_bits))
    info = ICONINFO()
    info.fIcon = True
    info.hbmMask = mask
    info.hbmColor = color
    icon = user32.CreateIconIndirect(ctypes.byref(info))
    gdi32.DeleteObject(blue)
    gdi32.DeleteObject(white)
    gdi32.DeleteObject(mask)
    gdi32.DeleteObject(color)
    gdi32.DeleteDC(memory)
    user32.ReleaseDC(None, screen)
    return int(icon or 0)


def cursor_pos() -> tuple[int, int]:
    point = POINT()
    if not user32.GetCursorPos(ctypes.byref(point)):
        return 0, 0
    return int(point.x), int(point.y)


def monitor_rect(x: int, y: int) -> tuple[int, int, int, int]:
    try:
        monitor = user32.MonitorFromPoint(POINT(int(x), int(y)), 2)
        if monitor:
            info = MONITORINFO()
            info.cbSize = ctypes.sizeof(MONITORINFO)
            if user32.GetMonitorInfoW(monitor, ctypes.byref(info)):
                rect = info.rcMonitor
                if rect.right > rect.left and rect.bottom > rect.top:
                    return int(rect.left), int(rect.top), int(rect.right), int(rect.bottom)
    except Exception:
        log_exc()
    return 0, 0, int(user32.GetSystemMetrics(0)), int(user32.GetSystemMetrics(1))


def column_count(count: int, vertical: bool, mon: tuple[int, int, int, int], reserve: int = 0) -> int:
    if count <= 0:
        return 1
    mon_w = mon[2] - mon[0]
    mon_h = mon[3] - mon[1]
    if vertical:
        avail_h = max(160, mon_h - 52 - reserve)
        cols = 1
        while math.ceil(count / cols) * 36 > avail_h and cols < 8:
            cols += 1
        return cols
    return max(1, max(240, mon_w - 16) // 124)


def popup_origin(
    cursor_x: int,
    cursor_y: int,
    width: int,
    height: int,
    mon: tuple[int, int, int, int],
    prefer: str = "right",
) -> tuple[int, int, str]:
    """游標旁的位置。預設放右邊；右邊放不下就改左邊。"""
    gap = 14
    left, top, right, bottom = mon
    right_x = cursor_x + gap
    left_x = cursor_x - gap - width
    options = [("right", right_x, right_x + width <= right - 4), ("left", left_x, left_x >= left + 4)]
    if prefer == "left":
        options.reverse()
    side = prefer if prefer in ("left", "right") else "right"
    x = right_x
    for name, origin, fits in options:
        if fits:
            side = name
            x = origin
            break
    else:
        if side == "left":
            x = left
        else:
            x = max(left, right - width)
            side = "right"
    y = cursor_y - height // 2
    y = max(top, min(y, max(top, bottom - height)))
    x = max(left, min(x, max(left, right - width)))
    return int(x), int(y), side


def key_is_down(vk: int) -> bool:
    return bool(user32.GetAsyncKeyState(vk) & 0x8000)


def process_is_elevated(process: wintypes.HANDLE) -> bool:
    token = wintypes.HANDLE()
    if not advapi32.OpenProcessToken(process, TOKEN_QUERY, ctypes.byref(token)):
        return False
    try:
        elevated = wintypes.DWORD()
        size = wintypes.DWORD()
        ok = advapi32.GetTokenInformation(
            token,
            TOKEN_ELEVATION,
            ctypes.byref(elevated),
            ctypes.sizeof(elevated),
            ctypes.byref(size),
        )
        return bool(ok and elevated.value)
    finally:
        kernel32.CloseHandle(token)


def window_is_elevated(hwnd: int) -> bool:
    pid = wintypes.DWORD()
    if not user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid)) or not pid.value:
        return False
    handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid.value)
    if not handle:
        return False
    try:
        return process_is_elevated(handle)
    finally:
        kernel32.CloseHandle(handle)


def focus_window(hwnd: int) -> None:
    foreground = hwnd_int(user32.GetForegroundWindow())
    if not hwnd or foreground == hwnd:
        return
    current_thread = kernel32.GetCurrentThreadId()
    other_thread = 0
    if foreground:
        pid = wintypes.DWORD()
        other_thread = user32.GetWindowThreadProcessId(foreground, ctypes.byref(pid))
    attached = bool(other_thread and other_thread != current_thread)
    if attached:
        user32.AttachThreadInput(current_thread, other_thread, True)
    user32.SetForegroundWindow(hwnd)
    user32.BringWindowToTop(hwnd)
    if attached:
        user32.AttachThreadInput(current_thread, other_thread, False)


def button_label(item: dict) -> str:
    label = str(item.get("label") or "").strip()
    return label or format_hotkey(item["hotkey"])


def visible_specs(config: dict, shortcuts: list[dict] | None = None) -> list[dict]:
    disabled = set(config.get("disabled") or [])
    source = shortcuts if shortcuts is not None else []
    return [
        {
            "id": item["id"],
            "group": item["group"],
            "label": button_label(item),
            "hotkey": item["hotkey"],
            "custom": not item.get("builtin"),
        }
        for item in source
        if item.get("enabled", item["id"] not in disabled)
    ]


def normalize_config(data: dict) -> dict:
    base = default_config()
    if not isinstance(data, dict) or "mode" not in data:
        return base
    mode = data.get("mode")
    if mode not in ("top", "cursor", "free"):
        mode = "top"
    orientation = data.get("orientation")
    if orientation not in ("horizontal", "vertical"):
        orientation = "vertical" if mode == "cursor" else "horizontal"
    side = data.get("side") if data.get("side") in ("left", "right") else "right"
    disabled: list[str] = []
    seen_disabled: set[str] = set()
    for id_ in data.get("disabled") or []:
        ident = str(id_).strip()
        if ident and ident not in seen_disabled:
            disabled.append(ident)
            seen_disabled.add(ident)
    custom = []
    for item in data.get("custom") or []:
        if not isinstance(item, dict):
            continue
        label = str(item.get("label") or "").strip()
        hotkey = str(item.get("hotkey") or "").strip()
        ident = str(item.get("id") or "").strip() or "custom-" + uuid.uuid4().hex[:8]
        if not label or not hotkey:
            continue
        try:
            hotkey = canonical_hotkey(hotkey)
        except ValueError:
            continue
        custom.append({"id": ident, "label": label, "hotkey": hotkey})
    try:
        opacity = float(data.get("opacity", 0.72))
    except (TypeError, ValueError):
        opacity = 0.72
    try:
        seconds = float(data.get("auto_hide_seconds", 5))
    except (TypeError, ValueError):
        seconds = 5
    toggle = str(data.get("toggle_hotkey") or "ctrl+alt+shift+h")
    try:
        toggle = canonical_hotkey(toggle)
    except ValueError:
        toggle = "ctrl+alt+shift+h"
    return {
        "mode": mode,
        "orientation": orientation,
        "side": side,
        "x": data.get("x"),
        "y": data.get("y"),
        "opacity": min(1.0, max(0.35, opacity)),
        "toggle_hotkey": toggle,
        "auto_hide_seconds": min(60.0, max(0.0, seconds)),
        "dblclick_left_paste": bool(data.get("dblclick_left_paste", True)),
        "dblclick_right_copy": bool(data.get("dblclick_right_copy", True)),
        "hidden": bool(data.get("hidden", False)),
        "disabled": disabled,
        "custom": custom,
    }


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        config = default_config()
        save_config(config)
        return config
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        log_exc()
        broken = CONFIG_PATH.with_suffix(".broken.json")
        try:
            if not broken.exists():
                CONFIG_PATH.replace(broken)
        except Exception:
            log_exc()
        config = default_config()
        save_config(config)
        return config
    if not isinstance(data, dict):
        return default_config()
    return normalize_config(data)


def save_config(config: dict) -> None:
    payload = {
        "mode": config.get("mode", "top"),
        "orientation": config.get("orientation", "horizontal"),
        "side": config.get("side", "right"),
        "x": config.get("x"),
        "y": config.get("y"),
        "opacity": config.get("opacity", 0.72),
        "toggle_hotkey": config.get("toggle_hotkey") or "ctrl+alt+shift+h",
        "auto_hide_seconds": config.get("auto_hide_seconds", 5),
        "dblclick_left_paste": bool(config.get("dblclick_left_paste", True)),
        "dblclick_right_copy": bool(config.get("dblclick_right_copy", True)),
        "hidden": bool(config.get("hidden")),
        "disabled": list(config.get("disabled") or []),
        "custom": list(config.get("custom") or []),
    }
    temporary = CONFIG_PATH.with_suffix(".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(CONFIG_PATH)


def config_mtime() -> float | None:
    try:
        return CONFIG_PATH.stat().st_mtime
    except OSError:
        return None


COMBO_KEYS: tuple[str, ...] = (
    *"abcdefghijklmnopqrstuvwxyz",
    *"0123456789",
    *(f"f{number}" for number in range(1, 13)),
    "esc",
    "tab",
    "enter",
    "space",
    "backspace",
    "delete",
    "insert",
    "home",
    "end",
    "pageup",
    "pagedown",
    "left",
    "up",
    "right",
    "down",
    "plus",
    "minus",
)


def modifier_sets() -> list[list[str]]:
    total = len(MOD_ORDER)
    sets: list[list[str]] = []
    for mask in range(1, 1 << total):
        chosen = {MOD_ORDER[index] for index in range(total) if mask & (1 << index)}
        sets.append([name for name in MOD_ORDER if name in chosen])
    return sets


BROWSER_HOTKEYS = {
    canonical_hotkey(hotkey) for _id, group, _label, hotkey in CATALOG if group == "瀏覽器" and canonical_hotkey(hotkey) != "ctrl+f5"
}
BUILTIN_GROUPS = ("一般", "瀏覽器")


def catalog_for(group_name: str) -> list[tuple[str, str, str, str]]:
    if group_name == "瀏覽器":
        rows = [item for item in CATALOG if canonical_hotkey(item[3]) != "ctrl+f5" or item[1] == "瀏覽器"]
        return [item for item in rows if not (item[0] == "shot-f5")]
    if group_name == "一般":
        return list(CATALOG)
    return [item for item in CATALOG if item[1] != "瀏覽器"]


def shortcuts_for(profile: dict) -> list[dict]:
    enabled = set(profile.get("enabled") or [])
    names = profile.get("names") if isinstance(profile.get("names"), dict) else {}
    items: list[dict] = []
    used: set[str] = set()
    for id_, group, label, hotkey in catalog_for(str(profile.get("name") or "一般")):
        hotkey = canonical_hotkey(hotkey)
        if hotkey in used:
            continue
        used.add(hotkey)
        items.append(
            {
                "id": id_,
                "group": group,
                "label": label,
                "hotkey": hotkey,
                "builtin": True,
                "enabled": hotkey in enabled,
            }
        )
    hide_browser = str(profile.get("name") or "") not in ("瀏覽器", "一般")
    custom: list[dict] = []
    for mods in modifier_sets():
        for key in COMBO_KEYS:
            hotkey = "+".join([*mods, key])
            if hotkey in used or (hide_browser and hotkey in BROWSER_HOTKEYS):
                continue
            custom.append(
                {
                    "id": "combo-" + hotkey.replace("+", "-"),
                    "group": "自訂快捷鍵",
                    "label": str(names.get(hotkey) or "").strip(),
                    "hotkey": hotkey,
                    "builtin": False,
                    "enabled": hotkey in enabled,
                }
            )
    custom.sort(key=lambda item: (item["hotkey"].count("+"), item["hotkey"]))
    return [*items, *custom]


def empty_profile(name: str, enabled: list[str] | None = None, names: dict | None = None) -> dict:
    return {"name": name, "enabled": list(enabled or []), "names": dict(names or {})}


def normalize_profile(item: dict, fallback: str) -> dict:
    name = str(item.get("name") or fallback).strip() or fallback
    enabled: list[str] = []
    seen: set[str] = set()
    for hotkey in item.get("enabled") or []:
        try:
            hotkey = canonical_hotkey(str(hotkey))
        except ValueError:
            continue
        if hotkey not in seen:
            enabled.append(hotkey)
            seen.add(hotkey)
    names: dict[str, str] = {}
    raw_names = item.get("names") if isinstance(item.get("names"), dict) else {}
    for hotkey, label in raw_names.items():
        try:
            hotkey = canonical_hotkey(str(hotkey))
        except ValueError:
            continue
        label = str(label or "").strip()
        if label:
            names[hotkey] = label
    return {"name": name, "enabled": enabled, "names": names}


def library_from_legacy(data) -> dict:
    raw = data.get("shortcuts") if isinstance(data, dict) else data
    general: list[str] = []
    browser: list[str] = []
    names: dict[str, str] = {}
    browser_ids = {id_ for id_, group, _label, _hotkey in CATALOG if group == "瀏覽器"}
    for item in raw or []:
        if not isinstance(item, dict):
            continue
        try:
            hotkey = canonical_hotkey(str(item.get("hotkey") or ""))
        except ValueError:
            continue
        browser_item = item.get("id") in browser_ids or item.get("group") == "瀏覽器"
        if browser_item:
            if item.get("enabled"):
                browser.append(hotkey)
            continue
        if item.get("enabled"):
            general.append(hotkey)
        if not item.get("builtin"):
            label = str(item.get("label") or "").strip()
            if label:
                names[hotkey] = label
    return {
        "active": "一般",
        "profiles": [empty_profile("一般", general, names), empty_profile("瀏覽器", browser)],
    }


def normalize_library(data: dict) -> dict:
    profiles: list[dict] = []
    seen: set[str] = set()
    for item in data.get("profiles") or []:
        if not isinstance(item, dict):
            continue
        profile = normalize_profile(item, "一般")
        if profile["name"] in seen:
            continue
        seen.add(profile["name"])
        profiles.append(profile)
    for name in BUILTIN_GROUPS:
        if name not in seen:
            profiles.insert(0 if name == "一般" else len(profiles), empty_profile(name))
    active = str(data.get("active") or "一般")
    if active not in {item["name"] for item in profiles}:
        active = "一般"
    return {"active": active, "profiles": profiles}


def read_stored_shortcuts() -> list[dict]:
    if not SHORTCUTS_PATH.exists():
        return []
    try:
        data = json.loads(SHORTCUTS_PATH.read_text(encoding="utf-8"))
    except Exception:
        log_exc()
        return []
    raw = data.get("shortcuts") if isinstance(data, dict) else data
    return [item for item in raw or [] if isinstance(item, dict)]


def stored_disabled() -> set[str]:
    if not CONFIG_PATH.exists():
        return set()
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return set()
    if not isinstance(data, dict):
        return set()
    return {str(item).strip() for item in data.get("disabled") or [] if str(item).strip()}


def duplicate_message(
    shortcuts: list[dict],
    hotkey: str,
    label: str,
    ignore_id: str | None = None,
) -> str | None:
    hotkey = canonical_hotkey(hotkey)
    label = label.strip()
    for item in shortcuts:
        if item["id"] == ignore_id:
            continue
        if item["hotkey"] == hotkey:
            return f"{format_hotkey(hotkey)} 已經用在「{item['label']}」。"
        if item["label"] == label:
            return f"名稱「{label}」已經有了。"
    return None


def load_library() -> dict:
    data = None
    if SHORTCUTS_PATH.exists():
        try:
            data = json.loads(SHORTCUTS_PATH.read_text(encoding="utf-8"))
        except Exception:
            log_exc()
    if isinstance(data, dict) and isinstance(data.get("profiles"), list):
        library = normalize_library(data)
    else:
        library = library_from_legacy(data if isinstance(data, dict) else {})
    if json.dumps(data, ensure_ascii=False, sort_keys=True) != json.dumps(library, ensure_ascii=False, sort_keys=True):
        save_library(library)
    return library


def save_library(library: dict) -> None:
    temporary = SHORTCUTS_PATH.with_suffix(".tmp")
    temporary.write_text(json.dumps(library, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(SHORTCUTS_PATH)


def materialize(library: dict) -> list[dict]:
    active = str(library.get("active") or "一般")
    profile = next((item for item in library.get("profiles") or [] if item.get("name") == active), None)
    if profile is None:
        profile = empty_profile("一般")
    return shortcuts_for(profile)


def shortcuts_mtime() -> float | None:
    try:
        return SHORTCUTS_PATH.stat().st_mtime
    except OSError:
        return None


def lighten(color: str, amount: float = 0.18) -> str:
    red = int(color[1:3], 16)
    green = int(color[3:5], 16)
    blue = int(color[5:7], 16)
    red = min(255, int(red + (255 - red) * amount))
    green = min(255, int(green + (255 - green) * amount))
    blue = min(255, int(blue + (255 - blue) * amount))
    return f"#{red:02x}{green:02x}{blue:02x}"


def acquire_mutex() -> bool:
    global MUTEX_HANDLE
    handle = kernel32.CreateMutexW(None, False, MUTEX_NAME)
    error = ctypes.get_last_error()
    if not handle:
        return True
    if error == ERROR_ALREADY_EXISTS:
        kernel32.CloseHandle(handle)
        return False
    MUTEX_HANDLE = handle
    return True


def inside(widget: tk.Misc, event) -> bool:
    left = widget.winfo_rootx()
    top = widget.winfo_rooty()
    return left <= event.x_root < left + widget.winfo_width() and top <= event.y_root < top + widget.winfo_height()


class ActionBar:
    def __init__(self) -> None:
        self.config = load_config()
        self.library = load_library()
        self.shortcuts = materialize(self.library)
        self._mtime = config_mtime()
        self._shortcuts_mtime = shortcuts_mtime()
        self._alive = True
        self._editors = 0
        self._drag_dx = 0
        self._drag_dy = 0
        self._dragging = False
        self._toggle_requested = False
        self._tray_show = False
        self._tray_menu = False
        self._tray_added = False
        self._tray_icon = 0
        self._in_tray = False
        self._last_target = 0
        self._old_procs: dict[int, ctypes.c_void_p] = {}
        self._proc = None
        self._menu = None
        self._hide_job = None
        self._tip = None
        self._tip_frame = None
        self._tip_show_job = None
        self._tip_hide_job = None
        self._tip_watch_job = None
        self._hotkey_ok = False
        self._mouse_hook = None
        self._mouse_proc = None
        self._click_prev = {"left": None, "right": None}
        self._right_state = "idle"
        self._right_x = 0
        self._right_y = 0
        self._right_tick = 0
        self._right_timer = False
        self._pending_replay = False
        self._pending_replay_down = False
        self._pending_drag_up = False
        self._right_up_x = 0
        self._right_up_y = 0
        self._right_cooldown = 0
        self._pending_paste = False
        self._pending_copy = False
        self._copy_hwnd = 0
        self._gear_win = None
        self._elevated = process_is_elevated(kernel32.GetCurrentProcess())
        self.hwnd = 0

        self.root = tk.Tk()
        self.root.title("TopActionBar")
        self.root.configure(bg=BORDER)
        self.root.overrideredirect(True)
        self.root.withdraw()
        self.root.attributes("-topmost", True)
        self.root.report_callback_exception = self._report
        self.shell = tk.Frame(self.root, bg=BAR)
        self.shell.pack(fill="both", expand=True, padx=1, pady=(1, 2))
        self.tools = tk.Frame(self.shell, bg=BAR)
        self.tools.pack(side="top", fill="x")
        self.body = tk.Frame(self.shell, bg=BAR)
        self.body.pack(side="top", fill="both")
        self.relayout()
        self.apply_opacity()
        if not self.config.get("hidden"):
            self.root.deiconify()
        self.root.update()
        self.hwnd = native_hwnd(int(self.root.winfo_id()))
        self._install_proc(self.hwnd)
        self._apply_exstyle(self.hwnd)
        self._ensure_tray()
        self.register_toggle()
        self._install_mouse_hook()
        self.root.after(80, self._pump)
        self.root.after(1500, self._reinforce)

    def run(self) -> None:
        self.root.mainloop()

    def _report(self, exc_type, exc, tb) -> None:
        traceback.print_exception(exc_type, exc, tb)
        log_exc()

    def _install_proc(self, hwnd: int) -> None:
        if self._proc is None:
            self._proc = WNDPROC(self._wndproc)
        old = user32.GetWindowLongPtrW(hwnd, GWLP_WNDPROC)
        self._old_procs[int(hwnd)] = old
        user32.SetWindowLongPtrW(hwnd, GWLP_WNDPROC, ctypes.cast(self._proc, ctypes.c_void_p))

    def _wndproc(self, hwnd, msg, wparam, lparam):
        try:
            if msg == WM_MOUSEACTIVATE and self._editors <= 0:
                return MA_NOACTIVATE
            if msg == WM_HOTKEY and int(wparam) == HOTKEY_ID:
                self._toggle_requested = True
                return 0
            if msg == WM_APP_DBL:
                self._run_pending_clicks()
                return 0
            if msg == WM_TIMER and int(wparam) == TIMER_RIGHT_CLICK:
                self._finish_right_click()
                return 0
            if msg == WM_TRAY:
                event = int(lparam) & 0xFFFF
                if event in (WM_LBUTTONUP, WM_LBUTTONDBLCLK, NIN_SELECT):
                    self._tray_show = True
                elif event in (WM_RBUTTONUP, WM_CONTEXTMENU):
                    self._tray_menu = True
                return 0
        except Exception:
            log_exc()
        old = self._old_procs.get(int(hwnd))
        if not old:
            return 0
        return user32.CallWindowProcW(old, hwnd, msg, wparam, lparam)

    def _apply_exstyle(self, hwnd: int) -> None:
        if not hwnd or self._editors > 0:
            return
        style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        needed = WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW
        flags = SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE
        if style & needed != needed:
            user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | needed)
            flags |= SWP_FRAMECHANGED
        user32.SetWindowPos(hwnd, topmost_handle(), 0, 0, 0, 0, flags)
        self._raise_tip()

    def _allow_activate(self, allow: bool) -> None:
        if not self.hwnd:
            return
        style = user32.GetWindowLongW(self.hwnd, GWL_EXSTYLE)
        if allow:
            style &= ~WS_EX_NOACTIVATE
        else:
            style |= WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW
        user32.SetWindowLongW(self.hwnd, GWL_EXSTYLE, style)
        user32.SetWindowPos(
            self.hwnd,
            topmost_handle(),
            0,
            0,
            0,
            0,
            SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_FRAMECHANGED,
        )
        self._raise_tip()

    def register_toggle(self) -> None:
        if not self.hwnd:
            return
        user32.UnregisterHotKey(self.hwnd, HOTKEY_ID)
        self._hotkey_ok = False
        spec = str(self.config.get("toggle_hotkey") or "")
        if not spec:
            return
        try:
            mods, key = parse_hotkey(spec)
        except ValueError:
            return
        flags = 0x4000
        for name in mods:
            flags |= MOD_FLAG[name]
        self._hotkey_ok = bool(user32.RegisterHotKey(self.hwnd, HOTKEY_ID, flags, KEY_VK[key]))

    def apply_opacity(self) -> None:
        try:
            opacity = float(self.config.get("opacity", 0.72))
        except (TypeError, ValueError):
            opacity = 0.72
        self.root.attributes("-alpha", min(1.0, max(0.35, opacity)))

    def is_shown(self) -> bool:
        try:
            return bool(self.root.winfo_viewable())
        except tk.TclError:
            return False

    def _target_monitor(self) -> tuple[int, int, int, int]:
        mode = self.config.get("mode")
        if mode == "free" and self.config.get("x") is not None and self.config.get("y") is not None:
            return monitor_rect(int(self.config["x"]) + 10, int(self.config["y"]) + 10)
        cursor_x, cursor_y = cursor_pos()
        return monitor_rect(cursor_x, cursor_y)

    def relayout(self) -> None:
        self._hide_tip()
        for child in self.tools.winfo_children():
            child.destroy()
        for child in self.body.winfo_children():
            child.destroy()
        self._build_tools()
        specs = visible_specs(self.config, self.shortcuts)
        vertical = self.config.get("orientation") == "vertical"
        mon = self._target_monitor()
        cols = column_count(len(specs), vertical, mon, reserve=88) if specs else 1
        self._build_nav_pad().grid(row=0, column=0, columnspan=cols, padx=2, pady=(2, 4))
        if not specs:
            empty = tk.Label(self.body, text="沒有選擇快捷鍵", bg=BAR, fg=HINT, font=FONT, padx=16, pady=12)
            empty.grid(row=1, column=0)
            empty.bind("<Button-3>", self._open_bar_menu)
        else:
            for index, spec in enumerate(specs):
                self._make_key(spec, vertical).grid(
                    row=1 + index // cols,
                    column=index % cols,
                    padx=2,
                    pady=2,
                    sticky="nsew",
                )
            for column in range(cols):
                self.body.grid_columnconfigure(column, weight=1)
        self.root.update_idletasks()
        self._move(mon)
        if self.hwnd:
            self._apply_exstyle(self.hwnd)

    def _move(self, mon: tuple[int, int, int, int] | None = None) -> None:
        self.root.update_idletasks()
        width = max(self.shell.winfo_reqwidth() + 2, 48)
        height = max(self.shell.winfo_reqheight() + 3, 28)
        if mon is None:
            mon = self._target_monitor()
        mode = self.config.get("mode")
        if mode == "cursor":
            cursor_x, cursor_y = cursor_pos()
            mon = monitor_rect(cursor_x, cursor_y)
            x, y, side = popup_origin(
                cursor_x,
                cursor_y,
                width,
                height,
                mon,
                str(self.config.get("side") or "right"),
            )
            self.config["side"] = "right" if self.config.get("side") != "left" else "left"
            self._last_side = side
        elif mode == "top":
            mon_w = mon[2] - mon[0]
            x = mon[0] + max(0, (mon_w - width) // 2)
            y = mon[1]
            x = max(mon[0], min(x, max(mon[0], mon[2] - width)))
        else:
            saved_x = self.config.get("x")
            saved_y = self.config.get("y")
            cursor_x, cursor_y = cursor_pos()
            anchor_x = int(saved_x) if saved_x is not None else cursor_x
            anchor_y = int(saved_y) if saved_y is not None else mon[1]
            mon = monitor_rect(anchor_x, anchor_y)
            x = max(mon[0], min(anchor_x, max(mon[0], mon[2] - width)))
            y = max(mon[1], min(anchor_y, max(mon[1], mon[3] - height)))
        self.root.geometry(f"{width}x{height}+{int(x)}+{int(y)}")

    def _build_tools(self) -> None:
        group_name = str(self.library.get("active") or "一般")
        buttons = [
            ("拖", None, True),
            ("選", self.choose_shortcuts, False),
            (group_name, self._open_group_menu, False),
            ("上", self.dock_top, False),
            ("鼠", self.follow_cursor, False),
            ("⚙", self.open_click_settings, False),
            ("—", self.minimize_to_tray, False),
            ("×", self.quit, False),
        ]
        for text, command, drag in buttons:
            label = tk.Label(
                self.tools,
                text=text,
                bg=TOOL,
                fg=TEXT,
                font=FONT if text in ("拖", "選", "上", "鼠", group_name) else FONT_TOOL,
                cursor="fleur" if drag else "hand2",
                takefocus=False,
                padx=8,
                pady=4,
            )
            label.pack(side="left", padx=1, pady=2)
            label.bind("<Button-3>", self._open_bar_menu)
            label.bind("<Enter>", lambda _event, widget=label: widget.configure(bg=lighten(TOOL)))
            label.bind("<Leave>", lambda _event, widget=label: widget.configure(bg=TOOL))
            if drag:
                label.bind("<ButtonPress-1>", self._drag_start)
                label.bind("<B1-Motion>", self._drag_move)
                label.bind("<ButtonRelease-1>", self._drag_end)
            else:
                label.bind(
                    "<ButtonRelease-1>",
                    lambda event, widget=label, cmd=command: cmd() if inside(widget, event) else None,
                )

    def _build_nav_pad(self) -> tk.Frame:
        pad = tk.Frame(self.body, bg=BAR)
        text_rows = (
            (
                ("pageup", "PgUp", "PGUP"),
                ("pagedown", "PgDn", "PGDN"),
                ("home", "Home", "HOME"),
                ("end", "End", "END"),
            ),
            (
                ("backspace", "Bksp", "BKSP"),
                ("delete", "Del", "DEL"),
                ("tab", "\u21e5", "TAB"),
                ("enter", "\u23ce", "ENTER"),
            ),
        )
        arrows = (
            (("up", "\u25b2", "UP"), ("down", "\u25bc", "DOWN")),
            (("left", "\u25c0", "LEFT"), ("right", "\u25b6", "RIGHT")),
        )
        for row_index, keys in enumerate(text_rows):
            for column, (hotkey, glyph, tip_name) in enumerate(keys):
                self._make_icon_key(pad, hotkey, glyph, tip_name).grid(row=row_index, column=column, padx=2, pady=2)
        for row_index, keys in enumerate(arrows):
            for column, (hotkey, glyph, tip_name) in enumerate(keys):
                self._make_icon_key(pad, hotkey, glyph, tip_name).grid(
                    row=row_index, column=4 + column, padx=2, pady=2
                )
        return pad

    def _make_icon_key(self, parent, hotkey: str, glyph: str, tip_name: str) -> tk.Frame:
        spec = {"id": "nav-" + hotkey, "group": "常用鍵", "label": glyph, "hotkey": hotkey}
        bg = "#e7eee8"
        font = ("Segoe UI Symbol", 12) if len(glyph) == 1 else ("Microsoft JhengHei UI", 8, "bold")
        frame = tk.Frame(
            parent,
            bg=bg,
            width=48,
            height=30,
            cursor="hand2",
            takefocus=False,
            highlightthickness=1,
            highlightbackground="#9aa89a",
        )
        frame.pack_propagate(False)
        frame.grid_propagate(False)
        title = tk.Label(frame, text=glyph, bg=bg, fg="#1b1c20", font=font, takefocus=False)
        title.place(relx=0.5, rely=0.5, anchor="center")
        frame._bg = bg
        frame._fg = "#1b1c20"
        frame._hover = "#174ea6"
        frame._edge = "#9aa89a"
        frame._tip_name = tip_name
        frame._label = title
        frame._hint = None
        frame._hint_text = ""
        frame._hint_fg = "#ffffff"
        frame._pressed = False
        frame._busy = False
        frame._gen = 0
        for widget in (frame, title):
            widget.bind("<ButtonPress-1>", lambda _event, box=frame: self._press_key(box))
            widget.bind("<ButtonRelease-1>", lambda event, box=frame, item=spec: self._release_key(event, box, item))
            widget.bind("<Enter>", lambda _event, box=frame: self._hover_key(box, True))
            widget.bind("<Leave>", lambda _event, box=frame: self._hover_key(box, False))
            widget.bind("<Button-3>", self._open_bar_menu)
        return frame

    def _make_key(self, spec: dict, vertical: bool) -> tk.Frame:
        bg = BTN
        try:
            hint = format_hotkey(spec["hotkey"])
            hint_fg = HINT
        except ValueError:
            hint = str(spec["hotkey"])
            hint_fg = "#f28b82"
        frame = tk.Frame(
            self.body,
            bg=bg,
            cursor="hand2",
            takefocus=False,
            width=210 if vertical else 120,
            height=32 if vertical else 44,
        )
        frame.pack_propagate(False)
        frame.grid_propagate(False)
        title = tk.Label(frame, text=spec["label"], bg=bg, fg=TEXT, font=FONT, takefocus=False)
        subtitle = tk.Label(frame, text=hint, bg=bg, fg=hint_fg, font=FONT_HINT, takefocus=False)
        if vertical:
            title.pack(side="left", padx=(8, 4))
            subtitle.pack(side="right", padx=(4, 8))
        else:
            title.pack(pady=(5, 0))
            subtitle.pack()
        frame._bg = bg
        frame._fg = TEXT
        frame._hover = lighten(bg)
        frame._label = title
        frame._hint = subtitle
        frame._hint_text = hint
        frame._hint_fg = hint_fg
        frame._pressed = False
        frame._busy = False
        frame._gen = 0
        for widget in (frame, title, subtitle):
            widget.bind("<ButtonPress-1>", lambda _event, box=frame: self._press_key(box))
            widget.bind("<ButtonRelease-1>", lambda event, box=frame, item=spec: self._release_key(event, box, item))
            widget.bind("<Enter>", lambda _event, box=frame: self._hover_key(box, True))
            widget.bind("<Leave>", lambda _event, box=frame: self._hover_key(box, False))
            widget.bind("<Button-3>", lambda event, item=spec: self._open_key_menu(event, item))
        return frame

    def _paint_key(self, frame, bg: str, fg: str, hint_fg: str) -> None:
        if not frame.winfo_exists():
            return
        frame.configure(bg=bg)
        frame._label.configure(bg=bg, fg=fg)
        edge = getattr(frame, "_edge", None)
        if edge:
            frame.configure(highlightbackground=edge if bg == frame._bg else bg)
        if frame._hint is not None:
            frame._hint.configure(bg=bg, fg=hint_fg)

    def _paint_key_normal(self, frame) -> None:
        if frame.winfo_exists():
            self._paint_key(frame, frame._bg, frame._fg, frame._hint_fg)

    def _pointer_inside(self, frame) -> bool:
        try:
            pointer_x, pointer_y = frame.winfo_pointerxy()
            left, top = frame.winfo_rootx(), frame.winfo_rooty()
        except tk.TclError:
            return False
        return left <= pointer_x < left + frame.winfo_width() and top <= pointer_y < top + frame.winfo_height()

    def _hover_key(self, frame, entering: bool) -> None:
        if not frame.winfo_exists() or frame._busy:
            return
        if not entering:
            if self._pointer_inside(frame):
                return
            frame._pressed = False
            self._paint_key_normal(frame)
            self._schedule_tip_hide()
            return
        if not frame._pressed:
            self._paint_key(frame, frame._hover, "#ffffff", "#ffffff")
        self._schedule_tip(frame)

    def _cancel_tip_show(self) -> None:
        if self._tip_show_job is not None:
            try:
                self.root.after_cancel(self._tip_show_job)
            except tk.TclError:
                pass
            self._tip_show_job = None

    def _cancel_tip_hide(self) -> None:
        if self._tip_hide_job is not None:
            try:
                self.root.after_cancel(self._tip_hide_job)
            except tk.TclError:
                pass
            self._tip_hide_job = None

    def _schedule_tip(self, frame) -> None:
        name = str(getattr(frame, "_tip_name", "") or "")
        if not name:
            return
        self._cancel_tip_hide()
        if self._tip is not None and self._tip_frame is frame:
            return
        self._cancel_tip_show()
        self._tip_show_job = self.root.after(180, lambda box=frame, text=name: self._show_tip(box, text))

    def _schedule_tip_hide(self) -> None:
        self._cancel_tip_show()
        if self._tip is None and self._tip_hide_job is None:
            return
        self._cancel_tip_hide()
        self._tip_hide_job = self.root.after(80, self._finish_tip_hide)

    def _finish_tip_hide(self) -> None:
        self._tip_hide_job = None
        frame = self._tip_frame
        if frame is not None and frame.winfo_exists() and self._pointer_inside(frame):
            return
        if frame is not None and frame.winfo_exists() and not frame._busy:
            frame._pressed = False
            self._paint_key_normal(frame)
        self._hide_tip()

    def _rects_hit(self, a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> bool:
        return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])

    def _raise_tip(self) -> None:
        tip = self._tip
        if tip is None:
            return
        try:
            if not tip.winfo_exists():
                return
            hwnd = native_hwnd(tip.winfo_id())
        except tk.TclError:
            return
        if hwnd:
            user32.SetWindowPos(hwnd, topmost_handle(), 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE)

    def _tip_origin(self, frame, width: int, height: int) -> tuple[int, int]:
        left, top = frame.winfo_rootx(), frame.winfo_rooty()
        box_w, box_h = frame.winfo_width(), frame.winfo_height()
        mon = monitor_rect(left, top)
        try:
            pointer_x, pointer_y = frame.winfo_pointerxy()
        except tk.TclError:
            pointer_x, pointer_y = left + box_w // 2, top + box_h // 2
        cursor = (pointer_x - 6, pointer_y - 6, pointer_x + 48, pointer_y + 48)
        button = (left, top, left + box_w, top + box_h)
        spots: list[tuple[int, int]] = []
        for gap in (6, 14):
            spots.extend(
                (
                    (left - width - gap, top - height - gap),
                    (left - width - gap, top + (box_h - height) // 2),
                    (left + (box_w - width) // 2, top - height - gap),
                    (left + box_w + gap, top - height - gap),
                    (left + box_w + gap, top + (box_h - height) // 2),
                    (left - width - gap, top + box_h + gap),
                    (left + (box_w - width) // 2, top + box_h + gap),
                    (left + box_w + gap, top + box_h + gap),
                )
            )

        def on_screen(x: int, y: int) -> bool:
            return mon[0] + 4 <= x and mon[1] + 4 <= y and x + width <= mon[2] - 4 and y + height <= mon[3] - 4

        def blocked(x: int, y: int) -> bool:
            rect = (x, y, x + width, y + height)
            return self._rects_hit(rect, cursor) or self._rects_hit(rect, button)

        clear = [(x, y) for x, y in spots if on_screen(x, y) and not blocked(x, y)]
        if clear:
            return int(clear[0][0]), int(clear[0][1])
        x = max(mon[0] + 4, min(spots[0][0], mon[2] - width - 4))
        y = max(mon[1] + 4, min(spots[0][1], mon[3] - height - 4))
        return int(x), int(y)

    def _show_tip(self, frame, text: str) -> None:
        self._tip_show_job = None
        if not frame.winfo_exists() or not self._pointer_inside(frame):
            return
        if self._tip is not None and self._tip_frame is frame:
            try:
                if self._tip.winfo_exists():
                    self._arm_tip_watch()
                    return
            except tk.TclError:
                pass
        self._close_tip_window()
        tip = tk.Toplevel(self.root)
        tip.overrideredirect(True)
        tip.attributes("-topmost", True)
        tip.configure(bg="#000000")
        tk.Label(
            tip,
            text=text,
            bg="#000000",
            fg="#ffffff",
            font=("Microsoft JhengHei UI", 9, "bold"),
            padx=8,
            pady=3,
        ).pack()
        tip.withdraw()
        tip.update_idletasks()
        width, height = tip.winfo_reqwidth(), tip.winfo_reqheight()
        x, y = self._tip_origin(frame, width, height)
        tip.geometry(f"{width}x{height}+{int(x)}+{int(y)}")
        tip.attributes("-alpha", 1.0)
        hwnd = native_hwnd(tip.winfo_id())
        if hwnd:
            style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            style = (style | WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW) & ~WS_EX_TRANSPARENT
            user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
            user32.SetWindowPos(
                hwnd,
                topmost_handle(),
                int(x),
                int(y),
                width,
                height,
                SWP_NOACTIVATE | SWP_SHOWWINDOW,
            )
        tip.deiconify()
        try:
            tip.attributes("-alpha", 1.0)
        except tk.TclError:
            pass
        self._tip = tip
        self._tip_frame = frame
        self._arm_tip_watch()

    def _place_tip(self, tip, frame) -> None:
        try:
            if not tip.winfo_exists():
                return
            width, height = tip.winfo_width(), tip.winfo_height()
            current = (tip.winfo_x(), tip.winfo_y(), tip.winfo_x() + width, tip.winfo_y() + height)
        except tk.TclError:
            return
        left, top = frame.winfo_rootx(), frame.winfo_rooty()
        button = (left, top, left + frame.winfo_width(), top + frame.winfo_height())
        try:
            pointer_x, pointer_y = frame.winfo_pointerxy()
        except tk.TclError:
            return
        cursor = (pointer_x - 6, pointer_y - 6, pointer_x + 48, pointer_y + 48)
        if not self._rects_hit(current, cursor) and not self._rects_hit(current, button):
            return
        x, y = self._tip_origin(frame, width, height)
        tip.geometry(f"+{int(x)}+{int(y)}")

    def _arm_tip_watch(self) -> None:
        if self._tip_watch_job is None:
            self._tip_watch_job = self.root.after(120, self._tip_watch)

    def _cancel_tip_watch(self) -> None:
        if self._tip_watch_job is not None:
            try:
                self.root.after_cancel(self._tip_watch_job)
            except tk.TclError:
                pass
            self._tip_watch_job = None

    def _tip_watch(self) -> None:
        self._tip_watch_job = None
        frame = self._tip_frame
        if frame is None or not frame.winfo_exists() or not self._pointer_inside(frame):
            if frame is not None and frame.winfo_exists() and not frame._busy:
                frame._pressed = False
                self._paint_key_normal(frame)
            self._hide_tip()
            return
        name = str(getattr(frame, "_tip_name", "") or "")
        alive = False
        if self._tip is not None and self._tip_frame is frame:
            try:
                alive = bool(self._tip.winfo_exists())
            except tk.TclError:
                alive = False
        if name and not alive:
            self._show_tip(frame, name)
        if self._tip_watch_job is None:
            self._tip_watch_job = self.root.after(120, self._tip_watch)

    def _close_tip_window(self) -> None:
        tip = self._tip
        self._tip = None
        self._tip_frame = None
        if tip is not None:
            try:
                tip.destroy()
            except tk.TclError:
                pass

    def _hide_tip(self) -> None:
        self._cancel_tip_show()
        self._cancel_tip_hide()
        self._cancel_tip_watch()
        self._close_tip_window()

    def _press_key(self, frame) -> None:
        frame._pressed = True
        if not getattr(frame, "_tip_name", ""):
            self._hide_tip()
        self._paint_key(frame, PRESS, "#ffffff", "#ffffff")

    def _release_key(self, event, frame, spec: dict) -> None:
        pressed = frame._pressed
        frame._pressed = False
        if pressed and inside(frame, event):
            self.root.after(30, lambda item=spec, box=frame: self._activate(item, box))
            return
        if frame.winfo_exists() and not frame._busy:
            self._paint_key_normal(frame)

    def _flash(self, frame, ok: bool, message: str | None) -> None:
        if frame is None or not frame.winfo_exists():
            return
        frame._gen += 1
        generation = frame._gen
        frame._busy = True
        if message and frame._hint is not None:
            frame._hint.configure(text=message)
        self._paint_key(frame, PRESS if ok else BAD, "#ffffff", "#ffffff")

        def restore() -> None:
            if not frame.winfo_exists() or frame._gen != generation:
                return
            frame._busy = False
            if frame._hint is not None:
                frame._hint.configure(text=frame._hint_text)
            if getattr(frame, "_tip_name", "") and self._pointer_inside(frame):
                self._paint_key(frame, frame._hover, "#ffffff", "#ffffff")
            else:
                self._paint_key_normal(frame)

        frame.after(900 if message else 140, restore)

    def _belongs_to_us(self, hwnd: int) -> bool:
        current = int(hwnd)
        seen: set[int] = set()
        while current and current not in seen:
            if current == self.hwnd:
                return True
            seen.add(current)
            parent = hwnd_int(user32.GetParent(current))
            owner = hwnd_int(user32.GetWindow(current, GW_OWNER))
            nxt = parent or owner
            if nxt == current:
                break
            current = nxt
        return False

    def _prepare_target(self) -> str:
        foreground = hwnd_int(user32.GetForegroundWindow())
        if not foreground or foreground == self.hwnd or self._belongs_to_us(foreground):
            foreground = self._last_target
            if not foreground:
                return "missing"
            focus_window(foreground)
            time.sleep(0.05)
            foreground = hwnd_int(user32.GetForegroundWindow())
            if not foreground or self._belongs_to_us(foreground):
                return "missing"
        else:
            self._last_target = foreground
        if window_is_elevated(foreground) and not self._elevated:
            return "elevated"
        return "ok"

    def _activate(self, spec: dict, frame) -> None:
        try:
            mods, key = parse_hotkey(spec["hotkey"])
        except ValueError:
            self._flash(frame, False, "格式錯誤")
            return
        status = self._prepare_target()
        if status == "elevated":
            self._flash(frame, False, "權限不足")
        elif status != "ok":
            self._flash(frame, False, "沒有目標")
        else:
            ok = send_hotkey(mods, key)
            self._flash(frame, ok, None if ok else "送出失敗")

    def schedule_hide(self) -> None:
        self._cancel_hide()
        try:
            seconds = float(self.config.get("auto_hide_seconds", 5))
        except (TypeError, ValueError):
            seconds = 5
        if seconds <= 0 or not self.is_shown():
            return
        self._hide_job = self.root.after(int(seconds * 1000), self._auto_hide)

    def _cancel_hide(self) -> None:
        if self._hide_job is not None:
            try:
                self.root.after_cancel(self._hide_job)
            except tk.TclError:
                pass
            self._hide_job = None

    def _auto_hide(self) -> None:
        self._hide_job = None
        if not self._alive:
            return
        if self._editors or self._dragging:
            self.schedule_hide()
            return
        self.hide()

    def hide(self) -> None:
        self._cancel_hide()
        self._close_menu()
        self.config["hidden"] = True
        if self.is_shown():
            self.root.withdraw()

    def show(self) -> None:
        self._in_tray = False
        self.config["hidden"] = False
        if self.config.get("mode") == "cursor":
            self.relayout()
        elif not self.is_shown():
            self._move()
        self.root.deiconify()
        self.root.lift()
        self.root.update()
        self._apply_exstyle(self.hwnd)

    def toggle(self) -> None:
        if self._editors:
            return
        if self.is_shown():
            self.hide()
        else:
            self.show()

    def dock_top(self) -> None:
        self.config["mode"] = "top"
        self.config["orientation"] = "horizontal"
        self.config["hidden"] = False
        self._save()
        self.relayout()
        if not self.is_shown():
            self.root.deiconify()

    def follow_cursor(self) -> None:
        self.config["mode"] = "cursor"
        self.config["orientation"] = "vertical"
        if self.config.get("side") not in ("left", "right"):
            self.config["side"] = "right"
        self.config["hidden"] = False
        self._save()
        self.relayout()
        if not self.is_shown():
            self.root.deiconify()

    def _watch_foreground(self) -> None:
        foreground = hwnd_int(user32.GetForegroundWindow())
        if foreground and foreground != self.hwnd and not self._belongs_to_us(foreground):
            self._last_target = foreground

    def _install_mouse_hook(self) -> None:
        if self._mouse_hook:
            return
        self._mouse_proc = HOOKPROC(self._mouse_hook_proc)
        handle = user32.SetWindowsHookExW(WH_MOUSE_LL, self._mouse_proc, kernel32.GetModuleHandleW(None), 0)
        self._mouse_hook = handle or None

    def _remove_mouse_hook(self) -> None:
        handle = self._mouse_hook
        self._mouse_hook = None
        if handle:
            user32.UnhookWindowsHookEx(handle)

    def _point_is_ours(self, x: int, y: int) -> bool:
        hwnd = hwnd_int(user32.WindowFromPoint(POINT(int(x), int(y))))
        return bool(hwnd) and self._belongs_to_us(hwnd)

    def _double_click(self, kind: str, x: int, y: int, tick: int) -> bool:
        prev = self._click_prev.get(kind)
        if not prev:
            return False
        elapsed = (int(tick) - int(prev[0])) & 0xFFFFFFFF
        if elapsed > int(user32.GetDoubleClickTime() or 500):
            return False
        return abs(int(x) - int(prev[1])) <= abs(int(user32.GetSystemMetrics(SM_CXDOUBLECLK) or 4)) and abs(int(y) - int(prev[2])) <= abs(int(user32.GetSystemMetrics(SM_CYDOUBLECLK) or 4))

    def _capture_focus(self, x: int, y: int) -> int:
        under = hwnd_int(user32.WindowFromPoint(POINT(int(x), int(y))))
        caret = focus = active = 0
        info = GUITHREADINFO()
        info.cbSize = ctypes.sizeof(GUITHREADINFO)
        if user32.GetGUIThreadInfo(0, ctypes.byref(info)):
            caret = hwnd_int(info.hwndCaret)
            focus = hwnd_int(info.hwndFocus)
            active = hwnd_int(info.hwndActive)
        foreground = hwnd_int(user32.GetForegroundWindow())
        for value in (caret, under, focus, active, foreground):
            if value and not self._belongs_to_us(value):
                return value
        return 0

    def _mouse_hook_proc(self, nCode, wParam, lParam):
        if nCode < 0 or not self._mouse_hook:
            return user32.CallNextHookEx(self._mouse_hook, nCode, wParam, lParam)
        try:
            info = ctypes.cast(lParam, ctypes.POINTER(MSLLHOOKSTRUCT)).contents
            if int(info.dwExtraInfo) == RIGHT_MARK or int(info.flags) & LLMHF_INJECTED:
                return user32.CallNextHookEx(self._mouse_hook, nCode, wParam, lParam)
            msg = int(wParam)
            x, y = int(info.pt.x), int(info.pt.y)
            tick = int(info.time)
            if msg == WM_LBUTTONDOWN and self.config.get("dblclick_left_paste", True):
                if self._point_is_ours(x, y):
                    self._click_prev["left"] = None
                elif self._double_click("left", x, y, tick):
                    self._click_prev["left"] = None
                    self._pending_paste = True
                    if self.hwnd:
                        user32.PostMessageW(self.hwnd, WM_APP_DBL, 0, 0)
                else:
                    self._click_prev["left"] = (tick, x, y)
            elif self.config.get("dblclick_right_copy", True) and self._on_right_button(msg, x, y, tick):
                return 1
        except Exception:
            log_exc()
        return user32.CallNextHookEx(self._mouse_hook, nCode, wParam, lParam)

    def _run_pending_clicks(self) -> None:
        paste = self._pending_paste
        copy = self._pending_copy
        replay = self._pending_replay
        replay_down = self._pending_replay_down
        drag_up = self._pending_drag_up
        target = self._copy_hwnd
        self._pending_paste = False
        self._pending_copy = False
        self._pending_replay = False
        self._pending_replay_down = False
        self._pending_drag_up = False
        try:
            if replay:
                self._replay_right_click()
            elif replay_down and drag_up:
                self._send_right_button(True, True, [(self._right_x, self._right_y), (self._right_up_x, self._right_up_y)])
            elif replay_down:
                self._send_right_button(True, False)
            if paste and self.config.get("dblclick_left_paste", True):
                send_hotkey(["ctrl"], "v")
            if copy and self.config.get("dblclick_right_copy", True):
                self._copy_selection(target)
        except Exception:
            log_exc()

    def _right_near(self, x: int, y: int) -> bool:
        limit_x = abs(int(user32.GetSystemMetrics(SM_CXDOUBLECLK) or 4))
        limit_y = abs(int(user32.GetSystemMetrics(SM_CYDOUBLECLK) or 4))
        return abs(int(x) - self._right_x) <= limit_x and abs(int(y) - self._right_y) <= limit_y

    def _right_in_time(self, tick: int) -> bool:
        elapsed = (int(tick) - int(self._right_tick)) & 0xFFFFFFFF
        return elapsed <= int(user32.GetDoubleClickTime() or 500)

    def _arm_right_timer(self, now: int) -> None:
        if not self.hwnd:
            return
        limit = int(user32.GetDoubleClickTime() or 500)
        elapsed = (int(now) - int(self._right_tick)) & 0xFFFFFFFF
        delay = max(1, limit - elapsed)
        user32.SetTimer(self.hwnd, TIMER_RIGHT_CLICK, delay, None)
        self._right_timer = True

    def _kill_right_timer(self) -> None:
        if self._right_timer and self.hwnd:
            user32.KillTimer(self.hwnd, TIMER_RIGHT_CLICK)
        self._right_timer = False

    def _post_click_work(self) -> None:
        if self.hwnd:
            user32.PostMessageW(self.hwnd, WM_APP_DBL, 0, 0)

    def _on_right_button(self, msg: int, x: int, y: int, tick: int) -> bool:
        if msg == WM_RBUTTONDOWN:
            if self._right_cooldown and self._right_in_time_from(self._right_cooldown, tick):
                return False
            self._right_cooldown = 0
            if self._right_state == "wait" and self._right_near(x, y) and self._right_in_time(tick):
                self._kill_right_timer()
                self._right_state = "second"
                return True
            if self._right_state == "wait":
                self._kill_right_timer()
                self._pending_replay = True
                self._begin_right_hold(x, y, tick)
                self._post_click_work()
                return True
            if self._right_state == "drag":
                return False
            if self._point_is_ours(x, y):
                return False
            self._begin_right_hold(x, y, tick)
            return True
        if msg == WM_RBUTTONUP and self._right_state == "held":
            if self._right_near(x, y):
                self._right_state = "wait"
                self._arm_right_timer(tick)
            else:
                self._release_right_drag(x, y)
            return True
        if msg == WM_RBUTTONUP and self._right_state == "second":
            self._right_state = "idle"
            self._right_cooldown = tick
            self._pending_copy = True
            self._post_click_work()
            return True
        if msg == WM_RBUTTONUP and self._right_state == "drag":
            if self._pending_replay_down:
                self._right_up_x, self._right_up_y = x, y
                self._pending_drag_up = True
                self._right_state = "idle"
                return True
            self._right_state = "idle"
            return False
        if msg == WM_MOUSEMOVE and self._right_state == "held" and not self._right_near(x, y):
            self._right_state = "drag"
            self._pending_replay_down = True
            self._post_click_work()
            return True
        return False

    def _begin_right_hold(self, x: int, y: int, tick: int) -> None:
        self._copy_hwnd = self._capture_focus(x, y)
        self._right_x, self._right_y, self._right_tick = x, y, tick
        self._right_state = "held"

    def _right_in_time_from(self, start: int, tick: int) -> bool:
        elapsed = (int(tick) - int(start)) & 0xFFFFFFFF
        return elapsed <= int(user32.GetDoubleClickTime() or 500)

    def _release_right_drag(self, x: int, y: int) -> None:
        self._right_up_x, self._right_up_y = x, y
        self._right_state = "idle"
        self._pending_replay_down = True
        self._pending_drag_up = True
        self._post_click_work()

    def _finish_right_click(self) -> None:
        self._kill_right_timer()
        if self._right_state == "wait":
            self._right_state = "idle"
            self._replay_right_click()

    def _send_right_button(self, down: bool, up: bool, points: list[tuple[int, int]] | None = None) -> None:
        steps = [(down, MOUSEEVENTF_RIGHTDOWN), (up, MOUSEEVENTF_RIGHTUP)]
        chosen = [(flag, point) for (enabled, flag), point in zip(steps, points or [None, None]) if enabled]
        if not chosen:
            return
        events = []
        for flag, point in chosen:
            event = INPUT()
            event.type = INPUT_MOUSE
            event.mi.dwFlags = flag
            event.mi.dwExtraInfo = RIGHT_MARK
            if point is not None:
                event.mi.dx, event.mi.dy = self._absolute_point(point[0], point[1])
                event.mi.dwFlags |= MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_VIRTUALDESK
            events.append(event)
        array = (INPUT * len(events))(*events)
        user32.SendInput(len(events), array, ctypes.sizeof(INPUT))

    def _absolute_point(self, x: int, y: int) -> tuple[int, int]:
        origin_x = int(user32.GetSystemMetrics(SM_XVIRTUALSCREEN))
        origin_y = int(user32.GetSystemMetrics(SM_YVIRTUALSCREEN))
        width = max(1, int(user32.GetSystemMetrics(SM_CXVIRTUALSCREEN)) - 1)
        height = max(1, int(user32.GetSystemMetrics(SM_CYVIRTUALSCREEN)) - 1)
        nx = int(round((int(x) - origin_x) * 65535 / width))
        ny = int(round((int(y) - origin_y) * 65535 / height))
        return max(0, min(65535, nx)), max(0, min(65535, ny))

    def _replay_right_click(self) -> None:
        origin = (self._right_x, self._right_y)
        self._send_right_button(True, True, [origin, origin])

    def _copy_selection(self, target: int) -> None:
        hwnd = int(target or 0)
        if not hwnd or not user32.IsWindow(hwnd):
            return
        user32.SendMessageTimeoutW(hwnd, WM_COPY, 0, 0, SMTO_ABORTIFHUNG, 200, ctypes.byref(ctypes.c_size_t()))
        root = hwnd_int(user32.GetAncestor(hwnd, GA_ROOT)) or hwnd
        foreground = hwnd_int(user32.GetForegroundWindow())
        foreground_root = hwnd_int(user32.GetAncestor(foreground, GA_ROOT)) if foreground else 0
        if root == foreground_root:
            send_hotkey(["ctrl"], "c")

    def open_click_settings(self) -> None:
        existing = self._gear_win
        if existing is not None:
            try:
                if existing.winfo_exists():
                    existing.lift()
                    existing.focus_force()
                    return
            except tk.TclError:
                pass
        self._begin_modal()
        win = tk.Toplevel(self.root)
        self._gear_win = win
        win.title("連點")
        win.resizable(False, False)
        win.attributes("-topmost", True)
        win.configure(bg="#f6f7f8")
        body = tk.Frame(win, bg="#f6f7f8", padx=16, pady=14)
        body.pack()
        left_var = tk.BooleanVar(value=bool(self.config.get("dblclick_left_paste", True)))
        right_var = tk.BooleanVar(value=bool(self.config.get("dblclick_right_copy", True)))

        def apply() -> None:
            self.config["dblclick_left_paste"] = bool(left_var.get())
            self.config["dblclick_right_copy"] = bool(right_var.get())
            self._save()

        tk.Label(body, text="連點", bg="#f6f7f8", font=("Microsoft JhengHei UI", 12, "bold")).pack(anchor="w")
        tk.Checkbutton(
            body,
            text="左鍵連點貼上    Ctrl+V",
            variable=left_var,
            command=apply,
            bg="#f6f7f8",
            activebackground="#f6f7f8",
            font=FONT_UI,
            anchor="w",
        ).pack(anchor="w", pady=(10, 0))
        tk.Checkbutton(
            body,
            text="右鍵連點複製    Ctrl+C",
            variable=right_var,
            command=apply,
            bg="#f6f7f8",
            activebackground="#f6f7f8",
            font=FONT_UI,
            anchor="w",
        ).pack(anchor="w", pady=(4, 0))
        tk.Label(
            body,
            text="右鍵先按住。沒有第二下才開原來的選單；連點則複製已經選好的文字。",
            bg="#f6f7f8",
            fg="#5f6368",
            font=FONT_HINT,
            wraplength=280,
            justify="left",
        ).pack(anchor="w", pady=(8, 0))

        def close() -> None:
            self._gear_win = None
            if win.winfo_exists():
                win.destroy()
            self._end_modal()

        tk.Button(body, text="關閉", command=close).pack(anchor="e", pady=(12, 0))
        win.protocol("WM_DELETE_WINDOW", close)
        win.lift()
        win.focus_force()

    def _pump(self) -> None:
        if not self._alive:
            return
        try:
            if self._pending_paste or self._pending_copy:
                self._run_pending_clicks()
            if self._toggle_requested:
                self._toggle_requested = False
                self.toggle()
            if self._tray_show and self._editors <= 0:
                self._tray_show = False
                if self.is_shown():
                    self.minimize_to_tray()
                else:
                    self._in_tray = False
                    self.show()
            elif self._tray_show:
                self._tray_show = False
            if self._tray_menu and self._editors <= 0:
                self._tray_menu = False
                self._open_tray_menu()
            elif self._tray_menu:
                self._tray_menu = False
            self._watch_foreground()
            self._watch_config()
            self._watch_shortcuts()
        except Exception:
            log_exc()
        if self._alive:
            self.root.after(200, self._pump)

    def _reinforce(self) -> None:
        if not self._alive:
            return
        try:
            if self.is_shown():
                self.root.attributes("-topmost", True)
            if self.hwnd and self._editors <= 0:
                self._apply_exstyle(self.hwnd)
            self._raise_tip()
            if self._tip is not None:
                self.root.after(1, self._raise_tip)
        except Exception:
            log_exc()
        if self._alive:
            self.root.after(1500, self._reinforce)

    def _watch_config(self) -> None:
        if self._editors or self._dragging:
            return
        mtime = config_mtime()
        if mtime is None or mtime == self._mtime:
            return
        try:
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            self.config = normalize_config(data)
        except Exception:
            log_exc()
            self._mtime = mtime
            return
        self._mtime = mtime
        self.apply_opacity()
        self.relayout()
        self.register_toggle()
        if self.config.get("hidden"):
            self.hide()
        elif not self.is_shown():
            self.show()

    def _watch_shortcuts(self) -> None:
        if self._editors or self._dragging:
            return
        mtime = shortcuts_mtime()
        if mtime is None or mtime == self._shortcuts_mtime:
            return
        try:
            self.library = load_library()
            self.shortcuts = materialize(self.library)
        except Exception:
            log_exc()
            self._shortcuts_mtime = mtime
            return
        self._shortcuts_mtime = shortcuts_mtime()
        self.relayout()

    def _active_profile(self) -> dict:
        name = str(self.library.get("active") or "一般")
        for profile in self.library.get("profiles") or []:
            if profile.get("name") == name:
                return profile
        profile = empty_profile("一般")
        self.library.setdefault("profiles", []).insert(0, profile)
        self.library["active"] = "一般"
        return profile

    def _capture_active(self) -> None:
        profile = self._active_profile()
        profile["enabled"] = [item["hotkey"] for item in self.shortcuts if item.get("enabled")]
        profile["names"] = {
            item["hotkey"]: str(item.get("label") or "").strip()
            for item in self.shortcuts
            if not item.get("builtin") and str(item.get("label") or "").strip()
        }

    def _save_shortcuts(self) -> None:
        self._capture_active()
        save_library(self.library)
        self._shortcuts_mtime = shortcuts_mtime()

    def activate_group(self, name: str) -> None:
        if self._editors or name == self.library.get("active"):
            return
        if not any(item.get("name") == name for item in self.library.get("profiles") or []):
            return
        self._capture_active()
        self.library["active"] = name
        self.shortcuts = materialize(self.library)
        save_library(self.library)
        self._shortcuts_mtime = shortcuts_mtime()
        self.relayout()

    def _open_group_menu(self) -> None:
        rows = []
        active = self.library.get("active")
        for profile in self.library.get("profiles") or []:
            name = profile["name"]
            rows.append((("● " if name == active else "   ") + name, lambda chosen=name: self.activate_group(chosen)))
        rows.append(None)
        rows.append(("管理群組", self.choose_shortcuts))
        x, y = cursor_pos()
        self._open_menu(x, y, rows)

    def _drag_start(self, event) -> None:
        self._dragging = True
        self._cancel_hide()
        self._drag_dx = event.x_root - self.root.winfo_x()
        self._drag_dy = event.y_root - self.root.winfo_y()

    def _drag_move(self, event) -> None:
        mon = monitor_rect(event.x_root, event.y_root)
        width = max(self.root.winfo_width(), 1)
        height = max(self.root.winfo_height(), 1)
        x = event.x_root - self._drag_dx
        y = event.y_root - self._drag_dy
        x = max(mon[0], min(x, max(mon[0], mon[2] - width)))
        y = max(mon[1], min(y, max(mon[1], mon[3] - height)))
        self.root.geometry(f"{width}x{height}+{int(x)}+{int(y)}")

    def _drag_end(self, _event) -> None:
        self._dragging = False
        self.config["mode"] = "free"
        self.config["x"] = self.root.winfo_x()
        self.config["y"] = self.root.winfo_y()
        self._save()

    def _save(self) -> None:
        save_config(self.config)
        self._mtime = config_mtime()

    def _begin_modal(self) -> None:
        self._editors += 1
        self._cancel_hide()
        self._allow_activate(True)

    def _end_modal(self) -> None:
        self._editors = max(0, self._editors - 1)
        if self._editors == 0:
            self._apply_exstyle(self.hwnd)

    def choose_shortcuts(self) -> None:
        self._begin_modal()
        win = tk.Toplevel(self.root)
        win.title("選擇要出現的快捷鍵")
        win.geometry("640x720")
        win.attributes("-topmost", True)
        win.configure(bg="#f6f7f8")
        style = ttk.Style(win)
        style.configure("TNotebook.Tab", font=FONT_UI, padding=(12, 4))
        query = tk.StringVar()
        group_var = tk.StringVar(value=str(self.library.get("active") or "一般"))
        header = tk.Frame(win, bg="#f6f7f8")
        header.pack(fill="x", padx=12, pady=(10, 0))
        tk.Label(header, text="勾選要出現在列上的快捷鍵", bg="#f6f7f8", font=FONT_UI).pack(side="left")
        count = tk.Label(header, text="", bg="#f6f7f8", fg="#5f6368", font=FONT_HINT)
        count.pack(side="right")
        groups = tk.Frame(win, bg="#f6f7f8")
        groups.pack(fill="x", padx=12, pady=(8, 0))
        tk.Label(groups, text="群組", bg="#f6f7f8", font=FONT_UI).pack(side="left")
        combo = ttk.Combobox(groups, textvariable=group_var, state="readonly", width=16, font=FONT_UI)
        combo.pack(side="left", padx=(8, 0))
        tk.Entry(win, textvariable=query, font=FONT_UI).pack(fill="x", padx=12, pady=8)
        actions = tk.Frame(win, bg="#f6f7f8")
        actions.pack(side="bottom", fill="x", padx=12, pady=10)
        book = ttk.Notebook(win)
        book.pack(fill="both", expand=True, padx=12, pady=(0, 4))
        page_all = tk.Frame(book, bg="#f6f7f8")
        page_on = tk.Frame(book, bg="#f6f7f8")
        book.add(page_all, text="全部")
        book.add(page_on, text="已勾選")
        canvas = tk.Canvas(page_all, bg="#f6f7f8", highlightthickness=0)
        scroll = tk.Scrollbar(page_all, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        inner = tk.Frame(canvas, bg="#f6f7f8")
        window_id = canvas.create_window((0, 0), window=inner, anchor="nw")
        variables: list[tuple[str, tk.BooleanVar, dict, bool]] = []
        sections: list[dict] = []
        rename_job: dict[str, str] = {}
        state = {"building": False}

        def refresh_groups() -> None:
            combo["values"] = [item["name"] for item in self.library.get("profiles") or []]
            group_var.set(str(self.library.get("active") or "一般"))

        def refresh_count() -> None:
            checked = sum(1 for item in self.shortcuts if item.get("enabled"))
            count.configure(text=f"{checked} / {len(self.shortcuts)}")

        def checked_only() -> bool:
            try:
                return book.index(book.select()) == 1
            except tk.TclError:
                return False

        def mount(_event=None) -> None:
            parent = page_on if checked_only() else page_all
            scroll.pack_forget()
            canvas.pack_forget()
            scroll.pack(in_=parent, side="right", fill="y")
            canvas.pack(in_=parent, side="left", fill="both", expand=True)
            apply_filter()

        def apply_filter(*_args) -> None:
            if state["building"]:
                return
            needle = query.get().strip().lower()
            only = checked_only()
            for child in inner.winfo_children():
                child.pack_forget()
            shown = False
            for info in sections:
                visible = []
                for row, search, var in info["rows"]:
                    if needle and needle not in search["text"]:
                        continue
                    if only and not var.get():
                        continue
                    visible.append(row)
                if not visible:
                    continue
                shown = True
                info["header"].pack(anchor="w", pady=(8, 2))
                for row in visible:
                    row.pack(fill="x")
            if not shown:
                empty.pack(anchor="w", pady=12)

        def flush() -> None:
            by_id = {item["id"]: item for item in self.shortcuts}
            for id_, var, search, builtin in variables:
                item = by_id.get(id_)
                if item is None:
                    continue
                if not builtin and search.get("name") is not None:
                    item["label"] = str(search["name"].get()).strip()
                item["enabled"] = bool(var.get())
            self._capture_active()

        def apply_now() -> None:
            if state["building"]:
                return
            flush()
            save_library(self.library)
            self._shortcuts_mtime = shortcuts_mtime()
            refresh_count()
            self.relayout()
            apply_filter()

        def commit_name(item: dict, name_var: tk.StringVar) -> None:
            rename_job.pop(item["id"], None)
            if state["building"] or all(current is not item for current in self.shortcuts):
                return
            item["label"] = name_var.get().strip()
            self._save_shortcuts()
            if item.get("enabled"):
                self.relayout()

        def schedule_name(item: dict, name_var: tk.StringVar) -> None:
            previous = rename_job.get(item["id"])
            if previous:
                try:
                    win.after_cancel(previous)
                except tk.TclError:
                    pass
            rename_job[item["id"]] = win.after(200, lambda current=item, source=name_var: commit_name(current, source))

        def cancel_renames() -> None:
            for job in rename_job.values():
                try:
                    win.after_cancel(job)
                except tk.TclError:
                    pass
            rename_job.clear()

        empty = tk.Label(inner, text="這個頁籤沒有符合的快捷鍵", bg="#f6f7f8", fg="#5f6368", font=FONT_UI)

        def rebuild() -> None:
            state["building"] = True
            cancel_renames()
            for child in list(inner.winfo_children()):
                if child is not empty:
                    child.destroy()
            variables.clear()
            sections.clear()
            group = None
            section: dict | None = None
            for item in self.shortcuts:
                group_name = item["group"]
                if group_name != group:
                    group = group_name
                    title = tk.Label(
                        inner,
                        text=group_name,
                        bg="#f6f7f8",
                        fg="#174ea6",
                        font=("Microsoft JhengHei UI", 10, "bold"),
                    )
                    section = {"header": title, "rows": []}
                    sections.append(section)
                shown = format_hotkey(item["hotkey"])
                search = {"text": f"{item.get('label') or ''} {shown}".lower(), "name": None}
                row = tk.Frame(inner, bg="#f6f7f8")
                var = tk.BooleanVar(value=bool(item.get("enabled")))
                tick = tk.Checkbutton(
                    row,
                    text=item["label"] if item.get("builtin") else "",
                    variable=var,
                    bg="#f6f7f8",
                    activebackground="#f6f7f8",
                    font=FONT_UI,
                    anchor="w",
                    width=14 if item.get("builtin") else 0,
                    command=apply_now,
                )
                tick.pack(side="left")
                if not item.get("builtin"):
                    name_var = tk.StringVar(value=item.get("label") or "")
                    search["name"] = name_var
                    entry = tk.Entry(row, textvariable=name_var, font=FONT_UI, width=14)
                    entry.pack(side="left", padx=(0, 6))
                    name_var.trace_add(
                        "write",
                        lambda *_args, current=item, source=name_var, box=search: (
                            box.update({"text": f"{source.get()} {format_hotkey(current['hotkey'])}".lower()}),
                            schedule_name(current, source),
                        ),
                    )
                tk.Label(row, text=shown, bg="#f6f7f8", fg="#5f6368", font=FONT_HINT, anchor="w").pack(side="left")
                variables.append((item["id"], var, search, bool(item.get("builtin"))))
                section["rows"].append((row, search, var))
            state["building"] = False
            refresh_groups()
            refresh_count()
            apply_filter()
            canvas.yview_moveto(0)

        def use_group(name: str) -> None:
            if state["building"] or name == self.library.get("active"):
                return
            if not any(item.get("name") == name for item in self.library.get("profiles") or []):
                return
            flush()
            self.library["active"] = name
            self.shortcuts = materialize(self.library)
            save_library(self.library)
            self._shortcuts_mtime = shortcuts_mtime()
            self.relayout()
            rebuild()

        def add_group() -> None:
            name = simpledialog.askstring("新增群組", "應用程式名稱", parent=win)
            if not name or not str(name).strip():
                return
            name = str(name).strip()
            if any(item.get("name") == name for item in self.library.get("profiles") or []):
                messagebox.showerror("群組", "這個名稱已經有了。", parent=win)
                return
            flush()
            source = next((item for item in self.library["profiles"] if item.get("name") == "一般"), empty_profile("一般"))
            self.library["profiles"].append(empty_profile(name, list(source.get("enabled") or []), dict(source.get("names") or {})))
            self.library["active"] = name
            self.shortcuts = materialize(self.library)
            save_library(self.library)
            self._shortcuts_mtime = shortcuts_mtime()
            self.relayout()
            rebuild()

        def delete_group() -> None:
            name = str(self.library.get("active") or "")
            if name in BUILTIN_GROUPS:
                messagebox.showinfo("群組", "一般和瀏覽器不能刪除。", parent=win)
                return
            if not messagebox.askyesno("群組", f"刪除「{name}」？", parent=win):
                return
            self.library["profiles"] = [item for item in self.library["profiles"] if item.get("name") != name]
            self.library["active"] = "一般"
            self.shortcuts = materialize(self.library)
            save_library(self.library)
            self._shortcuts_mtime = shortcuts_mtime()
            self.relayout()
            rebuild()

        def save_file() -> None:
            flush()
            path = filedialog.asksaveasfilename(
                parent=win,
                title="儲存快捷鍵設定",
                defaultextension=".json",
                filetypes=[("JSON", "*.json")],
                initialfile="快捷鍵設定.json",
            )
            if not path:
                return
            Path(path).write_text(json.dumps(self.library, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        def load_file() -> None:
            path = filedialog.askopenfilename(
                parent=win,
                title="載入快捷鍵設定",
                filetypes=[("JSON", "*.json")],
            )
            if not path:
                return
            try:
                data = json.loads(Path(path).read_text(encoding="utf-8"))
            except Exception:
                messagebox.showerror("載入", "這個檔案讀不起來。", parent=win)
                return
            if isinstance(data, dict) and isinstance(data.get("profiles"), list):
                library = normalize_library(data)
            elif isinstance(data, dict) and "shortcuts" in data:
                library = library_from_legacy(data)
            else:
                messagebox.showerror("載入", "這不是快捷鍵設定檔。", parent=win)
                return
            self.library = library
            self.shortcuts = materialize(self.library)
            save_library(self.library)
            self._shortcuts_mtime = shortcuts_mtime()
            self.relayout()
            rebuild()

        def on_group(_event=None) -> None:
            use_group(group_var.get())

        query.trace_add("write", apply_filter)
        combo.bind("<<ComboboxSelected>>", on_group)
        book.bind("<<NotebookTabChanged>>", mount)
        tk.Button(groups, text="新增", command=add_group).pack(side="left", padx=(8, 0))
        tk.Button(groups, text="刪除", command=delete_group).pack(side="left", padx=6)

        def on_configure(_event=None) -> None:
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_canvas(event) -> None:
            canvas.itemconfigure(window_id, width=event.width)

        def on_wheel(event) -> None:
            canvas.yview_scroll(int(-event.delta / 120), "units")

        inner.bind("<Configure>", on_configure)
        canvas.bind("<Configure>", on_canvas)
        win.bind("<MouseWheel>", on_wheel)

        def set_all(value: bool) -> None:
            for _id, var, _search, builtin in variables:
                if builtin:
                    var.set(value)
            apply_now()

        def close() -> None:
            cancel_renames()
            flush()
            save_library(self.library)
            self._shortcuts_mtime = shortcuts_mtime()
            if win.winfo_exists():
                win.destroy()
            self._end_modal()
            self.relayout()

        tk.Button(actions, text="全部顯示", command=lambda: set_all(True)).pack(side="left")
        tk.Button(actions, text="全部隱藏", command=lambda: set_all(False)).pack(side="left", padx=6)
        tk.Button(actions, text="儲存", command=save_file).pack(side="left", padx=(12, 0))
        tk.Button(actions, text="載入", command=load_file).pack(side="left", padx=6)
        tk.Button(actions, text="關閉", command=close).pack(side="right")
        win.protocol("WM_DELETE_WINDOW", close)
        rebuild()
        win.lift()
        win.focus_force()

    def set_toggle_hotkey(self) -> None:
        current = str(self.config.get("toggle_hotkey") or "ctrl+alt+shift+h")
        chosen = self._ask_chord("顯示／隱藏熱鍵", current)
        if not chosen:
            return
        self.config["toggle_hotkey"] = chosen
        self._save()
        self.register_toggle()
        if not self._hotkey_ok:
            messagebox.showwarning("熱鍵", f"沒有登記到 {format_hotkey(chosen)}，可能被其他程式占用。")

    def _ask_chord(self, title: str, initial: str) -> str | None:
        self._begin_modal()
        result: dict[str, str | None] = {"value": None}
        state = {"run": False, "after": None, "armed": False, "previous": initial}
        win = tk.Toplevel(self.root)
        win.title(title)
        win.resizable(False, False)
        win.attributes("-topmost", True)
        win.configure(bg="#f6f7f8")
        body = tk.Frame(win, bg="#f6f7f8", padx=16, pady=14)
        body.pack()
        hot_var = tk.StringVar(value=initial)
        tk.Label(body, text="快捷鍵", bg="#f6f7f8", font=FONT_UI).grid(row=0, column=0, sticky="w")
        entry = tk.Entry(body, textvariable=hot_var, font=("Consolas", 12), width=28)
        entry.grid(row=1, column=0, pady=(2, 4))
        record = tk.Button(body, text="錄製", font=FONT_UI)
        record.grid(row=1, column=1, padx=(8, 0))
        tk.Label(
            body,
            text="例子：ctrl+alt+shift+h、win+shift+s。加號鍵請寫 plus。",
            bg="#f6f7f8",
            fg="#5f6368",
            font=FONT_HINT,
            wraplength=320,
            justify="left",
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(0, 10))

        def stop() -> None:
            state["run"] = False
            if state["after"] is not None and win.winfo_exists():
                try:
                    win.after_cancel(state["after"])
                except tk.TclError:
                    pass
            state["after"] = None
            if entry.winfo_exists():
                entry.configure(state="normal")
            if record.winfo_exists():
                record.configure(text="錄製")

        def poll() -> None:
            if not state["run"] or not win.winfo_exists():
                return
            if key_is_down(0x1B):
                hot_var.set(state["previous"])
                stop()
                return
            mods = [name for name in MOD_ORDER if key_is_down(MOD_VK[name]) or (name == "win" and key_is_down(0x5C))]
            pressed = next((name for name, vk in KEY_VK.items() if key_is_down(vk)), None)
            if not state["armed"]:
                if pressed is None and not key_is_down(0x1B):
                    state["armed"] = True
                else:
                    hot_var.set("放開按鍵後開始…")
                state["after"] = win.after(30, poll)
                return
            if pressed:
                hot_var.set("+".join([*mods, pressed]))
                stop()
                return
            hot_var.set("+".join([*mods, "…"]) if mods else "請按下組合鍵…")
            state["after"] = win.after(30, poll)

        def start() -> None:
            if state["run"]:
                hot_var.set(state["previous"])
                stop()
                return
            state["previous"] = hot_var.get()
            state["run"] = True
            state["armed"] = False
            entry.configure(state="disabled")
            record.configure(text="取消")
            poll()

        record.configure(command=start)

        def close(ok: bool) -> None:
            stop()
            if ok:
                try:
                    result["value"] = canonical_hotkey(hot_var.get())
                except ValueError:
                    messagebox.showerror(title, "看不懂這個快捷鍵。", parent=win)
                    return
            if win.winfo_exists():
                win.destroy()
            self._end_modal()

        buttons = tk.Frame(body, bg="#f6f7f8")
        buttons.grid(row=3, column=0, columnspan=2, sticky="e")
        tk.Button(buttons, text="取消", command=lambda: close(False)).pack(side="right")
        tk.Button(buttons, text="確定", command=lambda: close(True)).pack(side="right", padx=(0, 6))
        win.protocol("WM_DELETE_WINDOW", lambda: close(False))
        win.lift()
        entry.focus_set()
        win.grab_set()
        self.root.wait_window(win)
        return result["value"]

    def hide_spec(self, spec: dict) -> None:
        for item in self.shortcuts:
            if item["id"] == spec["id"]:
                item["enabled"] = False
                break
        self._save_shortcuts()
        self.relayout()

    def _close_menu(self) -> None:
        menu = self._menu
        self._menu = None
        if menu is not None:
            try:
                if menu.winfo_exists():
                    menu.destroy()
            except tk.TclError:
                pass

    def _open_menu(self, x: int, y: int, rows: list) -> None:
        self._close_menu()
        win = tk.Toplevel(self.root)
        self._menu = win
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        win.configure(bg="#5f6368")
        frame = tk.Frame(win, bg="#2b2d31")
        frame.pack(padx=1, pady=1)
        state = {"armed": False}

        def run(command) -> None:
            self._close_menu()
            self.root.after(20, command)

        for row in rows:
            if row is None:
                tk.Frame(frame, bg="#5f6368", height=1).pack(fill="x", padx=8, pady=4)
                continue
            text, command = row
            item = tk.Label(
                frame,
                text=text,
                bg="#2b2d31",
                fg=TEXT,
                font=FONT_UI,
                anchor="w",
                padx=14,
                pady=6,
                cursor="hand2" if command else "arrow",
                takefocus=False,
            )
            item.pack(fill="x")
            if command is None:
                item.configure(fg=HINT)
                continue
            item.bind("<Enter>", lambda _event, widget=item: widget.configure(bg="#3c4048"))
            item.bind("<Leave>", lambda _event, widget=item: widget.configure(bg="#2b2d31"))
            item.bind("<ButtonRelease-1>", lambda _event, cmd=command: run(cmd))
        win.update_idletasks()
        width = win.winfo_reqwidth()
        height = win.winfo_reqheight()
        mon = monitor_rect(x, y)
        if x + width > mon[2]:
            x = max(mon[0], mon[2] - width)
        if y + height > mon[3]:
            y = max(mon[1], y - height)
        win.geometry(f"+{int(x)}+{int(y)}")

        def watch() -> None:
            if not win.winfo_exists():
                return
            down = key_is_down(0x01) or key_is_down(0x02)
            if not state["armed"]:
                if not down:
                    state["armed"] = True
            elif down:
                point_x, point_y = cursor_pos()
                left = win.winfo_rootx()
                top = win.winfo_rooty()
                outside = not (left <= point_x < left + win.winfo_width() and top <= point_y < top + win.winfo_height())
                if outside:
                    self._close_menu()
                    return
            if state["armed"] and key_is_down(0x1B):
                self._close_menu()
                return
            win.after(30, watch)

        win.after(30, watch)

    def _bar_rows(self) -> list:
        try:
            toggle = format_hotkey(self.config.get("toggle_hotkey") or "")
        except ValueError:
            toggle = str(self.config.get("toggle_hotkey") or "")
        note = f"顯示／隱藏：{toggle}"
        if not self._hotkey_ok:
            note += "（未登記）"
        return [
            (note, None),
            ("設定這個熱鍵", self.set_toggle_hotkey),
            None,
            ("選擇要出現的快捷鍵", self.choose_shortcuts),
            ("切換群組", self._open_group_menu),
            ("貼到螢幕上方", self.dock_top),
            ("出現在滑鼠右邊", self.follow_cursor),
            ("連點設定", self.open_click_settings),
            ("縮到小圖示", self.minimize_to_tray),
            None,
            ("結束程式", self.quit),
        ]

    def _open_bar_menu(self, event) -> None:
        self._open_menu(event.x_root, event.y_root, self._bar_rows())

    def _open_key_menu(self, event, spec: dict) -> None:
        rows = [("不要顯示這個", lambda item=spec: self.hide_spec(item))]
        self._open_menu(event.x_root, event.y_root, rows)

    def _ensure_tray(self) -> None:
        if self._tray_added or not self.hwnd:
            return
        nid = NOTIFYICONDATAW()
        nid.cbSize = ctypes.sizeof(NOTIFYICONDATAW)
        nid.hWnd = self.hwnd
        nid.uID = 1
        nid.uFlags = NIF_MESSAGE | NIF_ICON | NIF_TIP | NIF_SHOWTIP
        nid.uCallbackMessage = WM_TRAY
        try:
            icon = make_tray_icon()
        except Exception:
            log_exc()
            icon = 0
        if not icon:
            icon = int(user32.LoadIconW(None, ctypes.cast(32512, wintypes.LPCWSTR)) or 0)
        self._tray_icon = icon
        nid.hIcon = icon
        nid.szTip = "快捷列"
        nid.uVersion = 4
        if not shell32.Shell_NotifyIconW(NIM_ADD, ctypes.byref(nid)):
            try:
                with LOG_PATH.open("a", encoding="utf-8") as handle:
                    handle.write(
                        f"\ntray add failed {ctypes.get_last_error()} size {ctypes.sizeof(NOTIFYICONDATAW)}\n"
                    )
            except Exception:
                pass
            return
        shell32.Shell_NotifyIconW(NIM_SETVERSION, ctypes.byref(nid))
        self._nid = nid
        self._tray_added = True

    def _remove_tray(self) -> None:
        if not self._tray_added or self._nid is None:
            return
        shell32.Shell_NotifyIconW(NIM_DELETE, ctypes.byref(self._nid))
        self._tray_added = False
        if self._tray_icon:
            user32.DestroyIcon.argtypes = [wintypes.HICON]
            user32.DestroyIcon.restype = wintypes.BOOL
            user32.DestroyIcon(self._tray_icon)
            self._tray_icon = 0

    def _open_tray_menu(self) -> None:
        x, y = cursor_pos()
        if self.is_shown():
            rows = [("縮到小圖示", self.minimize_to_tray), ("結束程式", self.quit)]
        else:
            rows = [("顯示快捷列", self.show), ("結束程式", self.quit)]
        self._open_menu(x, y, rows)

    def minimize_to_tray(self) -> None:
        self._cancel_hide()
        self._close_menu()
        self._in_tray = True
        self._ensure_tray()
        if self.is_shown():
            self.root.withdraw()

    def quit(self) -> None:
        self._alive = False
        self._cancel_hide()
        self._remove_tray()
        self.config["hidden"] = False if self._in_tray else not self.is_shown()
        try:
            self._save()
        except Exception:
            log_exc()
        try:
            self._kill_right_timer()
            self._remove_mouse_hook()
            if self.hwnd:
                user32.UnregisterHotKey(self.hwnd, HOTKEY_ID)
            if self._proc is not None:
                for hwnd, old in list(self._old_procs.items()):
                    user32.SetWindowLongPtrW(hwnd, GWLP_WNDPROC, old)
        except Exception:
            log_exc()
        self.root.destroy()


def run_check() -> int:
    expected = 40 if ctypes.sizeof(ctypes.c_void_p) == 8 else 28
    size = ctypes.sizeof(INPUT)
    print(f"INPUT size {size} (expected {expected})")
    if size != expected:
        return 1
    failed = 0
    for ident, _group, label, hotkey in CATALOG:
        try:
            parse_hotkey(hotkey)
        except ValueError:
            print("bad", ident, label, hotkey)
            failed += 1
    print(f"catalog {len(CATALOG)} failed {failed}")
    sample = [{"id": "copy", "group": "編輯", "label": "複製", "hotkey": "ctrl+c"}]
    print("dup-key", duplicate_message(sample, "ctrl-c", "別的"))
    print("dup-name", duplicate_message(sample, "ctrl+shift+k", "複製"))
    print("fresh", duplicate_message(sample, "ctrl+shift+k", "別的"))
    print("toggle", format_hotkey("ctrl-alt-shift-h"))
    mon = (0, 0, 1920, 1080)
    print("right", popup_origin(400, 500, 200, 400, mon, "right"))
    print("flip", popup_origin(1800, 500, 200, 400, mon, "right"))
    print("columns", column_count(len(CATALOG), False, mon), column_count(len(CATALOG), True, mon))
    return 1 if failed else 0


def main() -> int:
    if sys.platform != "win32":
        print("這個程式只能在 Windows 上執行。")
        return 1
    if "--check" in sys.argv:
        return run_check()
    if not acquire_mutex():
        print("快捷列已經在執行。")
        return 0
    try:
        ActionBar().run()
    except Exception:
        log_exc()
        raise
    return 0


if __name__ == "__main__":
    sys.exit(main())
