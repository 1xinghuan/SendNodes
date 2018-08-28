# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 2017/3/10

import os
import re
import time
import shutil
import json
import threading
import sendNodes_path as SP
import sendNodes_nuke as SN

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


Users_Folder = SP.USERS_Folder
Current_User = os.path.expanduser('~').replace('\\','/').split("/")[-1]
# Current_User = "test"
Current_User_Folder = "%s/%s" % (Users_Folder, Current_User)
History_Folder = "%s/History" % Current_User_Folder
Pref_Folder = "%s/Pref" % Current_User_Folder
Pref_File = "%s/pref.json" % Pref_Folder
Groups_Pref_File = "%s/groups.json" % Pref_Folder
All_Groups_Folder = "%s/Groups" % Users_Folder
if not os.path.exists(All_Groups_Folder):
    os.makedirs(All_Groups_Folder)
    os.chmod(All_Groups_Folder, 0777)


def read_json(jsonFile):
    with open(jsonFile) as json_file:
        jsonData = json.load(json_file)
    return jsonData


def write_json(data, jsonFile):
    path = os.path.abspath(jsonFile)
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    jsonDic = json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '), encoding="utf-8", ensure_ascii=False)
    with open(jsonFile, 'w') as json_file:
        json_file.write(jsonDic)


def get_all_user(searchStr, type ="all"):
    allUser = []
    for user in os.listdir(Users_Folder):
        if user.find(searchStr) != -1:
            allUser.append(user)
    if "Groups" in allUser:
        allUser.remove("Groups")
    allUser.sort()
    if Current_User in allUser:
        allUser.remove(Current_User)
    # print allUser
    if type == "onlyUsers":
        return allUser
    withMessageUser = []
    for user in os.listdir(History_Folder):
        if user in allUser:
            withMessageUser.append(user)
    if "Groups" in withMessageUser:
        withMessageUser.remove("Groups")
    # print withMessageUser
    allUserWithMessage = []
    for user in withMessageUser:
        if user.find(searchStr) != -1:
            logFilePath = "%s/%s/message/new.txt.json" % (History_Folder, user)
            if os.path.exists(logFilePath):
                f = read_json(logFilePath)

                messageInfo1 = {}
                messageInfo1["time"] = f["TIME"]
                messageInfo1["user_label"] = user
                messageInfo1["note"] = f["MESSAGE"]
                messageInfo1["readed"] = f["READED"]
                messageInfo1["type"] = "user"
                messageInfo1["user_name"] = user

                messageInfo = []
                messageInfo.append(f["TIME"])  # time
                messageInfo.append(messageInfo1)  # dict
                # print messageInfo
                allUserWithMessage.append(messageInfo)
                if user in allUser:
                    allUser.remove(user)
    # print allUser
    allUserWithMessage.sort(reverse=True)
    if type == "withOneMessage":
        return allUserWithMessage[:1]
    if type == "withMessage":
        return allUserWithMessage

    # print allUserWithMessage
    allUserWithoutMessage = []
    for user in allUser:
        # userWithoutMessage = [0, user, "", True, "user", user]
        userWithoutMessage = [0, {"time":0, "user_label":user, "note":"", "readed":True, "type":"user", "user_name":user}]
        allUserWithoutMessage.append(userWithoutMessage)

    allUserWithMessage.extend(allUserWithoutMessage)
    # print allUserWithMessage
    if type == "all":
        return allUserWithMessage


