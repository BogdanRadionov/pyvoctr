'''
Created on Jul 1, 2011
TODO:
1. Load channel list from M3U file                DONE
2. Detect launch type by extension or marker
3. Add sopcast support
4. Full-screen checkbox                           DONE
5. Volume control?
6. Tree control?
7. embed console output
8. asx parsing
9. open/save/edt playlist                         DONE
10. add Edit Source                               DONE
11. handle screensaver!!! xorg, etc.
12. on top
13. add 'open with system default engine' by extension
14. add 'open with default browser'

@author: xh
'''

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.Qt import Qt
import subprocess
import time
import urllib
import codecs
import os
import sys

DEFAULT_CHANNELS_FILE = '/home/xh/es.m3u'
MPLAYER_PATH = r'c:\Program Files\mplayer\mplayer.exe'
VLC_PATH = r'c:\Program Files\VideoLAN\VLC\vlc.exe'
SOPCAST_SERVER_WAIT_SECS = 8

print('Python Version=' + sys.version)
is_win32 = sys.platform == "win32"

EDITOR = is_win32 and 'notepad' or os.path.exists('/usr/bin/leafpad') and 'leafpad' \
    or os.path.exists('/usr/bin/mousepad') and 'mousepad' \
    or os.path.exists('/usr/bin/gvim') and 'gvim' \
    or os.getenv('EDITOR', 'gvim')

window_id = None

def getFirstUrl(playlist):
    lines = urllib.urlopen(str(playlist)).readlines()
    for line in lines:
        if not line.startswith('#'):
            return line

def suspend_screensaver():
    if is_win32:
        return
    # get root windows id 
    global window_id
    window_id = commands.getoutput('xwininfo -root | grep xwininfo | cut -d" " -f4')
    print ('xwininfo -root output', window_id)

    #run xdg-screensaver on root window
    xdg_output = commands.getoutput('xdg-screensaver suspend ' + window_id)
    print('xdg-screen-suspend', xdg_output)

def resume_screensaver():
    if is_win32:
        return
    if window_id:
        xdg_output = commands.getoutput('xdg-screensaver resume %s ' % window_id)
        print('xdg-screen-resume', xdg_output)

