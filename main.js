const { app, BrowserWindow, Menu, shell } = require('electron');

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    title: 'Claude Desktop',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: true,
      partition: 'persist:claude'
    }
  });

  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'New Chat',
          accelerator: 'CmdOrCtrl+N',
          click: () => mainWindow.webContents.loadURL('https://claude.ai/')
        },
        { type: 'separator' },
        { label: 'Quit', accelerator: 'CmdOrCtrl+Q', click: () => app.quit() }
      ]
    },
    {
      label: 'Edit',
      submenu: [
        { role: 'undo' },
        { role: 'redo' },
        { type: 'separator' },
        { role: 'cut' },
        { role: 'copy' },
        { role: 'paste' }
      ]
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'toggleDevTools' },
        { type: 'separator' },
        { role: 'togglefullscreen' }
      ]
    }
  ];

  Menu.setApplicationMenu(Menu.buildFromTemplate(template));

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
