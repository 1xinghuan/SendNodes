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
import sendNodes_nuke as SN
import sendNodes_screenshot as SSHOT
import sendNodes_emoji as SE

reload(sys)
sys.setdefaultencoding('utf-8')

inNuke = SP.inNuke

Users_Folder = SP.USERS_Folder.replace("\\", "/")
Global_Folder = SP.GLOBAL_Folder.replace("\\", "/")

Icons_Folder = "%s/icons" % Global_Folder
Current_User = SH.Current_User
Current_User_Folder = SH.Current_User_Folder

VER = "v1.5.0202"
AUTHOR = "XingHuan"
DATE = "2018/02/02"


MessageTableColor = "rgb(50, 50, 50)"
ReciveMessagecolor = QColor(60, 60, 60)
SendMessagecolor = QColor(40, 90, 120)

MessageEditFontSize = 15
MessageFontSize = 15
TipFontSize = 5


def use_logging1(func):
    def wrapper(self, *args, **kwargs):
        if self.logActiveCheck.isChecked():
            print func.__name__
        u = func(self, *args, **kwargs)
        return u
    return wrapper


class SendNodes(QTabWidget):
    def __init__(self):
        super(SendNodes, self).__init__()
        self.userFolder = "%s/%s" % (Users_Folder, Current_User)
        # self.setWindowTitle("Nuke Chat (current user:%s)(current nk:%s)" % (Current_User, Current_NK))
        # self.setFixedSize(883, 656)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        if not inNuke:
            self.setStyleSheet("background-color: rgb(50, 50, 50)")
        self.create_dir()

        self.searchLabel = QLabel("Search")
        self.searchLineEdit = QLineEdit()
        self.searchLineEdit.textChanged.connect(self.search_user)
        self.searchLineEdit.setStyleSheet("border:none;"
                                          "color:rgb(220, 220, 220);"
                                          "padding: 2px 2px 2px 20px;"
                                          "background-image: url(%s/search.png);"
                                          "background-position: left;"
                                          "background-repeat: no-repeat" % Icons_Folder)
        self.searchLayout = QHBoxLayout()
        self.searchLayout.addWidget(self.searchLineEdit)

        self.buttonLayout = QHBoxLayout()
        self.showTipCheck = QCheckBox("Show Tip")
        self.showTipCheck.setToolTip("Show Tip")
        self.showTipCheck.setChecked(True)
        self.groupLabelButton = QLabelButton("group")
        self.groupLabelButton.buttonClicked.connect(self.show_group_widget)
        self.refreshLabelButton = QLabelButton("refresh")
        self.refreshLabelButton.buttonClicked.connect(self.manual_refresh)
        self.clearButton = QPushButton("Clear")
        self.clearButton.setToolTip("Clear History")
        self.clearButton.setFixedWidth(80)
        self.clearButton.clicked.connect(self.clear_history)
        self.buttonLayout.setAlignment(Qt.AlignLeft)
        self.buttonLayout.addWidget(self.showTipCheck)
        self.buttonLayout.addStretch()
        self.buttonLayout.addWidget(self.groupLabelButton)
        self.buttonLayout.addStretch()
        self.buttonLayout.addWidget(self.refreshLabelButton)
        self.buttonLayout.addStretch()
        self.buttonLayout.addWidget(self.clearButton)

        self.historyTable = HistorysTableWidget()
        self.historyTable.chooseOneUser.connect(self.choose_one_user)
        self.historyTable.deleteOneHistory.connect(self.delete_selected_history)

        self.usersTable = UsersTreeWidget()
        self.usersTable.chooseOneUser.connect(self.choose_one_user)

        self.chosenUser = ""
        self.chosenType = "user"

        self.userTabWidget = UsersTabWidget()
        self.userTabWidget.addTab(self.historyTable, '')
        self.userTabWidget.addTab(self.usersTable, "")

        self.leftLayout = QVBoxLayout()
        self.leftLayout1 = QVBoxLayout()
        self.leftLayout1.addLayout(self.searchLayout)
        self.leftLayout1.addLayout(self.buttonLayout)
        self.leftLayout2 = QHBoxLayout()
        self.userIconLabel = QLabel()
        self.userIconLabel.setPixmap(QPixmap("%s/userDefault.png" % Icons_Folder).scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        # self.leftLayout2.addSpacing(60)
        # self.leftLayout2.addWidget(self.userIconLabel)
        self.leftLayout2.addLayout(self.leftLayout1)
        self.leftLayout.setAlignment(Qt.AlignTop)
        self.leftLayout.addLayout(self.leftLayout2)
        self.leftLayout.addWidget(self.userTabWidget)
        # self.leftLayout.addWidget(self.historyTable)

        self.messageScrollArea = QScrollArea()
        self.messageTable = MessageTableWidget2()
        self.messageScrollArea.setWidget(self.messageTable)
        self.messageScrollArea.setWidgetResizable(True)
        # self.messageScrollArea.setFixedSize(600, 450)
        self.messageScrollArea.setMinimumSize(600, 450)
        self.messageScrollArea.setStyleSheet("QScrollArea{border:none}")

        self.messageEditLayout = QVBoxLayout()
        self.messageTextEdit = QTextEdit()
        self.messageTextEdit.setStyleSheet("QTextEdit {border:none; color:rgb(200, 200, 200); font-size:%spx}" % MessageEditFontSize)
        self.messageTextEdit.setWordWrapMode(QTextOption.WrapAnywhere)
        # self.messageTextEdit.setWordWrapMode(QTextOption.ManualWrap)
        self.messageEditLayout1 = QHBoxLayout()
        self.emojiButton = QLabelButton("emoji")
        self.emojiWidget = SE.MainWidget()
        self.emojiWidget.sendemoji.connect(self.send_emoji)
        self.screenshotMainButton = QLabelButton("screenshot")
        self.screenshotHideButton = QLabelButton("screenshot_hide")
        self.emojiButton.buttonClicked.connect(self.show_emoji_widget)
        self.screenshotMainButton.buttonClicked.connect(self.make_screenshot)
        self.screenshotHideButton.buttonClicked.connect(self.show_screenshot_hide_widget)
        self.screenshotHideBool = True
        self.screenshotHideWidget = ScreenshotHideWidget()
        self.screenshotHideWidget.setChecked(self.screenshotHideBool)
        self.messageEditLayout1.setSpacing(0)
        self.messageEditLayout1.addWidget(self.emojiButton)
        self.messageEditLayout1.addSpacing(10)
        self.messageEditLayout1.addWidget(self.screenshotMainButton)
        self.messageEditLayout1.addWidget(self.screenshotHideButton)
        self.messageEditLayout1.addStretch()
        self.messageEditLayout.addLayout(self.messageEditLayout1)
        self.messageEditLayout.addWidget(self.messageTextEdit)

        self.sendLayout = QHBoxLayout()
        self.sendButton = QPushButton("Send(Ctrl+Enter)")
        self.sendButton.setStyleSheet("color:rgb(180, 180, 180); background-color:rgb(39, 92, 132)")
        self.sendButton.clicked.connect(self.send)
        self.sendButton.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_Return))
        self.aboutButton = QLabelButton("about")
        self.aboutButton.buttonClicked.connect(self.show_about)
        self.settingButton = QLabelButton("setting")
        self.settingButton.buttonClicked.connect(self.show_setting)

        self.logActiveCheck = QCheckBox("log")
        self.logActiveCheck.setChecked(False)

        self.sendLayout.addStretch()
        if Current_User in ["john", "xinghuan"]:
            self.sendLayout.addWidget(self.logActiveCheck)
        self.sendLayout.addSpacing(5)
        self.sendLayout.addWidget(self.settingButton)
        self.sendLayout.addSpacing(5)
        self.sendLayout.addWidget(self.aboutButton)
        self.sendLayout.addSpacing(5)
        self.sendLayout.addWidget(self.sendButton)
        self.rightLayout = QVBoxLayout()
        self.rightLayout.addWidget(self.messageScrollArea)
        self.rightLayout.addStretch()
        self.rightLayout.addLayout(self.messageEditLayout)
        self.rightLayout.addLayout(self.sendLayout)
        self.rightLayout.setStretchFactor(self.messageScrollArea, 4)
        self.rightLayout.setStretchFactor(self.messageEditLayout, 1)
        self.rightLayout.setStretchFactor(self.sendLayout, 1)

        self.masterLayout = QHBoxLayout()
        self.masterLayout.setAlignment(Qt.AlignLeft)
        self.masterLayout.addLayout(self.leftLayout)
        # self.masterLayout.addStretch()
        self.masterLayout.addLayout(self.rightLayout)
        # self.masterLayout.addStretch()
        self.masterLayout.setStretchFactor(self.leftLayout, 1)
        self.masterLayout.setStretchFactor(self.rightLayout, 4)
        self.setLayout(self.masterLayout)

        self.lastUsersInfoWithMessage = []
        self.newUsersInfo = None
        self.tipWidget = TipWidget()
        self.tipWidget.noTip.connect(self.set_no_tip)
        self.tipWidget.openMain.connect(self.open_main_widget)
        self.refreshThread = QRefreshThread()
        self.refreshThread.start()
        self.refreshThread.refreshNow.connect(self.auto_refresh)
        self.refreshThread.refreshNow.connect(self.show_tip_widget)
        self.refreshThread.readed.connect(self.to_readed)

        screenRes = QDesktopWidget().screenGeometry()
        self.move(QPoint(screenRes.width()/2,screenRes.height()/2)-QPoint((self.width()/2),(self.height()/2)))
        self.load_pref()
        self.nkName = SN.get_nk_name()

        self.clearHistoryThread = ClearHistoryThread()
        self.clearHistoryThread.clearDone.connect(self.after_clear)
        self.delOneHistoryThread = DelOneHistoryThread()
        self.delOneHistoryThread.clearDone.connect(self.after_del)

        self.groupEditWidget = GroupEditWidget()
        self.groupEditWidget.addGroup.connect(self.build_user_list)
        self.groupEditWidget.leaveGroup.connect(self.build_user_list)
        self.groupEditWidget.delGroup.connect(self.build_user_list)
        self.groupEditWidget.addUserToGroup.connect(self.build_user_list)
        self.groupEditWidget.removeUsersFromGroup.connect(self.build_user_list)

        # self.setMouseTracking(True)

    def create_dir(self):
        dirs = [self.userFolder, "%s/Icon" % self.userFolder, "%s/Pref" % self.userFolder, "%s/History/Groups" % self.userFolder, "%s/tmp" % self.userFolder, "%s/emoji" % self.userFolder]
        for dir in dirs:
            if not os.path.exists(dir):
                try:
                    os.makedirs(dir)
                    os.chmod(dir, 0777)
                except:
                    print "error create_dir"
        if not os.path.exists("%s/Pref/pref.json" % self.userFolder):
            SH.create_default_pref()
        if not os.path.exists("%s/Pref/groups.json" % self.userFolder):
            SH.create_default_groups_pref()

    def load_pref(self):
        prefData = SH.load_pref()
        if "showTipDefault" not in prefData.keys():
            prefData["showTipDefault"] = True
        if "hideWindowWhenShotScreen" not in prefData.keys():
            prefData["hideWindowWhenShotScreen"] = True
        SH.change_pref(prefData)
        self.showTipCheck.setChecked(prefData["showTipDefault"])
        self.screenshotHideWidget.setChecked(prefData["hideWindowWhenShotScreen"])
        self.update()

    @use_logging1
    def auto_refresh(self, *args, **kwargs):
        # print "auto refresh"
        lastChosenUser = self.chosenUser
        self.newUsersInfo = SH.get_users_and_groups("","withMessage")
        self.build_user_list()
        # self.historyTable.clear_selection()
        if lastChosenUser != "":
            newIndex = 0
            if lastChosenUser in self.historyTable.userRow:
                newIndex = self.historyTable.userRow[lastChosenUser]
            self.historyTable.selectRow(newIndex)
            # self.historyTable.setItemSelected(self.historyTable.item(0, 0), True)
            # print newIndex
        # self.refresh_message()

    def show_tip_widget(self):
        newInfo = SH.get_users_and_groups("","withMessage")
        if not self.isActiveWindow():
            if self.showTipCheck.isChecked():
                if len(newInfo) > 0:
                    if newInfo[0][1]["readed"] == False:
                        self.tipWidget.updateInfo(self.nkName, newInfo[0][1]["user_label"], newInfo[0][1]["time"])
                        self.tipWidget.show()
                    else:
                        self.tipWidget.close()

    @use_logging1
    def to_readed(self):
        if not self.tipWidget.isHidden():
            self.tipWidget.close()
            self.historyTable.cellWidget(0, 0).toReaded()

    @use_logging1
    def choose_one_user(self):
        if self.userTabWidget.currentIndex() == 0:
            self.chosenUser = self.historyTable.chosenUser
            self.chosenType = self.historyTable.chosenType
            self.usersTable.clear_selection()
        elif self.userTabWidget.currentIndex() == 1:
            self.chosenUser = self.usersTable.chosenUser
            self.chosenType = self.usersTable.chosenType
            self.historyTable.clear_selection()
        # print self.chosenUser
        self.refresh_message()
        self.close_tip_widget()

    def close_tip_widget(self):
        if self.historyTable.chosenUser == self.tipWidget.fromWhom:
            # print "close tip"
            self.tipWidget.close()
            self.tipWidget.fromWhom = ""

    def set_no_tip(self):
        self.showTipCheck.setChecked(False)

    def update_nk_name(self):
        self.nkName = SN.get_nk_name()

    @use_logging1
    def open_main_widget(self):
        self.setWindowTitle("Nuke Chat (current user:%s)(current nk:%s)" % (Current_User, self.nkName))
        if self.isMinimized():
            self.setShown(False)
        self.refresh_user_list()
        self.historyTable.clear_selection()
        self.chosenUser = ""
        self.refresh_message()
        self.showNormal()

    @use_logging1
    def build_user_list(self, *args, **kwargs):
        # print "build user"
        self.historyTable.build_user_list("")
        self.usersTable.build_user_tree()
        self.newUsersInfo = self.historyTable.allUserWithMessage
        self.refresh_user_list()

    @use_logging1
    def refresh_user_list(self, *args, **kwargs):
        allHidden = self.historyTable.refresh_users_list(self.searchLineEdit.text())
        if allHidden:
            self.userTabWidget.setCurrentIndex(1)
        self.usersTable.refresh_user_list(self.searchLineEdit.text())

    def manual_refresh(self):
        self.build_user_list()
        # self.refresh_user_list()
        self.clear_message()
        self.chosenUser = ""

    @use_logging1
    def search_user(self, *args, **kwargs):
        self.refresh_user_list()
        self.historyTable.clear_selection()
        self.usersTable.clear_selection()
        self.clear_message()

    @use_logging1
    def clear_history(self, *args, **kwargs):
        self.clear_message()
        self.historyTable.clear_all()
        self.userTabWidget.setCurrentIndex(1)
        self.refreshThread.stop()
        self.clearHistoryThread.start()


    def after_clear(self):
        self.create_dir()
        self.refreshThread.runAgain()
        self.build_user_list()
        # self.refresh_user_list()
        # self.historyTable.clear_selection()
        self.chosenUser = ""

    @use_logging1
    def delete_selected_history(self, *args, **kwargs):
        self.clear_message()
        # print self.chosenType, self.chosenUser
        self.delOneHistoryThread.set_user(self.chosenType, self.chosenUser)
        self.historyTable.remove_selected()
        self.chosenUser = ""
        self.clear_message()
        self.refreshThread.stop()
        self.delOneHistoryThread.start()

    def after_del(self):
        self.refreshThread.runAgain()
        self.manual_refresh()
        # print self.chosenUser
        # self.chosenUser = ""

    def clear_message(self):
        widget = self.messageScrollArea.widget()
        if widget:
            try:
                widget.clearAll()
            except:
                pass
            widget.deleteLater()
        self.messageScrollArea.setWidget(LogoWidget())

    @use_logging1
    def refresh_message(self, *args, **kwargs):
        # print self.chosenUser
        self.clear_message()
        if self.chosenUser != "":
            self.messageTable = MessageTableWidget2()
            self.messageTable.refreshMessages(self.chosenUser, self.chosenType)
            self.messageScrollArea.setWidget(self.messageTable)
            verticalScrollBar = self.messageScrollArea.verticalScrollBar()
            verticalScrollBar.setStyleSheet("QScrollBar {width:5px;}")
            verticalScrollBar.setSliderPosition(verticalScrollBar.maximum())

    def get_scroll(self):
        messageScrollBar = self.messageScrollArea.verticalScrollBar()
        print messageScrollBar.maximum()

    def show_about(self):
        self.aboutWidget = AboutWidget()
        self.aboutWidget.show()

    def show_setting(self):
        self.prefWidget = PrefWidget()
        self.prefWidget.loadPref()
        self.prefWidget.show()

    def refresh_after_send(self):
        self.refreshThread.stop()
        self.messageTextEdit.clear()
        if self.userTabWidget.currentIndex() == 0:
            self.historyTable.move_to_top(self.historyTable.selectedIndexes()[0].row(), self.searchLineEdit.text())
        elif self.userTabWidget.currentIndex() == 1:
            self.userTabWidget.setCurrentIndex(0)
            self.historyTable.check_user_exist(self.chosenUser, self.searchLineEdit.text())
            # self.historyTable.selectRow(0)
        self.refreshThread.runAgain()

    @use_logging1
    def send(self, *args, **kwargs):
        # print self.messageTextEdit.toHtml()
        # print self.messageTextEdit.toPlainText()
        failed = False
        user = self.chosenUser
        if user != "":
            if self.chosenType == "user":
                users = SH.get_all_user("", type="onlyUsers")
                if user not in users:
                    print "user not exist"
                    failed = True
                else:
                    SH.send_user_message(user, str(self.messageTextEdit.toHtml()))
            elif self.chosenType == "group":
                users = SH.get_users_in_group(user)
                if Current_User not in users:
                    print "not in group"
                    failed = True
                else:
                    SH.send_group_message(user, str(self.messageTextEdit.toHtml()))
            if not failed:
                self.refresh_after_send()

    def show_group_widget(self):
        self.groupEditWidget.show()

    @use_logging1
    def make_screenshot(self, *args, **kwargs):
        self.screenshotHideBool = self.screenshotHideWidget.isChecked()
        if self.screenshotHideBool:
            self.showMinimized()
        self.screenshotWidget = SSHOT.MainWidget()
        self.screenshotWidget.move(0, 0)
        self.screenshotWidget.show()
        self.screenshotWidget.copytempscreenshot.connect(self.add_screenshot_to_text_edit)
        self.screenshotWidget.screenshotcancel.connect(self.show_normal)

    def show_screenshot_hide_widget(self):
        if self.screenshotHideWidget.isHidden():
            mousePos = self.screenshotHideButton.mousePos
            self.screenshotHideWidget.move(mousePos[0], mousePos[1]+10)
            self.screenshotHideWidget.show()
            self.screenshotHideWidget.checkclicked.connect(self.make_screenshot)
        else:
            self.screenshotHideWidget.close()

    def add_screenshot_to_text_edit(self):
        # print self.messageTextEdit.toHtml()
        screenshotUrl = self.screenshotWidget.screenshotUrl
        # print screenshotUrl
        pixmap = QPixmap(screenshotUrl)
        oldW = pixmap.width()
        oldH = pixmap.height()
        wh = float(oldW)/oldH
        newW = oldW
        newH = oldH
        if oldW > 380:
            newW = 380
            newH = newW/wh
        self.messageTextEdit.insertHtml('<img src="%s" width="%s" height="%s">' % (screenshotUrl, newW, newH))
        # print self.messageTextEdit.toHtml()
        self.show_normal()

    def show_normal(self):
        if self.isMinimized():
            self.setShown(False)
        self.showNormal()

    def show_emoji_widget(self):
        if not self.emojiWidget:
            self.emojiWidget = SE.MainWidget()
        if self.emojiWidget.isHidden():
            mousePos = self.emojiButton.mousePos
            widgetWH = [self.emojiWidget.width(), self.emojiWidget.height()]
            self.emojiWidget.move(mousePos[0] - 10, mousePos[1] - widgetWH[1] - 15)
            self.emojiWidget.show()
        else:
            self.emojiWidget.close()

    @use_logging1
    def send_emoji(self, *args, **kwargs):
        self.emojiWidget.close()
        emojiName = self.emojiWidget.sendEmojiName
        emojiType = self.emojiWidget.sendEmojiType
        emojiSize = self.emojiWidget.sendEmojiSize

        if emojiType == "defined":
            pixmap = QPixmap("%s/emoji/%s" % (Icons_Folder, emojiName))
            oriWidth = pixmap.size().width()
            oriHeight = pixmap.size().height()
            if emojiSize == 0:
                newWidth = oriWidth/5
                newHeight = oriHeight / 5
                if newWidth < 30:
                    newWidth = oriWidth/3
                    newHeight = oriHeight/3
            elif emojiSize == 1:
                newWidth = oriWidth / 2
                newHeight = oriHeight / 2
            elif emojiSize == 2:
                newWidth = oriWidth / 1
                newHeight = oriHeight / 1
            message = '<img src="%s/emoji/%s" width="%s" height="%s">' % (Icons_Folder, emojiName, newWidth, newHeight)
            # print message
        if emojiType == "custom":
            pixmap = QPixmap("%s/emoji/%s" % (Current_User_Folder, emojiName))
            oriWidth = pixmap.size().width()
            oriHeight = pixmap.size().height()
            if emojiSize == 0:
                newWidth = oriWidth / 5
                newHeight = oriHeight / 5
                if newWidth < 30 or newHeight < 30:
                    newWidth = oriWidth / 3
                    newHeight = oriHeight / 3
            elif emojiSize == 1:
                newWidth = oriWidth / 1.7
                newHeight = oriHeight / 1.7
            elif emojiSize == 2:
                newWidth = oriWidth / 1
                newHeight = oriHeight / 1
            message = '<img src="%s/emoji/%s" width="%s" height="%s">' % (Current_User_Folder, emojiName, newWidth, newHeight)
            # print message

        user = self.chosenUser
        failed = False
        if user != "":
            if self.chosenType == "user":
                users = SH.get_all_user("", type="onlyUsers")
                if user not in users:
                    print "user not exist"
                    failed = True
                else:
                    SH.send_user_message(user, message)
            elif self.chosenType == "group":
                users = SH.get_users_in_group(user)
                if Current_User not in users:
                    print "not in group"
                    failed = True
                else:
                    SH.send_group_message(user, message)
            if not failed:
                self.refresh_after_send()
                self.refresh_message()

    def close_child_widget(self):
        if not self.screenshotHideWidget.isHidden():
            self.screenshotHideWidget.close()
        if self.emojiWidget != None:
            self.emojiWidget.close()

    def mousePressEvent(self, event):
        self.currentPos = self.pos()
        self.mouseOriPos = event.globalPos()

    def mouseMoveEvent(self, event):
        # print "move"
        # if event.buttons() == Qt.NoButton:
        # print "move"
        self.close_child_widget()
        if event.buttons() == Qt.MiddleButton:
            if self.isMaximized():
                self.showNormal()
                self.move(event.globalPos().x()-self.width()/2, event.globalPos().y()-self.height()/2)
                self.currentPos = self.pos()
            self.mouseDesPos = event.globalPos()
            move = self.mouseDesPos-self.mouseOriPos
            self.move(self.currentPos + move)

    def moveEvent(self, *args, **kwargs):
        # print "move"
        self.close_child_widget()

    def mouseDoubleClickEvent(self, event):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def closeEvent(self, event):
        # print "close"
        # self.historyTable.clear_selection()
        # self.refreshThread.terminate()
        if self.emojiWidget != None:
            self.emojiWidget.close()


