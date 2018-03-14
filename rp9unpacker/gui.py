#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# The gui
#

import constants as const
import rp9util as util
from config import Config

import gettext
import os
import sys
import traceback

from pathlib import Path
from zipfile import is_zipfile
from PyQt5.QtGui import QIcon, QPixmap, QTextCursor
from PyQt5.QtCore import pyqtSlot, Qt, QSize, QThread
from PyQt5.QtWidgets import (QAbstractItemView, QAction, QCheckBox, QDialog, QFileDialog, QHBoxLayout, QLabel,
                             QListWidget, QListWidgetItem, QMainWindow, QPlainTextEdit, QPushButton, QSizePolicy,
                             QSplitter, QVBoxLayout, QWidget, QFrame, QDialogButtonBox, QGridLayout, QLineEdit,
                             QMessageBox, QTableWidget, QTableWidgetItem, QListView, QLayout)

images_path = Path(__file__).parent.joinpath('images')
resources_path = Path(__file__).parent.joinpath('resources')

localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locales')
translate = gettext.translation('gui', localedir, fallback=True)
_ = translate.gettext


class AboutDialog(QDialog):

    def __init__(self, *args):
        QDialog.__init__(self, *args)
        self.setWindowTitle(_('About rp9UnpAckEr for FS-UAE'))

        dlglyt = QVBoxLayout()
        self.setLayout(dlglyt)

        info = QWidget()
        infolyt = QHBoxLayout()
        info.setLayout(infolyt)
        dlglyt.addWidget(info)

        pixmap = QPixmap(str(images_path.joinpath('amigaballsmall.png')))
        lbl = QLabel(self)
        lbl.setPixmap(pixmap)
        infolyt.addWidget(lbl)

        text = QWidget()
        textlyt = QVBoxLayout()
        text.setLayout(textlyt)
        infolyt.addWidget(text)
        appstr = _('rp9UnpAckEr for FS-UAE')
        l1 = QLabel(appstr + ' ' + const.VERSION)
        l1.setStyleSheet('font: bold')
        l2 = QLabel(_('Copyright © 2018 Jens Kieselbach'))
        textlyt.addWidget(l1)
        textlyt.addWidget(l2)
        infolyt.addStretch()

        textedit = QPlainTextEdit(self)

        try:
            file = open(resources_path.joinpath('LICENSE'), 'r', encoding="utf-8")
            textedit.insertPlainText(file.read())
        except Exception as e:
            textedit.insertPlainText(str(e))

        textedit.moveCursor(QTextCursor.Start)
        textedit.setTextInteractionFlags(Qt.TextSelectableByKeyboard | Qt.TextSelectableByMouse)
        textedit.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        textedit.setStyleSheet('font: 9pt "Monospace"')
        dlglyt.addWidget(textedit)

        # ok_button = QPushButton(QIcon.fromTheme('dialog-ok'), 'OK', self)
        # ok_button.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))

        # button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        dlglyt.addWidget(button_box)

        self.resize(600, 400)


class DirectoryFieldButton(QPushButton):

    def __init__(self, icon, parent, ledit, dirsonly):
        QPushButton.__init__(self, icon, '', parent)
        self.line_edit = ledit
        self.directories_only = dirsonly
        self.clicked.connect(self.select_dir)

    @pyqtSlot()
    def select_dir(self):

        if self.directories_only:
            filename = QFileDialog.getExistingDirectory(self, 'Choose directory', self.line_edit.text(),
                                                        QFileDialog.ShowDirsOnly | QFileDialog.DontUseNativeDialog)
        else:
            filename, _ = QFileDialog.getOpenFileName(self, 'Choose file', self.line_edit.text(),
                                                      options=QFileDialog.DontUseNativeDialog)
        if filename:
            file = Path(filename)
            if self.directories_only:
                if file.is_dir():
                    self.line_edit.setText(filename)
                    self.line_edit.setFocus()
            else:
                if file.is_file():
                    self.line_edit.setText(filename)
                    self.line_edit.setFocus()


