# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 2017/3/7


'''
try:
    from BQt.QtGui import *
    from BQt.QtWidgets import *
    from BQt.QtCore import *
    from BQt.QtWidgets import *
    Signal = pyqtSignal
except:
    from PySide.QtGui import *
    from PySide.QtCore import *
'''


# try:
#     from PySide.QtGui import *
#     from PySide.QtCore import *
# except:
#     from PyQt4.QtGui import *
#     from PyQt4.QtCore import *
#     Signal = pyqtSignal

from module import *

import sys
import os
import shutil
import time
import sendNodes_path as SP
import sendNodes_helper as SH



reload(sys)
sys.setdefaultencoding('utf-8')


Users_Folder = SP.USERS_Folder
Global_Folder = SP.GLOBAL_Folder
Icons_Folder = "%s/icons" % Global_Folder
Current_User = SH.Current_User
Current_User_Folder = "%s/%s" % (Users_Folder, Current_User)



Emoji_Format = ["jpg", "png", "gif"]


class MainWidget(QTabWidget):
    sendemoji = Signal()

    def __init__(self):
        super(MainWidget, self).__init__()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)


        self.setStyleSheet("""
                            QScrollArea{border:none;}

                            """)

        self.definedEmojiArea = QScrollArea()
        self.definedEmojiArea.setAlignment(Qt.AlignCenter)
        self.definedEmojiGrid = DefinedEmojiGrid()
        self.definedEmojiGrid.emojiclicked.connect(self.send_defined_emoji)

        self.customEmojiArea = QScrollArea()
        self.customEmojiArea.setAlignment(Qt.AlignCenter)
        self.customEmojiGrid = CustomEmojiGrid()
        self.customEmojiGrid.emojiclicked.connect(self.send_custom_emoji)

        time1 = time.time()
        self.refresh_grid()
        time2 = time.time()
        #print time2 - time1

        self.definedEmojiArea.setWidget(self.definedEmojiGrid)
        self.customEmojiArea.setWidget(self.customEmojiGrid)

        self.addTab(self.definedEmojiArea, "in")
        self.addTab(self.customEmojiArea, "custom")

        self.sendEmojiName = ""
        self.sendEmojiType = "defined" # defined, custom
        self.sendEmojiSize = 0 # small, middle, big

        self.setFixedSize(350, 233)
        #self.adjustSize()
        #print self.width(), self.height()

        #self.timer = QTimer()
        #self.timer.start(1000)
        #self.timer.timeout.connect(self.test)

    def test(self):
        print 1

    def refresh_grid(self):
        self.definedEmojiGrid.refresh_grid()
        self.customEmojiGrid.refresh_grid()

    def send_defined_emoji(self):
        #print "send defined emoji"
        self.sendEmojiName = self.definedEmojiGrid.clickedEmoji["name"]
        self.sendEmojiType = "defined"
        self.sendEmojiSize = self.definedEmojiGrid.clickedEmoji["size"]
        self.sendemoji.emit()

    def send_custom_emoji(self):
        #print "send custom emoji"
        self.sendEmojiName = self.customEmojiGrid.clickedEmoji["name"]
        self.sendEmojiType = "custom"
        self.sendEmojiSize = self.customEmojiGrid.clickedEmoji["size"]
        self.sendemoji.emit()





class DefinedEmojiGrid(QWidget):
    emojiclicked = Signal()

    def __init__(self):
        super(DefinedEmojiGrid, self).__init__()

        self.column = 10
        self.emojiList = []
        self.masterLayout = QGridLayout()
        self.refresh_grid()
        self.setLayout(self.masterLayout)
        self.clickedEmoji = {}
        self.clickedEmoji["name"] = ""
        self.clickedEmoji["size"] = 0

        self.setFixedWidth(320)

    def load_emoji(self):
        for i in os.listdir("%s/emoji" % Icons_Folder):
            if len(i.split(".")) > 1 and i.split(".")[-1] in Emoji_Format:
                if not i in self.emojiList:
                    self.emojiList.append(i)
        self.emojiList.sort()

    def refresh_grid(self):
        self.clearLayout(self.masterLayout)
        self.load_emoji()
        for name in self.emojiList:
            index = self.emojiList.index(name)
            row = index / self.column
            column = index % self.column
            label = QEmojiButton(name, type="defined")
            self.masterLayout.addWidget(label, row, column)
            label.buttonClicked[QObject].connect(self.emoji_clicked)
        self.masterLayout.setAlignment(Qt.AlignTop)

    def clearLayout(self, layout):
        if layout != None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()
                elif child.layout() is not None:
                    self.clearLayout(child.layout())

    def emoji_clicked(self, label):
        self.clickedEmoji["name"] = label.name
        self.clickedEmoji["size"] = label.mouse
        self.emojiclicked.emit()


