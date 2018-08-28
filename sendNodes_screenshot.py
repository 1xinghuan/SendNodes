# -*- coding: utf-8 -*-
# __author__ = 'XingHuan-PC'
# 2016/12/16




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

import os
import sys
import time
import sendNodes_path as SP
import sendNodes_helper as SH


Global_Folder = SP.GLOBAL_Folder
Icons_Folder = "%s/icons" % Global_Folder

Users_Folder = SP.USERS_Folder
Current_User = SH.Current_User
Current_User_Folder = "%s/%s" % (Users_Folder, Current_User)
Temp_Folder = "%s/tmp" % Current_User_Folder


class MainWidget(QWidget):
    screenshotcancel = Signal()
    copytempscreenshot = Signal()

    def __init__(self):
        super(MainWidget, self).__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowState(Qt.WindowMaximized)

        self.origin = None
        self.destination = None
        self.x = self.width()/2
        self.y = self.height()/2
        self.r = 0
        self.t = 0
        self.finalX = 0
        self.finalY = 0
        self.finalR = 0
        self.finalT = 0
        self.setMouseTracking(True)
        self.status = "0"  # 0:NoButton; 1:LeftButton; 2:saveWidget; 3:paint

        self.paintOrigin = None
        self.paintDestination = None
        self.paintLines = []
        self.paintColor = QColor(255, 255, 255, 255)

        self.screenshotUrl = ""

        #self.resize(800, 800)

    def paintEvent(self, QPaintEvent):
        super(MainWidget, self).paintEvent(QPaintEvent)

        painter = QPainter(self)
        brush = QBrush(QColor(100, 100, 100, 1))
        painter.setBrush(brush)
        painter.drawRect(0, 0, self.width(), self.height())

        self.draw_border(painter)
        self.draw_tooltip(painter)
        self.draw_final_border(painter)
        self.draw_paint(painter)


    def draw_border(self, painter):
        pen = QPen(QColor(100, 150, 255))

        if self.status == "0":
            pen.setWidth(5)
            painter.setPen(pen)
            painter.drawRect(0, 0, self.width(), self.height())
        elif self.status == "1":
            inBrush = QBrush(QColor(100, 100, 100, 0))
            outBrush = QBrush(QColor(20, 20, 20, 100))
            inPen = QPen(QColor(100, 150, 255))
            inPen.setWidth(1)
            outPen = QPen(QColor(100, 150, 255, 0))
            painter.setBrush(inBrush)
            painter.setPen(inPen)
            painter.drawRect(self.x-1, self.y-1, self.r - self.x+1, self.t - self.y+1)
            painter.setBrush(outBrush)
            painter.setPen(outPen)
            self.draw_inRect(painter, self.x, self.y, self.r, self.t)


    def draw_inRect(self, painter, x, y, r, t):
        if r >= x and t >= y:  # right-down
            painter.drawRect(0, 0, x, self.height())
            painter.drawRect(r, 0, self.width() - r, self.height())
            painter.drawRect(x, 0, r - x, y)
            painter.drawRect(x, t, r - x, self.height() - t)
        elif r >= x and t < y:  # right-up
            painter.drawRect(0, 0, x, self.height())
            painter.drawRect(r, 0, self.width() - r, self.height())
            painter.drawRect(x, 0, r - x, t)
            painter.drawRect(x, y, r - x, self.height() - y)
        elif r <= x and t >= y:  # left-down
            painter.drawRect(0, 0, r, self.height())
            painter.drawRect(x, 0, self.width() - x, self.height())
            painter.drawRect(r, 0, x - r, y)
            painter.drawRect(r, t, x - r, self.height() - t)
        elif r <= x and t < y:  # left-up
            painter.drawRect(0, 0, r, self.height())
            painter.drawRect(x, 0, self.width() - x, self.height())
            painter.drawRect(r, 0, x - r, t)
            painter.drawRect(r, y, x - r, self.height() - y)

    def draw_tooltip(self, painter):
        if self.status in ["0", "1"]:
            tooltipBrush = QBrush(QColor(20, 20, 20, 200))
            tooltipPen = QPen(QColor(100, 150, 255, 0))
            tooltipPen.setWidth(0)
            painter.setBrush(tooltipBrush)
            painter.setPen(tooltipPen)
            tooltipRect = QRect(self.r, self.t, 300, 70)
            painter.drawRect(tooltipRect)
            textPen = QPen(QColor(200, 200, 200))
            text = "right click or press esc to quit"
            font = QFont("Arial", 10)
            painter.setFont(font)
            painter.setPen(textPen)
            painter.drawText(tooltipRect, Qt.AlignCenter, text)

    def draw_paint(self, painter):
        pen = QPen(self.paintColor)
        pen.setWidth(3)
        painter.setPen(pen)
        painter.setRenderHint(QPainter.Antialiasing)

        for line in self.paintLines:
            painter.drawLine(line)

        if self.paintDestination:
            line = QLine(self.paintOrigin, self.paintDestination)
            painter.drawLine(line)


    def mousePressEvent(self, event):
        #print "pressed"
        if event.buttons() == Qt.RightButton:
           self.close()
        self.origin = event.pos()
        self.x = event.pos().x()
        self.y = event.pos().y()
        #print self.x, self.y
        self.paintOrigin = event.pos()

    def mouseMoveEvent(self, event):
        #print "status: %s" % self.status
        if self.status in ["0", "1"]:
            if event.buttons() == Qt.LeftButton:
               self.status = "1"
            else:
                self.status = "0"
            self.destination = event.pos()
            self.r = event.pos().x()
            self.t = event.pos().y()
            #print self.r, self.t
        if self.status == "3":
            if event.buttons() == Qt.LeftButton:
                self.paintDestination = event.pos()
                self.paintLines.append(QLine(self.paintOrigin, self.paintDestination))
                self.paintOrigin = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        #print "released"
        #print self.r, self.t
        #print self.status

        if self.status == "0":
            self.finalX = 0
            self.finalY = 0
            self.finalR = self.width()
            self.finalT = self.height()
        elif self.status == "1":
            self.finalX = self.x
            self.finalY = self.y
            self.finalR = self.r
            self.finalT = self.t
        if self.status != "3":
            self.status = "2"
        self.show_save_widget()

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    def draw_final_border(self, painter):
        # print "draw_final_border"
        if self.status in ["2", "3"]:
            #print self.finalX, self.finalY, self.finalR, self.finalT
            inBrush = QBrush(QColor(100, 100, 100, 0))
            outBrush = QBrush(QColor(20, 20, 20, 100))
            inPen = QPen(QColor(100, 150, 255))
            inPen.setWidth(1)
            outPen = QPen(QColor(100, 150, 255, 0))
            painter.setBrush(inBrush)
            painter.setPen(inPen)
            # painter.drawRect(self.finalX-4, self.finalY-4, self.finalR - self.finalX+6, self.finalT - self.finalY+6)
            painter.drawRect(self.finalX, self.finalY, self.finalR - self.finalX, self.finalT - self.finalY)
            painter.setBrush(outBrush)
            painter.setPen(outPen)
            self.draw_inRect(painter, self.finalX, self.finalY, self.finalR, self.finalT)



    def get_pos(self, x, y, r, t, selfW, selfH):
        if r >= x and t >= y:  # right-down
            finalX = r - selfW
            if x == 0 and y == 0 and r == self.width() and t == self.height():
                finalY = 0
            elif t >= self.height() - selfH:
                finalY = t - selfH
            else:
                finalY = t
        elif r >= x and t < y:  # right-up
            finalX = r - selfW
            if t <= selfH:
                finalY = t
            else:
                finalY = t - selfH
        elif r <= x and t >= y:  # left-down
            finalX = r
            if t >= self.height() - selfH:
                finalY = t - selfH
            else:
                finalY = t
        elif r <= x and t < y:  # left-up
            finalX = r
            if t <= selfH:
                finalY = t
            else:
                finalY = t - selfH
        return [finalX, finalY]

    def show_save_widget(self):
        self.saveWidget = SaveWidget()
        pos = self.get_pos(self.finalX, self.finalY, self.finalR, self.finalT, self.saveWidget.width(), self.saveWidget.height())
        self.saveWidget.move(pos[0], pos[1]+2)
        self.saveWidget.show()
        self.saveWidget.cancelscreenshot.connect(self.cancel_screenshot)
        self.saveWidget.savescreenshot.connect(self.save_screenshot)
        self.saveWidget.copyscreenshot.connect(self.copy_screenshot)
        self.saveWidget.paintscreenshot.connect(self.paint_screenshot)
        self.saveWidget.newscreenshot.connect(self.new_screenshot)

    def cancel_screenshot(self):
        self.saveWidget.close()
        self.close()
        self.screenshotcancel.emit()

    def paint_screenshot(self):
        self.paintColor = self.saveWidget.paintColor
        self.status = "3"

    def new_screenshot(self):
        self.paintOrigin = None
        self.paintDestination = None
        self.paintLines = []
        self.update()
        self.status = "0"

    def save_screenshot(self):
        self.saveWidget.close()
        #self.close()
        self.shot_screen()
        self.close()
        shotFormat = "png"
        homePath = os.path.expanduser('~').replace('\\','/')
        fileName = QFileDialog.getSaveFileName(self, "save as", homePath, "%s Files (*.%s)" % (shotFormat.upper(), shotFormat))
        print fileName, type(fileName)
        if isinstance(fileName, tuple):
            if fileName[0] != "":
                self.screenshotPixmap.save(fileName[0], shotFormat)
        else:
            if fileName != "":
                self.screenshotPixmap.save(fileName, shotFormat)


    def copy_screenshot(self):
        self.saveWidget.close()
        # self.close()
        self.shot_screen()
        self.close()
        currentTime = int(time.time())
        tempFile = "%s/screenshot_%s.png" % (Temp_Folder, currentTime)
        if not os.path.exists(os.path.dirname(tempFile)):
            os.makedirs(os.path.dirname(tempFile))
        #print tempFile
        self.screenshotPixmap.save(tempFile, "png")
        self.screenshotUrl = tempFile
        self.copytempscreenshot.emit()

    def shot_screen(self):
        self.status = "0"
        self.update()
        # self.repaint()
        x = min(self.finalX, self.finalR)
        y = min(self.finalY, self.finalT)
        r = max(self.finalX, self.finalR)
        t = max(self.finalY, self.finalT)
        self.screenshotPixmap = QPixmap.grabWindow(QApplication.desktop().winId(), x+1, y+1, r-x-1, t-y-1)


