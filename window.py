import os
import random
import datetime

import requests
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox
from PyQt5.QtCore import QObject, Qt, QThread, pyqtSignal, QTimer
from PyQt5.Qt import QStandardItemModel, QStandardItem, QDesktopServices, QUrl
from PyQt5.QtGui import QFont, QColor
from qt_material import QtStyleTools

from wiki_parser import get_data_from_file, get_data_from_site, write_data_to_file


class StandardItem(QStandardItem):
    def __init__(self, text='', font_size=12, isBold=False, color=QColor(0, 0, 0)):
        super().__init__()
        font_ = QFont('Roboto', font_size)
        font_.setBold(isBold)

        self.setEditable(False)
        self.setForeground(color)
        self.setFont(font_)
        self.setText(text)


class JsonModel(QStandardItemModel):
    def __init__(self):
        super().__init__()

        self.root = self.invisibleRootItem()

    def FillFromJson(self, row, json_):
        if json_ is None:
            return
        elif isinstance(json_, dict):
            for key, val in sorted(json_.items()):
                newRow = StandardItem(key)
                row.appendRow(newRow)
                self.FillFromJson(newRow, val)
        elif isinstance(json_, (list, tuple)):
            for val in json_:
                text = (str(val) if not isinstance(val, (dict, list, tuple))
                        else '[%s]' % type(val).__name__)
                row.appendRow(StandardItem(text))
        else:
            row.appendRow(StandardItem(str(json_)))

    def FillModel(self, json_):
        try:
            self.FillFromJson(self.root, json_['weapons'])
        except KeyError:
            pass

    def Clear(self):
        self.clear()
        self.root = self.invisibleRootItem()


