import datetime
import os
import platform
import sys
import logging
from pathlib import Path

from PyQt5 import QtGui
from PyQt5.QtCore import QTranslator
from PyQt5.QtWidgets import QApplication
from qt_material import apply_stylesheet

from libs.main_window import MainWindow


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

    os.environ['VERSION_NOW'] = '0.16'


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


def init_logger():
    if getattr(sys, 'frozen', False):
        programDir = os.path.dirname(sys.executable)
    else:
        programDir = os.path.dirname(os.path.abspath(__file__))
    logger = logging.getLogger('TRND')
    logger.setLevel(logging.INFO)

    formatter_ = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logsPath = os.path.abspath(programDir + '/logs/')
    filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.log'
    fullPath = os.path.join(logsPath, filename)

    Path(logsPath).mkdir(parents=True, exist_ok=True)

    filesCount = len(os.listdir(logsPath))

    def clear_dir(directory):
        directory = Path(directory)
        for item in directory.iterdir():
            if item.is_dir():
                clear_dir(item)
            else:
                item.unlink()

    if filesCount > 10:
        clear_dir(logsPath)

    try:
        fileHandler = logging.FileHandler(fullPath)
    except PermissionError:
        pass
    else:
        fileHandler.setFormatter(formatter_)

        logger.addHandler(fileHandler)
        logger.info('Program started')


def main():
    suppress_qt_warnings()
    init_environ()
    init_logger()

    app = QApplication(sys.argv)

    translator = QTranslator(app)
    translator.load("data/qtbase_ru.qm")

    app.installTranslator(translator)
    apply_theme(app)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