class SaveWidget(QWidget):
    newscreenshot = Signal()
    paintscreenshot = Signal()
    savescreenshot = Signal()
    cancelscreenshot = Signal()
    copyscreenshot = Signal()

    def __init__(self):
        super(SaveWidget, self).__init__()

        self.setStyleSheet("background-color: rgb(25, 25, 25)")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        #self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.masterLayout = QHBoxLayout()

        self.newButton = QLabelButton("screenshot_new")
        self.newButton.setToolTip("new")
        self.paintButton = QLabelButton("screenshot_paint")
        self.paintButton.setToolTip("paint")
        self.saveButton = QLabelButton("screenshot_save")
        self.saveButton.setToolTip("save")
        self.cancelButton = QLabelButton("screenshot_cancel")
        self.cancelButton.setToolTip("cancel")
        self.copyButton = QLabelButton("screenshot_copy")
        self.copyButton.setToolTip("ok")
        self.newButton.buttonClicked.connect(self.new_screenshot)
        self.paintButton.buttonClicked.connect(self.paint_screenshot)
        self.paintButton.buttonDoubleClicked.connect(self.select_color)
        self.saveButton.buttonClicked.connect(self.save_screenshot)
        self.cancelButton.buttonClicked.connect(self.cancel_screenshot)
        self.copyButton.buttonClicked.connect(self.copy_screenshot)

        self.masterLayout.setAlignment(Qt.AlignRight)
        #self.masterLayout.addSpacing(10)
        self.masterLayout.addWidget(self.newButton)
        self.masterLayout.addSpacing(10)
        self.masterLayout.addWidget(self.paintButton)
        self.masterLayout.addSpacing(10)
        self.masterLayout.addWidget(self.saveButton)
        self.masterLayout.addSpacing(10)
        self.masterLayout.addWidget(self.cancelButton)
        self.masterLayout.addSpacing(10)
        self.masterLayout.addWidget(self.copyButton)

        self.paintColor = QColor.fromRgbF(1.0, 1.0, 1.0, 1.0)


        self.setLayout(self.masterLayout)

        self.adjustSize()

    def new_screenshot(self):
        self.newscreenshot.emit()
        self.close()

    def select_color(self):
        self.colorDialog = QColorDialog()
        self.colorDialog.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.colorDialog.show()
        self.colorDialog.colorSelected.connect(self.color_selected)
        # self.close()

    def color_selected(self):
        self.paintColor = self.colorDialog.selectedColor()
        #print self.paintColor
        self.paint_screenshot()

    def paint_screenshot(self):
        self.paintscreenshot.emit()

    def save_screenshot(self):
        #print "save_screenshot"
        self.savescreenshot.emit()
        self.close()

    def cancel_screenshot(self):
        #print "cancel_screenshot"
        self.cancelscreenshot.emit()
        self.close()

    def copy_screenshot(self):
        #print "copy_screenshot"
        self.copyscreenshot.emit()
        self.close()


