const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('fbmy', {
  goHome: () => ipcRenderer.invoke('browser:go-home'),
  reload: () => ipcRenderer.invoke('browser:reload'),
  back: () => ipcRenderer.invoke('browser:back'),
  forward: () => ipcRenderer.invoke('browser:forward'),
  setOpacity: (opacity) => ipcRenderer.invoke('browser:set-opacity', opacity),
  toggleTop: () => ipcRenderer.invoke('browser:toggle-top'),
  minimize: () => ipcRenderer.invoke('browser:minimize'),
  close: () => ipcRenderer.invoke('browser:close'),
  setClickThrough: (enabled) => ipcRenderer.invoke('browser:set-click-through', enabled),
  mouseLeft: () => ipcRenderer.invoke('browser:mouse-left'),
  mouseEntered: () => ipcRenderer.invoke('browser:mouse-entered'),
  fitWorkArea: () => ipcRenderer.invoke('browser:fit-work-area'),
});