class CustomEmojiGrid(QWidget):
    emojiclicked = Signal()

    def __init__(self):
        super(CustomEmojiGrid, self).__init__()

        self.column = 5
        self.emojiList = []
        self.masterLayout = QGridLayout()
        self.refresh_grid()
        self.setLayout(self.masterLayout)
        self.clickedEmoji = {}
        self.clickedEmoji["name"] = ""
        self.clickedEmoji["size"] = 0

        self.setFixedWidth(320)


    def load_emoji(self):
        for i in os.listdir("%s/emoji" % Current_User_Folder):
            if len(i.split(".")) > 1 and i.split(".")[-1] in Emoji_Format:
                if not i in self.emojiList:
                    self.emojiList.append(i)
        self.emojiList.sort()

    def refresh_grid(self):
        self.clearLayout(self.masterLayout)
        self.emojiList = []
        self.load_emoji()
        #print self.emojiList
        for name in self.emojiList:
            index = self.emojiList.index(name)
            row = index / self.column
            column = index % self.column
            label = QEmojiButton(name, type="custom")
            self.masterLayout.addWidget(label, row, column)
            label.buttonClicked[QObject].connect(self.emoji_clicked)
        addLabel = QLabelButton("add")
        addLabel.buttonClicked.connect(self.add_new_emoji)
        self.masterLayout.addWidget(addLabel, len(self.emojiList)/self.column, len(self.emojiList)%self.column)
        #print len(self.emojiList)
        if len(self.emojiList) < 4:
            for i in range(4 - len(self.emojiList)):
                row = 0
                column = (4-i)
                label = QEmojiButton("", type="custom")
                #print row, column
                self.masterLayout.addWidget(label, row, column)
        self.masterLayout.setAlignment(Qt.AlignCenter)

    def clearLayout(self, layout):
        if layout != None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()
                elif child.layout() is not None:
                    self.clearLayout(child.layout(buttonClicked()))

    def emoji_clicked(self, label):
        self.clickedEmoji["name"] = label.name
        self.clickedEmoji["size"] = label.mouse
        self.emojiclicked.emit()

    def add_new_emoji(self):
        print "add_new_emoji"
        imgFormat = "*.jpg *.png *.gif"
        homePath = os.path.expanduser('~').replace('\\', '/')
        fileName = QFileDialog.getOpenFileName(self, "open", homePath, "Image Files (%s)" % imgFormat)[0]
        print fileName
        if fileName[0] != "":
            self.save_custom_emoji(fileName[0])


    def save_custom_emoji(self, filePath):
        emojiId = int(time.time())
        emojiName = "emoji_%s" % emojiId
        emojiExt = os.path.splitext(filePath)[1]
        newPath = "%s/emoji/%s%s" % (Current_User_Folder, emojiName, emojiExt)
        #print newPath
        shutil.copyfile(filePath, newPath)
        self.refresh_grid()