class SettingsDialog(QDialog):

    def __init__(self, *args):
        QDialog.__init__(self, *args)
        self.setWindowTitle(_('Settings'))

        self.fsuae_command_edit = self.__lineedit()
        self.fsuae_documents_dir_edit = self.__lineedit()
        self.fsuae_rp9_dir_edit = self.__lineedit()
        self.temp_dir_edit = self.__lineedit()
        self.workbench_135_hd_edit = self.__lineedit()
        self.workbench_211_hd_edit = self.__lineedit()
        self.workbench_311_hd_edit = self.__lineedit()

        dlglyt = QVBoxLayout()
        dlglyt.setSizeConstraint(QLayout.SetFixedSize)
        self.setLayout(dlglyt)

        grid = QGridLayout()
        dlglyt.addLayout(grid)
        grid.setSpacing(10)

        grid.addWidget(self.__label(_('FS-UAE command:')), 0, 0)
        grid.addWidget(self.fsuae_command_edit, 0, 1)
        grid.addWidget(self.__dirbutton(self.fsuae_command_edit, False), 0, 2)

        grid.addWidget(self.__label(_('FS-UAE documents directory:')), 1, 0)
        grid.addWidget(self.fsuae_documents_dir_edit, 1, 1)
        grid.addWidget(self.__dirbutton(self.fsuae_documents_dir_edit, True), 1, 2)

        grid.addWidget(self.__label(_('RP9 extraction directory:')), 2, 0)
        grid.addWidget(self.fsuae_rp9_dir_edit, 2, 1)
        grid.addWidget(self.__dirbutton(self.fsuae_rp9_dir_edit, True), 2, 2)

        grid.addWidget(self.__label(_('Temp directory:')), 3, 0)
        grid.addWidget(self.temp_dir_edit, 3, 1)
        grid.addWidget(self.__dirbutton(self.temp_dir_edit, True), 3, 2)

        grid.addWidget(self.__label(_('Workbench-135 harddisk:')), 4, 0)
        grid.addWidget(self.workbench_135_hd_edit, 4, 1)
        grid.addWidget(self.__dirbutton(self.workbench_135_hd_edit, False), 4, 2)

        grid.addWidget(self.__label(_('Workbench-211 harddisk:')), 5, 0)
        grid.addWidget(self.workbench_211_hd_edit, 5, 1)
        grid.addWidget(self.__dirbutton(self.workbench_211_hd_edit, False), 5, 2)

        grid.addWidget(self.__label(_('Workbench-311 harddisk:')), 6, 0)
        grid.addWidget(self.workbench_311_hd_edit, 6, 1)
        grid.addWidget(self.__dirbutton(self.workbench_311_hd_edit, False), 6, 2)

        dlglyt.addSpacing(10)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        dlglyt.addWidget(button_box)

    @staticmethod
    def __label(name):
        label = QLabel(name)
        label.setAlignment(Qt.AlignRight)
        return label

    @staticmethod
    def __lineedit():
        edit = QLineEdit()
        edit.setFixedWidth(400)
        return edit

    def __dirbutton(self, ledit, dirsonly):
        button = DirectoryFieldButton(QIcon.fromTheme('folder-open'), self, ledit, dirsonly)
        return button


