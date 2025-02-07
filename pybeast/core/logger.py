# from built-in
import logging
import sys
import threading
# from third-party
from gi.repository import GLib
import wx

class BeastHandler(logging.StreamHandler):

    def __init__(self, beastLogWindow):
        super().__init__()

        #self.queue = queue
        self.beastLogWindow = beastLogWindow

    def emit(self, record):
        msg = self.format(record)
        GLib.idle_add(self.beastLogWindow.logMessage, msg)

class BeastLogWindow(wx.Frame):
    def __init__(self, mainWindow):
        super().__init__(parent=None, title='Log Window', size=(400, 300))

        self.mainWindow = mainWindow

        self.PopulateWindow()
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

        self.handler = BeastHandler(self)
        self.handler.setLevel(logging.INFO)
        self.handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

        self.consoleHandler = logging.StreamHandler(sys.stdout)
        self.consoleHandler.setLevel(logging.INFO)
        self.consoleHandler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def PopulateWindow(self):
        """
        Populates window with scrollable textbox to log and display application output
        """
        self.scrollWin = wx.ScrolledWindow(self, style=wx.VSCROLL)
        self.logCtrl = wx.TextCtrl(self.scrollWin, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.scrollWin.SetSizer(wx.BoxSizer(wx.VERTICAL))
        self.scrollWin.GetSizer().Add(self.logCtrl, 1, wx.EXPAND | wx.ALL, border=5)

        # Set the scrolled window as the main sizer of the frame
        self.SetSizer(wx.BoxSizer(wx.VERTICAL))
        self.GetSizer().Add(self.scrollWin, 1, wx.EXPAND)

    def CleanUp(self):

        self.scrollWin.Clear()
        self.PopulateWindow()

    def logMessage(self, msg: str):

        try:
            self.logCtrl.AppendText(msg + '\n')
        except RuntimeError as e:
            if str(e) == "wrapped C/C++ object of type TextCtrl has been deleted":
                # Error comes up in jupyter notebooks because of stale GUI references and can be savely ignored
                pass
            else:
                raise

    def OnClose(self, event: wx.CloseEvent):

        self.mainWindow.logWindow = None
        self.Destroy()