class QEmojiButton(QLabel, QObject):
    buttonClicked = Signal(QObject)

    def __init__(self, name, type):
        super(QEmojiButton, self).__init__()

        self.name = name
        self.type = type
        self.path = ""

        self.timer = QTimer()
        self.timer.timeout.connect(self.timeout)

        if self.type == "defined":
            self.path = '%s/emoji/%s' % (Icons_Folder, self.name)
            if self.name.split(".")[-1] != "gif":
                self.imageFile = self.path
                self.setPixmap(QPixmap(self.imageFile).scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                self.setStyleSheet("background-color: rgb(40, 40, 40, 0)")
            else:
                self.emojiMovie = QMovie(self.path)
                self.emojiMovie.setScaledSize(QSize(24, 24))
                self.setMovie(self.emojiMovie)
                self.emojiMovie.start()
                self.emojiMovie.stop()
        if self.type == "custom":
            self.path = '%s/emoji/%s' % (Current_User_Folder, self.name)
            if self.name != "":
                if self.name.split(".")[-1] != "gif":
                    self.imageFile = self.path
                    self.setPixmap(QPixmap(self.imageFile).scaled(52, 52, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    self.setStyleSheet("background-color: rgb(40, 40, 40, 0)")
                else:
                    pixmap = QPixmap(self.path)
                    newHeight = 52
                    try:
                        wh = float(pixmap.width())/pixmap.height()
                        #print wh
                        newHeight = int(52/wh)
                    except:
                        print "error emoji", self.path
                    #print newHeight
                    self.emojiMovie = QMovie(self.path)
                    self.emojiMovie.setScaledSize(QSize(52, newHeight))
                    self.setMovie(self.emojiMovie)
                    self.emojiMovie.start()
                    self.emojiMovie.stop()
            else:
                self.setFixedSize(52, 52)

        self.setAlignment(Qt.AlignCenter)

        self.mouse = 0 # 0:left, 1:right, 2:double

        self.mousePos = [0, 0]
        self.setMouseTracking(True)

        self.hoverTimer = QTimer()
        self.hoverTimer.timeout.connect(self.show_emoji_preview)
        self.emojiPreviewWidget = None

    def timeout(self):
        self.timer.stop()
        self.buttonClicked.emit(self)


    def mouseDoubleClickEvent(self, event):
        # print "mouseDoubleClickEvent"
        self.timer.stop()
        self.mouse = 2
        self.buttonClicked.emit(self)

    def enterEvent(self, event):
        self.setStyleSheet("background-color: rgb(70, 70, 70)")
        self.hoverTimer.start(500)


    def leaveEvent(self, event):
        self.setStyleSheet("background-color: rgb(40, 40, 40, 0)")
        self.hoverTimer.stop()
        if self.emojiPreviewWidget != None:
            self.emojiPreviewWidget.close()
            self.emojiPreviewWidget.deleteLater()
            self.emojiPreviewWidget = None

    def mousePressEvent(self, event):
        self.setStyleSheet("background-color: rgb(40, 40, 40)")
        if event.buttons() == Qt.LeftButton:
            self.mouse = 0
        if event.buttons() == Qt.RightButton:
            self.mouse = 1
        self.timer.start(200)
        self.hoverTimer.stop()
        if self.emojiPreviewWidget != None:
            self.emojiPreviewWidget.close()
            self.emojiPreviewWidget.deleteLater()
            self.emojiPreviewWidget = None


    def mouseReleaseEvent(self, event):
        #self.emit(SIGNAL('buttonClicked(QObject)'), self)
        self.setStyleSheet("background-color: rgb(70, 70, 70)")

    def mouseMoveEvent(self, event):
        #print "mouseMoveEvent"
        self.mousePos[0] = event.globalPos().x()
        self.mousePos[1] = event.globalPos().y()


    def show_emoji_preview(self):
        #print "show_emoji_preview"
        #print self.mousePos
        if self.emojiPreviewWidget == None:
            self.emojiPreviewWidget = EmojiBigView(self.path)
            self.emojiPreviewWidget.move(self.mousePos[0]-self.emojiPreviewWidget.width()/2, self.mousePos[1]+20)
            self.emojiPreviewWidget.show()



class EmojiBigView(QLabel):
    def __init__(self, path):
        super(EmojiBigView, self).__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        #print path
        self.emojiMovie = None

        if path != "":
            if path.split(".")[-1] != "gif":
                self.imageFile = path
                self.setPixmap(QPixmap(self.imageFile))
            else:
                self.emojiMovie = QMovie(path)
                self.setMovie(self.emojiMovie)
                self.emojiMovie.start()
                #self.movie.stop()
        self.adjustSize()

    def closeEvent(self, event):
        #print "close"
        if self.emojiMovie != None:
            self.emojiMovie.stop()
            self.emojiMovie = None








class QLabelButton(QLabel):
    buttonClicked = Signal()

    def __init__(self, name):
        super(QLabelButton, self).__init__()

        self.setToolTip("<font color=#FFFFFF>%s</font>" % name)
        self.imageFile = '%s/%s.png' % (Icons_Folder, name)
        self.setPixmap(QPixmap(self.imageFile).scaled(52, 52, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.setStyleSheet("background-color: rgb(40, 40, 40, 0)")

        self.mousePos = [0, 0]

    def enterEvent(self, event):
        self.setStyleSheet("background-color: rgb(70, 70, 70)")

    def leaveEvent(self, event):
        self.setStyleSheet("background-color: rgb(40, 40, 40, 0)")

    def mousePressEvent(self, event):
        self.setStyleSheet("background-color: rgb(40, 40, 40)")
        self.mousePos[0] = event.globalPos().x()
        self.mousePos[1] = event.globalPos().y()

    def mouseReleaseEvent(self, event):
        self.buttonClicked.emit()
        self.setStyleSheet("background-color: rgb(70, 70, 70)")














if __name__ == '__main__':
    App = QApplication(sys.argv)
    MainApp = MainWidget()
    MainApp.show()
    sys.exit(App.exec_())
