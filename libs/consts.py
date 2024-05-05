import os
import platform

GITHUB_LINK_RELEASES = "https://github.com/MangriMen/TRND/releases"
GITHUB_API_LINK_RELEASES = "https://api.github.com/repos/MangriMen/TRND/releases"

PROGRAM_NAME = "TRND"
VERSION = "0.17"

PROGRAM_FOLDER_WIN = "TRND"
PROGRAM_FOLDER_LINUX = ".trnd"
PARENT_FOLDER_ENV_WIN = "APPDATA"
PARENT_FOLDER_ENV_LINUX = "HOME"
LOGS_FOLDER = "logs"

DATA_FILE = "data.json"

LOGS_FILE_STRFTIME = "%Y-%m-%d_%H-%M-%S"
LOGS_FILE_EXTENSION = ".log"

PARTS_DATE_STRFTIME = "%d.%m.%Y %X"
LOGGER_FORMAT_STR = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

RESOURCE_FOLDER = "data"
STYLE_FILE = "additional_style.css"
ICON_FILE = "icon.ico"
MAIN_WINDOW_UI_FILE = "main_window.ui"
QT_TRANSLATOR_FILE = "qtbase_ru.qm"
PROJECT_TRANSLATION_FILE = "TRND.ru.qm"
FONT_FILE = "Roboto-Regular.ttf"
THEME_FILE = "tarkov_theme.xml"

LOGS_MAX_COUNT = 10
UPDATE_TIMEOUT_SECONDS = 60

DATA_WEAPONS_KEY = 'weapons'
DATA_MODS_KEY = 'mods'
DATA_MODS_CONFLICTS_KEY = 'modsConflicts'
DATA_WEAPONS_LAST_UPDATE_KEY = "weaponsLastUpdate"
DATA_MODS_LAST_UPDATE_KEY = "modsLastUpdate"


def get_program_folder_path():
    # Get platform to check Windows or Linux for data folder path
    platform_ = platform.system()

    # Set path for user data folder
    parentFolder = os.environ.get(PARENT_FOLDER_ENV_WIN if (platform_ == 'Windows') else PARENT_FOLDER_ENV_LINUX)
    programFolder = PROGRAM_FOLDER_WIN if (platform_ == 'Windows') else PROGRAM_FOLDER_LINUX
    fullPath = os.path.join(parentFolder, programFolder)

    return fullPath


def get_resource_path(filename):
    return os.path.join(RESOURCE_FOLDER, filename)