class UsersTabWidget(QTabWidget):
    def __init__(self):
        super(UsersTabWidget, self).__init__()

        self.setTabPosition(QTabWidget.West)

        self.setStyleSheet("""
                QTabWidget::pane{
                    border-top: 0px solid #C2C7CB;
                }
                QTabBar::tab{
                    border-bottom-color: #C2C7CB;
                    border-top-left-radius: 0px;
                    border-top-right-radius: 0px;
                    min-height:35px;
                    min-width: 35px;
                    padding: 2px;
                }
                QTabBar::tab:first:selected {
                    margin-left: 0;
                    margin-right: 7;
                    border-image:url(%s/tab_history_selected.png);
                }
                QTabBar::tab:first:!selected {
                    margin-left: -2;
                    margin-right: 9;
                    border-image: url(%s/tab_history_no_selected.png);
                }
                QTabBar::tab:first:hover:!selected {
                    margin-left: -2;
                    margin-right: 9;
                    border-image: url(%s/tab_history_hover.png);
                }
                QTabBar::tab:last:selected {
                    margin-left: 0;
                    margin-right: 7;
                    border-image:url(%s/tab_users_selected.png);
                }
                QTabBar::tab:last:!selected {
                    margin-left: -2;
                    margin-right: 9;
                    border-image: url(%s/tab_users_no_selected.png);
                }
                QTabBar::tab:last:hover:!selected {
                    margin-left: -2;
                    margin-right: 9;
                    border-image: url(%s/tab_users_hover.png);
                }
                """ % tuple([Icons_Folder] * 6))


