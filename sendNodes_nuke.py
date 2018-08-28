# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 2017/3/11

import os
import traceback
import sendNodes_path as SP

inNuke = SP.inNuke

try:
    import nuke
except ImportError:
    pass


def paste_nk(path):
    if inNuke:
        try:
            nuke.nodePaste(path)
        except:
            print "paste node failed"


def send_nk(path):
    nodesName = []
    nodesStr = ""
    if inNuke:
        if nuke.selectedNodes() != []:
            try:
                if not os.path.exists(os.path.dirname(path)):
                    os.makedirs(os.path.dirname(path))
                for n in nuke.selectedNodes():
                    nodesName.append(n.knob("name").value())
                if nodesName != []:
                    temp = " ".join(nodesName)
                    nodesStr = "%s..." % temp[:30]
                nuke.nodeCopy(path)
            except:
                f = open("%s/%s/traceback_log.txt" % (SP.USERS_Folder, os.path.expanduser('~').replace('\\','/').split("/")[-1]), 'a')
                traceback.print_exc(file=f)
                f.flush()
                f.close()
                print "send node failed"
    return nodesStr


def clear_selection():
    try:
        for n in nuke.selectedNodes():
            n.setSelected(False)
    except:
        pass


def get_nk_name():
    nkName = ""
    if inNuke:
        try:
            filePath = nuke.root().knob("name").value()
            if filePath == "":
                nkName = "Untitled"
            else:
                nkName = filePath.split("/")[-1]
        except:
            print "get nk name failed"
    return nkName