class Rp9Viewer(QFrame):

    def __init__(self, conf, *args):
        QFrame.__init__(self, *args)

        self.config = conf
        self.worker = None
        self.thread = None
        self.rp9_file = None
        self.rp9_documents = []
        self.rp9_images = []

        self.line_edits = []
        self.title_edit = self.__lineedit()
        self.system_edit = self.__lineedit()
        self.publisher_edit = self.__lineedit()
        self.type_edit = self.__lineedit()
        self.genre_edit = self.__lineedit()
        self.year_edit = self.__lineedit()
        self.language_edit = self.__lineedit()
        self.rating_edit = self.__lineedit()
        self.systemrom_edit = self.__lineedit()

        self.help_edit = self.__textedit()
        self.help_edit.setStyleSheet('font-family: Monospace;font-style: normal;')

        self.media_table = QTableWidget()
        self.media_table.setColumnCount(3)
        self.media_table.setRowCount(0)
        self.media_table.setHorizontalHeaderLabels([_('Type'), _('Priority'), _('Name')])
        self.media_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.image_list = QListWidget()
        self.image_list.setSelectionMode(QAbstractItemView.NoSelection)
        self.image_list.setViewMode(QListView.IconMode)
        self.image_list.setIconSize(QSize(160, 160))
        self.image_list.setGridSize(QSize(170, 170))
        self.image_list.setStyleSheet("QListWidget::item {border-top: 4px solid transparent; }")

        vbox = QVBoxLayout()
        self.setLayout(vbox)

        grid = QGridLayout()
        vbox.addLayout(grid)
        grid.setSpacing(10)

        grid.addWidget(self.__label(_('Title:')), 0, 0)
        grid.addWidget(self.title_edit, 0, 1, 1, 3)

        grid.addWidget(self.__label(_('System:')), 1, 0)
        grid.addWidget(self.system_edit, 1, 1)
        grid.addWidget(self.__label(_('Publisher:')), 1, 2)
        grid.addWidget(self.publisher_edit, 1, 3)

        grid.addWidget(self.__label(_('Type:')), 2, 0)
        grid.addWidget(self.type_edit, 2, 1)
        grid.addWidget(self.__label(_('Genre:')), 2, 2)
        grid.addWidget(self.genre_edit, 2, 3)

        grid.addWidget(self.__label(_('Year:')), 3, 0)
        grid.addWidget(self.year_edit, 3, 1)
        grid.addWidget(self.__label(_('Language:')), 3, 2)
        grid.addWidget(self.language_edit, 3, 3)

        grid.addWidget(self.__label(_('Rating:')), 4, 0)
        grid.addWidget(self.rating_edit, 4, 1)
        grid.addWidget(self.__label(_('System-ROM:')), 4, 2)
        grid.addWidget(self.systemrom_edit, 4, 3)

        grid.addWidget(self.__label(_('Help:')), 5, 0, 1, 1)
        grid.addWidget(self.help_edit, 5, 1, 1, 3)

        grid.addWidget(self.__label(_('Media:')), 6, 0, 1, 1)
        grid.addWidget(self.media_table, 6, 1, 1, 3)

        grid.addWidget(self.__label(_('Images:')), 7, 0, 1, 1)
        grid.addWidget(self.image_list, 7, 1, 1, 3)

        button_box = QDialogButtonBox()
        vbox.addWidget(button_box)

        self.run_from_temp_button = button_box.addButton('Run in temporary configuration', QDialogButtonBox.NoRole)
        self.run_from_config_button = button_box.addButton('Write configuration and run', QDialogButtonBox.NoRole)
        self.write_config_button = button_box.addButton('Write configuration', QDialogButtonBox.NoRole)

        self.run_from_temp_button.clicked.connect(self.run_from_temp)
        self.run_from_config_button.clicked.connect(self.run_from_config)
        self.write_config_button.clicked.connect(self.write_config)

        self.run_from_temp_button.setEnabled(False)
        self.run_from_config_button.setEnabled(False)
        self.write_config_button.setEnabled(False)

    @pyqtSlot()
    def exit_thread(self):
        if self.thread is not None and self.thread.isRunning():
            self.thread.exit()

    @pyqtSlot()
    def run_from_temp(self):
        try:
            if self.thread is not None and self.thread.isRunning():
                QMessageBox.warning(self, _('Run rp9'), _('The previous fs-uae process is still running.'),
                                    QMessageBox.Ok)
                return

            self.worker = util.run_from_temp(self.rp9_file, self.config)
            self.thread = QThread()
            self.thread.started.connect(self.worker.execute)
            self.worker.moveToThread(self.thread)
            self.worker.exitSignal.connect(self.exit_thread)
            self.thread.start()

        except util.Rp9UtilException as ex:
            QMessageBox.critical(self, _('Run rp9'), str(ex), QMessageBox.Ok)

        except Exception:
            sys.stderr.write('Could not run rp9 file: \'' + str(self.rp9_file) + '\'\n')
            traceback.print_exc(file=sys.stderr)
            QMessageBox.critical(self, _('Run rp9'), _('Error while trying to run rp9 file!'), QMessageBox.Ok)

    @pyqtSlot()
    def run_from_config(self):
        print('run_from_config')

    @pyqtSlot()
    def write_config(self):
        print('write_config')

    @staticmethod
    def __label(name):
        label = QLabel(name)
        label.setAlignment(Qt.AlignRight)
        return label

    def __lineedit(self):
        edit = QLineEdit()
        edit.setReadOnly(True)
        self.line_edits.append(edit)
        return edit

    def __textedit(self):
        edit = QPlainTextEdit()
        edit.setReadOnly(True)
        self.line_edits.append(edit)
        return edit

    def open_rp9(self, file):

        self.rp9_file = file
        for edit in self.line_edits:
            edit.clear()
        self.media_table.setRowCount(0)
        self.rp9_documents.clear()
        self.rp9_images.clear()
        self.image_list.clear()
        self.run_from_temp_button.setEnabled(False)
        self.run_from_config_button.setEnabled(False)
        self.write_config_button.setEnabled(False)

        try:
            info = util.get_info(self.rp9_file, load_extras=True)

            self.title_edit.setText(info.description_title)
            self.publisher_edit.setText(info.description_publisher)
            self.type_edit.setText(info.description_type)
            self.genre_edit.setText(info.description_genre)
            self.year_edit.setText(info.description_year)
            self.language_edit.setText(info.description_language)
            self.rating_edit.setText(info.description_rating)
            self.systemrom_edit.setText(info.description_systemrom)
            self.system_edit.setText(info.configuration_system)

            length = len(info.media)
            self.media_table.setRowCount(length)
            for i in range(length):
                media = info.media[i]
                self.media_table.setItem(i, 0, QTableWidgetItem(media.type))
                self.media_table.setItem(i, 1, QTableWidgetItem(media.priority))
                self.media_table.setItem(i, 2, QTableWidgetItem(media.name))
            self.media_table.resizeColumnsToContents()

            with_title = len(info.embedded_help) > 1
            newline = False
            for helpdoc in info.embedded_help:
                if helpdoc.text is not None:
                    if with_title:
                        if newline:
                            self.help_edit.insertPlainText('\n')
                        newline = True
                        self.help_edit.insertPlainText(helpdoc.name)
                        self.help_edit.insertPlainText('\n')
                        for i in range(len(helpdoc.name)):
                            self.help_edit.insertPlainText('=')
                        self.help_edit.insertPlainText('\n')
                    self.help_edit.insertPlainText(helpdoc.text)

            for image in info.embedded_images:
                if image.image is not None:
                    icon = QIcon()
                    icon.addPixmap(QPixmap.fromImage(image.image), QIcon.Normal, QIcon.Off)
                    self.image_list.addItem(QListWidgetItem(icon, ''))

            self.run_from_temp_button.setEnabled(True)
            self.run_from_config_button.setEnabled(True)
            self.write_config_button.setEnabled(True)

        except util.Rp9UtilException as ex:
            QMessageBox.critical(self, _('Run rp9'), str(ex), QMessageBox.Ok)

        except Exception:
            sys.stderr.write('Could not rp9 file: \'' + str(file) + '\'\n')
            traceback.print_exc(file=sys.stderr)
            QMessageBox.critical(self, _('Open rp9'), _('This is not a valid rp9 file!'), QMessageBox.Ok)


