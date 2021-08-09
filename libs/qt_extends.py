import typing

from PyQt5.Qt import QStandardItemModel, QStandardItem, QObject, QMessageBox
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread
from PyQt5.QtGui import QFont, QColor, QPixmap, QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication

from libs import utils


class StandardItem(QStandardItem):
    def __init__(self, text='', fontSize=12, isBold=False, color=QColor(0, 0, 0)):
        super(StandardItem, self).__init__()

        font_ = QFont('Roboto', fontSize)
        font_.setBold(isBold)

        self.setEditable(False)
        self.setForeground(color)
        self.setFont(font_)
        self.setText(text)
        self.setToolTip(text)


class JsonModel(QStandardItemModel):
    def __init__(self):
        super(JsonModel, self).__init__()

        self.root = self.invisibleRootItem()

    def __fillFromJson(self, row, json_):
        if json_ is None:
            return

        if isinstance(json_, dict):
            for key, val in sorted(json_.items()):
                newItem = StandardItem(key)
                row.appendRow(newItem)
                self.__fillFromJson(newItem, val)
        elif isinstance(json_, (list, tuple)):
            for val in json_:
                text = (str(val) if not isinstance(val, (dict, list, tuple))
                        else '[%s]' % type(val).__name__)
                row.appendRow(StandardItem(text))
        else:
            row.appendRow(StandardItem(str(json_)))

    def fillModel(self, json_):
        self.clearModel()
        try:
            self.__fillFromJson(self.root, json_)
        except KeyError:
            pass

    def clearModel(self):
        self.clear()
        self.root = self.invisibleRootItem()

    @staticmethod
    def copyItemWithChildren(row, item):
        for i in range(item.rowCount()):
            newItem = item.child(i, 0).clone()
            row.appendRow(newItem)
            JsonModel.copyItemWithChildren(newItem, item.child(i, 0))

    @staticmethod
    def modelToText(item, indent=''):
        text = ''
        for i in range(item.rowCount()):
            text += indent + item.child(i, 0).text() + '\n'
            text += JsonModel.modelToText(item.child(i, 0), indent + '    ')
        return text

    @staticmethod
    def modelToJson(item, json_, key_):
        if item.hasChildren():
            isDict = False
            for i in range(item.rowCount()):
                if item.child(i, 0).hasChildren():
                    isDict = True
                    break
            json_[key_] = dict() if isDict else list()
            for i in range(item.rowCount()):
                JsonModel.modelToJson(item.child(i, 0), json_[key_], item.child(i, 0).text())
        else:
            json_.append(item.text())


class ThreadController:
    def __init__(self, function_, **kwargs):
        self.thread = QThread()
        self.worker = ThreadWorker(function_, **kwargs)

        self.isRunning = False

        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.finished.connect(self.__stopThread)

    def start(self):
        self.isRunning = True
        self.thread.start()

    def stop(self):
        self.worker.stop()

    def terminate(self):
        self.isRunning = False
        self.thread.terminate()

    def __stopThread(self):
        self.isRunning = False
        self.thread.quit()
        self.thread.wait()


class ThreadWorker(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str, str, str)

    def __init__(self, function_, **kwargs):
        super(ThreadWorker, self).__init__()
        self.isRunning = False
        self.function_ = function_
        self.args = kwargs
        self.error.connect(self.stop)
        self.error.connect(showDetailedError)

    def run(self):
        utils.thread_print('worker.run')
        self.isRunning = True
        self.function_(self, self.args)
        self.finished.emit()

    def stop(self):
        self.isRunning = False
        self.finished.emit()

    def addSignal(self, name, *args):
        self.__class__ = type(
            self.__class__.__name__, self.__class__.__bases__,
            {**self.__class__.__dict__, name: pyqtSignal(*args)},
        )


def findMainWindow() -> typing.Union[QMainWindow, None]:
    app = QApplication.instance()
    for widget in app.topLevelWidgets():
        if isinstance(widget, QMainWindow):
            return widget
    return None


@pyqtSlot(str, str, str)
def showDetailedError(title, text, detailedText):
    detailedMessage = QMessageBox(findMainWindow())
    detailedMessage.setWindowIcon(QIcon(QPixmap('data/icon.ico')))
    detailedMessage.setIcon(QMessageBox.Critical)
    detailedMessage.setWindowTitle(title)
    detailedMessage.setText(text)
    detailedMessage.setDetailedText(detailedText)
    detailedMessage.setDefaultButton(QMessageBox.Ok)
    detailedMessage.show()