class MyWindow(QMainWindow, QtStyleTools):
    def __init__(self):
        super(MyWindow, self).__init__()
        uic.loadUi('TRND.ui', self)

        self.thread = None
        self.worker = None
        self.JsonData = None
        self.isThreadRunning = False
        self.isUpdateQuestion = True

        self.TreeModel = JsonModel()
        self.UpdateJson()

        self.twMain.setModel(self.TreeModel)

        self.btnImport.clicked.connect(self.ImportJson)
        self.btnExport.clicked.connect(self.ExportJson)
        self.btnClearData.clicked.connect(self.ClearJson)

        self.btnRandom.clicked.connect(self.Random)
        self.btnUpdateWeapons.clicked.connect(lambda: self.UpdateData('weapons'))
        self.btnUpdateMods.clicked.connect(lambda: self.UpdateData('mods'))
        self.leFind.textChanged[str].connect(self.FindWeapon)

        self.twMain.collapsed.connect(lambda: self.twMain.resizeColumnToContents(0))
        self.twMain.expanded.connect(lambda: self.twMain.resizeColumnToContents(0))

        self.twRandom.collapsed.connect(lambda: self.twRandom.resizeColumnToContents(0))
        self.twRandom.expanded.connect(lambda: self.twRandom.resizeColumnToContents(0))

        self.btnCheckNewVersion.clicked.connect(lambda : self.CheckNewVersion('button'))

        self.lblVersion.setText(os.environ.get('VERSION_NOW'))

        self.btnGithubLink.clicked.connect(lambda: QDesktopServices.openUrl(QUrl('https://github.com/MangriMen/TRND'
                                                                                 '/releases')))

        self.CheckNewVersion()

        self.updateTimer = QTimer()
        self.updateTimer.start(300000)
        self.updateTimer.timeout.connect(self.CheckNewVersion)

    def CheckNewVersion(self, sender='timer'):
        response = requests.get("https://api.github.com/repos/MangriMen/TRND/releases/latest").json()
        if ('message' not in response) or (response['message'] != 'Not Found'):
            self.lblLatestVersion.setText(response["name"])
            self.teUpdateChangeList.setText(response['body'])
            if sender == 'timer':
                if (float(response['name']) > float(os.environ.get('VERSION_NOW'))) and self.isUpdateQuestion:
                    res = QMessageBox.question(self, 'Новая версия', 'Доступна новая версия. Перейти к странице '
                                                                     'обновления?',
                                               (QMessageBox.Ok | QMessageBox.Cancel))
                    if res == QMessageBox.Ok:
                        self.tabWidgetMain.setCurrentIndex(2)
                    elif res == QMessageBox.Cancel:
                        self.isUpdateQuestion = False
        else:
            self.lblLatestVersion.setText('не найдена')

    def ImportJson(self):
        pathToJson = QFileDialog().getOpenFileName(self, 'Import JSON', '/', "json(*.json);; all(*.*)")[0]
        self.WriteFromToFile(pathToJson, os.environ.get('DATAFILE'))
        self.UpdateJson()

    def ExportJson(self):
        pathToJson = QFileDialog().getSaveFileName(self, 'Export JSON', '/', "json(*.json)")[0]
        self.WriteFromToFile(os.environ.get('DATAFILE'), pathToJson)

    def ClearJson(self):
        res = QMessageBox.question(self, 'Очистка данных', 'Все данные будут удалены. Продолжить?',
                                   (QMessageBox.Ok | QMessageBox.Cancel))
        if res == QMessageBox.Ok:
            os.remove(os.environ.get('DATAFILE'))
            self.UpdateJson()

    @staticmethod
    def WriteFromToFile(fileInPath, fileOutPath):
        try:
            with open(fileInPath, 'r', encoding='utf-8') as fileIn:
                with open(fileOutPath, "w", encoding='utf-8') as fileOut:
                    for line in fileIn:
                        fileOut.write(line)
        except FileNotFoundError:
            return False
        else:
            return True

    def FindWeapon(self, text):
        if self.twMain.model().rowCount == 0:
            return

        if text == '':
            self.twMain.setModel(self.TreeModel)
            return

        model = JsonModel()

        for item in self.TreeModel.findItems(text, Qt.MatchContains):
            newRow = item.clone()
            model.appendRow(newRow)
            self.GetChildrenReq(newRow, item)

        self.twMain.setModel(model)

    def Random(self):
        self.RandomItem(self.twMain, self.twRandom, self.JsonData, self.btnIsRandomWeapon.isChecked())

    def DateToStr(self, iso_date):
        if iso_date == 'unknown':
            return 'неизвестно'

        date_format_str = '%d.%m.%Y %X'
        try:
            out = datetime.datetime.fromisoformat(iso_date).strftime(date_format_str)
        except ValueError:
            iso_date = datetime.datetime.now().isoformat()
            out = self.DateToStr(iso_date)
        return out

    def UpdateJson(self):
        data = get_data_from_file()
        self.JsonData = data[0]

        if self.JsonData is None:
            self.JsonData = dict()
        if 'weaponsLastUpdate' not in self.JsonData:
            self.JsonData['weaponsLastUpdate'] = 'unknown'
        if 'modsLastUpdate' not in self.JsonData:
            self.JsonData['modsLastUpdate'] = 'unknown'
        if 'weapons' not in self.JsonData:
            self.JsonData['weapons'] = dict()
        if 'mods' not in self.JsonData:
            self.JsonData['mods'] = dict()

        self.lblUpdateWeapons.setText("Оружие обновленно " + self.DateToStr(self.JsonData['weaponsLastUpdate']))
        self.lblUpdateMods.setText("Моды обновленны " + self.DateToStr(self.JsonData['modsLastUpdate']))

        write_data_to_file(self.JsonData)

        self.TreeModel.Clear()
        self.TreeModel.FillModel(self.JsonData)
        self.twMain.setModel(self.TreeModel)
        self.twMain.setCurrentIndex(self.TreeModel.createIndex(0, 0))

    class Worker(QObject):
        finished = pyqtSignal()
        local_progress = pyqtSignal(int)
        global_progress = pyqtSignal(int)
        display_text = pyqtSignal(str)

        def __init__(self, function, type_, JsonData):
            super().__init__()
            self.isRunning = False
            self.function = function
            self.type = type_
            self.is_debug = False
            self.JsonData = JsonData

        def run(self):
            self.isRunning = True
            parsedJson = self.function(self)
            if parsedJson is not None:
                write_data_to_file(parsedJson)
            self.finished.emit()

        @staticmethod
        def finish(self):
            self.btnUpdateWeapons.setEnabled(True)
            self.btnUpdateMods.setEnabled(True)
            self.btnUpdateWeapons.setText(self.btnUpdateWeapons.accessibleName())
            self.btnUpdateMods.setText(self.btnUpdateMods.accessibleName())
            self.progressNow.setValue(0)
            self.progressTotal.setValue(0)
            self.lblProgress.setText("")
            self.UpdateJson()
            self.isThreadRunning = False

        def stop(self):
            self.isRunning = False

    def UpdateData(self, type_):
        if self.isThreadRunning:
            self.worker.stop()
            self.worker.finished.emit()
            self.thread.quit()
            self.thread.wait()
            self.thread = None

            self.teUpdateInfo.append('----------------------------------------')
            self.teUpdateInfo.append('Прервано пользователем')

            self.btnUpdateWeapons.setText(self.btnUpdateWeapons.accessibleName())
            self.btnUpdateMods.setText(self.btnUpdateMods.accessibleName())
            return

        self.teUpdateInfo.clear()

        self.thread = QThread()
        self.worker = self.Worker(get_data_from_site, type_, self.JsonData)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()
        self.isThreadRunning = True

        if type_ == 'weapons':
            self.btnUpdateWeapons.setText("Cancel")
            self.btnUpdateMods.setEnabled(False)
        elif type_ == 'mods':
            self.btnUpdateMods.setText("Cancel")
            self.btnUpdateWeapons.setEnabled(False)

        self.thread.finished.connect(
            lambda: self.worker.finish(self)
        )

        self.worker.local_progress.connect(
            lambda value: self.progressNow.setValue(value)
        )
        self.worker.global_progress.connect(
            lambda value: self.progressTotal.setValue(value)
        )
        self.worker.display_text.connect(
            lambda value: self.teUpdateInfo.append(value)
        )
        self.worker.display_text.connect(
            lambda value: self.lblProgress.setText(value.strip())
        )

    @staticmethod
    def GetChildrenReq(row, item):
        if item.hasChildren():
            for i in range(item.rowCount()):
                newRow = item.child(i, 0).clone()
                row.appendRow(newRow)
                MyWindow.GetChildrenReq(newRow, item.child(i, 0))

    def RandomItem(self, twMain, treeViewOut, JsonData, isRandWeapon=True):
        if twMain.model().rowCount() == 0:
            return

        if len(twMain.selectedIndexes()) == 0:
            twMain.setCurrentIndex(twMain.model().createIndex(0, 0))

        if isRandWeapon:
            index = random.randrange(0, twMain.model().root.rowCount())
            twMain.setCurrentIndex(twMain.model().createIndex(index, 0))

        name = twMain.selectedIndexes()[0]
        while name.parent().data() is not None:
            name = name.parent()
        name = name.data()

        OutModel = QStandardItemModel()
        Root = OutModel.invisibleRootItem()
        treeViewOut.setModel(OutModel)

        newRow = StandardItem(name)
        Root.appendRow(newRow)

        self.RandomReq(newRow, JsonData['weapons'][name])

        treeViewOut.expandAll()

    def RandomReq(self, row, json_):
        if json_ is None:
            return
        elif isinstance(json_, dict):
            for key, val in sorted(json_.items()):
                newRow = StandardItem(key)
                row.appendRow(newRow)
                self.RandomReq(newRow, val)
        elif isinstance(json_, (list, tuple)):
            rand = random.choice(json_)
            rand_str = str(rand)
            newRow = StandardItem(rand_str)
            if rand_str in self.JsonData['mods']:
                self.RandomReq(newRow, self.JsonData['mods'][rand])
            row.appendRow(newRow)
