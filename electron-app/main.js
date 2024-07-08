const { app, BrowserWindow } = require('electron')

let mainWindow;

app.whenReady().then(() => {
    mainWindow = new BrowserWindow(() => {

    });
    mainWindow.loadURL(`file://${__dirname}/src/index.html`)
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
})
