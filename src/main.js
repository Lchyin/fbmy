const { app, BrowserWindow, BrowserView, globalShortcut, ipcMain, screen } = require('electron');

const HOME_URL = 'https://www.fenbi.com/';
const MIN_OPACITY = 0.2;
const MAX_OPACITY = 1;
const DEFAULT_OPACITY = 0.88;

let mainWindow;
let webView;
let isHiddenByMouse = false;

function clampOpacity(value) {
  const parsed = Number(value);
  if (Number.isNaN(parsed)) {
    return DEFAULT_OPACITY;
  }
  return Math.min(MAX_OPACITY, Math.max(MIN_OPACITY, parsed));
}

function updateViewBounds() {
  if (!mainWindow || !webView) return;

  const [width, height] = mainWindow.getContentSize();
  webView.setBounds({ x: 0, y: 72, width, height: Math.max(0, height - 72) });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1160,
    height: 760,
    minWidth: 760,
    minHeight: 480,
    transparent: true,
    frame: false,
    hasShadow: true,
    backgroundColor: '#00000000',
    opacity: DEFAULT_OPACITY,
    title: '粉笔摸鱼浏览器',
    webPreferences: {
      preload: `${__dirname}/preload.js`,
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  webView = new BrowserView({
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
  });

  mainWindow.setBrowserView(webView);
  mainWindow.loadFile(`${__dirname}/renderer.html`);
  webView.webContents.loadURL(HOME_URL);
  updateViewBounds();

  mainWindow.on('resize', updateViewBounds);
  mainWindow.on('enter-full-screen', updateViewBounds);
  mainWindow.on('leave-full-screen', updateViewBounds);

  mainWindow.on('blur', () => {
    if (mainWindow?.isAlwaysOnTop()) return;
    mainWindow?.setOpacity(Math.min(mainWindow.getOpacity(), 0.55));
  });

  mainWindow.on('focus', () => {
    mainWindow?.setOpacity(DEFAULT_OPACITY);
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
    webView = null;
  });
}

function registerShortcuts() {
  globalShortcut.register('CommandOrControl+Shift+H', () => {
    if (!mainWindow) return;
    if (mainWindow.isVisible()) {
      mainWindow.hide();
    } else {
      mainWindow.show();
      mainWindow.focus();
    }
  });

  globalShortcut.register('CommandOrControl+Shift+Q', () => app.quit());
}

app.whenReady().then(() => {
  createWindow();
  registerShortcuts();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

app.on('will-quit', () => {
  globalShortcut.unregisterAll();
});

ipcMain.handle('browser:go-home', () => webView?.webContents.loadURL(HOME_URL));
ipcMain.handle('browser:reload', () => webView?.webContents.reload());
ipcMain.handle('browser:back', () => {
  if (webView?.webContents.canGoBack()) webView.webContents.goBack();
});
ipcMain.handle('browser:forward', () => {
  if (webView?.webContents.canGoForward()) webView.webContents.goForward();
});
ipcMain.handle('browser:set-opacity', (_event, opacity) => {
  const nextOpacity = clampOpacity(opacity);
  mainWindow?.setOpacity(nextOpacity);
  return nextOpacity;
});
ipcMain.handle('browser:toggle-top', () => {
  if (!mainWindow) return false;
  const next = !mainWindow.isAlwaysOnTop();
  mainWindow.setAlwaysOnTop(next, 'floating');
  return next;
});
ipcMain.handle('browser:minimize', () => mainWindow?.minimize());
ipcMain.handle('browser:close', () => app.quit());
ipcMain.handle('browser:set-click-through', (_event, enabled) => {
  mainWindow?.setIgnoreMouseEvents(Boolean(enabled), { forward: true });
  return Boolean(enabled);
});
ipcMain.handle('browser:mouse-left', () => {
  if (!mainWindow || isHiddenByMouse) return;
  isHiddenByMouse = true;
  mainWindow.setOpacity(0.08);
});
ipcMain.handle('browser:mouse-entered', () => {
  if (!mainWindow || !isHiddenByMouse) return;
  isHiddenByMouse = false;
  mainWindow.setOpacity(DEFAULT_OPACITY);
});
ipcMain.handle('browser:fit-work-area', () => {
  if (!mainWindow) return;
  const { width, height } = screen.getPrimaryDisplay().workAreaSize;
  mainWindow.setSize(Math.round(width * 0.72), Math.round(height * 0.76));
  mainWindow.center();
});
