import os
import logging

from PyQt5 import QtGui
from PyQt5.QtCore import QTranslator
from PyQt5.QtWidgets import QApplication
from qt_material import apply_stylesheet

from libs import consts
from libs.main_window import MainWindow


class Application(QApplication):
    def __init__(self, argv_):
        super(Application, self).__init__(argv_)
        self.init_translation()
        self.init_theme()

        window = MainWindow()
        window.show()

    def init_translation(self):
        # Loading standard widget localization
        self.load_translation(os.path.join(consts.RESOURCE_FOLDER, consts.QT_TRANSLATOR_FILE))

        # Loading custom project localization
        self.load_translation(os.path.join(consts.RESOURCE_FOLDER, consts.PROJECT_TRANSLATION_FILE))

    def init_theme(self):
        # Adding custom font
        QtGui.QFontDatabase.addApplicationFont(os.path.join(consts.RESOURCE_FOLDER, consts.FONT_FILE))

        # Applying custom theme
        apply_stylesheet(self, theme=os.path.join(consts.RESOURCE_FOLDER, consts.THEME_FILE))

        # Apply additional styles on top of a theme
        with open(os.path.join(consts.RESOURCE_FOLDER, consts.STYLE_FILE)) as file:
            self.setStyleSheet(self.styleSheet() + file.read().format(**os.environ))

    def load_translation(self, path):
        translator = QTranslator(self)
        if translator.load(path):
            self.installTranslator(translator)
        else:
            logging.getLogger(consts.PROGRAM_NAME).error(''.join(['Unable to load translation. Path: ', path]))
