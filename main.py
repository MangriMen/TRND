import os
import platform
import sys

from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication
from qt_material import apply_stylesheet

from window import MyWindow

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    os.chdir(sys._MEIPASS)


# Adding path to internal json
def init_environ():
    if platform.system() == 'Windows':
        os.environ['DATAFOLDER'] = os.environ.get('APPDATA') + '\\TRND\\'
        os.environ['DATAFILE'] = os.environ.get('APPDATA') + '\\TRND\\data.json'
    else:
        os.environ['DATAFOLDER'] = os.environ.get('USERPROFILE') + '\\.trnd\\'
        os.environ['DATAFILE'] = os.environ.get('USERPROFILE') + '\\.trnd\\data.json'
    if not os.path.exists(os.environ.get('DATAFOLDER')):
        os.makedirs(os.environ.get('DATAFOLDER'))
    os.environ['VERSION_NOW'] = '0.11'


def suppress_qt_warnings():
    os.environ["QT_DEVICE_PIXEL_RATIO"] = "0"
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    os.environ["QT_SCREEN_SCALE_FACTORS"] = "1"
    os.environ["QT_SCALE_FACTOR"] = "1"


def main():
    # init
    suppress_qt_warnings()
    init_environ()
    app = QApplication(sys.argv)

    QtGui.QFontDatabase.addApplicationFont("Roboto-Regular.ttf")  # add font
    apply_stylesheet(app, theme="tarkov_theme.xml")  # apply theme

    #  apply additional style
    with open('additional_style.css') as file:
        app.setStyleSheet(app.styleSheet() + file.read().format(**os.environ))

    # create windows
    window = MyWindow()
    window.show()

    # exit
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