class MyForm(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        # setGeometry(x_pos, y_pos, width, height)
        self.setGeometry(100, 150, 500, 460)
        self.readSettings()
        self.setWindowTitle("ChanChan - " + self.chanells_path)
        self.icon_path = os.path.join(os.path.dirname(sys.argv[0]), 'chanchan.ico')
        self.setWindowIcon(QIcon(self.icon_path))

        # the mplayer subprocess process
        self.proc = None
        self.proc_sopcast = None
        self.is_sopcast = False


        # use a grid layout for the widgets
        grid = QGridLayout()

        ###btn_load = QPushButton("Load List")
        # bind the button click to a function reference
        # new connect style, needs PyQt 4.5+
        ###btn_load.clicked.connect(self.load_channels_data)    

        btn_play = QPushButton("Play")
        btn_play.clicked.connect(self.play_media)
        btn_kill = QPushButton("Stop")
        btn_kill.clicked.connect(self.kill_proc)

        self.listbox = QListWidget()
        # new connect style, needs PyQt 4.5+
        self.listbox.clicked.connect(self.on_select)

        self.listbox.doubleClicked.connect(self.on_double_click)

        # attach right-click handler
        self.listbox.setContextMenuPolicy(Qt.ActionsContextMenu)
        #self.listbox.setContextMenuPolicy(Qt.CustomContextMenu)
        #http://talk.maemo.org/showthread.php?t=64034
        self.actionCopyUrl = QAction("Copy URL", self.listbox)
        self.connect(self.actionCopyUrl, SIGNAL("triggered()"), self.copy_to_clipboard)
        self.actionPlay = QAction("Play", self.listbox)
        self.actionReloadChannels = QAction("Reload List", self.listbox)
        self.actionEditChannels = QAction("Edit Playlist", self.listbox)
        self.actionOpenChannelsFile = QAction("Open Playlist File", self.listbox)
        self.actionEditSource = QAction("Edit Source", self.listbox)

        self.listbox.addAction(self.actionPlay)
        self.listbox.addAction(self.actionCopyUrl)
        self.listbox.addAction(self.actionReloadChannels)
        self.listbox.addAction(self.actionEditChannels)
        self.listbox.addAction(self.actionOpenChannelsFile)
        self.listbox.addAction(self.actionEditSource)

        self.connect(self.actionPlay, SIGNAL("triggered()"), self.on_double_click)
        self.connect(self.actionReloadChannels, SIGNAL("triggered()"), self.load_channels_data)
        self.connect(self.actionEditChannels, SIGNAL("triggered()"), lambda: self.edit_file(str(self.chanells_path)))
        self.connect(self.actionOpenChannelsFile, SIGNAL("triggered()"), self.open_channels_file)
        self.connect(self.actionEditSource, SIGNAL("triggered()"), lambda: self.edit_file(path=sys.argv[0], editor='scite'))
#        self.listbox.connect(self.listbox, SIGNAL("customContextMenuRequested(QPoint)"), 
#                             self.on_right_click) 

        self.txtChanInfo = QLineEdit()
        self.txtChanInfo.setReadOnly(True)

#        self.logWindow = QTextEdit()
#        self.logWindow.setSizePolicyx(QSizePolicy.)
#        self.status = QLabel()

        self.groupBox = QGroupBox("Engine")
#        self.groupBox.setEnabled(True)
#        self.groupBox.setStyle(QStyle.C)
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
#        self.groupBox.setAutoFillBackground(True)

        self.rbMplayer = QRadioButton('Mplayer', self.groupBox)
        self.rbMplayer.setChecked(True)
        self.rbGstreamer = QRadioButton('GStreamer', self.groupBox)
        self.rbVlc = QRadioButton('Vlc', self.groupBox)
        self.rbTotem = QRadioButton('Totem', self.groupBox)

        self.hBoxTop = QHBoxLayout()
        self.hBoxTop.addWidget(self.rbMplayer)
        self.hBoxTop.addWidget(self.rbGstreamer)
        self.hBoxTop.addWidget(self.rbVlc)
        self.hBoxTop.addWidget(self.rbTotem)
        self.groupBox.setLayout(self.hBoxTop)

        self.cbPlaylistFlag = QCheckBox('Playlist')
        self.cbPlaylistFlag.setToolTip('Resource is a M3U, ASX or PLS playlist')

        self.cbFullScreen = QCheckBox('Full Screen')
        self.cbFullScreen.setToolTip('Start video in full screen')
        self.cbFullScreen.setChecked(self.is_full_screen)
        self.cbInhibitScreensaver = QCheckBox('Inhibit Screensaver')
        self.cbInhibitScreensaver.setToolTip('Disable screensaver while playing stream')
        self.cbInhibitScreensaver.setChecked(self.is_inhibit_screen)
#        self.hBoxFlags = QHBoxLayout()
#        self.hBoxFlags.addWidget(self.cbPlaylistFlag)
#        self.hBoxFlags.addWidget(self.cbFullScreen)
        # addWidget(widget, row, column, rowSpan, columnSpan)
        ###grid.addWidget(btn_load, 0, 0, 1, 1)
#        grid.addWidget(self.rbMplayer, )
#        grid.addWidget(self.rbGroup, 0, 0, 0, 1)
        grid.addWidget(self.groupBox, 0, 0, 1, 3)
        grid.addWidget(btn_play, 0, 4, 1, 1)
        grid.addWidget(btn_kill, 0, 5, 1, 1)
        # listbox spans over 5 rows and 2 columns
        grid.addWidget(self.listbox, 1, 0, 5, 6)
        ## BAD grid.addWidget(self.hBoxFlags, 6, 0, 1, 1)
#        grid.addLayout(self.hBoxFlags, 6, 0, 1, 1, Qt.Alignmen
        grid.addWidget(self.cbPlaylistFlag, 6, 0, 1, 1)
        grid.addWidget(self.cbFullScreen, 6, 1, 1, 1)
        grid.addWidget(self.cbInhibitScreensaver, 6, 2, 1, 1)
        grid.addWidget(self.txtChanInfo, 7, 0, 1, 6)
#        grid.addWidget(self.logWindow, 8, 0, 1, 6)
#        grid.addWidget(self.status, 8, 0, 1, 3)
        self.setLayout(grid)
                # make chanells available for methods
#        self.chanells_path = None
        self.chanells = self.load_channels_data()

    def closeEvent(self, event):

        quit_msg = "Are you sure you want to exit the program?"
        reply = QMessageBox.question(self, 'Message',
                                           quit_msg, QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.writeSettings()
            event.accept()
#            self.tray_.deleteLater()
            QApplication.instance().quit()
            #self.destroy()  # causes QObject::killTimers: timers cannot be stopped from another thread
        else:
            event.ignore()

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.listbox.currentItem().text())

    def load_channels_data(self):
        """the load button has been clicked, load the listbox"""
        fh = None;
        try:
            fh = codecs.open(self.chanells_path, 'r', 'utf8')
            self.chanells = [ch.strip() for ch in fh.readlines()]
        except:
            pass

        if not fh:
            self.open_channels_file()

        self.chanells = [ch.strip() for ch in self.chanells]
        self.chanells = [(ch.startswith('#EXTINF:-1,') and ch[11:] or ch) for ch in self.chanells]
        self.listbox.clear()
        for chan in self.chanells:
            if not len(chan):
                continue
            item = None
            if chan.startswith('#'):
                item = QListWidgetItem(chan[1:])
                item.setFlags(item.flags() ^ Qt.ItemIsSelectable)
                item.setFlags(item.flags() ^ Qt.ItemIsEnabled)
                item.setBackgroundColor(QColor('#CEE1B6'))
                                           #Qt.gray)
                item.setTextColor(QColor('#9F5700'))
            else:
                item = QListWidgetItem(chan)
                item.setIcon(QIcon('chanchan.ico'))
#                item.setFlags(item.flags() | Qt.ItemIsEditable)
            item.setStatusTip(chan)
            self.listbox.addItem(item)
#        self.listbox.addItems(self.chanells)
        self.setWindowTitle('ChanChan - ' + self.chanells_path)

    def edit_file(self, path, editor=EDITOR):
        subprocess.Popen([editor, path])

    def open_channels_file(self):
        self.chanells_path = QFileDialog.getOpenFileName(self,
                                                           'Load Playlist file',
                                                           '',
                                                           "Playlist files (*.m3u);;All Files (*.*);")
        if os.path.exists(self.chanells_path):
            self.load_channels_data()
        else:
            print ('No such file:', self.chanells_path)

    def on_quit(self):
        QApplication.instance().quit()

    def on_select(self):
        """an item in the listbox has been clicked/selected"""
        #current_channel = self.listbox.selectedItems()[0].text()
        current_channel = self.listbox.currentItem().text()
#        self.setWindowTitle(current_channel)
        self.txtChanInfo.setText(current_channel)
        is_playlist = (str(current_channel)[-4:]).lower() in ['.m3u', '.asx', '.pls']
        self.cbPlaylistFlag.setChecked(is_playlist)
#        self.status.setText(current_channel)

    def on_double_click(self):
        self.play_media()
        """an item in the listbox has been double-clicked"""

    def play_media(self):
        #current_channel = self.listbox.selectedItems()[0].text()
        #       current_channel = self.listbox.currentItem().text()
        current_channel = self.listbox.currentItem().text()
        if self.proc and self.proc.pid:
            self.kill_proc()
            time.sleep(1)

        args = []

        # don't use xterm for vlc, totem
        if not is_win32 and (self.rbMplayer.isChecked() or self.rbGstreamer.isChecked()):
            args += ['xterm', '-geometry', '45x8-20+150', '-e']


        ################ SOPCAST #############
        if str(current_channel).startswith('sop://'):
            self.is_sopcast = True
            args_sopcast = ['xterm', '-geometry', '45x8-20+400', '-e', 'sopcast', current_channel, '3889', '37557' ]
            try:
                self.proc_sopcast = subprocess.Popen(args_sopcast)

            except Exception as e:
                QMessageBox.warning(self, '', "ERROR! Sopcast executable not found:\n%s" % str(e))

#            args += ['mplayer', '-cache', '256', '-ontop']
#            self.cbFullScreen.isChecked() and args.append('-fs')
            current_channel = 'http://127.0.0.1:37557'
            print ('Waiting for sopcast server starup at %s ...' % current_channel)
            time.sleep(SOPCAST_SERVER_WAIT_SECS)

        if self.rbMplayer.isChecked():
            if is_win32:
                args = ['cmd', '/k', MPLAYER_PATH, '-cache', '64', '-ontop']
            else:
                args += ['mplayer', '-cache', '1000', '-ontop']
            self.cbFullScreen.isChecked() and args.append('-fs')
            self.cbPlaylistFlag.isChecked() and args.append('-playlist')

        elif self.rbGstreamer.isChecked():
            args.append('gst123')
            if '.m3u' in current_channel:
                current_channel = getFirstUrl(current_channel)

        elif self.rbVlc.isChecked():
            if is_win32:
                args = [VLC_PATH]
            else:
                args = ['vlc']
            self.cbFullScreen.isChecked() and args.append('--fullscreen')
            args.append('--video-on-top')

        elif self.rbTotem.isChecked():
            args += ['totem', '--replace']
#            self.cbFullScreen.isChecked() and args.append('--fullscreen')
#            args.append('--replace')

        args.append(str(current_channel))

        print (args)
#        QMessageBox.information(self, 'double-clicked!', "DBL-CLICK-EVENT")
        try:
            if is_win32:
                self.proc = subprocess.Popen(args, creationflags=subprocess.CREATE_NEW_CONSOLE, cwd=os.path.dirname(sys.argv[0]))
            else:
                self.proc = subprocess.Popen(args, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
#                console_data = self.proc.stdout.read()
#                self.logWindow.setText(console_data)


        except Exception as e:
            QMessageBox.warning(self, '', "ERROR! Selected engine not available:\n%s" % str(e))

        if self.cbInhibitScreensaver.isChecked():
            suspend_screensaver()
        #### TODO Read non-blocking: 
        #### http://stackoverflow.com/questions/375427/non-blocking-read-on-a-subprocess-pipe-in-python
#        stdin, stdout = self.proc.communicate()
#        self.logWindow.setText(stdin)

    def on_right_click(self):
        QMessageBox.information(self, 'right-click!', "RT-CLICK-EVENT" + self.listbox.currentRow())


    def kill_proc(self):
        if self.cbInhibitScreensaver.isChecked():
            resume_screensaver()
        if self.proc:
            try:
                self.proc.kill()
            except:
                pass
        if self.is_sopcast and self.proc_sopcast:
            try:
                self.proc_sopcast.kill()
                os.system('killall sopcast')
            except:
                pass

    def readSettings(self):
        # store settings object
        self.settings = QSettings(QSettings.IniFormat, QSettings.UserScope, "xh", "chanchan")
        pos = self.settings.value("pos", QVariant(QPoint(200, 200))).toPoint()
        size = self.settings.value("size", QVariant(QSize(400, 400))).toSize()
        self.resize(size)
        self.move(pos)
        self.chanells_path = self.settings.contains('channels_file') and self.settings.value("channels_file").toString() or DEFAULT_CHANNELS_FILE
        self.is_inhibit_screen = self.settings.contains('inhibit_screen') and self.settings.value("inhibit_screen").toBool()
        self.is_full_screen = self.settings.contains('fullscreen') and self.settings.value("fullscreen").toBool()

    def writeSettings(self):
        settings = QSettings(QSettings.IniFormat, QSettings.UserScope, "xh", "chanchan")
        settings.setValue("pos", QVariant(self.pos()))
        settings.setValue("size", QVariant(self.size()))
        settings.setValue("channels_file", QVariant(self.chanells_path))
        settings.setValue("inhibit_screen", QVariant(self.cbInhibitScreensaver.isChecked()))
        settings.setValue("fullscreen", QVariant(self.cbFullScreen.isChecked()))
        settings.sync()
#       self.setWindowTitle(current_channel)

app = QApplication([])
form = MyForm()
form.show()
app.exec_()

