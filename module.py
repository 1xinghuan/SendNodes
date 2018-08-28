

try:
    from BQt.QtGui import *
    from BQt.QtWidgets import *
    from BQt.QtCore import *
    Signal = pyqtSignal
except ImportError:
    try:  # nuke10
        from PySide.QtGui import *
        from PySide.QtCore import *
    except ImportError:
        try:  # pycharm
            from PyQt4.QtGui import *
            from PyQt4.QtCore import *
            Signal = pyqtSignal
        except ImportError:
            try:  # nuke11
                from PySide2.QtGui import *
                from PySide2.QtCore import *
                from PySide2.QtWidgets import *
            except ImportError:
                pass




