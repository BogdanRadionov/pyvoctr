#!/usr/bin/env python
# -*- coding: utf-8 -*-
# TODO: Open file and save name in settings DONE
# TODO: Color picker for bg color DONE
# TODO: Set custom show interval DONE
# TODO: Set window style DONE
# TODO: Save settings DONE
# TODO: Option to 'Pin on top' DONE
# TODO: Advance to next word on click DONE
# TODO: Invoke 'Open file' if default dict file is not found DONE
# TODO: Add support for DSL files (??)
# TODO: Set display font/size
# TODO: Improve text scaling method
# TODO: Optional delay before second word appears DONE
# TODO: Swap words
# TODO: Autoresize font size for long phrases
# TODO: Hide from task bar, create icon in systray DONE
# TODO: Fix think time delay on click skip
# TODO: Add configuration for separation character
# TODO: Create options dialog
#
import sys
import os

from PyQt4 import QtCore, QtGui
WINDOW_TITLE = "Vocabulary Trainer"
DEFAULT_SHOW_DECORATIONS = False
DEFAULT_ALWAYS_ON_TOP = True
DEFAULT_THINK_TIME = 2000

DEFAULT_SHOW_TIME = 10000
DEFAULT_BG_COLOR = '#ffffff'
DEFAULT_DICT_FILE = 'en-es-pict.txt'
RELEASE = '8-8008'
ABOUT = '''Python Vocabulary Trainer %s

Author:\tGhinion Surdu
Email:\tdogpizza@gmail.com
Web:\thttp://pyvoctr.googlecode.com

Copywhite 2009, xhuman
''' % RELEASE

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(330,125)
        MainWindow.setWindowTitle(WINDOW_TITLE)
        self.centralwidget = QtGui.QWidget(MainWindow)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        # self.gridLayout.setMargin(0)
        # self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.vbox_work_area = QtGui.QVBoxLayout()
        self.vbox_work_area.setSpacing(3)
        self.vbox_work_area.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.vbox_work_area.setObjectName("vbox_work_area")
        self.lb_source = QtGui.QLabel(self.centralwidget)
        self.lb_source.setTextFormat(QtCore.Qt.RichText)
        self.lb_source.setAlignment(QtCore.Qt.AlignCenter)
        self.lb_source.setObjectName("lb_source")
        self.vbox_work_area.addWidget(self.lb_source)
        self.lb_target = QtGui.QLabel(self.centralwidget)
        self.lb_target.setTextFormat(QtCore.Qt.RichText)
        self.lb_target.setAlignment(QtCore.Qt.AlignCenter)
        self.lb_target.setObjectName("lb_target")
        self.vbox_work_area.addWidget(self.lb_target)
        self.gridLayout.addLayout(self.vbox_work_area,7,0,1,1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0,0,330,23))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)