class HistorysTableWidget(QTableWidget):
    deleteOneHistory = Signal()
    chooseOneUser = Signal()

    def __init__(self):
        super(HistorysTableWidget, self).__init__()

        self.setStyleSheet("""
                            QTableWidget:item:selected{background-color:rgb(40,40,50)}
                            QTableWidget{border:none}
                            """)

        self.setMinimumWidth(210)
        self.setShowGrid(False)
        self.setColumnCount(1)
        # self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # verticalScrollBar = self.verticalScrollBar()
        # verticalScrollBar.setStyleSheet("width:5px;")
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setDefaultSectionSize(62)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.horizontalHeader().setStretchLastSection(True)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SingleSelection)

        self.chosenUser = ""
        self.chosenType = "user"
        self.userRow = {}

        self.itemSelectionChanged.connect(self.choose_user)
        self.build_user_list("")

        self.createContextMenu()

    def createContextMenu(self):
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)

        self.contextMenu = QMenu(self)
        self.deleteAction = self.contextMenu.addAction("delete history")

        self.deleteAction.triggered.connect(self.delete_history)

    def showContextMenu(self, pos):
        self.contextMenu.move(QCursor.pos())
        self.contextMenu.show()

    def delete_history(self):
        self.deleteOneHistory.emit()
        self.chosenUser = ""

    def build_user_list(self, searchStr):
        # print "build list"
        self.clear_all()
        self.itemSelectionChanged.disconnect(self.choose_user)
        self.allUserWithMessage = SH.get_users_and_groups(searchStr, "withMessage")

        self.usersNum = len(self.allUserWithMessage)
        self.setRowCount(self.usersNum)
        for i in range(self.usersNum):
            userName = self.allUserWithMessage[i][1]["user_name"]
            user = HistoryWidget(userName)
            user.updateInfo(self.allUserWithMessage[i][1]["time"], self.allUserWithMessage[i][1]["note"],
                            self.allUserWithMessage[i][1]["readed"],self.allUserWithMessage[i][1]["type"],
                            self.allUserWithMessage[i][1]["user_label"])
            self.setCellWidget(i, 0, user)
        self.refresh_user_row()
        self.itemSelectionChanged.connect(self.choose_user)


    def refresh_users_list(self, searchStr):
        allHidden = True
        for i in range(self.rowCount()):
            user = self.cellWidget(i, 0).label
            if user.find(searchStr) != -1:
                self.setRowHidden(i, False)
                allHidden = False
            else:
                self.setRowHidden(i, True)
        return allHidden

    def refresh_user_row(self):
        self.userRow = {}
        for i in range(self.rowCount()):
            userName = self.cellWidget(i, 0).name
            self.userRow.update({userName:i})


    def move_to_top(self, row, searchStr):
        # print "move ", row, " to top"
        self.allUserWithMessage = SH.get_users_and_groups("", "withMessage")
        userName = self.allUserWithMessage[0][1]["user_name"]
        user = HistoryWidget(userName)
        user.updateInfo(self.allUserWithMessage[0][1]["time"], self.allUserWithMessage[0][1]["note"],
                        self.allUserWithMessage[0][1]["readed"], self.allUserWithMessage[0][1]["type"],
                        self.allUserWithMessage[0][1]["user_label"])
        self.insertRow(0)
        self.setCellWidget(0, 0, user)
        self.refresh_users_list(searchStr)
        self.clearSelection()
        self.selectRow(0)
        self.removeRow(row+1)
        self.refresh_user_row()

    def check_user_exist(self, user, searchStr):
        # print self.userRow
        if user in self.userRow:
            self.move_to_top(self.userRow[user], searchStr)
        else:
            self.add_top(user, searchStr)

    def add_top(self, addUser, searchStr):
        # print "add top"
        self.allUserWithMessage = SH.get_users_and_groups("", "withMessage")
        userName = self.allUserWithMessage[0][1]["user_name"]
        user = HistoryWidget(userName)
        user.updateInfo(self.allUserWithMessage[0][1]["time"], self.allUserWithMessage[0][1]["note"],
                        self.allUserWithMessage[0][1]["readed"], self.allUserWithMessage[0][1]["type"],
                        self.allUserWithMessage[0][1]["user_label"])
        self.insertRow(0)
        self.setCellWidget(0, 0, user)
        self.refresh_users_list(searchStr)
        self.clearSelection()
        self.selectRow(0)
        self.refresh_user_row()

    def choose_user(self):
        # print "choose user"
        if self.isActiveWindow():
            if self.selectedIndexes() != []:
                chosenIndex = self.selectedIndexes()[0].row()
                # print chosenIndex
                self.chosenType = self.cellWidget(chosenIndex, 0).type
                self.chosenUser = self.cellWidget(chosenIndex, 0).name
                # print self.chosenUser
                self.cellWidget(chosenIndex, 0).toReaded()
                self.chooseOneUser.emit()

    def clear_selection(self):
        self.clearSelection()
        self.chosenUser = ""
        self.chosenType = "user"

    def clear_all(self):
        # self.clear()
        self.itemSelectionChanged.disconnect(self.choose_user)
        for i in range(self.rowCount()):
            self.removeRow(0)
        self.clear()
        self.itemSelectionChanged.connect(self.choose_user)

    def remove_selected(self):
        self.itemSelectionChanged.disconnect(self.choose_user)
        lastRow = self.selectedIndexes()[0].row()
        self.removeRow(lastRow)
        self.itemSelectionChanged.connect(self.choose_user)


