import datetime
import os
import platform
import sys
import logging
from pathlib import Path

from libs import consts
from libs import utils
from libs.qt_extends import QtTweaks
from libs.application import Application


class TRND:
    def __init__(self):
        QtTweaks.suppress_warnings()
        self.__init_logger_basic()
        self.__init_environ()
        self.errors = []
        self.errors += self.__init_folders()
        self.errors += self.__init_logger()

        self.app = Application(sys.argv, self.errors)

        utils.get_logger_for_module().info("Initialization done")

    def run(self):
        sys.exit(self.app.exec_())

    @staticmethod
    def __init_logger_basic():
        logging.basicConfig(
            format=consts.LOGGER_FORMAT_STR,
            level=logging.INFO,
        )

    @staticmethod
    def __init_logger():
        logsFolder = os.path.abspath(os.environ.get('LOGS_FOLDER_PATH'))
        fileName = ''.join([datetime.datetime.now().strftime(consts.LOGS_FILE_STRFTIME), consts.LOGS_FILE_EXTENSION])
        filePath = os.path.join(logsFolder, fileName)

        try:
            if len((fileList := os.listdir(logsFolder))) > consts.LOGS_MAX_COUNT:
                os.remove(os.path.join(logsFolder, fileList[0]))

            handler = logging.FileHandler(filePath, encoding='utf-8')
        except FileNotFoundError as err:
            utils.get_logger_for_module().exception(err)
            return [err]
        else:
            logger = logging.getLogger(consts.PROGRAM_NAME)
            formatter = logging.Formatter(consts.LOGGER_FORMAT_STR)
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            return []

    @staticmethod
    def __init_environ():
        # Change dir to sys._MEIPASS if run from frozen executable
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            os.chdir(sys._MEIPASS)

        os.environ['DATA_FOLDER_PATH'] = consts.get_program_folder_path()
        os.environ['DATA_FILE_PATH'] = os.path.join(os.environ.get('DATA_FOLDER_PATH'), consts.DATA_FILE)
        os.environ['LOGS_FOLDER_PATH'] = os.path.join(os.environ.get('DATA_FOLDER_PATH'), consts.LOGS_FOLDER)

    @staticmethod
    def __init_folders():
        errors = []

        try:
            Path(os.environ.get('DATA_FOLDER_PATH')).mkdir(parents=True, exist_ok=True)
        except PermissionError as err:
            utils.get_logger_for_module().exception(err)
            errors.append(err)

        try:
            Path(os.environ.get('LOGS_FOLDER_PATH')).mkdir(parents=True, exist_ok=True)
        except PermissionError as err:
            utils.get_logger_for_module().exception(err)
            errors.append(err)

        return errors