class MainWindow(QMainWindow):

    def __init__(self, *args):
        QMainWindow.__init__(self, *args)
        appstr = _('rp9UnpAckEr for FS-UAE')
        self.setWindowTitle(appstr + ' ' + const.VERSION)
        self.setWindowIcon(QIcon(str(images_path.joinpath('amigaball.png'))))

        # load config
        self.config = Config()
        self.config.load()
        self.current_dir = self.config.current_dir

        self.move(self.config.mainwindow_x, self.config.mainwindow_y)
        self.resize(self.config.mainwindow_witdh, self.config.mainwindow_height)

        # Menu Bar
        self.settings_action = QAction(_('Settings'), self)
        self.exit_action = QAction(_('Exit'), self)
        self.exit_action.setMenuRole(QAction.QuitRole)

        file_menu = self.menuBar().addMenu(_('Program'))
        file_menu.addAction(self.settings_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        self.about_action = QAction(_('About'), self)
        help_menu = self.menuBar().addMenu(_('Help'))
        help_menu.addAction(self.about_action)

        # Widgets
        self.splitter = QSplitter(Qt.Horizontal)
        self.rp9_viewer = Rp9Viewer(self.config)
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.dir_button = QPushButton(QIcon.fromTheme('folder-open'), '', self)
        self.show_hidden_check = QCheckBox('Show hidden files', self)

        # Connects
        self.dir_button.clicked.connect(self.select_dir)
        self.about_action.triggered.connect(self.show_about_dialog)
        self.settings_action.triggered.connect(self.show_settings_dialog)
        self.exit_action.triggered.connect(self.close)
        self.show_hidden_check.stateChanged.connect(self.update_dir)
        self.file_list.itemDoubleClicked.connect(self.show_file)

        # Layout
        self.setCentralWidget(self.splitter)

        left_widget = QWidget()
        self.splitter.addWidget(left_widget)
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)

        left_layout.addWidget(self.dir_button)
        left_layout.addWidget(self.file_list)
        left_layout.addWidget(self.show_hidden_check)

        self.splitter.addWidget(self.rp9_viewer)

        # inital state
        self.show_hidden_check.setChecked(self.config.show_hidden)
        self.file_list.setFocus()
        self.update_dir()

    @pyqtSlot()
    def update_text(self):
        self.hello_world_label.setText(self.edit_text.text())

    @pyqtSlot()
    def show_about_dialog(self):
        dialog = AboutDialog(self)
        dialog.exec_()

    @pyqtSlot()
    def show_settings_dialog(self):
        dialog = SettingsDialog(self)
        dialog.fsuae_command_edit.setText(self.config.fsuae_command)
        dialog.fsuae_documents_dir_edit.setText(self.config.fsuae_documents_dir)
        dialog.fsuae_rp9_dir_edit.setText(self.config.fsuae_rp9_dir)
        dialog.temp_dir_edit.setText(self.config.temp_dir)
        dialog.workbench_135_hd_edit.setText(self.config.workbench_135_hd)
        dialog.workbench_211_hd_edit.setText(self.config.workbench_211_hd)
        dialog.workbench_311_hd_edit.setText(self.config.workbench_311_hd)

        result = dialog.exec_()
        if result == QDialog.Accepted:
            self.config.fsuae_command = dialog.fsuae_command_edit.text().strip()
            self.config.fsuae_documents_dir = dialog.fsuae_documents_dir_edit.text().strip()
            self.config.fsuae_rp9_dir = dialog.fsuae_rp9_dir_edit.text().strip()
            self.config.temp_dir = dialog.temp_dir_edit.text().strip()
            self.config.workbench_135_hd = dialog.workbench_135_hd_edit.text().strip()
            self.config.workbench_211_hd = dialog.workbench_211_hd_edit.text().strip()
            self.config.workbench_311_hd = dialog.workbench_311_hd_edit.text().strip()

    @pyqtSlot()
    def select_dir(self):
        filename = QFileDialog.getExistingDirectory(self, 'Choose directory to show', str(self.current_dir),
                                                    QFileDialog.ShowDirsOnly | QFileDialog.DontUseNativeDialog)
        if filename:
            file = Path(filename)
            if file.is_dir():
                self.current_dir = file
                self.update_dir()

    @pyqtSlot()
    def update_dir(self):
        self.config.current_dir = self.current_dir
        if len(self.current_dir.parts) > 1:
            self.dir_button.setText(self.current_dir.name)
        else:
            self.dir_button.setText(self.current_dir.anchor)
        self.config.show_hidden = self.show_hidden_check.isChecked()
        self.file_list.clear()

        folders = []
        files = []
        for path in self.current_dir.iterdir():
            if not path.name.startswith('.') or self.config.show_hidden:
                if path.is_dir():
                    folders.append(path.name)
                elif path.is_file():
                    if path.name.lower().endswith('.rp9') and is_zipfile(str(path)):
                        files.append(path.name)

        if len(self.current_dir.parts) > 1:
            self.file_list.addItem(QListWidgetItem(QIcon.fromTheme('folder'), '..'))

        folders.sort(key=str.lower)
        for fol in folders:
            self.file_list.addItem(QListWidgetItem(QIcon.fromTheme('folder'), fol))
        files.sort(key=str.lower)
        for fil in files:
            self.file_list.addItem(
                QListWidgetItem(QIcon.fromTheme('fs-uae', QIcon.fromTheme('package-x-generic')), fil))

    @pyqtSlot(QListWidgetItem)
    def show_file(self, item):
        name = item.text()
        if name == '..':
            self.current_dir = self.current_dir.parent
            self.update_dir()
        else:
            file = self.current_dir.joinpath(name)
            if file.is_dir():
                self.current_dir = file
                self.update_dir()
            elif file.is_file():
                self.rp9_viewer.open_rp9(file)

    def closeEvent(self, event):
        self.config.mainwindow_witdh = self.width()
        self.config.mainwindow_height = self.height()
        self.config.mainwindow_x = self.x()
        self.config.mainwindow_y = self.y()
        self.config.save()

        super(MainWindow, self).closeEvent(event)
