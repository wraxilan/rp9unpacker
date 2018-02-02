#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# The gui
#

import constants as const
from config import Config

import gettext
import os
import traceback

from pathlib import Path
from zipfile import ZipFile, is_zipfile
from PyQt5.QtGui import QIcon, QPixmap, QTextCursor
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import (QAbstractItemView, QAction, QCheckBox, QDialog, QFileDialog, QHBoxLayout, QLabel,
                             QListWidget, QListWidgetItem, QMainWindow, QPlainTextEdit, QPushButton, QSizePolicy,
                             QSplitter, QVBoxLayout, QWidget, QFrame, QDialogButtonBox, QGridLayout, QLineEdit)

images_path = Path(__file__).parent.joinpath('images')
resources_path = Path(__file__).parent.joinpath('resources')

localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locales')
translate = gettext.translation('gui', localedir, fallback=True)
_ = translate.gettext


class AboutDialog(QDialog):

    def __init__(self, *args):
        QDialog.__init__(self, *args)

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
        # button_box.rejected.connect(self.reject)
        dlglyt.addWidget(button_box)

        self.resize(600, 400)


class Rp9Viewer(QFrame):

    def __init__(self, *args):
        QFrame.__init__(self, *args)
        self.setFrameShape(QFrame.StyledPanel | QFrame.Raised)

        type_label = QLabel('Type:')
        type_label.setAlignment(Qt.AlignRight)
        title_label = QLabel('Title:')
        title_label.setAlignment(Qt.AlignRight)
        genre_label = QLabel('Genre:')
        genre_label.setAlignment(Qt.AlignRight)

        self.type_edit = QLineEdit()
        self.title_edit = QPlainTextEdit()
        self.genre_edit = QLineEdit()

        grid = QGridLayout()
        self.setLayout(grid)
        grid.setSpacing(10)

        grid.addWidget(type_label, 0, 0)
        grid.addWidget(self.type_edit, 0, 1)
        grid.addWidget(title_label, 0, 2)
        grid.addWidget(self.title_edit, 0, 3, 5, 1)

        grid.addWidget(genre_label, 1, 0)
        grid.addWidget(self.genre_edit, 1, 1)



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
        self.splitter = QSplitter(Qt.Horizontal)
        self.rp9_viewer = Rp9Viewer()
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
        self.setCentralWidget(self.splitter)

        left_widget = QWidget()
        self.splitter.addWidget(left_widget)
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)

        left_layout.addWidget(self.dir_button)
        left_layout.addWidget(self.file_list)
        left_layout.addWidget(self.show_hidden_check)

        right_widget = QWidget()
        self.splitter.addWidget(right_widget)
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)

        right_layout.addWidget(self.rp9_viewer)

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
                self.open_rp9(file)

    def open_rp9(self, file):
        with ZipFile(str(file)) as zipfile:
            print(zipfile.filelist)

    def closeEvent(self, event):
        self.config.mainwindow_witdh = self.width()
        self.config.mainwindow_height = self.height()
        self.config.mainwindow_x = self.x()
        self.config.mainwindow_y = self.y()
        self.config.save()

        super(MainWindow, self).closeEvent(event)
