# 浏览器（Python 版）

一个受 Thief 网页摸鱼思路启发的 Python 桌面脚本。默认打开粉笔网，但地址栏支持输入任意网址，适合在半透明窗口中浏览网页。

## 功能

- 默认加载 `https://www.fenbi.com/`，也可以在地址栏输入任意网址后回车或点击“打开”
- 页面内普通链接、`target=_blank` / 新窗口链接都会在当前浏览器窗口中跳转
- 无边框半透明窗口，可拖拽顶部工具栏移动
- 鼠标拖拽窗口边缘或四角即可调整页面宽高
- 后退、前进、打开、首页、刷新、居中、置顶、隐藏、退出
- 透明度滑块
- “穿透”按钮会让网页区域忽略鼠标事件，工具栏仍可点击以便关闭穿透
- 鼠标离开窗口后自动隐藏为低透明悬浮小条，鼠标移回小条时恢复
- 快捷键：`Ctrl/⌘ + Shift + H` 隐藏/恢复，`Ctrl/⌘ + Shift + Q` 退出
- 支持 Windows 10/11、macOS、Linux（依赖 Qt WebEngine 能力）

## Windows 使用

推荐安装 Python 3.10 或更新版本，然后在 PowerShell 中执行：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python fbmy.py
```

如果 PowerShell 禁止激活虚拟环境，可以先执行：

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## macOS / Linux 使用

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python fbmy.py
```

## 检查

```bash
python -m py_compile fbmy.py
```

## 参考实现

本项目参考了 Thief 的网页摸鱼思路：透明置顶窗口、网页模式、快捷键隐藏/恢复、透明度调整等；Python 版保留这些核心交互，并增加任意网址访问、当前窗口内链接跳转、鼠标拖拽缩放和网页区域穿透。

> 注意：Python/Qt 版的“穿透”默认作用于网页区域，保留工具栏可点击，避免开启穿透后无法关闭。
