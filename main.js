const { app, BrowserWindow, shell } = require('electron');
const path = require('path');

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    title: 'Claude Desktop',
    icon: path.join(__dirname, 'icon.png'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: true,
      partition: 'persist:claude'
    }
  });

  // Remove the menu bar completely
  mainWindow.setMenuBarVisibility(false);

  // Handle OAuth popups - THIS IS THE KEY!
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    if (url.includes('accounts.google.com') || 
        url.includes('oauth') ||
        url.includes('login')) {
      return {
        action: 'allow',
        overrideBrowserWindowOptions: {
          width: 500,
          height: 700,
          icon: path.join(__dirname, 'icon.png'),
          webPreferences: { partition: 'persist:claude' }
        }
      };
    }
    shell.openExternal(url);
    return { action: 'deny' };
  });

  mainWindow.loadURL('https://claude.ai/');
  mainWindow.on('closed', () => { mainWindow = null; });
  
  console.log('✓ Claude Desktop started - Google OAuth fully supported!');
}

app.whenReady().then(createWindow);
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});
app.on('activate', () => {
  if (mainWindow === null) createWindow();
});
