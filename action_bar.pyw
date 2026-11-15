"""螢幕快捷鍵列。

預設貼在滑鼠所在螢幕的上緣，半透明，內建常用 Windows 快捷鍵。
左鍵送出快捷鍵。Ctrl+Alt+Shift+H 顯示或隱藏。
拖 ≡ 可放到任意位置。按「鼠」會改到游標右邊直排，右邊放不下就改到左邊。
按「上」貼回螢幕上緣。工具列上的群組名稱可切換應用程式。
按「選」管理快捷鍵。一般群組列出全部快捷鍵。同一組合在不同群組可以有不同名稱。
頁籤「已勾選」只列出有打勾的鍵。可儲存或載入目前的勾選。勾選後立刻套用。
按 — 縮到工作列旁的小圖示。按 × 結束程式。按齒輪可開關左鍵連點貼上、右鍵連點複製。
快捷列最上方第一列是 PgUp、PgDn、Home、End、上、下，第二列是 Bksp、Del、Tab、Enter、左、右。
其下以分隔線隔出六個格子，可從清單把快捷鍵拖進去。滑鼠停在常用鍵或格子上時，名稱以黑底白字顯示，直到滑鼠離開。

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


PIN_COUNT = 6
DRAG_START_PX = 6


def normalize_pins(raw) -> list[str]:
    cells = list(raw) if isinstance(raw, (list, tuple)) else []
    cells = (cells + [""] * PIN_COUNT)[:PIN_COUNT]
    pins: list[str] = []
    for cell in cells:
        text = str(cell or "").strip()
        try:
            pins.append(canonical_hotkey(text) if text else "")
        except ValueError:
            pins.append("")
    seen: set[str] = set()
    for index in range(PIN_COUNT - 1, -1, -1):
        if not pins[index]:
            continue
        if pins[index] in seen:
            pins[index] = ""
        else:
            seen.add(pins[index])
    return pins


def set_pin(pins: list, index: int, value) -> list:
    if not 0 <= index < PIN_COUNT:
        return list(pins)
    blank = 0 if isinstance(value, int) else ""
    result = [blank if cell == value else cell for cell in pins]
    result[index] = value
    return result


def pin_at(x: int, y: int, rects: list, slop: int = 2) -> int:
    for index, rect in enumerate(rects):
        if rect is None:
            continue
        left, top, right, bottom = rect
        if left - slop <= x < right + slop and top - slop <= y < bottom + slop:
            return index
    return -1


def pin_face(label: str, main_key: str) -> str:
    label = (label or "").strip()
    if not label:
        return main_key
    return label if len(label) <= 3 else label[:2] + "…"


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


def empty_profile(
    name: str,
    enabled: list[str] | None = None,
    names: dict | None = None,
    pins: list[str] | None = None,
) -> dict:
    return {"name": name, "enabled": list(enabled or []), "names": dict(names or {}), "pins": normalize_pins(pins)}


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
    return {"name": name, "enabled": enabled, "names": names, "pins": normalize_pins(item.get("pins"))}


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


SEED_GROUPS = (
    (1, "編輯"),
    (2, "檔案總管"),
    (3, "視窗"),
    (4, "系統"),
    (5, "瀏覽器"),
    (6, "媒體"),
    (7, "常用"),
    (8, "自訂"),
)
CATALOG_GROUP_NAME = {"虛擬桌面": "視窗"}
MODIFIER_KEYCODES = {16, 17, 18, 91, 92, 160, 161, 162, 163, 164, 165}
BACKUP_PATH = APP_DIR / "shortcuts.v1.bak.json"
VK_TO_KEY = {}
for _name, _vk in KEY_VK.items():
    VK_TO_KEY.setdefault(_vk, _name)


def log_note(text: str) -> None:
    try:
        with LOG_PATH.open("a", encoding="utf-8") as handle:
            handle.write(text.rstrip() + "\n")
    except Exception:
        pass


def seed_ids() -> dict[str, int]:
    return {name: gid for gid, name in SEED_GROUPS}


def group_by_id(library: dict, gid: int) -> dict | None:
    for group in library.get("groups") or []:
        if group.get("id") == gid:
            return group
    return None


def group_name_of(library: dict, gid: int) -> str:
    group = group_by_id(library, gid)
    return str(group.get("name") or "") if group else ""


def shortcut_by_id(library: dict, sid: int) -> dict | None:
    for item in library.get("shortcuts") or []:
        if item.get("id") == sid:
            return item
    return None


def normalize_pin_ids(raw, valid: set[int]) -> list[int]:
    cells = list(raw) if isinstance(raw, (list, tuple)) else []
    cells = (cells + [0] * PIN_COUNT)[:PIN_COUNT]
    pins: list[int] = []
    for cell in cells:
        try:
            sid = int(cell)
        except (TypeError, ValueError):
            sid = 0
        pins.append(sid if sid in valid else 0)
    seen: set[int] = set()
    for index in range(PIN_COUNT - 1, -1, -1):
        if not pins[index]:
            continue
        if pins[index] in seen:
            pins[index] = 0
        else:
            seen.add(pins[index])
    return pins


def fresh_library() -> dict:
    ids = seed_ids()
    shortcuts: list[dict] = []
    next_sid = 1
    for _id, group, label, hotkey in CATALOG:
        gid = ids[CATALOG_GROUP_NAME.get(group, group)]
        shortcuts.append(
            {"id": next_sid, "hotkey": canonical_hotkey(hotkey), "name": label, "groups": [gid]}
        )
        next_sid += 1
    library = {
        "version": 2,
        "next_group_id": 9,
        "next_shortcut_id": next_sid,
        "active_group": 0,
        "groups": [{"id": gid, "name": name} for gid, name in SEED_GROUPS],
        "shortcuts": shortcuts,
        "pins": [0] * PIN_COUNT,
    }
    library["active_group"] = first_occupied(library)
    return library


def first_occupied(library: dict) -> int:
    counts: dict[int, int] = {}
    for item in library.get("shortcuts") or []:
        for gid in item.get("groups") or []:
            counts[int(gid)] = counts.get(int(gid), 0) + 1
    for group in library.get("groups") or []:
        if counts.get(int(group["id"])):
            return int(group["id"])
    groups = library.get("groups") or []
    return int(groups[0]["id"]) if groups else 0


def members_of(library: dict, group_id: int) -> list[dict]:
    name = group_name_of(library, group_id)
    rows: list[dict] = []
    for item in library.get("shortcuts") or []:
        if group_id not in (item.get("groups") or []):
            continue
        rows.append(
            {
                "id": item["id"],
                "group": name,
                "label": str(item.get("name") or "").strip(),
                "hotkey": item["hotkey"],
                "builtin": False,
                "enabled": True,
            }
        )
    return rows


def materialize(library: dict) -> list[dict]:
    return members_of(library, int(library.get("active_group") or 0))


def visible_pairs(library: dict, group_id: int) -> list[tuple[str, str]]:
    return [(item["hotkey"], item["label"]) for item in members_of(library, group_id)]


def check_shortcut(library: dict, hotkey: str, name: str, group_ids: list[int], ignore_id: int | None = None) -> str | None:
    name = str(name or "").strip()
    for item in library.get("shortcuts") or []:
        if ignore_id is not None and item.get("id") == ignore_id:
            continue
        if item.get("hotkey") == hotkey and str(item.get("name") or "").strip() == name:
            return "已有這一筆，請在它的群組欄勾選要加入的群組。"
    for gid in group_ids:
        for item in library.get("shortcuts") or []:
            if ignore_id is not None and item.get("id") == ignore_id:
                continue
            if item.get("hotkey") == hotkey and gid in (item.get("groups") or []):
                label = str(item.get("name") or "").strip() or format_hotkey(hotkey)
                return f"「{group_name_of(library, gid)}」已有 {format_hotkey(hotkey)}（{label}）。"
    return None


def add_shortcut(library: dict, hotkey: str, name: str, group_ids: list[int]) -> str | None:
    hotkey = canonical_hotkey(hotkey)
    name = str(name or "").strip()
    groups = [int(gid) for gid in group_ids]
    error = check_shortcut(library, hotkey, name, groups)
    if error:
        return error
    sid = int(library.get("next_shortcut_id") or 1)
    library["next_shortcut_id"] = sid + 1
    library.setdefault("shortcuts", []).append({"id": sid, "hotkey": hotkey, "name": name, "groups": groups})
    return None


def update_shortcut(library: dict, sid: int, hotkey: str, name: str, group_ids: list[int]) -> str | None:
    item = shortcut_by_id(library, sid)
    if item is None:
        return "找不到這一筆。"
    hotkey = canonical_hotkey(hotkey)
    name = str(name or "").strip()
    groups = [int(gid) for gid in group_ids]
    error = check_shortcut(library, hotkey, name, groups, ignore_id=sid)
    if error:
        return error
    item["hotkey"] = hotkey
    item["name"] = name
    item["groups"] = groups
    return None


def delete_shortcut(library: dict, sid: int) -> None:
    library["shortcuts"] = [item for item in library.get("shortcuts") or [] if item.get("id") != sid]
    valid = library_pin_ids(library) | {int(sid)}
    library["pins"] = [0 if pin == sid else pin for pin in normalize_pin_ids(library.get("pins"), valid)]
    library["pins"] = normalize_pin_ids(library["pins"], library_pin_ids(library))


def group_name_taken(library: dict, name: str, ignore_id: int | None = None) -> bool:
    cleaned = str(name or "").strip()
    for group in library.get("groups") or []:
        if ignore_id is not None and group.get("id") == ignore_id:
            continue
        if str(group.get("name") or "").strip() == cleaned:
            return True
    return False


def add_group_row(library: dict, name: str) -> str | None:
    cleaned = str(name or "").strip()
    if not cleaned:
        return "請輸入群組名稱。"
    if group_name_taken(library, cleaned):
        return "這個群組名稱已經有了。"
    gid = int(library.get("next_group_id") or 1)
    library["next_group_id"] = gid + 1
    library.setdefault("groups", []).append({"id": gid, "name": cleaned})
    return None


def rename_group_row(library: dict, gid: int, name: str) -> str | None:
    group = group_by_id(library, gid)
    if group is None:
        return "找不到這個群組。"
    cleaned = str(name or "").strip()
    if not cleaned:
        return "請輸入群組名稱。"
    if group_name_taken(library, cleaned, ignore_id=gid):
        return "這個群組名稱已經有了。"
    group["name"] = cleaned
    return None


def ungrouped_if_removed(library: dict, gid: int) -> int:
    count = 0
    for item in library.get("shortcuts") or []:
        groups = [int(value) for value in item.get("groups") or []]
        if groups == [gid]:
            count += 1
    return count


def delete_group_row(library: dict, gid: int) -> str | None:
    if group_by_id(library, gid) is None:
        return "找不到這個群組。"
    for item in library.get("shortcuts") or []:
        item["groups"] = [int(value) for value in item.get("groups") or [] if int(value) != gid]
    library["groups"] = [group for group in library.get("groups") or [] if group.get("id") != gid]
    if not library["groups"]:
        new_id = int(library.get("next_group_id") or 1)
        library["next_group_id"] = new_id + 1
        library["groups"] = [{"id": new_id, "name": "常用"}]
    if int(library.get("active_group") or 0) not in {group["id"] for group in library["groups"]}:
        library["active_group"] = int(library["groups"][0]["id"])
    return None


def _positive_id(value) -> int:
    if isinstance(value, bool):
        return 0
    try:
        number = int(value)
    except (TypeError, ValueError):
        return 0
    return number if number > 0 else 0


def library_pin_ids(library: dict) -> set[int]:
    found: set[int] = set()
    for key in ("shortcuts", "retained"):
        for item in library.get(key) or []:
            if isinstance(item, dict):
                sid = _positive_id(item.get("id"))
                if sid:
                    found.add(sid)
    return found


def ensure_counters(library: dict) -> None:
    group_ids = [int(group["id"]) for group in library.get("groups") or [] if isinstance(group.get("id"), int)]
    shortcut_ids = [int(item["id"]) for item in library.get("shortcuts") or [] if isinstance(item.get("id"), int)]
    for item in library.get("retained_groups") or []:
        if isinstance(item, dict) and _positive_id(item.get("id")):
            group_ids.append(_positive_id(item.get("id")))
    for item in library.get("retained") or []:
        if isinstance(item, dict) and _positive_id(item.get("id")):
            shortcut_ids.append(_positive_id(item.get("id")))
    library["next_group_id"] = max(int(library.get("next_group_id") or 1), max(group_ids, default=0) + 1)
    library["next_shortcut_id"] = max(int(library.get("next_shortcut_id") or 1), max(shortcut_ids, default=0) + 1)


def repair_v2(data: dict) -> tuple[dict, list[str]]:
    problems: list[str] = []
    retained_groups: list = []
    seen_names: set[str] = set()
    kept_groups: list[tuple[dict, str, int]] = []
    for item in data.get("groups") or []:
        if not isinstance(item, dict):
            retained_groups.append(item)
            problems.append("略過無法讀取的群組。")
            continue
        name = str(item.get("name") or "").strip()
        if not name or name in seen_names:
            retained_groups.append(dict(item))
            problems.append(f"略過群組「{name or '未命名'}」。")
            continue
        seen_names.add(name)
        kept_groups.append((item, name, _positive_id(item.get("id"))))
    claimed_groups: set[int] = set()
    pending_groups: list[tuple[dict, str, int, int | None]] = []
    for item, name, gid in kept_groups:
        if gid and gid not in claimed_groups:
            claimed_groups.add(gid)
            pending_groups.append((item, name, gid, gid))
        else:
            pending_groups.append((item, name, gid, None))
    for item in retained_groups:
        if isinstance(item, dict):
            claimed_groups.add(_positive_id(item.get("id")))
    claimed_groups.discard(0)
    next_group = max(claimed_groups, default=0) + 1
    remap: dict[int, int] = {}
    groups: list[dict] = []
    for item, name, gid, assigned in pending_groups:
        if assigned is None:
            assigned = next_group
            next_group += 1
            problems.append(f"群組「{name}」的編號已重編為 {assigned}。")
        else:
            remap.setdefault(gid, assigned)
        row = dict(item)
        row["id"] = assigned
        row["name"] = name
        groups.append(row)
    if not groups:
        groups = [{"id": next_group, "name": "常用"}]
        next_group += 1
        problems.append("沒有群組，已暫時使用「常用」。")
    valid_groups = {int(group["id"]) for group in groups}

    retained: list = []
    parsed_shortcuts: list[tuple[dict, str, int]] = []
    for item in data.get("shortcuts") or []:
        if not isinstance(item, dict):
            retained.append(item)
            problems.append("略過無法讀取的快捷鍵。")
            continue
        try:
            hotkey = canonical_hotkey(str(item.get("hotkey") or ""))
        except ValueError:
            retained.append(dict(item))
            problems.append(f"略過無效組合：{item.get('hotkey')}")
            continue
        parsed_shortcuts.append((item, hotkey, _positive_id(item.get("id"))))
    claimed: set[int] = set()
    pending_shortcuts: list[tuple[dict, str, int | None]] = []
    for item, hotkey, sid in parsed_shortcuts:
        if sid and sid not in claimed:
            claimed.add(sid)
            pending_shortcuts.append((item, hotkey, sid))
        else:
            pending_shortcuts.append((item, hotkey, None))
    for item in retained:
        if isinstance(item, dict):
            claimed.add(_positive_id(item.get("id")))
    claimed.discard(0)
    next_shortcut = max(claimed, default=0) + 1
    shortcuts: list[dict] = []
    for item, hotkey, assigned in pending_shortcuts:
        if assigned is None:
            assigned = next_shortcut
            next_shortcut += 1
            problems.append(f"快捷鍵 {hotkey} 的編號已重編為 {assigned}。")
        linked: list[int] = []
        for value in item.get("groups") or []:
            gid = _positive_id(value)
            gid = remap.get(gid, gid)
            if gid in valid_groups and gid not in linked:
                linked.append(gid)
        row = dict(item)
        row["id"] = assigned
        row["hotkey"] = hotkey
        row["name"] = str(item.get("name") or "").strip()
        row["groups"] = linked
        shortcuts.append(row)
    valid_ids = {int(item["id"]) for item in shortcuts}
    for item in retained:
        if isinstance(item, dict):
            sid = _positive_id(item.get("id"))
            if sid:
                valid_ids.add(sid)
    active = _positive_id(data.get("active_group"))
    active = remap.get(active, active)
    if active not in valid_groups:
        active = int(groups[0]["id"])
    library = {
        key: value
        for key, value in data.items()
        if key not in {"groups", "shortcuts", "pins", "active_group", "version", "next_group_id", "next_shortcut_id"}
        and not str(key).startswith("_")
    }
    library.update(
        {
            "version": 2,
            "active_group": active,
            "groups": groups,
            "shortcuts": shortcuts,
            "pins": normalize_pin_ids(data.get("pins"), valid_ids),
            "retained": retained,
            "retained_groups": retained_groups,
        }
    )
    ensure_counters(library)
    return library, problems


def _append_custom(library: dict, hotkey: str, name: str) -> int:
    sid = int(library["next_shortcut_id"])
    library["next_shortcut_id"] = sid + 1
    library["shortcuts"].append({"id": sid, "hotkey": hotkey, "name": name, "groups": []})
    return sid


def _link(library: dict, sid: int, gid: int) -> None:
    item = shortcut_by_id(library, sid)
    if item is None or not gid:
        return
    groups = [int(value) for value in item.get("groups") or []]
    if gid not in groups:
        groups.append(gid)
    item["groups"] = groups


def migrate_v1(data) -> dict:
    if isinstance(data, dict) and isinstance(data.get("profiles"), list):
        old = normalize_library(data)
    else:
        old = library_from_legacy(data if isinstance(data, dict) else {})
    library = fresh_library()
    ids = seed_ids()
    shot = next(item["id"] for item in library["shortcuts"] if item["hotkey"] == "ctrl+f5" and item["name"] == "擷圖")
    hard = next(item["id"] for item in library["shortcuts"] if item["hotkey"] == "ctrl+f5" and item["name"] == "強制重新整理")
    catalog_hotkeys = {canonical_hotkey(hotkey) for *_rest, hotkey in ((row[0], row[1], row[2], row[3]) for row in CATALOG)}
    named: dict[str, str] = {}
    extras: set[str] = set()

    def remember(hotkey: str, name: str = "") -> None:
        if not hotkey or hotkey in catalog_hotkeys:
            return
        extras.add(hotkey)
        if name and not named.get(hotkey):
            named[hotkey] = name

    for profile in old["profiles"]:
        names = profile.get("names") or {}
        for hotkey, label in names.items():
            remember(str(hotkey), str(label or "").strip())
        for hotkey in profile.get("enabled") or []:
            remember(str(hotkey), str(names.get(hotkey) or "").strip())
        for hotkey in profile.get("pins") or []:
            if hotkey:
                remember(str(hotkey), str(names.get(hotkey) or "").strip())
    known = {item["hotkey"]: item["id"] for item in library["shortcuts"] if item["hotkey"] != "ctrl+f5"}
    for hotkey in sorted(extras, key=lambda value: (value.count("+"), value)):
        sid = _append_custom(library, hotkey, named.get(hotkey, ""))
        known[hotkey] = sid
        if named.get(hotkey):
            _link(library, sid, ids["自訂"])

    def resolve(profile_name: str, hotkey: str) -> int:
        if hotkey == "ctrl+f5":
            return hard if profile_name == "瀏覽器" else shot
        return int(known.get(hotkey) or 0)

    general = next((profile for profile in old["profiles"] if profile.get("name") == "一般"), None)
    if general is not None:
        for row in shortcuts_for(general):
            if row.get("enabled"):
                _link(library, resolve("一般", row["hotkey"]), ids["常用"])
    for profile in old["profiles"]:
        name = str(profile.get("name") or "")
        if name in ("一般", "瀏覽器"):
            continue
        gid = ids.get(name)
        if gid is None:
            gid = int(library["next_group_id"])
            library["next_group_id"] = gid + 1
            library["groups"].append({"id": gid, "name": name})
            ids[name] = gid
        for row in shortcuts_for(profile):
            if row.get("enabled"):
                _link(library, resolve(name, row["hotkey"]), gid)
    for item in library["shortcuts"]:
        if not item["groups"] and item["hotkey"] in extras:
            item["groups"] = [ids["自訂"]]
    active_name = str(old.get("active") or "一般")
    active = next((profile for profile in old["profiles"] if profile.get("name") == active_name), old["profiles"][0])
    pins: list[int] = []
    for hotkey in active.get("pins") or []:
        pins.append(resolve(active_name, str(hotkey)) if hotkey else 0)
    library["pins"] = normalize_pin_ids(pins, {item["id"] for item in library["shortcuts"]})
    library["active_group"] = ids["常用"]
    ensure_counters(library)
    return library


def save_library(library: dict) -> None:
    payload = {
        key: value
        for key, value in library.items()
        if not str(key).startswith("_") and key not in ("retained", "retained_groups")
    }
    payload["shortcuts"] = list(payload.get("shortcuts") or []) + list(library.get("retained") or [])
    payload["groups"] = list(payload.get("groups") or []) + list(library.get("retained_groups") or [])
    temporary = SHORTCUTS_PATH.with_suffix(".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(SHORTCUTS_PATH)


def open_library() -> tuple[dict, str | None]:
    if not SHORTCUTS_PATH.exists():
        return fresh_library(), None
    try:
        raw = SHORTCUTS_PATH.read_text(encoding="utf-8")
        data = json.loads(raw)
    except Exception:
        log_exc()
        return fresh_library(), "快捷鍵檔讀不起來。這次不會覆寫原檔，畫面上的是暫時資料。"
    if isinstance(data, dict):
        version = data.get("version")
        version_number = version if isinstance(version, int) and not isinstance(version, bool) else None
        shaped = isinstance(data.get("groups"), list) and isinstance(data.get("shortcuts"), list)
        if version_number is not None and version_number > 2:
            return fresh_library(), "快捷鍵檔是較新的版本。這次不會覆寫原檔，畫面上的是暫時資料。"
        if version_number == 2 or (version_number is None and shaped):
            library, problems = repair_v2(data)
            for line in problems:
                log_note(line)
            return library, None
    try:
        if not BACKUP_PATH.exists():
            BACKUP_PATH.write_text(raw, encoding="utf-8")
        library = migrate_v1(data)
        save_library(library)
        return library, None
    except Exception:
        log_exc()
        return fresh_library(), "舊的快捷鍵檔轉換失敗。這次不會覆寫原檔，請看 error.log。"


def load_library() -> dict:
    library, _message = open_library()
    return library


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
        self.library, self._library_message = open_library()
        self._library_readonly = self._library_message is not None
        self._readonly_noted = False
        self._by_id: dict[int, dict] = {}
        self._capturing = False
        self._reindex()
        self.shortcuts = materialize(self.library)
        self._mtime = config_mtime()
        self._shortcuts_mtime = shortcuts_mtime()
        self._alive = True
        self._editors = 0
        self._drag_dx = 0
        self._drag_dy = 0
        self._dragging = False
        self._key_drag = None
        self._pin_frames: list = []
        self._pin_parent = None
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
        self._tip_label = None
        self._tip_show_job = None
        self._tip_show_frame = None
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
        if self._library_message:
            self.root.after(300, lambda: messagebox.showwarning("快捷鍵", self._library_message))

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
        self._raise_ghost()

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
        self._raise_ghost()

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
        self._cancel_key_drag()
        self._hide_tip()
        for child in self.tools.winfo_children():
            child.destroy()
        for child in self.body.winfo_children():
            child.destroy()
        self._build_tools()
        specs = visible_specs(self.config, self.shortcuts)
        vertical = self.config.get("orientation") == "vertical"
        mon = self._target_monitor()
        cols = column_count(len(specs), vertical, mon, reserve=136) if specs else 1
        self._build_nav_pad().grid(row=0, column=0, columnspan=cols, padx=2, pady=(2, 4))
        if not specs:
            empty = tk.Label(self.body, text="這個群組還沒有快捷鍵，按「選」加入", bg=BAR, fg=HINT, font=FONT, padx=16, pady=12)
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
        group_name = self._active_group_name()
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
        self._pin_rule(pad, 2, (4, 3))
        self._pin_parent = pad
        self._pin_frames = []
        for index, sid in enumerate(normalize_pin_ids(self.library.get("pins"), library_pin_ids(self.library))):
            cell = self._make_pin_key(pad, index, int(sid))
            cell.grid(row=3, column=index, padx=2, pady=2)
            self._pin_frames.append(cell)
        self._pin_rule(pad, 4, (3, 0))
        return pad

    def _pin_rule(self, pad, row: int, pady: tuple[int, int]) -> None:
        rule = tk.Frame(pad, bg="#4a4e57", width=1, height=1, highlightthickness=0, bd=0)
        rule.grid_propagate(False)
        rule.grid(row=row, column=0, columnspan=6, sticky="ew", pady=pady)

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
            widget.bind("<ButtonPress-1>", lambda event, box=frame, item=spec: self._press_list_key(event, box, item))
            widget.bind("<B1-Motion>", self._key_drag_move)
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
        drag = self._key_drag
        if drag is not None and drag["active"]:
            return
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
        self._tip_show_frame = None

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
        if self._tip_show_job is not None and self._tip_show_frame is frame:
            return
        self._cancel_tip_show()
        delay = 20 if self._tip is not None else 180
        self._tip_show_frame = frame
        self._tip_show_job = self.root.after(delay, lambda box=frame, text=name: self._show_tip(box, text))

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

    def _raise_ghost(self) -> None:
        drag = self._key_drag
        if drag is None or not drag.get("active"):
            return
        ghost = drag.get("ghost")
        if ghost is None:
            return
        try:
            if not ghost.winfo_exists():
                return
            hwnd = native_hwnd(ghost.winfo_id())
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
        self._tip_show_frame = None
        if not frame.winfo_exists() or not self._pointer_inside(frame):
            return
        if self._tip is not None and self._tip_frame is frame:
            try:
                if self._tip.winfo_exists():
                    self._arm_tip_watch()
                    return
            except tk.TclError:
                pass
        if self._tip is not None and self._tip_label is not None:
            try:
                if self._tip.winfo_exists():
                    self._tip_label.configure(text=text)
                    self._tip.update_idletasks()
                    width, height = self._tip.winfo_reqwidth(), self._tip.winfo_reqheight()
                    x, y = self._tip_origin(frame, width, height)
                    self._tip.geometry(f"{width}x{height}+{int(x)}+{int(y)}")
                    self._raise_tip()
                    self._tip_frame = frame
                    self._arm_tip_watch()
                    return
            except tk.TclError:
                pass
        self._close_tip_window()
        tip = tk.Toplevel(self.root)
        tip.overrideredirect(True)
        tip.attributes("-topmost", True)
        tip.configure(bg="#000000")
        label = tk.Label(
            tip,
            text=text,
            bg="#000000",
            fg="#ffffff",
            font=("Microsoft JhengHei UI", 9, "bold"),
            padx=8,
            pady=3,
        )
        label.pack()
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
        self._tip_label = label
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
        exists = False
        if frame is not None:
            try:
                exists = bool(frame.winfo_exists())
            except tk.TclError:
                exists = False
        if frame is None or not exists:
            self._hide_tip()
            return
        if not self._pointer_inside(frame):
            if not frame._busy:
                frame._pressed = False
                self._paint_key_normal(frame)
            if self._tip_show_job is not None or self._tip_hide_job is not None:
                self._arm_tip_watch()
                return
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
        self._tip_label = None
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

    def _pin_text_for(self, sid: int) -> tuple[str, str, str]:
        item = self._by_id.get(int(sid or 0))
        if not item:
            return "", "", ""
        try:
            _mods, key = parse_hotkey(item["hotkey"])
            full = format_hotkey(item["hotkey"])
        except ValueError:
            return "", "", ""
        label = str(item.get("name") or "").strip()
        tip = f"{label} · {full}" if label else full
        return pin_face(label, display_key(key)), tip, item["hotkey"]

    def _make_pin_key(self, parent, index: int, sid: int):
        face, tip, hotkey = self._pin_text_for(sid)
        filled = bool(sid and hotkey)
        bg, edge = ("#dbe6f7", "#8aa0c8") if filled else ("#24262b", "#5a5f6a")
        frame = tk.Frame(
            parent,
            bg=bg,
            width=48,
            height=30,
            cursor="hand2" if filled else "arrow",
            takefocus=False,
            highlightthickness=1,
            highlightbackground=edge,
        )
        frame.pack_propagate(False)
        frame.grid_propagate(False)
        title = tk.Label(
            frame,
            text=face,
            bg=bg,
            fg="#1b1c20",
            takefocus=False,
            font=("Microsoft JhengHei UI", 8, "bold"),
        )
        title.place(relx=0.5, rely=0.5, anchor="center")
        frame._bg = bg
        frame._fg = "#1b1c20"
        frame._hover = "#174ea6"
        frame._edge = edge
        frame._tip_name = tip
        frame._label = title
        frame._hint = None
        frame._hint_text = ""
        frame._hint_fg = "#ffffff"
        frame._pressed = False
        frame._busy = False
        frame._gen = 0
        spec = {"id": sid, "group": "格子", "label": face, "hotkey": hotkey}
        for widget in (frame, title):
            widget.bind("<Button-3>", lambda event, i=index: self._open_pin_menu(event, i))
            if filled:
                widget.bind("<ButtonPress-1>", lambda _event, box=frame: self._press_key(box))
                widget.bind("<ButtonRelease-1>", lambda event, box=frame, item=spec: self._release_key(event, box, item))
                widget.bind("<Enter>", lambda _event, box=frame: self._hover_key(box, True))
                widget.bind("<Leave>", lambda _event, box=frame: self._hover_key(box, False))
        return frame

    def _press_list_key(self, event, frame, spec) -> None:
        self._press_key(frame)
        if self._editors or frame._busy or self._key_drag is not None:
            return
        self._key_drag = {
            "frame": frame,
            "spec": spec,
            "x0": event.x_root,
            "y0": event.y_root,
            "active": False,
            "ghost": None,
            "target": -1,
        }

    def _key_drag_move(self, event) -> None:
        drag = self._key_drag
        if drag is None or self._editors:
            return
        if not drag["active"]:
            if abs(event.x_root - drag["x0"]) < DRAG_START_PX and abs(event.y_root - drag["y0"]) < DRAG_START_PX:
                return
            drag["active"] = True
            self._dragging = True
            self._cancel_hide()
            self._hide_tip()
            drag["frame"]._pressed = False
            self._paint_key_normal(drag["frame"])
            spec = drag["spec"]
            label = spec.get("label") or ""
            if not label:
                try:
                    label = format_hotkey(spec["hotkey"])
                except ValueError:
                    label = str(spec.get("hotkey") or "")
            drag["ghost"] = self._make_ghost(label, event.x_root, event.y_root)
        self._move_ghost(drag["ghost"], event.x_root, event.y_root)
        target = pin_at(event.x_root, event.y_root, self._pin_rects())
        if target != drag["target"]:
            self._mark_pin(drag["target"], False)
            self._mark_pin(target, True)
            drag["target"] = target
        self._raise_ghost()

    def _finish_drag(self, drag, event) -> None:
        self._end_drag_ui(drag)
        index = pin_at(event.x_root, event.y_root, self._pin_rects())
        if index >= 0 and drag["spec"].get("id"):
            self._place_pin(index, int(drag["spec"]["id"]))

    def _end_drag_ui(self, drag) -> None:
        self._dragging = False
        self._mark_pin(drag["target"], False)
        ghost = drag.get("ghost")
        drag["ghost"] = None
        if ghost is not None:
            try:
                ghost.destroy()
            except tk.TclError:
                pass

    def _cancel_key_drag(self) -> None:
        drag = self._key_drag
        self._key_drag = None
        if drag is not None and drag["active"]:
            self._end_drag_ui(drag)

    def _make_ghost(self, text: str, x: int, y: int):
        ghost = tk.Toplevel(self.root)
        ghost.overrideredirect(True)
        ghost.withdraw()
        ghost.attributes("-topmost", True)
        ghost.configure(bg="#fbbc04")
        tk.Label(
            ghost,
            text=text,
            bg="#fbbc04",
            fg="#1b1c20",
            padx=8,
            pady=3,
            font=("Microsoft JhengHei UI", 9, "bold"),
        ).pack()
        ghost.update_idletasks()
        try:
            ghost.attributes("-alpha", 1.0)
        except tk.TclError:
            pass
        self._move_ghost(ghost, x, y)
        hwnd = native_hwnd(ghost.winfo_id())
        if hwnd:
            style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            style = (style | WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW) & ~WS_EX_TRANSPARENT
            user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
            user32.SetWindowPos(
                hwnd,
                topmost_handle(),
                0,
                0,
                0,
                0,
                SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_SHOWWINDOW,
            )
        ghost.deiconify()
        try:
            ghost.attributes("-alpha", 1.0)
        except tk.TclError:
            pass
        return ghost

    def _move_ghost(self, ghost, x: int, y: int) -> None:
        try:
            if ghost is None or not ghost.winfo_exists():
                return
            width, height = ghost.winfo_reqwidth(), ghost.winfo_reqheight()
        except tk.TclError:
            return
        mon = monitor_rect(x, y)
        origin_x = max(mon[0], min(x + 14, mon[2] - width))
        origin_y = max(mon[1], min(y + 14, mon[3] - height))
        ghost.geometry(f"+{int(origin_x)}+{int(origin_y)}")

    def _pin_rects(self) -> list:
        rects = []
        for frame in self._pin_frames:
            try:
                left, top = frame.winfo_rootx(), frame.winfo_rooty()
                rects.append((left, top, left + frame.winfo_width(), top + frame.winfo_height()))
            except tk.TclError:
                rects.append(None)
        return rects

    def _mark_pin(self, index: int, on: bool) -> None:
        if not 0 <= index < len(self._pin_frames):
            return
        frame = self._pin_frames[index]
        try:
            if not frame.winfo_exists():
                return
            frame.configure(highlightbackground="#fbbc04" if on else frame._edge)
        except tk.TclError:
            pass

    def _note_readonly(self) -> None:
        if self._readonly_noted:
            return
        self._readonly_noted = True
        messagebox.showwarning("快捷鍵", self._library_message or "目前不能修改快捷鍵。")

    def _place_pin(self, index: int, sid: int) -> None:
        if self._editors:
            return
        if self._library_readonly:
            self._note_readonly()
            return
        valid = library_pin_ids(self.library)
        old = normalize_pin_ids(self.library.get("pins"), valid)
        new = set_pin(old, index, int(sid))
        if new == old:
            return
        self.library["pins"] = new
        self._store()
        self._refresh_pins(old, new)

    def clear_pin_cell(self, index: int) -> None:
        if self._editors:
            return
        if self._library_readonly:
            self._note_readonly()
            return
        valid = library_pin_ids(self.library)
        old = normalize_pin_ids(self.library.get("pins"), valid)
        new = list(old)
        if 0 <= index < PIN_COUNT:
            new[index] = 0
        if new == old:
            return
        self.library["pins"] = new
        self._store()
        self._refresh_pins(old, new)

    def _refresh_pins(self, old: list, new: list) -> None:
        self._hide_tip()
        parent = self._pin_parent
        if parent is None:
            return
        try:
            if not parent.winfo_exists():
                return
        except tk.TclError:
            return
        for index, frame in enumerate(self._pin_frames):
            if old[index] == new[index]:
                continue
            try:
                frame.destroy()
            except tk.TclError:
                pass
            fresh = self._make_pin_key(parent, index, new[index])
            fresh.grid(row=3, column=index, padx=2, pady=2)
            self._pin_frames[index] = fresh
        self.root.update_idletasks()
        for frame in self._pin_frames:
            if getattr(frame, "_tip_name", "") and self._pointer_inside(frame):
                self._hover_key(frame, True)
                break

    def _open_pin_menu(self, event, index: int) -> None:
        rows = self._bar_rows()
        pins = normalize_pin_ids(self.library.get("pins"), library_pin_ids(self.library))
        if index < len(pins) and pins[index]:
            rows = [("清空這格", lambda i=index: self.clear_pin_cell(i)), None, *rows]
        self._open_menu(event.x_root, event.y_root, rows)

    def _press_key(self, frame) -> None:
        frame._pressed = True
        if not getattr(frame, "_tip_name", ""):
            self._hide_tip()
        self._paint_key(frame, PRESS, "#ffffff", "#ffffff")

    def _release_key(self, event, frame, spec: dict) -> None:
        drag = self._key_drag
        if drag is not None and drag["frame"] is frame:
            self._key_drag = None
            if drag["active"]:
                self._finish_drag(drag, event)
                return
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
        self._cancel_key_drag()
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
            drag = self._key_drag
            if drag is not None and not key_is_down(0x01):
                self._cancel_key_drag()
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
            self._raise_ghost()
            if self._tip is not None:
                self.root.after(1, self._raise_tip)
            if self._key_drag is not None and self._key_drag.get("ghost") is not None:
                self.root.after(1, self._raise_ghost)
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
            library, message = open_library()
        except Exception:
            log_exc()
            self._shortcuts_mtime = mtime
            return
        self._library_readonly = message is not None
        self._library_message = message
        if message is None:
            self._readonly_noted = False
        self._shortcuts_mtime = mtime
        if message:
            return
        self.library = library
        self._reindex()
        self.shortcuts = materialize(self.library)
        self._shortcuts_mtime = shortcuts_mtime()
        self.relayout()

    def _reindex(self) -> None:
        self._by_id = {int(item["id"]): item for item in self.library.get("shortcuts") or []}

    def _store(self) -> None:
        if self._library_readonly:
            return
        try:
            save_library(self.library)
        except Exception:
            log_exc()
            messagebox.showerror("快捷鍵", "快捷鍵檔沒有寫入。請看 error.log。")
            return
        self._shortcuts_mtime = shortcuts_mtime()
        self._reindex()

    def _active_group_name(self) -> str:
        return group_name_of(self.library, int(self.library.get("active_group") or 0)) or "群組"

    def activate_group(self, gid: int) -> None:
        if self._editors:
            return
        if self._library_readonly:
            self._note_readonly()
            return
        if int(gid) == int(self.library.get("active_group") or 0):
            return
        if group_by_id(self.library, int(gid)) is None:
            return
        self.library["active_group"] = int(gid)
        self.shortcuts = materialize(self.library)
        self._store()
        self.relayout()

    def _open_group_menu(self) -> None:
        rows = []
        active = int(self.library.get("active_group") or 0)
        for group in self.library.get("groups") or []:
            name = str(group.get("name") or "")
            gid = int(group["id"])
            rows.append((("● " if gid == active else "   ") + name, lambda chosen=gid: self.activate_group(chosen)))
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

    def _manage_groups(self, parent, refresh) -> None:
        if self._library_readonly:
            return
        dialog = tk.Toplevel(parent)
        dialog.title("群組")
        dialog.attributes("-topmost", True)
        dialog.transient(parent)
        frame = tk.Frame(dialog, padx=12, pady=12)
        frame.pack()
        box = tk.Listbox(frame, width=24, height=10, font=FONT_UI)
        box.pack()
        ids: list[int] = []

        def refill() -> None:
            box.delete(0, "end")
            ids.clear()
            for group in self.library.get("groups") or []:
                box.insert("end", group["name"])
                ids.append(int(group["id"]))

        def current() -> int | None:
            picked = box.curselection()
            if not picked:
                return None
            return ids[int(picked[0])]

        def add() -> None:
            name = simpledialog.askstring("新增群組", "名稱", parent=dialog)
            error = add_group_row(self.library, name or "")
            if error:
                messagebox.showinfo("群組", error, parent=dialog)
                return
            self._store()
            refill()
            refresh()

        def rename() -> None:
            gid = current()
            if gid is None:
                return
            name = simpledialog.askstring(
                "改名", "名稱", parent=dialog, initialvalue=group_name_of(self.library, gid)
            )
            error = rename_group_row(self.library, gid, name or "")
            if error:
                messagebox.showinfo("群組", error, parent=dialog)
                return
            self._store()
            refill()
            refresh()

        def remove() -> None:
            gid = current()
            if gid is None:
                return
            count = ungrouped_if_removed(self.library, gid)
            if not messagebox.askyesno(
                "群組",
                f"刪除「{group_name_of(self.library, gid)}」？\n{count} 個快捷鍵會變成未分組。",
                parent=dialog,
            ):
                return
            delete_group_row(self.library, gid)
            self._store()
            refill()
            refresh()

        refill()
        buttons = tk.Frame(frame)
        buttons.pack(pady=8)
        tk.Button(buttons, text="新增", command=add).pack(side="left")
        tk.Button(buttons, text="改名", command=rename).pack(side="left", padx=6)
        tk.Button(buttons, text="刪除", command=remove).pack(side="left")
        dialog.lift()

    def choose_shortcuts(self) -> None:
        if self._library_readonly:
            messagebox.showwarning("快捷鍵", self._library_message or "目前不能修改快捷鍵。")
            return
        self._begin_modal()
        win = tk.Toplevel(self.root)
        win.title("快捷鍵")
        win.geometry("760x640")
        win.attributes("-topmost", True)
        win.configure(bg="#f6f7f8")
        outer = tk.Frame(win, bg="#f6f7f8", padx=12, pady=12)
        outer.pack(fill="both", expand=True)
        top = tk.Frame(outer, bg="#f6f7f8")
        top.pack(fill="x")
        tk.Label(top, text="群組", bg="#f6f7f8", font=FONT_UI).pack(side="left")
        filter_var = tk.StringVar(value="全部")
        filter_box = ttk.Combobox(top, textvariable=filter_var, state="readonly", width=16)
        filter_box.pack(side="left", padx=(6, 12))
        tk.Label(top, text="搜尋", bg="#f6f7f8", font=FONT_UI).pack(side="left")
        search_var = tk.StringVar()
        search_entry = tk.Entry(top, textvariable=search_var, font=FONT_UI, width=24)
        search_entry.pack(side="left", padx=6)
        manage_btn = tk.Button(top, text="群組管理…")
        manage_btn.pack(side="right")
        hint_var = tk.StringVar()
        tk.Label(outer, textvariable=hint_var, bg="#f6f7f8", fg="#5f6368", font=FONT_HINT, anchor="w").pack(fill="x", pady=(6, 0))

        tree_wrap = tk.Frame(outer, bg="#f6f7f8")
        tree_wrap.pack(fill="both", expand=True, pady=8)
        tree = ttk.Treeview(tree_wrap, columns=("shown", "hotkey", "name", "groups"), show="headings", height=12)
        tree.heading("shown", text="顯示")
        tree.column("shown", width=120, anchor="center", stretch=False)
        tree.heading("hotkey", text="快捷鍵")
        tree.heading("name", text="名稱")
        tree.heading("groups", text="群組")
        tree.column("hotkey", width=170, anchor="w")
        tree.column("name", width=140, anchor="w")
        tree.column("groups", width=240, anchor="w")
        scroll = ttk.Scrollbar(tree_wrap, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)

        form = tk.Frame(outer, bg="#f6f7f8")
        form.pack(fill="x")
        mods = {name: tk.BooleanVar() for name in ("ctrl", "shift", "alt", "win")}
        mod_row = tk.Frame(form, bg="#f6f7f8")
        mod_row.pack(fill="x", pady=2)
        for name, label in (("ctrl", "Ctrl"), ("shift", "Shift"), ("alt", "Alt"), ("win", "Win")):
            tk.Checkbutton(
                mod_row, text=label, variable=mods[name], bg="#f6f7f8",
                command=lambda: preview(),
            ).pack(side="left", padx=4)
        key_row = tk.Frame(form, bg="#f6f7f8")
        key_row.pack(fill="x", pady=4)
        tk.Label(key_row, text="主鍵", bg="#f6f7f8", font=FONT_UI).pack(side="left")
        key_var = tk.StringVar()
        key_by_label: dict[str, str] = {}
        key_labels = []
        for name in KEY_VK:
            label = "`" if name == "backquote" else DISPLAY_KEY.get(name, name)
            if label in key_by_label and key_by_label[label] != name:
                label = name
            key_by_label[label] = name
            key_labels.append(label)
        key_labels.sort(key=str.lower)
        key_box = ttk.Combobox(key_row, textvariable=key_var, state="readonly", values=key_labels, width=18)
        key_box.pack(side="left", padx=6)
        capture_btn = tk.Button(key_row, text="按下主鍵")
        capture_btn.pack(side="left")
        preview_var = tk.StringVar(value="預覽：")
        tk.Label(key_row, textvariable=preview_var, bg="#f6f7f8", font=FONT_UI).pack(side="left", padx=8)
        name_var = tk.StringVar()
        tk.Label(form, text="名稱", bg="#f6f7f8", font=FONT_UI).pack(anchor="w")
        name_entry = tk.Entry(form, textvariable=name_var, font=FONT_UI)
        name_entry.pack(fill="x", pady=(0, 6))
        group_host = tk.Frame(form, bg="#f6f7f8")
        group_host.pack(fill="x")
        group_vars: dict[int, tk.BooleanVar] = {}
        selected = {"id": None}
        capturing = {"on": False}

        def current_hotkey() -> str | None:
            key_name = key_by_label.get(key_var.get())
            if not key_name:
                return None
            chosen = [name for name in MOD_ORDER if mods[name].get()]
            try:
                return canonical_hotkey("+".join([*chosen, key_name]))
            except ValueError:
                return None

        def preview(*_args) -> None:
            hotkey = current_hotkey()
            preview_var.set("預覽：" + (format_hotkey(hotkey) if hotkey else "（尚未選擇主鍵）"))

        def selected_groups() -> list[int]:
            return [gid for gid, var in group_vars.items() if var.get()]

        def rebuild_groups(keep: list[int] | None = None) -> None:
            for child in group_host.winfo_children():
                child.destroy()
            group_vars.clear()
            tk.Label(group_host, text="群組", bg="#f6f7f8", font=FONT_UI).pack(anchor="w")
            row = tk.Frame(group_host, bg="#f6f7f8")
            row.pack(fill="x")
            for group in self.library.get("groups") or []:
                var = tk.BooleanVar(value=int(group["id"]) in (keep or []))
                group_vars[int(group["id"])] = var
                tk.Checkbutton(row, text=group["name"], variable=var, bg="#f6f7f8").pack(side="left", padx=3)
            names = ["全部", "未分組"] + [str(group["name"]) for group in self.library.get("groups") or []]
            filter_box["values"] = names
            if filter_var.get() not in names:
                filter_var.set("全部")
            refresh_shown_label()

        def refresh_shown_label() -> None:
            name = group_name_of(self.library, int(self.library.get("active_group") or 0)) or "群組"
            hint_var.set(f"勾了「顯示」才出現在「{name}」。上方篩選只改清單，這一欄仍是「{name}」。")
            tree.heading("shown", text=f"顯示·{name}")
            tree.column("shown", width=max(120, 18 * len(name) + 52), anchor="center", stretch=False)

        def group_text(item: dict) -> str:
            labels = [group_name_of(self.library, int(gid)) for gid in item.get("groups") or []]
            return "、".join(label for label in labels if label) or "未分組"

        def refresh(*_args) -> None:
            children = tree.get_children()
            if children:
                tree.delete(*children)
            query = search_var.get().strip().lower()
            chosen = filter_var.get()
            for item in self.library.get("shortcuts") or []:
                linked = [int(gid) for gid in item.get("groups") or []]
                if chosen == "未分組" and linked:
                    continue
                if chosen not in ("全部", "未分組"):
                    group = next((row for row in self.library["groups"] if row["name"] == chosen), None)
                    if group is None or int(group["id"]) not in linked:
                        continue
                try:
                    shown = format_hotkey(item["hotkey"])
                except ValueError:
                    shown = str(item.get("hotkey") or "")
                blob = f"{shown} {item.get('name') or ''} {item.get('hotkey') or ''}".lower()
                if query and query not in blob:
                    continue
                gid = int(self.library.get("active_group") or 0)
                mark = "☑" if gid and gid in linked else "☐"
                tree.insert("", "end", iid=str(item["id"]), values=(mark, shown, item.get("name") or "", group_text(item)))

        def toggle_shown(event):
            if self._library_readonly or tree.identify_region(event.x, event.y) != "cell":
                return
            if tree.identify_column(event.x) != "#1":
                return
            iid = tree.identify_row(event.y)
            item = shortcut_by_id(self.library, int(iid)) if iid else None
            gid = int(self.library.get("active_group") or 0)
            if item is None or not gid:
                return "break"
            groups = [int(value) for value in item.get("groups") or []]
            removing = gid in groups
            if removing:
                groups = [value for value in groups if value != gid]
            else:
                error = check_shortcut(
                    self.library,
                    str(item.get("hotkey") or ""),
                    str(item.get("name") or "").strip(),
                    [gid],
                    ignore_id=int(iid),
                )
                if error:
                    messagebox.showinfo("快捷鍵", error, parent=win)
                    return "break"
                groups.append(gid)
            item["groups"] = groups
            if selected["id"] == int(iid) and gid in group_vars:
                group_vars[gid].set(gid in groups)
            self._store()
            chosen = filter_var.get()
            active_name = group_name_of(self.library, gid)
            hide = (removing and chosen == active_name) or (not removing and chosen == "未分組")
            if hide:
                tree.delete(iid)
            else:
                tree.set(iid, "shown", "☐" if removing else "☑")
                tree.set(iid, "groups", group_text(item))
            return "break"

        def load_selected(_event=None) -> None:
            picked = tree.focus()
            if not picked:
                return
            item = shortcut_by_id(self.library, int(picked))
            if item is None:
                return
            selected["id"] = int(picked)
            try:
                mod_names, key = parse_hotkey(item["hotkey"])
            except ValueError:
                return
            for name in mods:
                mods[name].set(name in mod_names)
            key_var.set("`" if key == "backquote" else DISPLAY_KEY.get(key, key))
            name_var.set(item.get("name") or "")
            for gid, var in group_vars.items():
                var.set(gid in (item.get("groups") or []))
            preview()

        def clear_form() -> None:
            selected["id"] = None
            tree.selection_remove(tree.selection())
            for var in mods.values():
                var.set(False)
            key_var.set("")
            name_var.set("")
            for var in group_vars.values():
                var.set(False)
            preview()

        def clear_entry() -> None:
            selected["id"] = None
            tree.selection_remove(tree.selection())
            key_var.set("")
            name_var.set("")
            preview()

        def apply_edit(creating: bool) -> None:
            hotkey = current_hotkey()
            if not hotkey:
                messagebox.showinfo("快捷鍵", "請選擇主鍵。", parent=win)
                return
            groups = selected_groups()
            if creating and not groups:
                if not messagebox.askyesno(
                    "快捷鍵",
                    "沒有勾選群組，這一筆會變成未分組，列上看不到。仍要新增嗎？",
                    parent=win,
                ):
                    return
            kept = None if creating or selected["id"] is None else int(selected["id"])
            if creating:
                error = add_shortcut(self.library, hotkey, name_var.get(), groups)
            else:
                if kept is None:
                    messagebox.showinfo("快捷鍵", "請先選一筆再儲存修改。", parent=win)
                    return
                error = update_shortcut(self.library, kept, hotkey, name_var.get(), groups)
            if error:
                messagebox.showinfo("快捷鍵", error, parent=win)
                return
            self._store()
            refresh()
            if creating:
                new_id = None
                rows = self.library.get("shortcuts") or []
                if rows:
                    new_id = rows[-1].get("id")
                clear_entry()
                if new_id is not None:
                    try:
                        tree.see(str(int(new_id)))
                    except (tk.TclError, ValueError):
                        pass
            elif kept is not None:
                selected["id"] = kept
                try:
                    tree.selection_set(str(kept))
                    tree.focus(str(kept))
                    tree.see(str(kept))
                except tk.TclError:
                    pass

        def remove_selected() -> None:
            if selected["id"] is None:
                return
            if not messagebox.askyesno("快捷鍵", "刪除這一筆？格子裡若有用到也會清掉。", parent=win):
                return
            delete_shortcut(self.library, int(selected["id"]))
            selected["id"] = None
            self._store()
            refresh()

        def stop_capture() -> None:
            capturing["on"] = False
            self._capturing = False
            try:
                if capture_btn.winfo_exists():
                    capture_btn.configure(text="按下主鍵")
            except tk.TclError:
                pass

        def on_key(event):
            if not capturing["on"]:
                return
            code = int(getattr(event, "keycode", 0) or 0)
            if code == 27 or str(getattr(event, "keysym", "")) == "Escape":
                stop_capture()
                return "break"
            if code in MODIFIER_KEYCODES or code == 229:
                if code == 229:
                    preview_var.set("預覽：這個鍵無法擷取，請用下拉")
                return "break"
            name = VK_TO_KEY.get(code)
            if name:
                key_var.set("`" if name == "backquote" else DISPLAY_KEY.get(name, name))
                preview()
                stop_capture()
            else:
                preview_var.set("預覽：這個鍵無法擷取，請用下拉")
            return "break"

        def toggle_capture() -> None:
            if capturing["on"]:
                stop_capture()
                return
            capturing["on"] = True
            self._capturing = True
            capture_btn.configure(text="擷取中，Esc 取消")
            win.lift()
            try:
                win.focus_force()
            except tk.TclError:
                pass

        def capture_inside() -> bool:
            try:
                focus = win.focus_get()
            except (tk.TclError, KeyError):
                return False
            if focus is None:
                return False
            try:
                return focus.winfo_toplevel() == win
            except (tk.TclError, KeyError):
                return False

        def check_capture_focus() -> None:
            try:
                inside = capture_inside()
            except (tk.TclError, KeyError):
                inside = False
            if capturing["on"] and not inside:
                stop_capture()

        def on_focus_out(_event) -> None:
            if capturing["on"] and win.winfo_exists():
                win.after(20, check_capture_focus)

        def close() -> None:
            try:
                stop_capture()
            finally:
                try:
                    if win.winfo_exists():
                        win.destroy()
                except tk.TclError:
                    pass
                self._end_modal()
                self.shortcuts = materialize(self.library)
                self.relayout()

        capture_btn.configure(command=toggle_capture)
        manage_btn.configure(command=lambda: self._manage_groups(
            win, lambda: (rebuild_groups(selected_groups()), refresh())
        ))
        buttons = tk.Frame(outer, bg="#f6f7f8")
        buttons.pack(fill="x", pady=(8, 0))
        tk.Button(buttons, text="新增", command=lambda: apply_edit(True)).pack(side="left")
        tk.Button(buttons, text="儲存修改", command=lambda: apply_edit(False)).pack(side="left", padx=6)
        tk.Button(buttons, text="刪除", command=remove_selected).pack(side="left")
        tk.Button(buttons, text="清空表單", command=clear_form).pack(side="left", padx=6)
        tk.Button(buttons, text="關閉", command=close).pack(side="right")
        win.bind("<KeyPress>", on_key)
        win.bind("<FocusOut>", on_focus_out)
        for widget in (name_entry, search_entry, key_box, filter_box):
            widget.bind("<KeyPress>", on_key)
        tree.bind("<Button-1>", toggle_shown)
        tree.bind("<<TreeviewSelect>>", load_selected)
        search_var.trace_add("write", lambda *_args: refresh())
        filter_box.bind("<<ComboboxSelected>>", refresh)
        key_box.bind("<<ComboboxSelected>>", lambda _event: preview())
        win.protocol("WM_DELETE_WINDOW", close)
        rebuild_groups()
        refresh()
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

    def remove_from_group(self, spec: dict) -> None:
        if self._editors:
            return
        if self._library_readonly:
            self._note_readonly()
            return
        item = self._by_id.get(int(spec.get("id") or 0))
        gid = int(self.library.get("active_group") or 0)
        if item is None or gid not in (item.get("groups") or []):
            return
        item["groups"] = [int(value) for value in item["groups"] if int(value) != gid]
        self._store()
        self.shortcuts = materialize(self.library)
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
        rows = [("從這個群組移除", lambda item=spec: self.remove_from_group(item))]
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
        self._cancel_key_drag()
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
