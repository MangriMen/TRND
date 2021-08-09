import os
import random
import re
import subprocess
import sys
import tempfile

import requests
from PyQt5 import uic
from PyQt5.Qt import QDesktopServices, QUrl, QMenu, QApplication
from PyQt5.QtCore import Qt, QTimer, QTimeLine, pyqtSlot
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QProgressDialog, QPushButton, QLabel, QProgressBar
from PyQt5 import QtWinExtras

from libs import utils
from libs.qt_extends import JsonModel, ThreadController, showDetailedError
from libs.wiki_parser import get_data_from_wiki


class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        uic.loadUi('data/TRND.ui', self)

        self.date_format_str = '%d.%m.%Y %X'
        self.updateCheckTimeout = 60
        self.githubLink = 'https://github.com/MangriMen/TRND/releases'
        self.githubLinkLastRelease = 'https://api.github.com/repos/MangriMen/TRND/releases'

        self.update_thread = None
        self.data_thread = None
        self.jsonData = None
        self.isUpdateQuestion = True

        self.twMainModel = JsonModel()
        self.twRandomModel = JsonModel()
        self.updateTimer = QTimer()
        self.updateTimeoutTimer = QTimeLine()

        self.btnImportData.clicked.connect(self.import_json)
        self.btnExportData.clicked.connect(self.export_json)
        self.btnClearData.clicked.connect(self.clear_json)
        self.btnRandomWeapon.clicked.connect(self.random_weapon)
        self.btnUpdateApp.clicked.connect(self.update_app)
        self.leFind.textChanged[str].connect(self.find_and_display_weapons)
        self.btnCheckNewVersion.clicked.connect(lambda: self.check_new_version('button'))
        self.btnGithubLink.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(self.githubLink)))
        self.btnUpdateWeapons.clicked.connect(lambda: self.update_data('weapons'))
        self.btnUpdateMods.clicked.connect(lambda: self.update_data('mods'))
        self.twMain.collapsed.connect(lambda: self.twMain.resizeColumnToContents(0))
        self.twMain.expanded.connect(lambda: self.twMain.resizeColumnToContents(0))
        self.twRandom.collapsed.connect(lambda: self.twRandom.resizeColumnToContents(0))
        self.twRandom.expanded.connect(lambda: self.twRandom.resizeColumnToContents(0))
        self.updateTimer.timeout.connect(lambda: self.check_new_version('timer'))
        self.updateTimeoutTimer.valueChanged.connect(lambda value: self.btnCheckNewVersion.setText(''.join([
            self.btnCheckNewVersion.accessibleName(),
            ' (',
            str(self.updateCheckTimeout - round(self.updateTimeoutTimer.currentTime() / 1000)),
            ')'
        ])))
        self.updateTimeoutTimer.finished.connect(lambda: self.btnCheckNewVersion.setEnabled(True))
        self.updateTimeoutTimer.finished.connect(lambda: self.btnCheckNewVersion.setText(
            self.btnCheckNewVersion.accessibleName()
        ))
        self.updateTimeoutTimer.valueChanged.connect(lambda value: self.btnUpdateApp.setText(''.join([
            self.btnUpdateApp.accessibleName(),
            ' (',
            str(self.updateCheckTimeout - round(self.updateTimeoutTimer.currentTime() / 1000)),
            ')'
        ])))
        self.updateTimeoutTimer.finished.connect(lambda: self.btnUpdateApp.setEnabled(True))
        self.updateTimeoutTimer.finished.connect(lambda: self.btnUpdateApp.setText(
            self.btnUpdateApp.accessibleName()
        ))

        self.twMain.setModel(self.twMainModel)
        self.twRandom.setModel(self.twRandomModel)
        self.twRandom.setItemsExpandable(False)
        self.twRandom.customContextMenuRequested.connect(lambda location: self.custom_tree_view_context_menu(location))
        self.twRandom.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabWidgetMain.setCurrentWidget(self.tabMain)
        self.lblVersion.setText(os.environ.get('VERSION_NOW'))

        if QtWinExtras.QtWin.isCompositionEnabled():
            QtWinExtras.QtWin.extendFrameIntoClientArea(self, 0, 0, 0, 0)
        else:
            QtWinExtras.QtWin.resetExtendedFrame(self)

        self.taskbarBtn = QtWinExtras.QWinTaskbarButton(self)
        self.taskbarProgress = QtWinExtras.QWinTaskbarProgress(self)
        self.taskbarProgress = self.taskbarBtn.progress()
        self.taskbarProgress.setMinimum(-1)
        self.taskbarBtn.setWindow(self.windowHandle())

        self.updateTimer.start(300000)
        self.update_json()
        self.check_new_version()

    @pyqtSlot()
    def import_json(self):
        pathToJson = QFileDialog().getOpenFileName(self, 'Import JSON', '/', "json(*.json);; all(*.*)")[0]
        utils.rewrite_file_to_file(pathToJson, os.environ.get('DATAFILE'))
        self.update_json()

    @pyqtSlot()
    def export_json(self):
        pathToJson = QFileDialog().getSaveFileName(self, 'Export JSON', '/', "json(*.json)")[0]
        utils.rewrite_file_to_file(os.environ.get('DATAFILE'), pathToJson)

    @pyqtSlot()
    def clear_json(self):
        res = QMessageBox.information(self, 'Очистка данных', 'Все данные будут удалены. Продолжить?',
                                      (QMessageBox.Ok | QMessageBox.Cancel))
        if res == QMessageBox.Ok:
            os.remove(os.environ.get('DATAFILE'))
            self.update_json()

    @pyqtSlot()
    def update_json(self):
        self.jsonData = utils.load_data()
        self.jsonData = utils.validate_data(self.jsonData)

        self.lblUpdateWeapons.setText(
            "ОРУЖИЕ ОБНОВЛЕННО "
            + utils.date_to_str(self.jsonData['weaponsLastUpdate'], self.date_format_str).upper()
        )
        self.lblUpdateMods.setText(
            "МОДЫ ОБНОВЛЕННЫ "
            + utils.date_to_str(self.jsonData['modsLastUpdate'], self.date_format_str).upper()
        )

        utils.dump_data(self.jsonData)

        self.twMainModel.fillModel(self.jsonData['weapons'])
        self.twMain.setModel(self.twMainModel)
        self.twMain.setCurrentIndex(self.twMainModel.createIndex(0, 0))

    @pyqtSlot(str)
    def find_and_display_weapons(self, query):
        if query == '':
            self.twMain.setModel(self.twMainModel)
            return

        if self.twMainModel.rowCount == 0:
            return

        searchModel = JsonModel()

        for item in self.twMainModel.findItems(query, Qt.MatchContains):
            item_clone = item.clone()
            searchModel.appendRow(item_clone)
            JsonModel.copyItemWithChildren(item_clone, item)

        self.twMain.setModel(searchModel)

    @pyqtSlot()
    def create_random_weapon(self, randomJson_, key_, json_):
        randomJson_[key_] = dict()
        if json_ is None:
            return
        elif isinstance(json_, dict):
            for key, val in sorted(json_.items()):
                self.create_random_weapon(randomJson_[key_], key, val)
        elif isinstance(json_, (list, tuple)):
            rand_str = str(random.choice(json_))
            if rand_str in self.jsonData['mods']:
                self.create_random_weapon(randomJson_[key_], rand_str, self.jsonData['mods'][rand_str])
            else:
                randomJson_[key_] = list()
                randomJson_[key_].append(rand_str)

    @pyqtSlot()
    def random_weapon(self):
        if self.twMainModel.rowCount() == 0:
            return

        if len(self.twMain.selectedIndexes()) == 0:
            self.twMain.setCurrentIndex(self.twMainModel.createIndex(0, 0))

        if self.chboxIsRandomWeapon.isChecked():
            index = random.randrange(0, self.twMainModel.root.rowCount())
            self.twMain.setCurrentIndex(self.twMainModel.createIndex(index, 0))

        name = self.twMain.selectedIndexes()[0]
        if not self.chboxIsRandomWeapon.isChecked():
            while name.parent().data() is not None:
                name = name.parent()
        name = name.data()

        self.create_random_weapon(randomJson := dict(), name, self.jsonData['weapons'][name])

        self.twRandomModel.fillModel(randomJson)
        self.twRandom.expandAll()

        self.resolve_mod_conflicts()

    @pyqtSlot()
    def resolve_mod_conflicts(self):
        def get_last_children(item, json_, conflicts_):
            if item.hasChildren():
                isDict = False
                for i in range(item.rowCount()):
                    if item.child(i, 0).hasChildren():
                        isDict = True
                        break
                if isDict:
                    for i in range(item.rowCount()):
                        get_last_children(item.child(i, 0), json_[item.child(i, 0).text()], conflicts_)
                else:
                    for i in range(item.rowCount()):
                        child_ = item.child(i, 0)
                        if child_.text() in self.jsonData['modsConflicts']:
                            redBackgroundColor = QColor(140, 42, 42)
                            isConflict = False
                            for conflict in self.jsonData['modsConflicts'][child_.text()]:
                                conflictItems = self.twRandomModel.findItems(
                                    conflict,
                                    (Qt.MatchContains | Qt.MatchRecursive)
                                )
                                for conflictItem in conflictItems:
                                    conflictItem.setBackground(redBackgroundColor)
                                    conflicts_.append(conflictItem)
                                    isConflict = True
                            if isConflict:
                                child_.setBackground(redBackgroundColor)
                                conflicts_.append(child_)

        if self.twRandomModel and self.twRandomModel.rowCount():
            isQuestion = True
            while True:
                rootFirstChild_ = self.twRandomModel.invisibleRootItem().child(0, 0)
                JsonModel.modelToJson(rootFirstChild_, weaponJson := dict(), rootFirstChild_.text())
                get_last_children(rootFirstChild_, weaponJson[rootFirstChild_.text()], conflicts := list())

                if not conflicts:
                    break

                if isQuestion:
                    res = QMessageBox.question(self, 'Конфликт модов', 'Некоторые моды конфликтуют между '
                                                                       'собой.\nХотите перегенерировать их?')
                    if res == QMessageBox.Yes:
                        isQuestion = False
                    else:
                        return

                if not isQuestion:
                    for conflict_ in conflicts:
                        conflict_.setBackground(QColor(0, 0, 0, 0))
                    randomConflict = random.choice(conflicts)
                    conflictIndex = self.twRandomModel.indexFromItem(randomConflict)
                    if randomConflict.hasChildren():
                        conflictIndex = conflictIndex.parent()
                    self.custom_tree_view_replace_random(conflictIndex)

    @pyqtSlot()
    def start_update_restrict_timeout(self):
        self.btnCheckNewVersion.setEnabled(False)
        self.btnCheckNewVersion.setText(''.join([
            self.btnCheckNewVersion.accessibleName(),
            ' (',
            str(self.updateCheckTimeout),
            ')'
        ]))
        self.btnUpdateApp.setEnabled(False)
        self.btnUpdateApp.setText(''.join([
            self.btnUpdateApp.accessibleName(),
            ' (',
            str(self.updateCheckTimeout),
            ')'
        ]))

        self.updateTimeoutTimer.setDuration(self.updateCheckTimeout * 1000)
        self.updateTimeoutTimer.setUpdateInterval(1000)
        self.updateTimeoutTimer.start()

    @pyqtSlot(str)
    def check_new_version(self, sender='timer'):
        if sender == 'button':
            self.start_update_restrict_timeout()

        response = utils.get_update_info(self.githubLinkLastRelease)

        if not response['result']:
            if sender == 'button':
                showDetailedError(
                    'Ошибка обновления: ' + str(response['error']),
                    'Невозможно получить данные для обновления.',
                    str(response['error_msg']))
            return

        self.teUpdateChangeList.setText('Последняя версия: ' + response['data'][0]['tag_name'])
        self.teUpdateChangeList.append('')
        indent = '  '
        for version in response['data']:
            self.teUpdateChangeList.append(version['name'])
            if version['body']:
                body = indent + version['body'].replace('\n', '\n' + indent)
            else:
                body = indent + 'Description not found'
            self.teUpdateChangeList.append(body)

        if float(response['data'][0]['tag_name']) > float(os.environ.get('VERSION_NOW')):
            self.tabWidgetMain.setTabText(2, self.tabUpdate.accessibleName() + ' (новая версия)')
            if (sender == 'timer' and self.isUpdateQuestion) or self.tabWidgetMain.currentWidget() == self.tabUpdate:
                if sender == 'timer':
                    message = 'Перейти на страницу обновления?'
                else:
                    message = 'Обновить сейчас?'
                res = QMessageBox.information(self, 'Новая версия', 'Доступна новая версия. ' + message,
                                              (QMessageBox.Ok | QMessageBox.Cancel))
                if res == QMessageBox.Ok:
                    if sender == 'timer':
                        self.tabWidgetMain.setCurrentWidget(self.tabUpdate)
                    else:
                        self.update_app()
                elif res == QMessageBox.Cancel:
                    self.isUpdateQuestion = False
        else:
            if sender == 'button':
                QMessageBox.information(self, 'Обновление', 'Установлена последняя версия.', QMessageBox.Ok)
            self.tabWidgetMain.setTabText(2, self.tabUpdate.accessibleName())

    @pyqtSlot()
    def update_app(self):
        self.start_update_restrict_timeout()

        @pyqtSlot()
        def get_file(worker_, dict_):
            downloaded_file_ = dict_['downloaded_file_']
            total_length_ = dict_['total_length_']
            with open(tempfile.gettempdir() + '\\TRND_update.exe', 'wb') as file:
                if total_length_ is None:
                    file.write(downloaded_file_.content)
                else:
                    dl = 0
                    for data in downloaded_file_.iter_content(chunk_size=4096):
                        if not worker_.isRunning:
                            break
                        dl += len(data)
                        file.write(data)
                        worker_.progress.emit(dl)

        @pyqtSlot()
        def stop_process():
            self.taskbarProgress.hide()
            if dlg.wasCanceled():
                return
            subprocess.Popen([tempfile.gettempdir() + '\\TRND_update.exe', '/VERYSILENT'])
            self.close()
            sys.exit()

        response = utils.get_update_info(self.githubLinkLastRelease + '/latest')

        if not response['result']:
            showDetailedError(
                'Ошибка обновления: ' + response['error'],
                'Невозможно получить данные для обновления.',
                response['error_msg']
            )
            return

        if 'assets' not in response['data']:
            QMessageBox.warning(self, 'Ошибка', 'Ошибка получения данных.', QMessageBox.Ok)
            return

        if float(response['data']['tag_name']) <= float(os.environ.get('VERSION_NOW')):
            QMessageBox.information(self, 'Обновление', 'Установлена последняя версия.', QMessageBox.Ok)
            return

        self.btnUpdateApp.setEnabled(False)

        download_link = ''
        for asset in response['data']['assets']:
            if re.search('.exe', asset['browser_download_url']):
                download_link = asset['browser_download_url']
                break

        if download_link == '':
            QMessageBox.warning(self, 'Ошибка', 'Ошибка получения данных.', QMessageBox.Ok)
            return

        downloaded_file = requests.get(download_link, allow_redirects=True, stream=True)

        total_length = downloaded_file.headers.get('content-length')
        total_length_display = str(int(int(total_length) / 1024)) + ' КБ'

        dlg = QProgressDialog('', 'Отмена', 0, int(total_length), self,
                              (Qt.WindowTitleHint | Qt.WindowCloseButtonHint | Qt.Dialog))
        dlg.setWindowTitle('Загрузка инсталлятора')

        font_ = QFont('Roboto', 10)
        font_.setBold(True)
        lblText = QLabel()
        lblText.setFont(font_)
        lblText.setAlignment(Qt.AlignCenter)
        dlg.setLabel(lblText)

        progressUpdate = QProgressBar()
        progressUpdate.setMaximum(int(total_length))
        progressUpdate.setTextVisible(False)
        dlg.setBar(progressUpdate)
        dlg.setAutoReset(False)

        btnCancel = QPushButton()
        dlg.setCancelButton(btnCancel)
        btnCancel.hide()

        dlg.setFixedSize(dlg.width()*1.5, dlg.height())
        dlg.canceled.connect(lambda: self.update_thread.stop())

        dlg.show()

        self.update_thread = ThreadController(get_file, downloaded_file_=downloaded_file, total_length_=total_length)
        self.update_thread.worker.addSignal('progress', [int])

        self.update_thread.worker.progress.connect(lambda value: dlg.setValue(value))
        self.update_thread.worker.progress.connect(lambda value: self.taskbarProgress.setValue(
            (int(value) / int(total_length))*100))
        self.update_thread.worker.progress.connect(lambda value: lblText.setText(str(int(value / 1024)) + ' КБ / ' +
                                                                                 total_length_display))
        self.update_thread.thread.finished.connect(stop_process)

        self.taskbarProgress.show()
        self.update_thread.thread.start()

    @pyqtSlot(str)
    def update_data(self, type_):
        @pyqtSlot()
        def get_data(worker_, dict_):
            parsedJson = get_data_from_wiki(worker_, dict_)
            if parsedJson is not None:
                utils.dump_data(parsedJson)

        @pyqtSlot()
        def finish(main):
            main.btnUpdateWeapons.setEnabled(True)
            main.btnUpdateMods.setEnabled(True)
            main.btnUpdateWeapons.setText(main.btnUpdateWeapons.accessibleName())
            main.btnUpdateMods.setText(main.btnUpdateMods.accessibleName())
            self.progressNow.setTextVisible(False)
            self.progressTotal.setTextVisible(False)
            main.progressNow.setValue(0)
            main.progressTotal.setValue(0)
            main.lblProgress.setText("")
            main.update_json()
            main.taskbarProgress.hide()

        if self.data_thread and self.data_thread.isRunning:
            self.data_thread.stop()
            self.teUpdateInfo.append('----------------------------------------')
            self.teUpdateInfo.append('Прервано пользователем')
            self.btnUpdateWeapons.setText(self.btnUpdateWeapons.accessibleName())
            self.btnUpdateMods.setText(self.btnUpdateMods.accessibleName())
            return

        self.teUpdateInfo.clear()
        self.progressNow.setTextVisible(True)
        self.progressTotal.setTextVisible(True)

        if type_ == 'weapons':
            self.btnUpdateWeapons.setText("Отмена")
            self.btnUpdateMods.setEnabled(False)
        elif type_ == 'mods':
            self.btnUpdateMods.setText("Отмена")
            self.btnUpdateWeapons.setEnabled(False)

        self.data_thread = ThreadController(get_data, type=type_, is_debug=False, jsonData=self.jsonData)
        self.data_thread.worker.addSignal('local_progress', [int])
        self.data_thread.worker.addSignal('global_progress', [int])
        self.data_thread.worker.addSignal('display_text', [str])

        self.data_thread.worker.local_progress.connect(lambda value: self.progressNow.setValue(value))
        self.data_thread.worker.global_progress.connect(lambda value: self.progressTotal.setValue(value))
        self.data_thread.worker.global_progress.connect(lambda value: self.taskbarProgress.setValue(value))
        self.data_thread.worker.display_text.connect(lambda value: self.teUpdateInfo.append(value))
        self.data_thread.worker.display_text.connect(lambda value: self.lblProgress.setText(value.strip()))
        self.data_thread.thread.finished.connect(lambda: finish(self))

        self.taskbarProgress.show()
        self.data_thread.start()

    @pyqtSlot(object)
    def custom_tree_view_copy_row(self, index_):
        if self.twRandomModel:
            QApplication.clipboard().setText(self.twRandomModel.itemFromIndex(index_).text())

    @pyqtSlot(object)
    def replace_random_and_check_conflicts(self, index_):
        self.custom_tree_view_replace_random(index_)
        self.resolve_mod_conflicts()

    @pyqtSlot()
    def custom_tree_view_copy_text(self):
        if self.twRandomModel:
            twRandomRoot = self.twRandomModel.invisibleRootItem()
            out = JsonModel.modelToText(twRandomRoot)
            QApplication.clipboard().setText(out.rstrip())

    @pyqtSlot()
    def custom_tree_view_copy_json(self):
        if self.twRandomModel:
            twRandomRoot = self.twRandomModel.invisibleRootItem()
            JsonModel.modelToJson(twRandomRoot.child(0, 0), out := dict(), twRandomRoot.child(0, 0).text())
            out = utils.get_json_dump(out)
            if out is not None:
                QApplication.clipboard().setText(out)

    @pyqtSlot(str)
    def custom_tree_view_paste_json(self, json_):
        if not self.twRandomModel:
            self.twRandom.setModel(JsonModel())
        json_ = utils.get_json_loads(json_)
        if json_ is not None:
            self.twRandomModel.fillModel(json_)
            self.twRandom.expandAll()
            self.resolve_mod_conflicts()

    @pyqtSlot(object)
    def custom_tree_view_replace_random(self, index_):
        twRandomFirstChild = self.twRandomModel.invisibleRootItem().child(0, 0)
        clickedRowText = self.twRandomModel.itemFromIndex(index_).text()

        pathToRootList = list()
        while (item := self.twRandomModel.itemFromIndex(index_)) is not None\
                and (index_ := index_.parent()) is not None:
            pathToRootList.append(item.text())
        pathToRootList.reverse()

        out = dict()
        json_ = self.jsonData['weapons'].copy()
        jsonTemp = json_

        if len(pathToRootList) == 1:
            outTemp = out
            outKey = clickedRowText
            jsonTemp = jsonTemp[clickedRowText]
        else:
            JsonModel.modelToJson(twRandomFirstChild, out, twRandomFirstChild.text())
            outTemp = out
            if len(pathToRootList) == 2:
                outTemp = outTemp[pathToRootList[0]]
                outKey = clickedRowText
                jsonTemp = jsonTemp[pathToRootList[0]][clickedRowText]
            else:
                def scanDict(scanList_, scanDict_):
                    lastIndex_ = 0
                    for lastIndex_ in range(len(scanList_)):
                        path_ = pathToRootList[lastIndex_]
                        nextIndex = lastIndex_ + 1
                        if (nextIndex < len(scanList_)) and (pathToRootList[nextIndex] == clickedRowText):
                            break
                        if isinstance(scanDict_[path_], list):
                            break
                        scanDict_ = scanDict_[path_]
                    return scanDict_, lastIndex_

                outTemp, lastIndexOut = scanDict(pathToRootList, outTemp)
                outKey = pathToRootList[lastIndexOut]
                jsonTemp, lastIndexJson = scanDict(pathToRootList, jsonTemp)

                if outKey in jsonTemp:
                    jsonTemp = jsonTemp[pathToRootList[lastIndexJson]]
                else:
                    jsonTemp = self.jsonData['mods'][pathToRootList[lastIndexOut]]

        self.create_random_weapon(outTemp, outKey, jsonTemp)

        self.twRandomModel.fillModel(out)
        self.twRandom.expandAll()

    @pyqtSlot()
    def custom_tree_view_context_menu(self, location):
        menu = QMenu(self)
        if (index := self.twRandom.indexAt(location)).isValid():
            menu.addAction('Копировать', lambda: self.custom_tree_view_copy_row(index))
            menu.addAction('Перегенерировать', lambda: self.replace_random_and_check_conflicts(index))
            menu.addSeparator()
        menu.addAction('Копировать текст', self.custom_tree_view_copy_text)
        menu.addAction('Копировать оружие', self.custom_tree_view_copy_json)
        menu.addAction('Вставить оружие', lambda: self.custom_tree_view_paste_json(QApplication.clipboard().text()))
        menu.popup(self.twRandom.mapToGlobal(location))