class HistoryWidget(QWidget):
    def __init__(self, name):
        super(HistoryWidget, self).__init__()

        self.setStyleSheet("QWidget{background-color: rgb(40, 40, 40, 0)}")

        self.name = name
        self.date = ""
        self.message = ""
        self.status = "unreaded"
        self.type = "user"
        self.label = name

        self.head = "%s/userDefault_nothing.png" % Icons_Folder
        self.headLabel = QLabel()
        self.headLabel.setPixmap(QPixmap(self.head).scaled(36, 36))

        self.upLayout = QHBoxLayout()
        self.labelLabel = QLabel(self.label)
        self.labelLabel.setStyleSheet("color:rgb(220, 220, 220); font-family:Arial; font-size:15px")
        self.dateLabel = QLabel(self.date)
        self.dateLabel.setStyleSheet("color:rgb(100, 100, 100); font-family:Arial; font-size:15px")
        self.upLayout.addWidget(self.labelLabel)
        self.upLayout.addStretch()
        self.upLayout.addWidget(self.dateLabel)

        self.messageLabel = QLabel(u'%s' % self.message)
        self.messageLabel.setAlignment(Qt.AlignTop)
        self.messageLabel.setStyleSheet("color:rgb(100, 100, 100); font-family:Arial; font-size:15px")

        self.rightLayout = QVBoxLayout()
        self.rightLayout.addLayout(self.upLayout)
        self.rightLayout.addWidget(self.messageLabel)

        self.masterLayout = QHBoxLayout()
        self.masterLayout.addWidget(self.headLabel)
        self.masterLayout.addSpacing(10)
        self.masterLayout.addLayout(self.rightLayout)
        self.setLayout(self.masterLayout)




    def paintEvent(self, QPaintEvent):
        super(HistoryWidget, self).paintEvent(QPaintEvent)

        painter = QPainter(self)
        if self.type == "user":
            self.userIcon = "%s/userDefault.png" % Icons_Folder
            userIcon = "%s/%s/Icon/user.png" % (Users_Folder, self.name)
            if os.path.exists(userIcon):
                self.userIcon = userIcon
        elif self.type == "group":
            self.userIcon = "%s/groupDefault.png" % Icons_Folder
            groupIcon = "%s/Groups/%s.png" % (Users_Folder, self.name)
            if os.path.exists(groupIcon):
                self.userIcon = groupIcon
        self.headImage = QPixmap(self.userIcon).scaled(36, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        painter.drawPixmap(QPoint(10, 13), self.headImage)

        #self.ellipseColor = QColor(240, 60, 40)
        self.ellipseBrush = QBrush(self.ellipseColor)
        pen = QPen(QColor(0, 0, 0, 0))
        painter.setPen(pen)
        painter.setBrush(self.ellipseBrush)
        painter.drawEllipse(41, 8, 10, 10)

    def updateInfo(self, date, message, readInfo, type, label):
        self.type = type
        self.label = label
        self.labelLabel.setText(self.label)
        if self.type == "user":
            self.setToolTip(self.name)
        elif self.type == "group":
            usersInGroup = SH.get_users_in_group(self.name)
            usersInGroup.sort()
            usersStr = ",\n".join(usersInGroup)
            self.setToolTip("id:\n%s\nusers:\n%s" % (self.name, usersStr))

        if date != 0:
            self.date = time.strftime("%H:%M:%S", time.localtime(int(date)))
            self.dateLabel.setText(self.date)
            if message != "":
                self.message = message
            else:
                self.message = "nodes..."
        self.messageLabel.setText(u'%s' % self.message)
        if readInfo == True:
            self.ellipseColor = QColor(240, 60, 40, 0)
        else:
            self.ellipseColor = QColor(240, 60, 40)
        self.update()

    def toReaded(self):
        self.ellipseColor = QColor(240, 60, 40, 0)
        self.update()
        SH.new_to_readed(self.name, self.type)


class UsersTreeWidget(QTreeWidget):
    chooseOneUser = Signal()
    def __init__(self):
        super(UsersTreeWidget, self).__init__()

        self.setStyleSheet("""
        QTreeWidget{border:none;}
        """)
        self.setHeaderHidden(True)

        self.itemSelectionChanged.connect(self.choose_user)
        self.build_user_tree()
        self.chosenUser = None
        self.chosenType = "user"


    def build_user_tree(self):
        self.itemSelectionChanged.disconnect(self.choose_user)
        self.clear()
        self.myGroups = SH.get_groups("", type="all")
        self.myGroupItems = []
        self.groupRootItem = RootTreeItem("my group")
        self.addTopLevelItem(self.groupRootItem)
        self.setFirstItemColumnSpanned(self.groupRootItem, True)
        for group in self.myGroups:
            groupName = group[1]["user_name"]
            groupLabel = group[1]["user_label"]
            type = group[1]["type"]
            groupItem = UserTreeItem(name=groupName, type=type, label=groupLabel)
            self.groupRootItem.addChild(groupItem)
            self.myGroupItems.append(groupItem)

        self.allUsers = SH.get_all_user("", type="all")
        self.allUserItems = []
        self.upperList = []
        self.upperItems = []
        for user in self.allUsers:
            if user[1]["user_label"][0] not in self.upperList:
                self.upperList.append(user[1]["user_label"][0])
        self.upperList.sort()
        for i in self.upperList:
            rootItem = RootTreeItem(i)
            self.addTopLevelItem(rootItem)
            self.setFirstItemColumnSpanned(rootItem, True)
            self.upperItems.append(rootItem)
        for user in self.allUsers:
            userName = user[1]["user_name"]
            userLabel = user[1]["user_label"]
            type = user[1]["type"]
            userItem = UserTreeItem(name=userName, type=type, label=userLabel)
            upperText = userLabel[0]
            rootItem = self.get_root_item(upperText)
            rootItem.addChild(userItem)
            self.allUserItems.append(userItem)

        self.expandAll()
        self.setRootIsDecorated(False)
        self.setAnimated(True)
        self.itemSelectionChanged.connect(self.choose_user)

    def get_root_item(self, text):
        return self.findItems(text, Qt.MatchExactly)[0]

    def refresh_user_list(self, searchStr):
        self.search_item(self.groupRootItem, searchStr)
        for item in self.upperItems:
            self.search_item(item, searchStr)

    def search_item(self, rootItem, searchStr):
        allHidden = True
        for item in rootItem.children():
            if searchStr != "":
                if item.label.find(searchStr) != -1:
                    item.setHidden(False)
                    allHidden = False
                else:
                    item.setHidden(True)
            else:
                item.setHidden(False)
                allHidden = False
        if allHidden:
            rootItem.setHidden(True)
        else:
            rootItem.setHidden(False)

    def choose_user(self):
        # print "choose user"
        if self.isActiveWindow():
            if self.selectedItems() != []:
                chosenItem = self.selectedItems()[0]
                self.chosenType = chosenItem.type
                self.chosenUser = chosenItem.name
                if self.chosenUser:
                    self.chooseOneUser.emit()

    def clear_selection(self):
        self.clearSelection()
        self.chosenUser = None
        self.chosenType = "user"


class RootTreeItem(QTreeWidgetItem):
    def __init__(self, i):
        super(RootTreeItem, self).__init__()

        self.upperText = i
        self.setText(0, self.upperText)
        self.setBackground(0, QColor(65, 65, 65))
        self.setSizeHint(0, QSize(30, 30))

        self.childrenItems = []
        self.name = None
        self.type = None
        self.label = None

    def children(self):
        self.childrenItems = []
        for i in range(self.childCount()):
            self.childrenItems.append(self.child(i))
        return self.childrenItems


class UserTreeItem(QTreeWidgetItem):
    def __init__(self, name="", type="user", label=""):
        super(UserTreeItem, self).__init__()

        self.setSizeHint(0, QSize(30, 30))

        self.name = name
        self.type = type
        self.label = label

        if self.type == "user":
            self.userIcon = "%s/userDefault.png" % Icons_Folder
            userIcon = "%s/%s/Icon/user.png" % (Users_Folder, self.name)
            if os.path.exists(userIcon):
                self.userIcon = userIcon
        elif self.type == "group":
            self.userIcon = "%s/groupDefault.png" % Icons_Folder
            groupIcon = "%s/Groups/%s.png" % (Users_Folder, self.name)
            if os.path.exists(groupIcon):
                self.userIcon = groupIcon

        self.setIcon(0, QIcon(self.userIcon))
        self.setText(0, self.label)

        if self.type == "user":
            self.setToolTip(0, self.name)
        elif self.type == "group":
            usersInGroup = SH.get_users_in_group(self.name)
            usersInGroup.sort()
            usersStr = ",\n".join(usersInGroup)
            self.setToolTip(0, "id:\n%s\nusers:\n%s" % (self.name, usersStr))


class MessageTableWidget2(QWidget, QObject):
    def __init__(self):
        super(MessageTableWidget2, self).__init__()

        self.setStyleSheet("background:%s" % MessageTableColor)

        self.masterLayout = QVBoxLayout()
        self.messageLayout = QVBoxLayout()
        self.masterLayout.setAlignment(Qt.AlignTop)

        self.masterLayout.addLayout(self.messageLayout)
        self.masterLayout.addStretch(3)

        self.setLayout(self.masterLayout)

        self.refreshMessages("")

        # self.setMouseTracking(True)

    def refreshMessages(self, user, type = "user"):
        self.clearAll()
        if user != "":
            #print "refresh"
            if type == "user":
                messageInfoList = SH.get_user_messages(user)
            elif type == "group":
                messageInfoList = SH.get_group_messages(user)
            # print type
            # print user
            # print messageInfoList
            self.messageLayout.setAlignment(Qt.AlignTop)
            for i in range(len(messageInfoList)):
                date = int(messageInfoList[i][0])
                if messageInfoList[i][1] == "in":
                    self.message = ReciveMessageWidget(date, user, messageInfoList[i][2], messageInfoList[i][3], messageInfoList[i][4], messageInfoList[i][5])
                else:
                    self.message = SendMessageWidget(date, user, messageInfoList[i][2], messageInfoList[i][3], messageInfoList[i][4], messageInfoList[i][5], type)
                self.messageLayout.addWidget(self.message)


    def clearAll(self):
        '''
        for i in range(len(self.messageWidgetList)):
            messageWidget = self.messageWidgetList[0]
            #print nodeWidget
            self.messageWidgetList.pop(0)
            messageWidget.deleteLater()
        '''
        self.clearLayout(self.messageLayout)
        #self.messageLayout.deleteLater()

    def clearLayout(self, layout):
        if layout != None:
            # print "clear", layout.count()
            while layout.count():
                child = layout.takeAt(0)
                # print child
                if child.widget() is not None:
                    child.widget().deleteLater()
                elif child.layout() is not None:
                    self.clearLayout(child.layout())


class ReciveMessageWidget(QWidget, QObject):
    def __init__(self, date, name, fromWhom, message, nodesStr, nodeExist):
        super(ReciveMessageWidget, self).__init__()

        self.setStyleSheet("background-color: rgb(40, 40, 40, 0)")
        #self.setFixedHeight(200)

        self.name = name
        self.fromWhom = fromWhom
        self.date = date
        self.nodeExist = nodeExist
        strfDate = time.strftime("%m-%d %H:%M:%S", time.localtime(int(date)))

        self.dateLayout = QHBoxLayout()
        self.dateLabel = QLabel("%s    %s" % (self.fromWhom, strfDate))
        self.dateLabel.setStyleSheet("color:rgb(100, 100, 100); font-family:Arial; font-size:15px")
        self.dateLayout.setAlignment(Qt.AlignLeft)
        self.dateLayout.addSpacing(70)
        self.dateLayout.addWidget(self.dateLabel)

        self.headImageLayout = QVBoxLayout()
        self.headImageLabel = QLabel()
        self.imageFile = "%s/userDefault.png" % Icons_Folder
        if os.path.exists("%s/%s/Icon/user.png" % (Users_Folder, self.fromWhom)):
            self.imageFile = "%s/%s/Icon/user.png" % (Users_Folder, self.fromWhom)
        self.headImageLabel.setPixmap(QPixmap(self.imageFile).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.headImageLayout.setAlignment(Qt.AlignTop)
        self.headImageLayout.addWidget(self.headImageLabel)
        self.headImageLayout.addStretch()

        self.messageLayout = QVBoxLayout()
        self.messageLayout1 = QHBoxLayout()
        if SH.is_emoji(message):
            self.messageLabel = QEmojiLabel(u'%s' % message)
        else:
            self.messageLabel = QMessageLabel(u'%s' % message)
        self.messageLabel.setTextInteractionFlags(Qt.TextEditorInteraction)
        if self.messageLabel.width() > 380:
            self.messageLabel.setFixedWidth(380)
        self.messageLabel.setWordWrap(True)
        self.messageLabel.setStyleSheet("color:rgb(180, 180, 180); padding: 5px 2px 2px 20px; font-size:%spx; font-family:Arial" % MessageFontSize)
        self.messageLabel.showbig.connect(self.show_big_label)
        #self.messageLabel.setAlignment(Qt.AlignTop)
        self.buttonLayout = QHBoxLayout()
        self.nodePasteButton = PasteButton(self.nodeExist)
        self.nodePasteButton.buttonClicked.connect(self.pasteNodes)
        self.nodesStrLabel = QLabel(u'%s' % nodesStr)
        self.nodesStrLabel.setStyleSheet("color:rgb(130, 130, 130); font-size:%spx; font-family:Arial" % (MessageFontSize))
        self.buttonLayout.addSpacing(20)
        self.buttonLayout.addWidget(self.nodePasteButton)
        if self.nodeExist:
            self.buttonLayout.addWidget(self.nodesStrLabel)
        self.buttonLayout.addStretch()
        self.messageLayout1.addWidget(self.messageLabel)
        self.messageLayout1.addStretch()
        self.messageLayout.addLayout(self.messageLayout1)
        self.messageLayout.addLayout(self.buttonLayout)

        self.downLayout = QHBoxLayout()
        self.downLayout.setAlignment(Qt.AlignLeft)
        self.downLayout.addLayout(self.headImageLayout)
        self.downLayout.addLayout(self.messageLayout)

        self.masterLayout = QVBoxLayout()
        self.masterLayout.setAlignment(Qt.AlignTop)
        self.masterLayout.addLayout(self.dateLayout)
        self.masterLayout.addLayout(self.downLayout)
        self.masterLayout.addSpacing(10)
        self.setLayout(self.masterLayout)

    def paintEvent(self, QPaintEvent):
        super(ReciveMessageWidget, self).paintEvent(QPaintEvent)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        if self.nodeExist:
            w = max(self.messageLabel.width(), self.nodesStrLabel.x()+self.nodesStrLabel.width()-self.messageLabel.x())
            self.rect1 = QRect(80, self.messageLabel.y(), w, self.messageLabel.height() + 40)
        elif self.messageLabel.height()>40:
            self.rect1 = QRect(80, self.messageLabel.y(), self.messageLabel.width(), self.messageLabel.height() + 5)
        else:
            self.rect1 = QRect(80, self.messageLabel.y(), self.messageLabel.width(), 45)

        self.rect2 = QRect(0, 0, 10, 10)

        self.rectBrush = QBrush(ReciveMessagecolor)
        pen = QPen(QColor(0, 0, 0, 0))
        painter.setPen(pen)
        painter.setBrush(self.rectBrush)
        painter.drawRoundedRect(self.rect1, 3, 3)
        painter.translate(80, self.messageLabel.y()+17)
        painter.rotate(45)
        painter.drawRect(self.rect2)

    def pasteNodes(self):
        #print "paste"
        if self.name != self.fromWhom:
            SH.paste_group_nodes(self.name, self.date)
        else:
            SH.paste_user_nodes(self.name, self.date)

    def show_big_label(self):
        #print "show_big_label"
        self.labelBigView = LabelBigView(self.messageLabel.text())
        self.labelBigView.show()

    def deleteLater(self):
        # print "delete send"
        self.clearLayout(self.masterLayout)

    def clearLayout(self, layout):
        if layout != None:
            # print "clear", layout.count()
            while layout.count():
                child = layout.takeAt(0)
                # print child
                if child.widget() is not None:
                    child.widget().deleteLater()
                elif child.layout() is not None:
                    self.clearLayout(child.layout())


class SendMessageWidget(QWidget, QObject):
    def __init__(self, date, name, fromWhom, message, nodesStr, nodeExist, type="user"):
        super(SendMessageWidget, self).__init__()

        self.setStyleSheet("background-color: rgb(40, 40, 40, 0)")
        #self.setFixedWidth(400)

        self.name = name
        self.fromWhom = fromWhom
        self.date = date
        self.nodeExist = nodeExist
        self.type = type
        strfDate = time.strftime("%m-%d %H:%M:%S", time.localtime(int(date)))

        self.dateLayout = QHBoxLayout()
        self.dateLabel = QLabel(strfDate)
        self.dateLabel.setStyleSheet("color:rgb(100, 100, 100); font-family:Arial; font-size:15px")
        self.dateLayout.setAlignment(Qt.AlignRight)
        self.dateLayout.addWidget(self.dateLabel)
        self.dateLayout.addSpacing(70)

        self.headImageLayout = QVBoxLayout()
        self.headImageLabel = QLabel()
        self.imageFile = "%s/userDefault.png" % Icons_Folder
        if os.path.exists("%s/%s/Icon/user.png" % (Users_Folder, Current_User)):
            self.imageFile = "%s/%s/Icon/user.png" % (Users_Folder, Current_User)
        self.headImageLabel.setPixmap(QPixmap(self.imageFile).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.headImageLayout.setAlignment(Qt.AlignTop)
        self.headImageLayout.addWidget(self.headImageLabel)
        self.headImageLayout.addStretch()

        self.messageLayout = QVBoxLayout()
        self.messageLayout1 = QHBoxLayout()
        if SH.is_emoji(message):
            self.messageLabel = QEmojiLabel(u'%s' % message)
        else:
            self.messageLabel = QMessageLabel(u'%s' % message)
        self.messageLabel.setTextInteractionFlags(Qt.TextEditorInteraction)
        #print message
        #print self.messageLabel.width()
        if self.messageLabel.width() > 380:
            self.messageLabel.setFixedWidth(380)
        self.messageLabel.setWordWrap(True)
        self.messageLabel.setStyleSheet("color:rgb(180, 180, 180); padding: 5px 20px 2px 2px; font-size:%spx; font-family:Arial" % MessageFontSize)
        self.messageLabel.showbig.connect(self.show_big_label)
        #self.messageLabel.setAlignment(Qt.AlignTop)
        self.buttonLayout = QHBoxLayout()
        self.nodePasteButton = PasteButton(self.nodeExist)
        self.nodePasteButton.buttonClicked.connect(self.pasteNodes)
        self.nodesStrLabel = QLabel(u'%s' % nodesStr)
        self.nodesStrLabel.setStyleSheet("color:rgb(130, 130, 130); font-size:%spx; font-family:Arial" % (MessageFontSize))
        self.nodesStrLabel.adjustSize()
        self.buttonLayout.addStretch()
        if self.nodeExist:
            self.buttonLayout.addWidget(self.nodesStrLabel)
        self.buttonLayout.addWidget(self.nodePasteButton)
        self.buttonLayout.addSpacing(20)
        self.messageLayout1.addStretch()
        self.messageLayout1.addWidget(self.messageLabel)
        self.messageLayout.addLayout(self.messageLayout1)
        self.messageLayout.addLayout(self.buttonLayout)

        self.downLayout = QHBoxLayout()
        self.downLayout.setAlignment(Qt.AlignRight)
        self.downLayout.addStretch()
        self.downLayout.addLayout(self.messageLayout)
        self.downLayout.addLayout(self.headImageLayout)


        self.masterLayout = QVBoxLayout()
        self.masterLayout.setAlignment(Qt.AlignTop)
        self.masterLayout.addLayout(self.dateLayout)
        self.masterLayout.addLayout(self.downLayout)
        self.masterLayout.addSpacing(10)
        self.setLayout(self.masterLayout)

    def paintEvent(self, QPaintEvent):
        super(SendMessageWidget, self).paintEvent(QPaintEvent)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        if self.nodeExist:
            #print self.nodesStrLabel.text()
            #print self.nodesStrLabel.x(), self.messageLabel.x()
            #print self.nodesStrLabel.width(), self.messageLabel.width()
            #print self.nodesStrLabel.text()
            x = min(self.nodesStrLabel.x(), self.messageLabel.x())
            w = max(self.messageLabel.x()+self.messageLabel.width()-self.nodesStrLabel.x(), self.messageLabel.width())
            self.rect1 = QRect(x-10, self.messageLabel.y(), w+10, self.messageLabel.height() + 40)
        elif self.messageLabel.height() > 40:
            self.rect1 = QRect(self.messageLabel.x()-10, self.messageLabel.y(), self.messageLabel.width()+10, self.messageLabel.height() + 5)
        else:
            self.rect1 = QRect(self.messageLabel.x() - 10, self.messageLabel.y(), self.messageLabel.width() + 10,45)
        self.rect2 = QRect(0, 0, 10, 10)

        self.rectBrush = QBrush(SendMessagecolor)
        pen = QPen(QColor(0, 0, 0, 0))
        painter.setPen(pen)
        painter.setBrush(self.rectBrush)
        painter.drawRoundedRect(self.rect1, 3, 3)
        painter.translate(self.messageLabel.x()-10 + self.messageLabel.width()+10, self.messageLabel.y()+17)
        painter.rotate(45)
        painter.drawRect(self.rect2)

    def pasteNodes(self):
        #print "paste"
        if self.type == "group":
            SH.paste_group_nodes(self.name, self.date)
        elif self.type == "user":
            SH.paste_user_nodes(self.name, self.date)

    def show_big_label(self):
        #print "show_big_label"
        self.labelBigView = LabelBigView(self.messageLabel.text())
        self.labelBigView.show()

    def deleteLater(self):
        # print "delete send"
        self.clearLayout(self.masterLayout)

    def clearLayout(self, layout):
        if layout != None:
            # print "clear", layout.count()
            while layout.count():
                child = layout.takeAt(0)
                # print child
                if child.widget() is not None:
                    child.widget().deleteLater()
                elif child.layout() is not None:
                    self.clearLayout(child.layout())


class QMessageLabel(QLabel):
    showbig = Signal()

    def __init__(self, text):
        super(QMessageLabel, self).__init__()
        self.setText(text)

        self.adjustSize()

    def mouseDoubleClickEvent(self, event):
        #print "mouseDoubleClickEvent"
        self.showbig.emit()


class QEmojiLabel(QLabel, QObject):
    showbig = Signal()
    def __init__(self, message):
        super(QEmojiLabel, self).__init__()

        emojiInfo = SH.get_info_from_html(message)

        self.path = emojiInfo["imgPath"]
        self.emojiWidth = emojiInfo["imgWidth"]
        self.emojiHeight = emojiInfo["imgHeight"]

        #self.setToolTip(self.path)

        self.emojiMovie = None
        if self.path.split(".")[-1] != "gif":
            self.imageFile = self.path
            self.setPixmap(QPixmap(self.imageFile).scaled(self.emojiWidth, self.emojiHeight, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.emojiMovie = QMovie(self.path)
            self.emojiMovie.setScaledSize(QSize(self.emojiWidth, self.emojiHeight))
            self.setMovie(self.emojiMovie)
            self.emojiMovie.start()

        self.adjustSize()

    def deleteLater(self):
        # print "delete emoji"
        if self.emojiMovie:
            self.emojiMovie.deleteLater()


class ScreenshotHideWidget(QCheckBox):
    checkclicked = Signal()

    def __init__(self):
        super(ScreenshotHideWidget, self).__init__()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setStyleSheet("padding: 10px 10px 10px 10px;background-color: rgb(70, 70, 70)")

        self.setText("hide window when taking screenshot")

        self.clicked.connect(self.check_clicked)

    def check_clicked(self):
        self.close()
        self.checkclicked.emit()


class LabelBigView(QWidget):
    def __init__(self, text):
        super(LabelBigView, self).__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        #print text
        #print SH.get_info_from_html(text, index="all")
        info = SH.get_info_from_html(text, index="all")
        try:
            for i in range(len(info["imgPath"])):
                text = text.replace('width="%s" height="%s"' % (info["imgWidth"][i], info["imgHeight"][i]), 'width="" height=""')
        except:
            print "LabelBigView error"
        #print text
        self.mainLabel = QLabel(text)
        self.mainLabel.setAlignment(Qt.AlignCenter)
        self.mainLabel.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.mainLabel.setStyleSheet("color:white")

        self.scrollArea = QScrollArea()
        self.scrollArea.setWidget(self.mainLabel)
        self.scrollArea.setAlignment(Qt.AlignCenter)
        self.scrollArea.setStyleSheet("background-color:transparent;border:none")

        self.masterLayout = QVBoxLayout()
        self.masterLayout.setAlignment(Qt.AlignCenter)
        self.masterLayout.addSpacing(100)
        self.masterLayout.addWidget(self.scrollArea)
        self.masterLayout.addSpacing(50)
        self.setLayout(self.masterLayout)

        self.adjustSize()
        #print self.width()
        #print self.height()


        self.setWindowState(Qt.WindowMaximized)

    def paintEvent(self, QPaintEvent):
        super(LabelBigView, self).paintEvent(QPaintEvent)

        painter = QPainter(self)
        brush = QBrush(QColor(20, 20, 20, 150))
        pen = QPen(QColor(20, 20, 20, 150))
        pen.setWidth(0)
        painter.setBrush(brush)
        painter.setPen(pen)
        painter.drawRect(0, 0, self.width(), self.height())

        textPen = QPen(QColor(220, 220, 220))
        text = "double click to close"
        font = QFont("Arial", 35)
        painter.setFont(font)
        painter.setPen(textPen)
        tooltipRect = QRect(0, 30, self.width(), self.height())
        painter.drawText(tooltipRect, Qt.AlignHCenter, text)


    def mouseDoubleClickEvent(self, event):
        self.close()


class PasteButton(QLabel):
    buttonClicked = Signal()

    def __init__(self, nodeExist):
        super(PasteButton, self).__init__()

        self.nodeExist = nodeExist

        self.setToolTip("<font color=#FFFFFF>paste</font>")
        if self.nodeExist:
            self.imageFile = '%s/paste.png' % (Icons_Folder)
        else:
            self.imageFile = '%s/paste_none.png' % (Icons_Folder)
        self.setPixmap(QPixmap(self.imageFile).scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.setStyleSheet("background-color: rgb(40, 40, 40, 0)")

    def enterEvent(self, event):
        if self.nodeExist:
            self.setStyleSheet("background-color: rgb(70, 70, 70)")

    def leaveEvent(self, event):
        if self.nodeExist:
            self.setStyleSheet("background-color: rgb(40, 40, 40, 0)")

    def mousePressEvent(self, event):
        if self.nodeExist:
            self.setStyleSheet("background-color: rgb(40, 40, 40)")

    def mouseReleaseEvent(self, event):
        if self.nodeExist:
            self.buttonClicked.emit()
            self.setStyleSheet("background-color: rgb(70, 70, 70)")


class QLabelButton(QLabel):
    buttonClicked = Signal()

    def __init__(self, name):
        super(QLabelButton, self).__init__()

        self.setToolTip("<font color=#FFFFFF>%s</font>" % name)
        self.imageFile = '%s/%s.png' % (Icons_Folder, name)
        self.setPixmap(QPixmap(self.imageFile).scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
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


class QRefreshThread(QThread):
    refreshNow = Signal()
    readed = Signal()

    def __init__(self):
        super(QRefreshThread, self).__init__()

        self.status = "running"
        # self.lastUsersInfoWithMessage = SH.get_users_and_groups("", "withOneMessage")
        self.lastUsersInfoWithMessage = []

    def run(self):
        i = 1
        while i > 0:
            if self.status == "running":
                try:
                    self.newUsersInfoWithMessage = SH.get_users_and_groups("", "withOneMessage")
                    # print self.newUsersInfoWithMessage
                    if self.newUsersInfoWithMessage != []:
                        if self.newUsersInfoWithMessage != self.lastUsersInfoWithMessage and self.newUsersInfoWithMessage[0][1]["readed"] == False:
                            self.refreshNow.emit()
                        if self.newUsersInfoWithMessage != self.lastUsersInfoWithMessage and self.newUsersInfoWithMessage[0][1]["readed"] == True:
                            self.readed.emit()
                    self.lastUsersInfoWithMessage = self.newUsersInfoWithMessage
                except:
                    pass
            # print i
            time.sleep(1)
            i = i + 1

    def runAgain(self):
        self.status = "running"

    def stop(self):
        self.status = "stop"

class ClearHistoryThread(QThread):
    clearDone = Signal()
    def __init__(self):
        super(ClearHistoryThread, self).__init__()

    def run(self):
        for user in os.listdir(SH.History_Folder):
            if user != "Groups":
                shutil.rmtree("%s/%s" % (SH.History_Folder, user), True)
        for group in os.listdir("%s/Groups" % SH.History_Folder):
            shutil.rmtree("%s/Groups/%s" % (SH.History_Folder, group), True)
        shutil.rmtree("%s/tmp" % SH.Current_User_Folder, True)
        self.clearDone.emit()


class DelOneHistoryThread(QThread):
    clearDone = Signal()
    def __init__(self):
        super(DelOneHistoryThread, self).__init__()

    def set_user(self, type, user):
        self.user = user
        self.type = type

    def run(self):
        if self.type == "user":
            if self.user in os.listdir(SH.History_Folder):
                shutil.rmtree("%s/%s" % (SH.History_Folder, self.user), True)
        if self.type == "group":
            if self.user in os.listdir("%s/Groups" % SH.History_Folder):
                shutil.rmtree("%s/Groups/%s" % (SH.History_Folder, self.user), True)
        self.clearDone.emit()



class TipWidget(QWidget):
    noTip = Signal()
    openMain = Signal()

    def __init__(self):
        super(TipWidget, self).__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint )
        self.w = 400
        self.h = 100
        self.setFixedSize(self.w, self.h)
        #self.setFixedHeight(self.h)
        self.setWindowTitle("Tip")
        self.setStyleSheet("background-color: rgb(60, 60, 60)")

        self.nkFile = ""
        self.fromWhom = ""
        self.messageTime = "0"

        self.layout0 = QHBoxLayout()
        self.layout0.setAlignment(Qt.AlignCenter)
        self.nkFileLabel = QLabel("current nk: %s" % self.nkFile)
        self.nkFileLabel.setStyleSheet("color:rgb(100, 150, 220)")
        self.layout0.addWidget(self.nkFileLabel)

        self.layout1 = QHBoxLayout()
        self.layout1.setAlignment(Qt.AlignCenter)
        self.showTipLabel = QPushLabel()
        self.showTipLabel.updateInfo("don't show", 0)
        self.showTipLabel.notShowAnymore.connect(self.notShowTip)
        # self.layout1.addSpacing(20)
        self.layout1.addWidget(self.showTipLabel)
        # self.layout1.addStretch()

        self.layout2 = QHBoxLayout()
        self.layout2.setAlignment(Qt.AlignRight)
        self.messageLabel = QPushLabel()
        self.messageLabel.updateInfo("<font>%s</font> send you a message... ..." % self.fromWhom, 1)
        self.messageLabel.openSendNodes.connect(self.openSendNodes)
        self.layout2.addStretch()
        self.layout2.addWidget(self.messageLabel)

        self.layout3 = QHBoxLayout()
        self.layout3.setAlignment(Qt.AlignRight)
        self.timeLabel = QLabel("0")
        self.layout3.addStretch()
        self.layout3.addWidget(self.timeLabel)
        self.layout3.addSpacing(10)

        self.layoutLeft = QVBoxLayout()
        self.layoutLeft.setAlignment(Qt.AlignCenter)
        #self.logoLabel = QLabel()
        #self.imageFile = '%s/%s.png' % (Icons_Folder, "tip_logo")
        #self.logoLabel.setPixmap(QPixmap(self.imageFile).scaled(72, 72, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.logoLabel = QEmojiLabel('<img src="%s/%s.gif" width="72" height="72">' % (Icons_Folder, "tip_logo"))
        self.layoutLeft.addStretch()
        self.layoutLeft.addWidget(self.logoLabel)
        self.layoutLeft.addSpacing(5)
        self.layoutLeft.addLayout(self.layout1)
        self.layoutLeft.addStretch()



        self.layoutRight = QVBoxLayout()
        self.layoutRight.addLayout(self.layout0)
        self.layoutRight.addStretch()
        self.layoutRight.addLayout(self.layout3)
        self.layoutRight.addLayout(self.layout2)
        #self.layoutRight.addSpacing(10)
        #self.layoutRight.addLayout(self.layout1)

        self.masterLayout = QHBoxLayout()
        self.masterLayout.addLayout(self.layoutLeft)
        self.masterLayout.addLayout(self.layoutRight)
        self.setLayout(self.masterLayout)


        #self.adjustSize()
        screenRes = QDesktopWidget().screenGeometry()
        self.move(QPoint(screenRes.width()-self.width(), screenRes.height()-self.height()))
        #self.move(QPoint(screenRes.width()/2,screenRes.height()/2)-QPoint((self.width()/2),(self.height()/2)))
        #self.move(QPoint(0, 0))

    def updateInfo(self, nkFile, user, messageTime):
        self.nkFile = nkFile
        self.fromWhom = user
        self.messageTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(messageTime))
        self.timeLabel.setText("<font color=#FFFF33><i>%s</i></font>" % self.messageTime)
        self.nkFileLabel.setText("current nk: <font color=#66aaff><i>%s</i></font>" % self.nkFile)
        self.messageLabel.updateInfo("<font color=#FFFF33><i>%s</i></font>" % self.fromWhom + " send you a message...", 1)
        self.update()

    def notShowTip(self):
        self.noTip.emit()
        self.close()

    def openSendNodes(self):
        self.openMain.emit()
        self.close()

    def paintEvent(self, QPaintEvent):
        super(TipWidget, self).paintEvent(QPaintEvent)

        self.color = QColor(1, 1, 1, 0)
        self.closeSize = 20

        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        brush = QBrush(self.color)
        painter.setBrush(brush)
        self.rect = QRect(self.w-self.closeSize, 0, self.w, self.closeSize)

        painter.drawRect(self.rect)
        self.image = QPixmap("%s/close.png" % Icons_Folder).scaled(self.closeSize, self.closeSize)
        painter.drawPixmap(QPoint(self.w-self.closeSize, 0), self.image)




    def mousePressEvent(self, event):
        pos = event.pos()
        if self.rect.contains(pos):
            self.close()
        else:
            pass

class QPushLabel(QLabel):
    notShowAnymore = Signal()
    openSendNodes = Signal()

    def __init__(self):# type 0-show/don't show 1-send you a message
        super(QPushLabel, self).__init__()
        self.textFont = "Arial"
        self.textSize1 = TipFontSize-1
        self.textSize2 = TipFontSize


    def updateInfo(self, text, type):
        self.text = text
        self.type = type
        if self.type == 0:
            self.setText('<font color = #eeeeee size = %s face = %s>%s</font>' % (self.textSize1, self.textFont, self.text))
        if self.type == 1:
            self.setText('<font color = #DDDDDD size = %s face = %s>%s</font>' % (self.textSize2, self.textFont, self.text))
        self.update()

    def enterEvent(self, event):
        if self.type == 0:
            self.setText('<font color = #ff5050 size = %s face = %s>%s</font>' % (self.textSize1, self.textFont, self.text))
        if self.type == 1:
            self.setText('<font color = #BAA0D4 size = %s face = %s>%s</font>' % (self.textSize2, self.textFont, self.text))

    def leaveEvent(self,event):
        if self.type == 0:
            self.setText('<font color = #eeeeee size = %s face = %s>%s</font>' % (self.textSize1, self.textFont, self.text))
        if self.type == 1:
            self.setText('<font color = #DDDDDD size = %s face = %s>%s</font>' % (self.textSize2, self.textFont, self.text))

    def mousePressEvent(self, event):
        if self.type == 0:
            self.setText('<font color = #dd3030 size = %s face = %s>%s</font>' % (self.textSize1, self.textFont, self.text))
        if self.type == 1:
            self.setText('<font color = #9A80B4 size = %s face = %s>%s</font>' % (self.textSize2, self.textFont, self.text))

    def mouseReleaseEvent(self,event):
        if self.type == 0:
            self.setText('<font color = #ff5050 size = %s face = %s>%s</font>' % (self.textSize1, self.textFont, self.text))
            self.notShowAnymore.emit()
        if self.type == 1:
            self.setText('<font color = #BAA0D4 size = %s face = %s>%s</font>' % (self.textSize2, self.textFont, self.text))
            self.openSendNodes.emit()


class AboutWidget(QWidget):
    def __init__(self):
        super(AboutWidget, self).__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setFixedSize(270, 250)
        self.setWindowTitle("About")

        self.setStyleSheet("color: white; background-color: rgb(50, 50, 50)")
        aboutToolbox = QLabel()
        aboutToolbox.setPixmap(QPixmap("%s/logo.png" % Icons_Folder).scaled(250, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        aboutVer = QLabel(VER)
        aboutVer.setStyleSheet("font:20px Arial")
        aboutAuthor = QLabel("Author:%s" % AUTHOR)
        aboutAuthor.setAlignment(Qt.AlignRight)
        aboutAuthor.setStyleSheet("font:15px Arial")
        aboutDate = QLabel("Date:%s" % DATE)
        aboutDate.setAlignment(Qt.AlignRight)
        aboutDate.setStyleSheet("font:15px Arial")

        self.masterLayout = QVBoxLayout()
        self.masterLayout.addWidget(aboutToolbox)
        self.masterLayout.addWidget(aboutVer)
        self.masterLayout.addWidget(aboutAuthor)
        self.masterLayout.addWidget(aboutDate)
        self.setLayout(self.masterLayout)

        self.adjustSize()
        screenRes = QDesktopWidget().screenGeometry()
        #self.move(QPoint(screenRes.width()/2,screenRes.height()/2)-QPoint((self.width()/2),(self.height()/2)))
        self.move(QPoint(0, 0))


class PrefWidget(QWidget):
    def __init__(self):
        super(PrefWidget, self).__init__()
        self.userFolder = "%s/%s" % (Users_Folder, Current_User)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setFixedHeight(250)
        self.setWindowTitle("Pref")

        #self.setStyleSheet("color: white; background-color: rgb(50, 50, 50)")

        self.showTipDefault = QCheckBox("show tip default")
        self.hideWindowWhenShotScreenDefault = QCheckBox("hide window when taking screenshot default")

        self.closeButtonLayout = QHBoxLayout()
        self.okButton = QPushButton("Ok")
        self.okButton.clicked.connect(self.changePref)
        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.close)
        self.closeButtonLayout.addWidget(self.okButton)
        self.closeButtonLayout.addWidget(self.cancelButton)


        self.masterLayout = QVBoxLayout()
        self.masterLayout.addWidget(self.showTipDefault)
        self.masterLayout.addWidget(self.hideWindowWhenShotScreenDefault)
        self.masterLayout.addStretch()
        self.masterLayout.addLayout(self.closeButtonLayout)
        self.setLayout(self.masterLayout)

        self.adjustSize()
        screenRes = QDesktopWidget().screenGeometry()
        self.move(QPoint(0, 0))

    def loadPref(self):
        prefData = SH.load_pref()
        self.showTipDefault.setChecked(prefData["showTipDefault"])
        self.hideWindowWhenShotScreenDefault.setChecked(prefData["hideWindowWhenShotScreen"])
        self.update()

    def changePref(self):
        prefData = {}
        prefData["showTipDefault"] = self.showTipDefault.isChecked()
        prefData["hideWindowWhenShotScreen"] = self.hideWindowWhenShotScreenDefault.isChecked()
        SH.change_pref(prefData)
        self.close()


class GroupEditWidget(QWidget):
    addGroup = Signal()
    leaveGroup = Signal()
    delGroup = Signal()
    addUserToGroup = Signal()
    removeUsersFromGroup = Signal()

    def __init__(self):
        super(GroupEditWidget, self).__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowTitle("My Groups")
        if not inNuke:
            self.setStyleSheet("color: white; background-color: rgb(50, 50, 50)")

        self.groupLayout = QHBoxLayout()
        self.groupButtonLayout = QVBoxLayout()
        self.groupAddButton = QLabelButton("add")
        self.groupAddButton.buttonClicked.connect(self.add_group)
        self.groupAddButton.setToolTip("add group")
        self.groupLeaveButton = QLabelButton("leave")
        self.groupLeaveButton.buttonClicked.connect(self.leave_group)
        self.groupLeaveButton.setToolTip("leave group")
        self.groupRemoveButton = QLabelButton("remove")
        self.groupRemoveButton.buttonClicked.connect(self.del_group)
        self.groupRemoveButton.setToolTip("delete group")
        self.groupButtonLayout.addStretch()
        self.groupButtonLayout.addWidget(self.groupAddButton)
        self.groupButtonLayout.addSpacing(15)
        self.groupButtonLayout.addWidget(self.groupLeaveButton)
        self.groupButtonLayout.addSpacing(15)
        self.groupButtonLayout.addWidget(self.groupRemoveButton)
        self.groupButtonLayout.addStretch()
        self.groupListLayout = QVBoxLayout()
        self.groupLabel = QLabel("groups")
        self.groupLabel.setAlignment(Qt.AlignCenter)
        self.groupListWidget = QListWidget()
        self.groupListWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.groupListWidget.itemClicked[QListWidgetItem].connect(self.refresh_users_list)
        self.groupListLayout.addWidget(self.groupLabel)
        self.groupListLayout.addWidget(self.groupListWidget)
        self.groupLayout.addLayout(self.groupButtonLayout)
        self.groupLayout.addLayout(self.groupListLayout)

        self.usersLayout = QHBoxLayout()
        self.usersListLayout = QVBoxLayout()
        self.usersLabel = QLabel("users")
        self.usersLabel.setAlignment(Qt.AlignCenter)
        self.usersInGroupLabel = QLabel("in ...")
        self.usersInGroupLabel.setAlignment(Qt.AlignCenter)
        self.usersListWidget = QListWidget()
        self.usersListWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.usersListLayout.addWidget(self.usersLabel)
        self.usersListLayout.addWidget(self.usersInGroupLabel)
        self.usersListLayout.addWidget(self.usersListWidget)
        self.usersLayout.addLayout(self.usersListLayout)

        self.allUsersLayout = QHBoxLayout()
        self.allUsersButtonLayout = QVBoxLayout()
        self.allUsersAddButton = QLabelButton("move_left")
        self.allUsersAddButton.buttonClicked.connect(self.add_users)
        self.allUsersAddButton.setToolTip("add to group")
        self.allUsersRemoveButton = QLabelButton("move_right")
        self.allUsersRemoveButton.buttonClicked.connect(self.remove_users)
        self.allUsersRemoveButton.setToolTip("remove from group")
        self.allUsersButtonLayout.addStretch()
        self.allUsersButtonLayout.addWidget(self.allUsersAddButton)
        self.allUsersButtonLayout.addSpacing(20)
        self.allUsersButtonLayout.addWidget(self.allUsersRemoveButton)
        self.allUsersButtonLayout.addStretch()
        self.allUsersListLayout = QVBoxLayout()
        self.allUsersLabel = QLabel("all users")
        self.allUsersLabel.setAlignment(Qt.AlignCenter)
        self.allUsersSearchLineEdit = QLineEdit()
        self.allUsersSearchLineEdit.textChanged.connect(self.refresh_all_users_list)
        self.allUsersSearchLineEdit.setStyleSheet("color:rgb(220, 220, 220); padding: 2px 2px 2px 20px;background-image: url(%s/search.png);background-position: left;background-repeat: no-repeat" % Icons_Folder)
        self.allUsersListWidget = QListWidget()
        self.allUsersListLayout.addWidget(self.allUsersLabel)
        self.allUsersListLayout.addWidget(self.allUsersSearchLineEdit)
        self.allUsersListLayout.addWidget(self.allUsersListWidget)
        self.allUsersLayout.addLayout(self.allUsersButtonLayout)
        self.allUsersLayout.addLayout(self.allUsersListLayout)

        self.masterLayout = QHBoxLayout()
        self.masterLayout.addLayout(self.groupLayout)
        self.masterLayout.addSpacing(20)
        self.masterLayout.addLayout(self.usersLayout)
        self.masterLayout.addLayout(self.allUsersLayout)
        self.setLayout(self.masterLayout)

        self.resize(650, 450)
        self.refresh_groups_list()
        self.refresh_all_users_list()
        self.move(QPoint(0, 0))

    def add_group(self):
        print "add group"
        groupName = ""
        groupName = QInputDialog.getText(self, "add group", "group name", QLineEdit.Normal, "")
        if groupName[0] != "":
            SH.add_group(str(groupName[0]))
            self.refresh_groups_list()
            self.refresh_users_list(self.groupListWidget.selectedItems()[0])
            self.addGroup.emit()

    def leave_group(self):
        print "leave group"
        if len(self.groupListWidget.selectedItems()) != 0:
            group = self.groupListWidget.selectedItems()[0].toolTip()
            SH.leave_group(str(group))
            self.refresh_groups_list()
            self.leaveGroup.emit()

    def del_group(self):
        print "del group"
        if len(self.groupListWidget.selectedItems()) != 0:
            group = self.groupListWidget.selectedItems()[0].toolTip()
            SH.del_group(str(group))
            self.refresh_groups_list()
            self.delGroup.emit()

    def add_users(self):
        print "add users"
        addUsers = []
        addGroup = ""
        if len(self.allUsersListWidget.selectedItems()) != 0:
            for user in self.allUsersListWidget.selectedItems():
                addUsers.append(user.text())
        if len(self.groupListWidget.selectedItems()) != 0:
            addGroup = self.groupListWidget.selectedItems()[0].toolTip()
        # print addUsers
        # print addGroup
        if addUsers != [] and addGroup != "":
            SH.add_user_to_group(addUsers, str(addGroup))
            self.refresh_users_list(self.groupListWidget.selectedItems()[0])
            self.addUserToGroup.emit()

    def remove_users(self):
        print "remove users"
        removeUsers = []
        removeGroup = ""
        if len(self.usersListWidget.selectedItems()) != 0:
            for user in self.usersListWidget.selectedItems():
                removeUsers.append(user.text())
        if len(self.groupListWidget.selectedItems()) != 0:
            removeGroup = self.groupListWidget.selectedItems()[0].toolTip()
        # print removeUsers
        # print removeGroup
        if removeUsers != [] and removeGroup != "":
            SH.remove_user_from_group(removeUsers, str(removeGroup))
            self.refresh_users_list(self.groupListWidget.selectedItems()[0])
            self.removeUsersFromGroup.emit()

    def refresh_groups_list(self):
        groups = SH.load_group()
        # print groups
        if len(groups) > 0:
            self.groupListWidget.clear()
            for group in groups:
                # print group
                i = QListWidgetItem(groups[group]["label"])
                i.setToolTip(group)
                # print i.toolTip()
                self.groupListWidget.addItem(i)
            self.groupListWidget.setCurrentRow(0)
            self.refresh_users_list(self.groupListWidget.selectedItems()[0])
        else:
            self.groupListWidget.clear()
            self.usersListWidget.clear()
            self.usersInGroupLabel.setText("in ...")

    def refresh_users_list(self, item):
        # print item.text()
        groupName = item.toolTip()
        self.usersInGroupLabel.setText("in %s" % groupName)
        users = SH.get_users_in_group(groupName)
        users.sort()
        self.usersLabel.setText("%s users" % len(users))
        # print users
        self.usersListWidget.clear()
        for user in users:
            i = QListWidgetItem(user)
            self.usersListWidget.addItem(i)

    def refresh_all_users_list(self):
        # print "refresh all users list"
        searchStr = self.allUsersSearchLineEdit.text()
        allUsersWithMessage = SH.get_all_user(searchStr, "all")
        allUsers = []
        for i in allUsersWithMessage:
            allUsers.append(i[1]["user_name"])
        allUsers.sort()
        # print allUsers
        self.allUsersListWidget.clear()
        for user in allUsers:
            i = QListWidgetItem(user)
            self.allUsersListWidget.addItem(i)
        self.allUsersListWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)


class LogoWidget(QLabel):
    def __init__(self):
        super(LogoWidget, self).__init__()

        self.imageFile = '%s/%s.png' % (Icons_Folder, "logo")
        self.setPixmap(QPixmap(self.imageFile).scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.setAlignment(Qt.AlignCenter)


def openUserFolder():
    import platform
    import subprocess

    operatingSystem = platform.system()

    path = Current_User_Folder

    if os.path.exists(path):

        if operatingSystem == "Windows":
            os.startfile(path)
        elif operatingSystem == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])





if __name__ == '__main__':
    app = QApplication(sys.argv)
    sendNodes = SendNodes()
    sendNodes.open_main_widget()
    app.exec_()

if inNuke:
    sendNodes = SendNodes()
    def showMain():
        sendNodes.open_main_widget()

    def updateNK():
        sendNodes.update_nk_name()

    def make_screenshot():
        sendNodes.make_screenshot()

