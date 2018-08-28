# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 2017/3/7

import os
import sys

inNuke = False

try:
    import nuke
    inNuke = True
except:
    print "not in nuke"

ThisPath = __file__


USERS_Folder = "F:/Temp/pycharm/SendNodes_users"
GLOBAL_Folder = os.path.dirname(ThisPath)









