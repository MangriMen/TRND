import os

from PyQt5 import QtGui
from PyQt5.QtCore import QTranslator
from PyQt5.QtWidgets import QApplication
from qt_material import apply_stylesheet

from libs import consts
from libs import utils
from libs.main_window import MainWindow


class Application(QApplication):
    def __init__(self, argv_, errors):
        super(Application, self).__init__(argv_)
        self.__init_translation()
        self.__init_theme()

        self.window = MainWindow(errors)
        self.window.show()

    def __init_translation(self):
        # Loading standard widget localization
        self.__load_translation(consts.get_resource_path(consts.QT_TRANSLATOR_FILE))

        # Loading custom project localization
        self.__load_translation(consts.get_resource_path(consts.PROJECT_TRANSLATION_FILE))

    def __init_theme(self):
        # Adding custom font
        self.__load_font(consts.get_resource_path(consts.FONT_FILE))
        # Applying custom theme
        self.__load_theme(consts.get_resource_path(consts.THEME_FILE))
        # Apply additional styles on top of a theme
        self.__load_additional_styles(consts.get_resource_path(consts.STYLE_FILE))

    @staticmethod
    def __load_font(path):
        QtGui.QFontDatabase.addApplicationFont(path)

    def __load_theme(self, path):
        apply_stylesheet(self, theme=path)

    def __load_additional_styles(self, path):
        try:
            with open(path) as file:
                self.setStyleSheet(self.styleSheet() + file.read().format(**os.environ))
        except FileNotFoundError:
            utils.get_logger_for_module().error(''.join(['Unable to load additional styles. File not found. Path: ',
                                                         path]))
        except KeyError as err:
            utils.get_logger_for_module().error('Unable to load additional styles')
            utils.get_logger_for_module().exception(err)

    def __load_translation(self, path):
        translator = QTranslator(self)
        if translator.load(path):
            self.installTranslator(translator)
        else:
            utils.get_logger_for_module().error(''.join(['Unable to load translation. File not found. Path: ', path]))
