# 粉笔摸鱼浏览器（Python 版）

一个受墨鱼阅读启发的 Python 桌面脚本，默认打开粉笔网，适合在半透明窗口中浏览和刷题。

## 功能

- 默认加载 `https://www.fenbi.com/`
- 无边框半透明窗口，可拖拽顶部工具栏移动
- 后退、前进、打开粉笔首页、刷新、居中、置顶、隐藏、退出
- 透明度滑块
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

> 注意：Python/Qt 版本保留了穿透开关的位置，但默认不会真正启用全窗口鼠标穿透，避免开启后无法再点击窗口恢复。若后续需要 Windows 原生鼠标穿透，可以继续用 `ctypes` 调 Windows API 扩展。
