@echo off
cd /d "%~dp0"
set "ASK=0"
if exist shortcuts.json set "ASK=1"
if exist config.json set "ASK=1"
if "%ASK%"=="1" (
  choice /m "已有 config.json 或 shortcuts.json。先備份再覆蓋嗎"
  if errorlevel 2 exit /b 0
  if exist config.json copy /y config.json config.before-generate.json >nul
  if exist shortcuts.json copy /y shortcuts.json shortcuts.before-generate.json >nul
)
set "SRC=%~f0"
where python >nul 2>&1
if %errorlevel%==0 goto :runpy
where py >nul 2>&1
if %errorlevel%==0 goto :runpy3
echo Python 3 was not found. Install it and tick "Add python.exe to PATH".
exit /b 1
:runpy
python -c "import pathlib; p = pathlib.Path(r'%SRC%'); t = p.read_bytes().decode('utf-8-sig').replace('\r\n', '\n'); c, rest = t.split('___CONFIG_JSON___\n', 1)[1].split('___SHORTCUTS_JSON___\n', 1); d = p.parent; d.joinpath('config.json').write_bytes(c.encode('utf-8')); d.joinpath('shortcuts.json').write_bytes(rest.encode('utf-8'))"
exit /b %errorlevel%
:runpy3
py -3 -c "import pathlib; p = pathlib.Path(r'%SRC%'); t = p.read_bytes().decode('utf-8-sig').replace('\r\n', '\n'); c, rest = t.split('___CONFIG_JSON___\n', 1)[1].split('___SHORTCUTS_JSON___\n', 1); d = p.parent; d.joinpath('config.json').write_bytes(c.encode('utf-8')); d.joinpath('shortcuts.json').write_bytes(rest.encode('utf-8'))"
exit /b %errorlevel%
___CONFIG_JSON___
{
  "mode": "free",
  "orientation": "vertical",
  "side": "right",
  "x": 206,
  "y": 219,
  "opacity": 0.72,
  "toggle_hotkey": "ctrl+alt+shift+h",
  "auto_hide_seconds": 0.0,
  "dblclick_left_paste": true,
  "dblclick_right_copy": true,
  "hidden": false,
  "disabled": [
    "redo",
    "save",
    "find",
    "replace",
    "print",
    "bold",
    "italic",
    "underline",
    "delete-perm",
    "properties",
    "context",
    "up",
    "back",
    "forward",
    "refresh",
    "new-folder",
    "address",
    "switch-back",
    "cycle",
    "maximize",
    "restore",
    "snap-left",
    "snap-right",
    "taskview",
    "restore-all",
    "close-doc",
    "new-tab",
    "reopen-tab",
    "fullscreen",
    "window-menu",
    "help",
    "lock",
    "settings",
    "search",
    "quick",
    "notify",
    "widgets",
    "emoji",
    "snip",
    "shot",
    "shot-win",
    "project",
    "voice",
    "zoom-in",
    "zoom-out",
    "taskmgr",
    "lang",
    "gamebar",
    "record",
    "desk-new",
    "desk-close",
    "desk-left",
    "desk-right",
    "url",
    "tab-next",
    "tab-prev",
    "hard-refresh",
    "page-in",
    "page-out",
    "page-100",
    "play",
    "next-track",
    "prev-track",
    "stop"
  ],
  "custom": []
}
___SHORTCUTS_JSON___
{
  "version": 2,
  "active_group": 7,
  "groups": [
    {
      "id": 1,
      "name": "編輯"
    },
    {
      "id": 2,
      "name": "檔案總管"
    },
    {
      "id": 3,
      "name": "視窗"
    },
    {
      "id": 4,
      "name": "系統"
    },
    {
      "id": 5,
      "name": "瀏覽器"
    },
    {
      "id": 6,
      "name": "媒體"
    },
    {
      "id": 7,
      "name": "常用"
    },
    {
      "id": 8,
      "name": "自訂"
    }
  ],
  "shortcuts": [
    {
      "id": 1,
      "hotkey": "ctrl+c",
      "name": "複製",
      "groups": [
        1,
        7
      ]
    },
    {
      "id": 2,
      "hotkey": "ctrl+v",
      "name": "貼上",
      "groups": [
        1,
        7
      ]
    },
    {
      "id": 3,
      "hotkey": "ctrl+x",
      "name": "剪下",
      "groups": [
        1,
        7
      ]
    },
    {
      "id": 4,
      "hotkey": "ctrl+z",
      "name": "復原",
      "groups": [
        1,
        7
      ]
    },
    {
      "id": 5,
      "hotkey": "ctrl+y",
      "name": "重做",
      "groups": [
        1
      ]
    },
    {
      "id": 6,
      "hotkey": "ctrl+a",
      "name": "全選",
      "groups": [
        1,
        7
      ]
    },
    {
      "id": 7,
      "hotkey": "ctrl+s",
      "name": "存檔",
      "groups": [
        1
      ]
    },
    {
      "id": 8,
      "hotkey": "ctrl+f",
      "name": "尋找",
      "groups": [
        1
      ]
    },
    {
      "id": 9,
      "hotkey": "ctrl+h",
      "name": "取代",
      "groups": [
        1
      ]
    },
    {
      "id": 10,
      "hotkey": "ctrl+p",
      "name": "列印",
      "groups": [
        1
      ]
    },
    {
      "id": 11,
      "hotkey": "ctrl+b",
      "name": "粗體",
      "groups": [
        1
      ]
    },
    {
      "id": 12,
      "hotkey": "ctrl+i",
      "name": "斜體",
      "groups": [
        1
      ]
    },
    {
      "id": 13,
      "hotkey": "ctrl+u",
      "name": "底線",
      "groups": [
        1
      ]
    },
    {
      "id": 14,
      "hotkey": "f2",
      "name": "重新命名",
      "groups": [
        2,
        7
      ]
    },
    {
      "id": 15,
      "hotkey": "delete",
      "name": "刪除",
      "groups": [
        2,
        7
      ]
    },
    {
      "id": 16,
      "hotkey": "shift+delete",
      "name": "永久刪除",
      "groups": [
        2
      ]
    },
    {
      "id": 17,
      "hotkey": "alt+enter",
      "name": "內容",
      "groups": [
        2
      ]
    },
    {
      "id": 18,
      "hotkey": "shift+f10",
      "name": "右鍵選單",
      "groups": [
        2
      ]
    },
    {
      "id": 19,
      "hotkey": "alt+up",
      "name": "上一層",
      "groups": [
        2
      ]
    },
    {
      "id": 20,
      "hotkey": "alt+left",
      "name": "返回",
      "groups": [
        2
      ]
    },
    {
      "id": 21,
      "hotkey": "alt+right",
      "name": "向前",
      "groups": [
        2
      ]
    },
    {
      "id": 22,
      "hotkey": "f5",
      "name": "重新整理",
      "groups": [
        2
      ]
    },
    {
      "id": 23,
      "hotkey": "ctrl+shift+n",
      "name": "新增資料夾",
      "groups": [
        2
      ]
    },
    {
      "id": 24,
      "hotkey": "alt+d",
      "name": "位址列",
      "groups": [
        2
      ]
    },
    {
      "id": 25,
      "hotkey": "alt+f4",
      "name": "關閉視窗",
      "groups": [
        3,
        7
      ]
    },
    {
      "id": 26,
      "hotkey": "alt+tab",
      "name": "切換視窗",
      "groups": [
        3,
        7
      ]
    },
    {
      "id": 27,
      "hotkey": "alt+shift+tab",
      "name": "反向切換",
      "groups": [
        3
      ]
    },
    {
      "id": 28,
      "hotkey": "alt+esc",
      "name": "循環視窗",
      "groups": [
        3
      ]
    },
    {
      "id": 29,
      "hotkey": "win+up",
      "name": "最大化",
      "groups": [
        3
      ]
    },
    {
      "id": 30,
      "hotkey": "win+down",
      "name": "還原",
      "groups": [
        3
      ]
    },
    {
      "id": 31,
      "hotkey": "win+left",
      "name": "靠左",
      "groups": [
        3
      ]
    },
    {
      "id": 32,
      "hotkey": "win+right",
      "name": "靠右",
      "groups": [
        3
      ]
    },
    {
      "id": 33,
      "hotkey": "win+tab",
      "name": "工作檢視",
      "groups": [
        3
      ]
    },
    {
      "id": 34,
      "hotkey": "win+d",
      "name": "顯示桌面",
      "groups": [
        3,
        7
      ]
    },
    {
      "id": 35,
      "hotkey": "win+m",
      "name": "全部縮小",
      "groups": [
        3,
        7
      ]
    },
    {
      "id": 36,
      "hotkey": "win+shift+m",
      "name": "還原縮小",
      "groups": [
        3
      ]
    },
    {
      "id": 37,
      "hotkey": "ctrl+w",
      "name": "關閉分頁",
      "groups": [
        3,
        7
      ]
    },
    {
      "id": 38,
      "hotkey": "ctrl+f4",
      "name": "關閉文件",
      "groups": [
        3
      ]
    },
    {
      "id": 39,
      "hotkey": "ctrl+t",
      "name": "新分頁",
      "groups": [
        3
      ]
    },
    {
      "id": 40,
      "hotkey": "ctrl+shift+t",
      "name": "重開分頁",
      "groups": [
        3
      ]
    },
    {
      "id": 41,
      "hotkey": "f11",
      "name": "全螢幕",
      "groups": [
        3
      ]
    },
    {
      "id": 42,
      "hotkey": "alt+space",
      "name": "視窗選單",
      "groups": [
        3
      ]
    },
    {
      "id": 43,
      "hotkey": "f1",
      "name": "說明",
      "groups": [
        3
      ]
    },
    {
      "id": 44,
      "hotkey": "win+l",
      "name": "鎖定",
      "groups": [
        4
      ]
    },
    {
      "id": 45,
      "hotkey": "win+r",
      "name": "執行",
      "groups": [
        4,
        7
      ]
    },
    {
      "id": 46,
      "hotkey": "win+i",
      "name": "設定",
      "groups": [
        4
      ]
    },
    {
      "id": 47,
      "hotkey": "win+e",
      "name": "檔案總管",
      "groups": [
        4,
        7
      ]
    },
    {
      "id": 48,
      "hotkey": "win+s",
      "name": "搜尋",
      "groups": [
        4
      ]
    },
    {
      "id": 49,
      "hotkey": "win+a",
      "name": "快速設定",
      "groups": [
        4
      ]
    },
    {
      "id": 50,
      "hotkey": "win+n",
      "name": "通知",
      "groups": [
        4
      ]
    },
    {
      "id": 51,
      "hotkey": "win+w",
      "name": "小工具",
      "groups": [
        4
      ]
    },
    {
      "id": 52,
      "hotkey": "win+v",
      "name": "剪貼簿",
      "groups": [
        4,
        7
      ]
    },
    {
      "id": 53,
      "hotkey": "win+period",
      "name": "表情",
      "groups": [
        4
      ]
    },
    {
      "id": 54,
      "hotkey": "win+shift+s",
      "name": "截圖",
      "groups": [
        4
      ]
    },
    {
      "id": 55,
      "hotkey": "printscreen",
      "name": "整張截圖",
      "groups": [
        4
      ]
    },
    {
      "id": 56,
      "hotkey": "alt+printscreen",
      "name": "視窗截圖",
      "groups": [
        4
      ]
    },
    {
      "id": 57,
      "hotkey": "ctrl+f5",
      "name": "擷圖",
      "groups": [
        4,
        7
      ]
    },
    {
      "id": 58,
      "hotkey": "win+p",
      "name": "投影",
      "groups": [
        4
      ]
    },
    {
      "id": 59,
      "hotkey": "win+h",
      "name": "語音輸入",
      "groups": [
        4
      ]
    },
    {
      "id": 60,
      "hotkey": "win+plus",
      "name": "放大鏡",
      "groups": [
        4
      ]
    },
    {
      "id": 61,
      "hotkey": "win+minus",
      "name": "縮小鏡",
      "groups": [
        4
      ]
    },
    {
      "id": 62,
      "hotkey": "ctrl+shift+esc",
      "name": "工作管理員",
      "groups": [
        4
      ]
    },
    {
      "id": 63,
      "hotkey": "win+space",
      "name": "切換輸入法",
      "groups": [
        4
      ]
    },
    {
      "id": 64,
      "hotkey": "win+g",
      "name": "遊戲列",
      "groups": [
        4
      ]
    },
    {
      "id": 65,
      "hotkey": "win+alt+r",
      "name": "錄製",
      "groups": [
        4
      ]
    },
    {
      "id": 66,
      "hotkey": "win+ctrl+d",
      "name": "新增桌面",
      "groups": [
        3
      ]
    },
    {
      "id": 67,
      "hotkey": "win+ctrl+f4",
      "name": "關閉桌面",
      "groups": [
        3
      ]
    },
    {
      "id": 68,
      "hotkey": "win+ctrl+left",
      "name": "左邊桌面",
      "groups": [
        3
      ]
    },
    {
      "id": 69,
      "hotkey": "win+ctrl+right",
      "name": "右邊桌面",
      "groups": [
        3
      ]
    },
    {
      "id": 70,
      "hotkey": "ctrl+l",
      "name": "網址列",
      "groups": [
        5
      ]
    },
    {
      "id": 71,
      "hotkey": "ctrl+tab",
      "name": "下一分頁",
      "groups": [
        5
      ]
    },
    {
      "id": 72,
      "hotkey": "ctrl+shift+tab",
      "name": "上一分頁",
      "groups": [
        5
      ]
    },
    {
      "id": 73,
      "hotkey": "ctrl+f5",
      "name": "強制重新整理",
      "groups": [
        5
      ]
    },
    {
      "id": 74,
      "hotkey": "ctrl+plus",
      "name": "頁面放大",
      "groups": [
        5
      ]
    },
    {
      "id": 75,
      "hotkey": "ctrl+minus",
      "name": "頁面縮小",
      "groups": [
        5
      ]
    },
    {
      "id": 76,
      "hotkey": "ctrl+0",
      "name": "實際大小",
      "groups": [
        5
      ]
    },
    {
      "id": 77,
      "hotkey": "playpause",
      "name": "播放",
      "groups": [
        6
      ]
    },
    {
      "id": 78,
      "hotkey": "nexttrack",
      "name": "下一首",
      "groups": [
        6
      ]
    },
    {
      "id": 79,
      "hotkey": "prevtrack",
      "name": "上一首",
      "groups": [
        6
      ]
    },
    {
      "id": 80,
      "hotkey": "mediastop",
      "name": "停止",
      "groups": [
        6
      ]
    },
    {
      "id": 81,
      "hotkey": "volumeup",
      "name": "音量加",
      "groups": [
        6,
        7
      ]
    },
    {
      "id": 82,
      "hotkey": "volumedown",
      "name": "音量減",
      "groups": [
        6,
        7
      ]
    },
    {
      "id": 83,
      "hotkey": "volumemute",
      "name": "靜音",
      "groups": [
        6,
        7
      ]
    },
    {
      "id": 84,
      "hotkey": "ctrl+alt+j",
      "name": "自動下捲",
      "groups": [
        8,
        7
      ]
    },
    {
      "id": 85,
      "hotkey": "ctrl+backquote",
      "name": "ditto",
      "groups": [
        7
      ]
    },
    {
      "id": 86,
      "kind": "run",
      "name": "CMD",
      "groups": [
        7
      ],
      "programs": [
        {
          "path": "cmd.exe",
          "args": "",
          "cwd": "",
          "admin": false
        }
      ]
    }
  ],
  "pins": [
    0,
    0,
    0,
    86,
    84,
    85
  ],
  "next_group_id": 9,
  "next_shortcut_id": 87
}