def get_groups(searchStr, type = "all"):
    groupsData = read_json(Groups_Pref_File)
    myGroups = []
    for group in groupsData.keys():
        groupLabel = groupsData[group]["label"]
        if groupLabel.find(searchStr) != -1:
            myGroups.append(group)
    myGroups.sort()
    withMessageGroup = []
    if os.path.exists("%s/Groups" % History_Folder):
        for group in os.listdir("%s/Groups" % History_Folder):
            if group in myGroups:
                withMessageGroup.append(group)
    allGroupWithMessage = []
    for group in withMessageGroup:
        if group.find(searchStr) != -1:
            logFilePath = "%s/Groups/%s/message/new.txt.json" % (History_Folder, group)
            if os.path.exists(logFilePath):
                f = read_json(logFilePath)
                groupLabel = read_json(Groups_Pref_File)[group]["label"]

                messageInfo1 = {}
                messageInfo1["time"] = f["TIME"]
                messageInfo1["user_label"] = groupLabel
                messageInfo1["note"] = f["MESSAGE"]
                messageInfo1["readed"] = f["READED"]
                messageInfo1["type"] = "group"
                messageInfo1["user_name"] = group

                messageInfo = []
                messageInfo.append(f["TIME"])  # time
                messageInfo.append(messageInfo1)  # dict
                # print messageInfo
                allGroupWithMessage.append(messageInfo)
                if group in myGroups:
                    myGroups.remove(group)

    allGroupWithMessage.sort(reverse=True)
    if type == "withOneMessage":
        return allGroupWithMessage[:1]
    if type == "withMessage":
        return allGroupWithMessage

    allGroupWithoutMessage = []
    for group in myGroups:
        groupLabel = read_json(Groups_Pref_File)[group]["label"]
        # groupWithoutMessage = [0, groupLabel, "", True, "group", group]
        groupWithoutMessage = [0, {"time":0, "user_label":groupLabel, "note":"", "readed":True, "type":"group", "user_name":group}]
        allGroupWithoutMessage.append(groupWithoutMessage)

    allGroupWithMessage.extend(allGroupWithoutMessage)
    if type == "all":
        return allGroupWithMessage


def get_users_and_groups(searchStr, type = "all"):
    users_and_groups = []
    allUsers = get_all_user(searchStr, type)
    myGroups = get_groups(searchStr, type)
    users_and_groupsWithMessage = []
    users_and_groupsWithOutMessage = []
    for user in allUsers:
        if user[1]["time"] == 0:
            users_and_groupsWithOutMessage.append(user)
        else:
            users_and_groupsWithMessage.append(user)
    for group in myGroups:
        if group[1]["time"] == 0:
            users_and_groupsWithOutMessage.append(group)
        else:
            users_and_groupsWithMessage.append(group)
    users_and_groupsWithMessage.sort(reverse=True)
    users_and_groupsWithOutMessage.sort(reverse=False)
    users_and_groups.extend(users_and_groupsWithMessage)
    users_and_groups.extend(users_and_groupsWithOutMessage)
    if type == "withOneMessage":
        if len(users_and_groups) > 0:
            return users_and_groups[:1]
        elif len(users_and_groups) == 0:
            return []
    elif type == "all":
        return users_and_groups
    elif type == "withMessage":
        return users_and_groupsWithMessage

# for i in get_users_and_groups("", "withMessage"):
#     print i


def get_users_in_group(group):
    users = []
    try:
        jsonData = read_json("%s/%s.json" % (All_Groups_Folder, group))
        users = jsonData["users"]
    except:
        pass
    return users


# users_and_groups = get_users_and_groups("", "all")
# print users_and_groups


def new_to_readed(name, type ="user"):
    if type == "user":
        logFilePath = "%s/%s/message/new.txt.json" % (History_Folder, name)
    elif type == "group":
        logFilePath = "%s/Groups/%s/message/new.txt.json" % (History_Folder, name)
    if os.path.exists(logFilePath):
        f = read_json(logFilePath)
        # print f
        newF = f
        if f["READED"] == False:
            newF["READED"] = True
        # print newF
        write_json(newF, logFilePath)





