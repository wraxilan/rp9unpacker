#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# The gui
#

import constants as const
from config import Config

import gettext
import os

from pathlib import Path
from PyQt5.QtGui import QIcon, QPixmap, QTextCursor
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import (QAbstractItemView, QAction, QCheckBox, QDialog, QFileDialog, QHBoxLayout, QLabel,
                             QListWidget, QListWidgetItem, QMainWindow, QPlainTextEdit, QPushButton, QSizePolicy,
                             QVBoxLayout, QWidget)

images_path = Path(__file__).parent.joinpath('images')
resources_path = Path(__file__).parent.joinpath('resources')

localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locales')
translate = gettext.translation('gui', localedir, fallback=True)
_ = translate.gettext


class AboutDialog(QDialog):

    def __init__(self, parent):
        super().__init__(parent)

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

        button = QWidget()
        buttonlyt = QHBoxLayout()
        button.setLayout(buttonlyt)
        dlglyt.addWidget(button)
        ok_button = QPushButton('OK', self)
        # ok_button = QPushButton(QIcon.fromTheme('dialog-ok'), 'OK', self)
        # ok_button.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        buttonlyt.addStretch()
        buttonlyt.addWidget(ok_button)
        buttonlyt.addStretch()

        self.resize(600, 400)
        ok_button.setFocus()
        ok_button.clicked.connect(self.accept)


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
        self.open_file_action = QAction(_('Settings'), self)
        self.exit_action = QAction(_('Exit'), self)
        self.exit_action.setMenuRole(QAction.QuitRole)

        file_menu = self.menuBar().addMenu(_('File'))
        file_menu.addAction(self.open_file_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        self.about_action = QAction(_('About'), self)
        help_menu = self.menuBar().addMenu(_('Help'))
        help_menu.addAction(self.about_action)

        # Widgets
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.dir_button = QPushButton(QIcon.fromTheme('folder-open'), '', self)
        self.show_hidden_check = QCheckBox('Show hidden files', self)

        # Connects
        self.dir_button.clicked.connect(self.select_dir)
        self.about_action.triggered.connect(self.show_about_dialog)
        self.exit_action.triggered.connect(self.close)
        self.show_hidden_check.stateChanged.connect(self.update_dir)
        self.file_list.itemDoubleClicked.connect(self.show_file)

        # Layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        main_layout.addWidget(self.dir_button)
        main_layout.addWidget(self.file_list)
        main_layout.addWidget(self.show_hidden_check)

        self.file_list.setFocus()
        self.update_dir()

    @pyqtSlot()
    def update_text(self):
        self.hello_world_label.setText(self.edit_text.text())

    @pyqtSlot()
    def show_about_dialog(self):
        dialog = AboutDialog(self)
        dialog.exec_()

        #
        # result = dialog.exec_()
        # if result == QDialog.Accepted:
        #    eingabe = str(eingabe.text())
        #    print(eingabe)
        # else:
        #    print("Abgebrochen")

    @pyqtSlot()
    def select_dir(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly
        filename, ignore = QFileDialog.getOpenFileName(self, 'Choose directory to show', str(self.current_dir),
                                                       'All Files (*)', options=options)
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
        show_hidden = self.show_hidden_check.isChecked()
        self.file_list.clear()

        folders = []
        files = []
        for path in self.current_dir.iterdir():
            if not path.name.startswith('.') or show_hidden:
                if path.is_dir():
                    folders.append(path.name)
                elif path.is_file():
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

    def closeEvent(self, event):
        self.config.mainwindow_witdh = self.width()
        self.config.mainwindow_height = self.height()
        self.config.mainwindow_x = self.x()
        self.config.mainwindow_y = self.y()
        self.config.save()

        super(MainWindow, self).closeEvent(event)
