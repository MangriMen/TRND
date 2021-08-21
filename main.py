import datetime
import os
import platform
import sys
import logging
from pathlib import Path

from libs import consts
from libs import utils
from libs.application import Application


def suppress_qt_warnings():
    os.environ["QT_DEVICE_PIXEL_RATIO"] = "0"
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    os.environ["QT_SCREEN_SCALE_FACTORS"] = "1"
    os.environ["QT_SCALE_FACTOR"] = "1"


def init_environ():
    # Change dir to sys._MEIPASS if run from frozen executable
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        os.chdir(sys._MEIPASS)

    # Set path for user data folder
    if platform.system() == 'Windows':
        os.environ['DATA_FOLDER_PATH'] = os.path.join(os.environ.get(consts.PARENT_FOLDER_ENV_WIN),
                                                      consts.PROGRAM_FOLDER_WIN)
    else:
        os.environ['DATA_FOLDER_PATH'] = os.path.join(os.environ.get(consts.PARENT_FOLDER_ENV_LINUX),
                                                      consts.PROGRAM_FOLDER_LINUX)

    os.environ['DATA_FILE_PATH'] = os.path.join(os.environ.get('DATA_FOLDER_PATH'), consts.DATA_FILE)
    os.environ['LOGS_FOLDER_PATH'] = os.path.join(os.environ.get('DATA_FOLDER_PATH'), consts.LOGS_FOLDER)

    Path(os.environ.get('DATA_FOLDER_PATH')).mkdir(parents=True, exist_ok=True)


def init_logger():
    logger = logging.getLogger(consts.PROGRAM_NAME)
    logger.setLevel(logging.INFO)

    logsPath = os.path.abspath(os.environ.get('LOGS_FOLDER_PATH'))
    filename = datetime.datetime.now().strftime(consts.LOGS_FILE_STRFTIME) + consts.LOGS_FILE_EXTENSION
    fullPath = os.path.join(logsPath, filename)

    try:
        Path(logsPath).mkdir(parents=True, exist_ok=True)

        if len(os.listdir(logsPath)) > consts.LOGS_MAX_COUNT:
            utils.clear_dir(logsPath)

        fileHandler = logging.FileHandler(fullPath)
    except WindowsError:
        pass
    else:
        formatter_ = logging.Formatter(consts.LOGGER_FORMAT_STR)
        fileHandler.setFormatter(formatter_)

        logger.addHandler(fileHandler)
        logger.info('Program started')


def main():
    suppress_qt_warnings()
    init_environ()
    init_logger()

    app = Application(sys.argv)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