def get_safe_list_dir(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
    return os.listdir(folder)

def get_user_messages(user):
    messageList = []
    if os.path.exists("%s/%s" % (History_Folder, user)):
        for i in get_safe_list_dir("%s/%s/message" % (History_Folder, user)):
            if i.split(".")[-2] == "log" and i.split(".")[-1] == "json":
                messageList.append(i.split(".")[0])
        messageList.sort()
        # print messageList
        messageInfoList = []
        for i in messageList:
            messageFilePath = "%s/%s/message/%s.log.json" % (History_Folder, user, i)
            f = read_json(messageFilePath)
            # print f.keys()
            nodeExist = False
            if os.path.exists("%s/%s/message/%s.nk" % (History_Folder, user, i)):
                nodeExist = True
            messageInfo = [i, f["IO"], f["USER"], f["MESSAGE"], f["NODES"], nodeExist]
            # i, IO, USER, MESSAGE, NODES, nodeExist
            messageInfoList.append(messageInfo)
        # print messageInfoList
        return messageInfoList
    else:
        return []


def get_group_messages(group):
    messageList = []
    if os.path.exists("%s/Groups/%s/message" % (History_Folder, group)):
        for i in os.listdir("%s/Groups/%s/message" % (History_Folder, group)):
            if i.split(".")[-2] == "log" and i.split(".")[-1] == "json":
                messageList.append(i.split(".")[0])
        messageList.sort()
        # print messageList
        messageInfoList = []
        for i in messageList:
            messageFilePath = "%s/Groups/%s/message/%s.log.json" % (History_Folder, group, i)
            f = read_json(messageFilePath)
            # print f.keys()
            nodeExist = False
            if os.path.exists("%s/Groups/%s/message/%s.nk" % (History_Folder, group, i)):
                nodeExist = True
            messageInfo = [i, f["IO"], f["USER"], f["MESSAGE"], f["NODES"], nodeExist]
            # i, IO, USER, MESSAGE, NODES, nodeExist
            messageInfoList.append(messageInfo)
        # print messageInfoList
        return messageInfoList
    else:
        return []


# messageInfoList = get_group_messages("group1503835494")
# print messageInfoList


def send_user_message(user, message):

    if is_emoji(message):
        info = get_info_from_html(message)
        if info["imgPath"].find(Users_Folder) != -1:
            copy_custom_emoji_to_user(info["imgPath"], Current_User, user)
        newMessage1 = message
        newMessage2 = convert_custom_emoji_url_to_user(message, user)
    else:
        temp = convert_screenshot_url_to_self(message, user)
        screenShotId = temp[0]
        newMessage1 = temp[1]
        newMessage2 = convert_screenshot_url_to_user(message, user)[1]
        copy_tmp_screenshot_to_self(screenShotId, Current_User, user)
        copy_tmp_screenshot_to_user(screenShotId, Current_User, user)

    nodeTime = int(time.time())

    userFolder = "%s/%s/message" % (History_Folder, user)
    if not os.path.exists(userFolder):
        os.makedirs(userFolder)
        os.chmod(userFolder, 0777)
    nkFilePath = "%s/%s/message/%s.nk" % (History_Folder, user, nodeTime)
    nodesStr = SN.send_nk(nkFilePath)
    SN.clear_selection()
    newMessageFilePath = "%s/%s/message/new.txt.json" % (History_Folder, user)
    f = {}
    f["READED"] = True
    f["TIME"] = nodeTime
    f["MESSAGE"] = newMessage1
    write_json(f, newMessageFilePath)
    # os.chmod(newMessageFilePath, 0777)
    messageFilePath = "%s/%s/message/%s.log.json" % (History_Folder, user, nodeTime)
    f = {}
    f["IO"] = "out"
    f["USER"] = Current_User
    f["MESSAGE"] = newMessage1
    f["NODES"] = nodesStr
    write_json(f, messageFilePath)

    sendUserThread = SendUserThread(user, newMessage2, nodeTime, nodesStr, nkFilePath)
    sendUserThread.start()


class SendUserThread(threading.Thread):
    def __init__(self, user, newMessage2, nodeTime, nodesStr, fromFile):
        super(SendUserThread, self).__init__()

        self.user = user
        self.newMessage2 = newMessage2
        self.nodeTime = nodeTime
        self.nodesStr = nodesStr
        self.fromFile = fromFile

    def run(self):
        userFolder = "%s/%s/History/%s/message" % (Users_Folder, self.user, Current_User)
        if not os.path.exists(userFolder):
            os.makedirs(userFolder)
            os.chmod(userFolder, 0777)
        nkFilePath = "%s/%s/History/%s/message/%s.nk" % (Users_Folder, self.user, Current_User, self.nodeTime)
        if os.path.exists(self.fromFile):
            shutil.copyfile(self.fromFile, nkFilePath)
        # nodesStr = SN.send_nk(nkFilePath)
        newMessageFilePath = "%s/%s/History/%s/message/new.txt.json" % (Users_Folder, self.user, Current_User)
        f = {}
        f["READED"] = False
        f["TIME"] = self.nodeTime
        f["MESSAGE"] = self.newMessage2
        write_json(f, newMessageFilePath)
        # os.chmod(newMessageFilePath, 0777)
        messageFilePath = "%s/%s/History/%s/message/%s.log.json" % (Users_Folder, self.user, Current_User, self.nodeTime)
        f = {}
        f["IO"] = "in"
        f["USER"] = Current_User
        f["MESSAGE"] = self.newMessage2
        f["NODES"] = self.nodesStr
        write_json(f, messageFilePath)


def send_group_message(group, message):
    info = {}
    screenShotId = []
    if is_emoji(message):
        info = get_info_from_html(message)
        newMessage1 = message
    else:
        temp = convert_screenshot_url_to_self(message, "", userType="group", group=group)
        screenShotId = temp[0]
        newMessage1 = temp[1]
        copy_tmp_screenshot_to_self(screenShotId, Current_User, "", userType="group", group=group)

    nodeTime = int(time.time())

    groupFolder = "%s/Groups/%s/message" % (History_Folder, group)
    if not os.path.exists(groupFolder):
        os.makedirs(groupFolder)
        os.chmod(groupFolder, 0777)
    nkFilePath = "%s/Groups/%s/message/%s.nk" % (History_Folder, group, nodeTime)
    nodesStr = SN.send_nk(nkFilePath)
    SN.clear_selection()
    newMessageFilePath = "%s/Groups/%s/message/new.txt.json" % (History_Folder, group)
    f = {}
    f["READED"] = True
    f["TIME"] = nodeTime
    f["MESSAGE"] = newMessage1
    write_json(f, newMessageFilePath)
    # os.chmod(newMessageFilePath, 0777)
    messageFilePath = "%s/Groups/%s/message/%s.log.json" % (History_Folder, group, nodeTime)
    f = {}
    f["IO"] = "out"
    f["USER"] = Current_User
    f["MESSAGE"] = newMessage1
    f["NODES"] = nodesStr
    write_json(f, messageFilePath)

    users = get_users_in_group(group)
    users.remove(Current_User)
    sendGroupThread = SendGroupThread1(group, users, message, info, screenShotId, nodeTime, nodesStr, nkFilePath)
    sendGroupThread.start()

    # SN.clear_selection()


class SendGroupThread(threading.Thread):
    def __init__(self, group, user, message, info, screenShotId):
        super(SendGroupThread, self).__init__()

        self.group = group
        self.user = user
        self.message = message
        self.info = info
        self.screenShotId = screenShotId

    def run(self):
        nodeTime = int(time.time())
        if is_emoji(self.message):
            if self.info["imgPath"].find(Users_Folder) != -1:
                copy_custom_emoji_to_user(self.info["imgPath"], Current_User, self.user, userType="group", group=self.group)
            newMessage2 = convert_custom_emoji_url_to_user(self.message, self.user, userType="group", group=self.group)
        else:
            newMessage2 = convert_screenshot_url_to_user(self.message, self.user, userType="group", group=self.group)[1]
            copy_tmp_screenshot_to_user(self.screenShotId, Current_User, self.user, userType="group", group=self.group)

        userFolder = "%s/%s/History/Groups/%s/message" % (Users_Folder, self.user, self.group)
        if not os.path.exists(userFolder):
            os.makedirs(userFolder)
            os.chmod(userFolder, 0777)
        nkFilePath = "%s/%s/History/Groups/%s/message/%s.nk" % (Users_Folder, self.user, self.group, nodeTime)
        nodesStr = SN.send_nk(nkFilePath)

        newMessageFilePath = "%s/%s/History/Groups/%s/message/new.txt.json" % (Users_Folder, self.user, self.group)
        f = {}
        f["READED"] = False
        f["TIME"] = nodeTime
        f["MESSAGE"] = newMessage2
        write_json(f, newMessageFilePath)
        # os.chmod(newMessageFilePath, 0777)
        messageFilePath = "%s/%s/History/Groups/%s/message/%s.log.json" % (Users_Folder, self.user, self.group, nodeTime)
        f = {}
        f["IO"] = "in"
        f["USER"] = Current_User
        f["MESSAGE"] = newMessage2
        f["NODES"] = nodesStr
        write_json(f, messageFilePath)



class SendGroupThread1(threading.Thread):
    def __init__(self, group, users, message, info, screenShotId, nodeTime, nodesStr, fromFile):
        super(SendGroupThread1, self).__init__()

        self.group = group
        self.users = users
        self.message = message
        self.info = info
        self.screenShotId = screenShotId
        self.nodeTime = nodeTime
        self.nodesStr = nodesStr
        self.fromFile = fromFile

    def run(self):
        for user in self.users:
            if is_emoji(self.message):
                if self.info["imgPath"].find(Users_Folder) != -1:
                    copy_custom_emoji_to_user(self.info["imgPath"], Current_User, user, userType="group", group=self.group)
                newMessage2 = convert_custom_emoji_url_to_user(self.message, user, userType="group", group=self.group)
            else:
                newMessage2 = convert_screenshot_url_to_user(self.message, user, userType="group", group=self.group)[1]
                copy_tmp_screenshot_to_user(self.screenShotId, Current_User, user, userType="group", group=self.group)

            userFolder = "%s/%s/History/Groups/%s/message" % (Users_Folder, user, self.group)
            if not os.path.exists(userFolder):
                os.makedirs(userFolder)
                os.chmod(userFolder, 0777)
            nkFilePath = "%s/%s/History/Groups/%s/message/%s.nk" % (Users_Folder, user, self.group, self.nodeTime)
            if os.path.exists(self.fromFile):
                shutil.copyfile(self.fromFile, nkFilePath)
            # nodesStr = SN.send_nk(nkFilePath)

            newMessageFilePath = "%s/%s/History/Groups/%s/message/new.txt.json" % (Users_Folder, user, self.group)
            f = {}
            f["READED"] = False
            f["TIME"] = self.nodeTime
            f["MESSAGE"] = newMessage2
            write_json(f, newMessageFilePath)
            # os.chmod(newMessageFilePath, 0777)
            messageFilePath = "%s/%s/History/Groups/%s/message/%s.log.json" % (Users_Folder, user, self.group, self.nodeTime)
            f = {}
            f["IO"] = "in"
            f["USER"] = Current_User
            f["MESSAGE"] = newMessage2
            f["NODES"] = self.nodesStr
            write_json(f, messageFilePath)

        # SN.clear_selection()






def is_emoji(message):
    if message.find("<img src=") == 0:
        return True
    else:
        return False


def get_info_from_html(message, index="one"):
    srcFilter = re.compile('src="(.*?)"')
    widthFilter = re.compile('width="(.*?)"')
    heightFilter = re.compile('height="(.*?)"')
    if index == "one":
        imgPath = srcFilter.findall(message)[0]
        imgWidth = int(float(widthFilter.findall(message)[0]))
        imgHeight = int(float(heightFilter.findall(message)[0]))
    if index == "all":
        imgPath = srcFilter.findall(message)
        imgWidth = widthFilter.findall(message)
        imgHeight = heightFilter.findall(message)
    info = {}
    info["imgPath"] = imgPath
    info["imgWidth"] = imgWidth
    info["imgHeight"] = imgHeight
    return info


def convert_screenshot_url_to_self(message, toWhom, userType="user", group=""):
    matchStr = "%s/tmp/screenshot_" % Current_User_Folder
    urlIndex = message.find(matchStr)
    if urlIndex != -1:
        imgUrl = get_info_from_html(message, index="all")["imgPath"]
        # print "found screenshot img", imgUrl
        if userType == "user":
            newMessage1 = message.replace(matchStr, "%s/%s/img/screenshot_" % (History_Folder, toWhom))
        if userType == "group":
            newMessage1 = message.replace(matchStr, "%s/Groups/%s/img/screenshot_" % (History_Folder, group))
        return [imgUrl, newMessage1]
    else:
        return [[], message]


def convert_screenshot_url_to_user(message, toWhom, userType="user", group=""):
    matchStr = "%s/tmp/screenshot_" % Current_User_Folder
    urlIndex = message.find(matchStr)
    if urlIndex != -1:
        imgUrl = get_info_from_html(message, index="all")["imgPath"]
        # print "found screenshot img", imgUrl
        if userType == "user":
            newMessage2 = message.replace(matchStr, "%s/%s/History/%s/img/screenshot_" % (Users_Folder, toWhom, Current_User))
        if userType == "group":
            newMessage2 = message.replace(matchStr, "%s/%s/History/Groups/%s/img/screenshot_" % (Users_Folder, toWhom, group))
        return [imgUrl, newMessage2]
    else:
        return [[], message]


def copy_tmp_screenshot_to_self(imgPathList, fromWhom, toWhom, userType="user", group=""):
    for i in range(len(imgPathList)):
        file = imgPathList[i]
        imgId = os.path.basename(file)
        if userType == "user":
            copyFile1 = "%s/%s/History/%s/img/%s" % (Users_Folder, fromWhom, toWhom, imgId)
        if userType == "group":
            copyFile1 = "%s/%s/History/Groups/%s/img/%s" % (Users_Folder, fromWhom, group, imgId)
        if os.path.exists(file):
            if not os.path.exists(os.path.dirname(copyFile1)):
                os.makedirs(os.path.dirname(copyFile1))
            shutil.copyfile(file, copyFile1)
        # print file
        # print copyFile1


def copy_tmp_screenshot_to_user(imgPathList, fromWhom, toWhom, userType="user", group=""):
    for i in range(len(imgPathList)):
        file = imgPathList[i]
        imgId = os.path.basename(file)
        if userType == "user":
            copyFile2 = "%s/%s/History/%s/img/%s" % (Users_Folder, toWhom, fromWhom, imgId)
        if userType == "group":
            copyFile2 = "%s/%s/History/Groups/%s/img/%s" % (Users_Folder, toWhom, group, imgId)
        if os.path.exists(file):
            if not os.path.exists(os.path.dirname(copyFile2)):
                os.makedirs(os.path.dirname(copyFile2))
            shutil.copyfile(file, copyFile2)
        # print file
        # print copyFile2


# copy_tmp_screenshot("screenshot_1506177862", "john", "aaa")

# text = '<img src="F:\\Temp\\pycharm\\SendNodes test v1.4/Users/john/tmp/screenshot_test.png" width="20" height="20"><img src="F:\\Temp\\pycharm\\SendNodes test v1.4/Users/john/tmp/screenshot_test1.png" width="40" height="20">'
# print convert_screenshot_url_to_self(text, "aaa")
# copy_tmp_screenshot_to_self(convert_screenshot_url_to_self(text, "aaa")[0], "john", "aaa")


def copy_custom_emoji_to_user(emojiPath, fromWhom, toWhom, userType="user", group=""):
    emojiFile = os.path.basename(emojiPath)
    if userType == "user":
        copyFile2 = "%s/%s/History/%s/img/%s" % (Users_Folder, toWhom, fromWhom, emojiFile)
    if userType == "group":
        copyFile2 = "%s/%s/History/Groups/%s/img/%s" % (Users_Folder, toWhom, group, emojiFile)
    if os.path.exists(emojiPath):
        if not os.path.exists(os.path.dirname(copyFile2)):
            os.makedirs(os.path.dirname(copyFile2))
        shutil.copyfile(emojiPath, copyFile2)
    # print emojiPath
    # print copyFile2


def convert_custom_emoji_url_to_user(message, toWhom, userType="user", group=""):
    matchStr = "%s/emoji" % Current_User_Folder
    urlIndex = message.find(matchStr)
    if urlIndex != -1:
        if userType == "user":
            newMessage2 = message.replace(matchStr, "%s/%s/History/%s/img" % (Users_Folder, toWhom, Current_User))
        if userType == "group":
            newMessage2 = message.replace(matchStr, "%s/%s/History/Groups/%s/img" % (Users_Folder, toWhom, group))
        return newMessage2
    else:
        return message


def paste_user_nodes(user, nodeTime):
    nkFilePath = "%s/%s/message/%s.nk" % (History_Folder, user, nodeTime)
    print "paste_user_nodes", nkFilePath
    SN.paste_nk(nkFilePath)

def paste_group_nodes(group, nodeTime):
    nkFilePath = "%s/Groups/%s/message/%s.nk" % (History_Folder, group, nodeTime)
    print "paste_group_nodes", nkFilePath
    SN.paste_nk(nkFilePath)


def create_default_pref():
    defaultPref = {}
    defaultPref["showTipDefault"] = True
    defaultPref["hideWindowWhenShotScreen"] = True
    write_json(defaultPref, Pref_File)


def load_pref():
    prefData = read_json(Pref_File)
    return prefData


def change_pref(prefData):
    write_json(prefData, Pref_File)


def create_default_groups_pref():
    defaultGroupsPref = {}
    write_json(defaultGroupsPref, Groups_Pref_File)


def load_group():
    if not os.path.exists(Groups_Pref_File):
        create_default_groups_pref()
    groups = read_json(Groups_Pref_File)
    # print groups
    return groups


def add_group(groupLabel):
    lastGroupInfo = read_json(Groups_Pref_File)
    groupInfo = lastGroupInfo
    groupId = "%s" % int(time.time())
    newGroupInfo = {}
    newGroupInfo["group%s" % groupId] = {}
    newGroupInfo["group%s" % groupId]["id"] = groupId
    newGroupInfo["group%s" % groupId]["label"] = groupLabel
    groupInfo.update(newGroupInfo)
    # print groupInfo
    write_json(groupInfo, Groups_Pref_File)


    groupContainInfo = {}
    groupContainInfo["id"] = groupId
    groupContainInfo["label"] = groupLabel
    groupContainInfo["users"] = ["%s" % Current_User]
    groupJsonFile = "%s/group%s.json" % (All_Groups_Folder, groupId)
    write_json(groupContainInfo, groupJsonFile)


def leave_group(group):
    lastGroupInfo = read_json(Groups_Pref_File)
    groupInfo = lastGroupInfo
    groupInfo.pop(group)
    # print groupInfo
    write_json(groupInfo, Groups_Pref_File)

    if os.path.exists("%s/Groups/%s" % (History_Folder, group)):
        shutil.rmtree("%s/Groups/%s" % (History_Folder, group))

    groupContainInfo = read_json("%s/%s.json" % (All_Groups_Folder, group))
    if Current_User in groupContainInfo["users"]:
        groupContainInfo["users"].remove(Current_User)
    write_json(groupContainInfo, "%s/%s.json" % (All_Groups_Folder, group))


def del_group(group):
    for user in get_users_in_group(group):
        # print user
        groupsPrefFile = "%s/%s/Pref/groups.json" % (Users_Folder, user)
        lastGroupInfo = read_json(groupsPrefFile)
        groupInfo = lastGroupInfo
        # print groupInfo
        if group in groupInfo.keys():
            groupInfo.pop(group)
            # print groupInfo

        write_json(groupInfo, groupsPrefFile)

        if os.path.exists("%s/%s/History/Groups/%s" % (Users_Folder, user, group)):
            shutil.rmtree("%s/%s/History/Groups/%s" % (Users_Folder, user, group))


    groupJsonFile = "%s/%s.json" % (All_Groups_Folder, group)
    if os.path.exists(groupJsonFile):
        os.remove(groupJsonFile)


def add_user_to_group(users, group):
    groupContainInfo = read_json("%s/%s.json" % (All_Groups_Folder, group))
    for user in users:
        user = str(user)
        if user not in groupContainInfo["users"]:
            groupContainInfo["users"].append(user)

            newGroupInfo = {}
            newGroupInfo[group] = {}
            newGroupInfo[group]["id"] = groupContainInfo["id"]
            newGroupInfo[group]["label"] = groupContainInfo["label"]
            userGroupPrefFile = "%s/%s/Pref/groups.json" % (Users_Folder, user)

            if not os.path.exists(userGroupPrefFile):
                write_json(newGroupInfo, userGroupPrefFile)
            else:
                lastGroupInfo = read_json(userGroupPrefFile)
                groupInfo = lastGroupInfo
                groupInfo.update(newGroupInfo)
                write_json(groupInfo, userGroupPrefFile)

    write_json(groupContainInfo, "%s/%s.json" % (All_Groups_Folder, group))


def remove_user_from_group(users, group):
    groupContainInfo = read_json("%s/%s.json" % (All_Groups_Folder, group))
    for user in users:
        if user != Current_User:
            if user in groupContainInfo["users"]:
                groupContainInfo["users"].remove(user)

                userGroupPrefFile = "%s/%s/Pref/groups.json" % (Users_Folder, user)
                if os.path.exists(userGroupPrefFile):
                    groupInfo = read_json(userGroupPrefFile)
                    if group in groupInfo.keys():
                        groupInfo.pop(group)
                        # print groupInfo

                    write_json(groupInfo, userGroupPrefFile)

                if os.path.exists("%s/%s/History/Groups/%s" % (Users_Folder, user, group)):
                    shutil.rmtree("%s/%s/History/Groups/%s" % (Users_Folder, user, group))


    write_json(groupContainInfo, "%s/%s.json" % (All_Groups_Folder, group))




# sendMessage("aaaa", "testtest")

# getMessages("ccc")




# clear_history()
# new_to_readed("ddd")
# get_all_user("")


# nodeTime = int(time.time())
# print nodeTime
# print time.strftime("%m-%d %H:%M:%S", time.localtime(nodeTime))