class QLabelButton(QLabel):
    buttonClicked = Signal()
    buttonDoubleClicked = Signal()

    def __init__(self, name):
        super(QLabelButton, self).__init__()

        self.setToolTip("<font color=#FFFFFF>%s</font>" % name)
        self.imageFile = '%s/%s.png' % (Icons_Folder, name)
        self.setPixmap(QPixmap(self.imageFile).scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.setStyleSheet("background-color: rgb(40, 40, 40, 0)")

    def enterEvent(self, event):
        self.setStyleSheet("background-color: rgb(70, 70, 70)")

    def leaveEvent(self, event):
        self.setStyleSheet("background-color: rgb(40, 40, 40, 0)")

    def mousePressEvent(self, event):
        self.setStyleSheet("background-color: rgb(40, 40, 40)")

    def mouseReleaseEvent(self, event):
        self.buttonClicked.emit()
        self.setStyleSheet("background-color: rgb(70, 70, 70)")

    def mouseDoubleClickEvent(self, *args, **kwargs):
        self.buttonDoubleClicked.emit()









if __name__ == '__main__':
    App = QApplication(sys.argv)
    MainApp = MainWidget()
    #MainApp = SaveWidget()
    #MainApp = DrawWidget(0, 0, 800, 800)
    MainApp.show()
    sys.exit(App.exec_())
