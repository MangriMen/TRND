import os
import platform
import sys

from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication
from qt_material import apply_stylesheet

from libs.window import MyWindow


def init_environ():
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        os.chdir(sys._MEIPASS)

    # Adding path to internal json
    if platform.system() == 'Windows':
        os.environ['DATAFOLDER'] = os.environ.get('APPDATA') + '\\TRND\\'
        os.environ['DATAFILE'] = os.environ.get('APPDATA') + '\\TRND\\data.json'
    else:
        os.environ['DATAFOLDER'] = os.environ.get('HOME') + '/.trnd/'
        os.environ['DATAFILE'] = os.environ.get('HOME') + '/.trnd/data.json'

    if not os.path.exists(os.environ.get('DATAFOLDER')):
        os.makedirs(os.environ.get('DATAFOLDER'))

    os.environ['VERSION_NOW'] = '0.13'


def suppress_qt_warnings():
    os.environ["QT_DEVICE_PIXEL_RATIO"] = "0"
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    os.environ["QT_SCREEN_SCALE_FACTORS"] = "1"
    os.environ["QT_SCALE_FACTOR"] = "1"


def apply_theme(app):
    QtGui.QFontDatabase.addApplicationFont("data/Roboto-Regular.ttf")
    apply_stylesheet(app, theme="data/tarkov_theme.xml")
    with open('data/additional_style.css') as file:
        app.setStyleSheet(app.styleSheet() + file.read().format(**os.environ))


def main():
    suppress_qt_warnings()
    init_environ()

    app = QApplication(sys.argv)
    apply_theme(app)

    window = MyWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