class qapp(QtGui.QMainWindow):

    def __init__(self, parent=None):
        super(qapp, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.readSettings()
        self.createActions()
        self.createMenus()
        # self.createTrayIcon()
        self.ctimer = QtCore.QTimer()

        ## single-shot timer
        if self.think_time_enabled:
            self.timer_think_time = QtCore.QTimer()

        #self.ctimer.start(self.show_time_value)
        self.setWindowIcon(QtGui.QIcon('pyvoc.ico'))
        self.is_dragging = False
        self.popup_menu = None
        self.words = {}
        self.keys = []
        self.cur_pos = 0
        self.setMouseTracking(True)
        QtCore.QObject.connect(self.ctimer, QtCore.SIGNAL("timeout()"), self.timer_update)
        QtCore.QMetaObject.connectSlotsByName(self)

        # self.timer_toggle()
        # self.timer_update()
        #self.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        #quitAction = QtGui.QAction("Quit", self)
        #quitAction.triggered.connect(self.close)

        ## make window draggable by labels too
        self.ui.lb_source.mousePressEvent = self.mousePressEvent
        self.ui.lb_source.mouseMoveEvent = self.mouseMoveEvent
        self.ui.lb_target.mousePressEvent = self.mousePressEvent
        self.ui.lb_target.mouseMoveEvent = self.mouseMoveEvent

        ## react to label clicks
        self.ui.lb_source.mouseReleaseEvent = self.timer_skip
        self.ui.lb_target.mouseReleaseEvent = self.timer_skip

        self.setStyleSheet("QWidget { background-color: %s }" % self.bg_color )
        #QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('plastique'))
        #QtCore.QObject.connect(self.ui.button_open,QtCore.SIGNAL("clicked()"), self.file_dialog)
        self.connect(self.ui.lb_source, QtCore.SIGNAL("clicked()"), self.timer_skip)
        QtCore.QObject.connect(self.ui.lb_source, QtCore.SIGNAL("clicked()"), self.timer_skip)
        #QtCore.QObject.connect(self.ui.lb_target, QtCore.SIGNAL("clicked()"), self.timer_skip)
        # self.ui.lb_source.connect(self.actToggleAlwaysOnTop, QtCore.SIGNAL("triggered()"), self.toggle_always_on_top)
        # self.ui.lb_target.setStyleSheet("QLabel {font-size: %spx;}" % str(side/10-3))
        # !!!!!!self.connect(self.actToggleAlwaysOnTop, QtCore.SIGNAL("triggered()"), self.toggle_always_on_top)
        self.update_widgets()

    def update_widgets(self):
        #flags = QtCore.Qt.WindowFlags()
        flags = QtCore.Qt.Tool

        if self.actToggleAlwaysOnTop.isChecked():
            flags |= QtCore.Qt.WindowStaysOnTopHint

        if not self.actToggleDecorations.isChecked():
            flags |= QtCore.Qt.FramelessWindowHint

        self.setWindowFlags(flags)
        self.show()

    def setBgColor(self):
        qtColor = QtGui.QColorDialog.getColor(QtGui.QColor(self.bg_color), self)
        if qtColor.isValid():
            self.bg_color = qtColor.name()
            print self.bg_color
            self.setStyleSheet("QWidget { background-color: %s }" % self.bg_color)

    def setShowTime(self):
        val, ok = QtGui.QInputDialog.getInteger(self, "Show word for... ",
                                                "Seconds:", self.show_time_value/1000, 0, 1000, 1)
        if ok:
            self.show_time_value = val * 1000
            self.timer_toggle()
            self.timer_toggle()
            # if current think time bigger than show_time_value then
            # set it to half the value of show time value
            if self.think_time_enabled and self.think_time_value > self.show_time_value:
                self.think_time_value = int(self.show_time_value / 2)

    def setThinkTime(self):
        val2, ok = QtGui.QInputDialog.getInteger(self, "Set think time",
                                                 "Seconds:", self.think_time_value/1000, 0, 1000, 1)
        if ok:
            if val2 * 1000 > self.show_time_value:
                QtGui.QMessageBox.information(self, self.tr("Invalid value"), "Entered value is greater than show time!")
            else:
                self.think_time_value = val2 * 1000
            self.timer_toggle()
            self.timer_toggle()

    def createPopupMenu(self):
        if not self.popup_menu:
            menu = QtGui.QMenu(self)
            menu.addAction(self.actOpenData)
            menu.addAction(self.actStartStop)
            menu.addAction(self.actToggleAlwaysOnTop)
            menu.addAction(self.actToggleDecorations)
            menu.addAction(self.actSetShowTime)
            menu.addAction(self.actSetThinkTime)
            menu.addAction(self.actSwapLang)
            menu.addAction(self.actSetBgColor)
            menu.addAction(self.actAbout)
            menu.addAction(self.exitAct)
            self.popup_menu = menu
        return self.popup_menu

    def contextMenuEvent(self, event):
        menu = self.createPopupMenu()
        menu.exec_(event.globalPos())

    # capture mouse drag on main window
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
            #print event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            self.move(event.globalPos() - self.dragPosition)
            event.accept()
            self.is_dragging = True
            #print event.pos()

    def resizeEvent(self, event):
        side = min(self.width(), self.height())
        ############################################print self.
        if side > 160:
            #self.ui.lb_source.setMinimumSize(Qt.QSize(side,side))
            #self.ui.lb_source.setStyleSheet("QLabel {font-size: %spx; border: 2px solid gray; border-radius: 8px;}" % str(side/10-3))
            self.ui.lb_source.setStyleSheet("QLabel {font-size: %spx;border-radius: 8px;}" % str(side/14-3))
            self.ui.lb_target.setStyleSheet("QLabel {font-size: %spx;}" % str(side/14-3))

    def update_file_label(self):
        if self.dict_file:
            fname = os.path.basename(str(self.dict_file)) or '<none>'
            self.actOpenData.setText('Open dictionary... (%s)' % fname)
            self.setWindowTitle(WINDOW_TITLE + " (%s)" % fname)

    def init_data(self):
        if os.path.exists(self.dict_file):
            print '[init_data] Found dictionary:', self.dict_file
        else:
            print 'No dictionary file'
            self.setDictionaryFile('Dictionary not found. Please select'+
                                   ' a dictionary file.')
        if not os.path.exists(self.dict_file):
            print 'No dictionary file selected'
        self.cur_pos = 0

        # if self.ctimer.isActive():
            # self.ctimer.stop()
        self.load_dictionary(self.dict_file)
        self.update_file_label()
        self.timer_update()

    def load_dictionary(self, file_name):
        print 'Loading dictionary file %s...' % file_name

        # reset dictionary
        if self.words:
            self.words.clear()
        for line in open(file_name).readlines():
            ## skip empty lines and comments
            if not line.strip() or line.startswith('#'):
                continue
            try:
                k, v = line.decode('utf8').split(' = ')
                k = k.replace('"','')
                #print k, v
                self.words[k.strip()] = v.strip()
            except Exception, e:
                try:
                    k, v = line.decode('utf8').split('=')
                    k = k.replace('"','')
                except Exception, e2:
                    print e2, line

        self.keys = self.words.keys()
        print 'Loaded %s entries from dictionary' % len(self.keys)
        #self.ui.progbar_constant.maximum = len(self.keys)
        #self.ui.progbar_constant.minimum = 0
        ## set initial values
        self.ui.lb_source.setText('<h2><font color="green">' + self.words[self.keys[self.cur_pos]] + '</h2>')
        self.ui.lb_target.setText('<h2><font color="darkblue">' + self.keys[self.cur_pos] + '</font></h2>')


    def toggle_always_on_top(self):
        print 'always on top', self.actToggleAlwaysOnTop.isChecked()
        self.update_widgets();


    def toggle_decorations(self):
        print 'show decorations', self.actToggleDecorations.isChecked()
        self.update_widgets()

    def swapLanguages(self):
        self.swap_languages = not self.swap_languages

    def setDictionaryFile(self, msg=None):
        self.dict_file = QtGui.QFileDialog.getOpenFileName(self,
                                                           msg or 'Load dictionary file',
                                                           '',
                                                           "Vocabulary files (*.txt);;All Files (*.*);")
        if os.path.exists(self.dict_file):
            self.init_data()
            self.update_file_label()
        else:
            print 'No such file:', self.dict_file

    def timer_update(self):
        """
        slot for show time timer
        """

        if  self.cur_pos >= len(self.keys):
            self.cur_pos = 0
            #self.ui.progbar_constant.reset()
        #self.ui.progbar_constant.setValue(self.cur_pos)
        if self.actSwapLang.isChecked():
            word1 = self.keys[self.cur_pos]
            word2 = self.words[self.keys[self.cur_pos]]
        else:
            word2 = self.keys[self.cur_pos]
            word1 = self.words[self.keys[self.cur_pos]]
        self.ui.lb_source.setText('<h3><font color="green">' + word1 + '</h3>')
        word2_formatted = '<h3><font color="darkblue">' + word2 + '</font></h3>'

        if not self.think_time_enabled or self.think_time_value == 0:
            self.ui.lb_target.setText(word2_formatted)
        else:
            self.ui.lb_target.setText('')
            self.timer_think_time.singleShot(self.think_time_value, lambda : self.ui.lb_target.setText(word2_formatted))
        self.cur_pos += 1

    def timer_skip(self, event):
        print 'timer_skip...'
        if not self.is_dragging and event.button() == QtCore.Qt.LeftButton:
            if self.ctimer.isActive():
                #self.ctimer.timout.emit()
                self.ctimer.emit(QtCore.SIGNAL("timeout()"))
            if self.timer_think_time.isActive():
                self.timer_think_time.emit(QtCore.SIGNAL("timeout()"))
                #self.timer_think_time.timeout.emit()
                #self.timer_toggle()
                #self.timer_toggle()
                ##self.timer_think_time.stop()

                ##self.ctimer.stop()
                ##self.ctimer.start()
                #self.timer_think_time.stop()
                #self.timer_think_time.start()
            #self.timer_update()
        if self.is_dragging:
            self.is_dragging = False

    def timer_toggle(self):
        """ Start/stop timer """
        if not self.ctimer.isActive():
            self.ctimer.start(self.show_time_value) # start timer
            #self.ui.btn_constant.setText('Stop')
            #self.ui.lnk_start.setText('Stop')
            self.actStartStop.setChecked(True)
        else:
            self.ctimer.stop()
            ##self.ui.btn_constant.setText('Start')
            #self.ui.lnk_start.setText('Start')
            self.actStartStop.setChecked(False)

    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu(u"\u263c")
        self.fileMenu.addAction(self.actOpenData)
        self.fileMenu.addAction(self.actToggleAlwaysOnTop)
        self.fileMenu.addAction(self.actToggleDecorations)
        self.fileMenu.addAction(self.actSetShowTime)
        #self.fileMenu.addAction(self.actHideWindowTitle)
        #self.fileMenu.addAction(self.actUnhideWindowTitle)
        self.fileMenu.addAction(self.actSwapLang)
        self.fileMenu.addAction(self.actStartStop)
        self.fileMenu.addAction(self.actSetBgColor)
        self.fileMenu.addAction(self.actAbout)
        self.fileMenu.addAction(self.exitAct)

    def createActions(self):
        self.exitAct = QtGui.QAction("E&xit", self)
        self.exitAct.setShortcut("Ctrl+Q")
        #self.exitAct.setStatusTip("Exit the application")
        self.connect(self.exitAct, QtCore.SIGNAL("triggered()"), self.close)

        self.actToggleAlwaysOnTop = QtGui.QAction("Always on top", self)
        self.actToggleAlwaysOnTop.setCheckable(True)
        self.actToggleAlwaysOnTop.setChecked(self.always_on_top)
#        self.connect(self.actToggleAlwaysOnTop, QtCore.SIGNAL("toggled(checked)"), self.toggle_always_on_top)
        self.connect(self.actToggleAlwaysOnTop, QtCore.SIGNAL("triggered()"), self.toggle_always_on_top)

        self.actToggleDecorations = QtGui.QAction("Show window &frame", self)
        self.actToggleDecorations.setCheckable(True)
        self.actToggleDecorations.setChecked(self.show_decorations)
        self.actToggleDecorations.setShortcut("Ctrl+B")
        self.connect(self.actToggleDecorations, QtCore.SIGNAL("triggered()"), self.toggle_decorations)
#        self.connect(self.actToggleDecorations, QtCore.SIGNAL("toggled(checked)"), self.toggle_decorations)
        #!!!!!! self.connect(self.deviceView, QtCore.SIGNAL('toggled(bool)'), self.showDeviceView)

        self.actStartStop = QtGui.QAction("S&tart/Stop", self)
        self.actStartStop.setShortcut("Ctrl+S")
        #self.actStartStop.setStatusTip("Toggle timer")
        self.actStartStop.setCheckable(True)
        self.connect(self.actStartStop, QtCore.SIGNAL("triggered()"), self.timer_toggle)

        self.actSetBgColor = QtGui.QAction("Set background &color", self)
        self.actSetBgColor.setShortcut("Ctrl+G")
        self.connect(self.actSetBgColor, QtCore.SIGNAL("triggered()"), self.setBgColor)

        self.actSetShowTime = QtGui.QAction("Set show time", self)
        self.connect(self.actSetShowTime, QtCore.SIGNAL("triggered()"), self.setShowTime)

        self.actSetThinkTime = QtGui.QAction("Set think time", self)
        self.connect(self.actSetThinkTime, QtCore.SIGNAL("triggered()"), self.setThinkTime)

        self.actOpenData = QtGui.QAction("Open dictionary", self)
        self.actOpenData.setShortcut("Ctrl+O")
        self.connect(self.actOpenData, QtCore.SIGNAL("triggered()"), self.setDictionaryFile)

        self.actSwapLang = QtGui.QAction("Swap languages", self)
        self.actSwapLang.setShortcut("Ctrl+W")
        self.actSwapLang.setCheckable(True)
        self.actSwapLang.setChecked(self.swap_languages)
        self.connect(self.actSwapLang, QtCore.SIGNAL("triggered()"), self.swapLanguages)

        self.actAbout = QtGui.QAction("About", self)
        self.connect(self.actAbout, QtCore.SIGNAL("triggered()"), self.showAboutDialog)

    def showAboutDialog(self):
        ret = QtGui.QMessageBox.information(self, 'About Python Vocabulary Trainer', ABOUT)


    def createTrayIcon(self):
        ik = QtCore.QString("pyvoc.ico")
        menu = self.createPopupMenu()
        # quitAction = menu.addAction('Quit')
        sicon = QtGui.QIcon(ik)
        tray = QtGui.QSystemTrayIcon(sicon)
        self.tray_ = tray
        tray.setContextMenu(menu)
        tray.show()

    def closeEvent(self, event):

        quit_msg = "Exit the program?"
        reply = QtGui.QMessageBox.question(self, 'Message',
                                           quit_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            self.writeSettings()
            event.accept()
            self.tray_.deleteLater()
            QtGui.QApplication.instance().quit()
            #self.destroy()  # causes QObject::killTimers: timers cannot be stopped from another thread
        else:
            event.ignore()

    def readSettings(self):
        # store settings object
        self.settings = QtCore.QSettings(QtCore.QSettings.IniFormat, QtCore.QSettings.UserScope, "xh", "pyvoctr")

        #store config in local variables
        self.bg_color = self.settings.contains('bg_color') and self.settings.value("bg_color").toString() or DEFAULT_BG_COLOR
        self.show_time_value = self.settings.contains('show_time_value') and self.settings.value("show_time_value").toInt()[0] or DEFAULT_SHOW_TIME
        self.dict_file = self.settings.contains('dict_file') and self.settings.value("dict_file").toString() or DEFAULT_DICT_FILE
        self.show_decorations = self.settings.contains('show_decorations') and self.settings.value("show_decorations").toBool() or DEFAULT_SHOW_DECORATIONS
        self.always_on_top = self.settings.contains('always_on_top') and self.settings.value("always_on_top").toBool() or DEFAULT_ALWAYS_ON_TOP
        self.think_time_enabled = self.settings.contains('think_time_enabled') and self.settings.value("think_time_enabled").toBool() or DEFAULT_THINK_TIME
        self.think_time_value = self.settings.contains('think_time_value') and self.settings.value("think_time_value").toInt()[0] or DEFAULT_THINK_TIME
        self.swap_languages = self.settings.contains('swap_languages') and self.settings.value("swap_languages").toBool() or False
        # restore positioning
        window_flags_ = self.settings.value("window_flags").toInt()[0]
        print 'window_flags_=', window_flags_, type(window_flags_)
        if isinstance(window_flags_, int) and window_flags_:
            self.setWindowFlags(QtCore.Qt.WindowType(window_flags_))
            self.windows_flags = window_flags_

        pos = self.settings.value("pos", QtCore.QVariant(QtCore.QPoint(200, 200))).toPoint()
        size = self.settings.value("size", QtCore.QVariant(QtCore.QSize(400, 400))).toSize()
        self.resize(size)
        self.move(pos)

    def writeSettings(self):
        settings = QtCore.QSettings(QtCore.QSettings.IniFormat, QtCore.QSettings.UserScope, "xh", "pyvoctr")
        settings.setValue("pos", QtCore.QVariant(self.pos()))
        settings.setValue("size", QtCore.QVariant(self.size()))
        settings.setValue("always_on_top", QtCore.QVariant(self.actToggleAlwaysOnTop.isChecked()))
        settings.setValue("show_decorations", QtCore.QVariant(self.actToggleDecorations.isChecked()))
        settings.setValue("think_time_enabled", QtCore.QVariant(self.think_time_enabled))
        settings.setValue("bg_color", QtCore.QVariant(self.bg_color))
        settings.setValue("show_time_value", QtCore.QVariant(self.show_time_value))
        settings.setValue("dict_file", QtCore.QVariant(self.dict_file))
        settings.setValue("window_flags", QtCore.QVariant(int(self.windowFlags())))
        settings.setValue("think_time_value", QtCore.QVariant(self.think_time_value))
        settings.setValue("swap_languages", QtCore.QVariant(self.swap_languages))
        settings.sync()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = qapp()
    myapp.init_data()
    myapp.timer_toggle()
    myapp.show()
    myapp.createTrayIcon()
    #myapp.update_widgets()
    sys.exit(app.exec_())
