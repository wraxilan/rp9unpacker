#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# The gui
#

import gettext
import os

import constants as const

from config import Config
from pathlib import Path
from PyQt5.QtWidgets import QLabel, QLineEdit, QMainWindow, QDialog, QLineEdit, QPushButton, QWidget, QHBoxLayout, QVBoxLayout, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot

localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locales')
translate = gettext.translation('gui', localedir, fallback=True)
_ = translate.gettext


class MainWindow(QMainWindow):

    def __init__(self, *args):
        QMainWindow.__init__(self, *args)
        self.setWindowTitle(_('rp9UnpAckEr for FS-UAE ' + const.VERSION))
        self.setWindowIcon(QIcon(str(Path(__file__).parents[0].joinpath('images').joinpath('amigaball.png'))))

        # load config
        self.config = Config()
        self.config.load()

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
        self.hello_world_label = QLabel(_('Hello World!'))
        self.update_text_button = QPushButton(_('Update'))
        self.edit_text = QLineEdit()

        # Connects
        self.update_text_button.clicked.connect(self.update_text)
        self.about_action.triggered.connect(self.show_about_dialog)
        self.exit_action.triggered.connect(self.close)

        # Layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        main_layout.addWidget(self.hello_world_label)
        main_layout.addWidget(self.edit_text)
        main_layout.addWidget(self.update_text_button)

    @pyqtSlot()
    def update_text(self):
        self.hello_world_label.setText(self.edit_text.text())

    @pyqtSlot()
    def show_about_dialog(self):
        #QMessageBox.information(self, 'Test', 'Test\nTest!')
        dialog = QDialog(self)
        eingabe = QLineEdit(dialog)
        ok_button = QPushButton('OK', dialog)

        layout = QHBoxLayout()
        layout.addWidget(eingabe)
        layout.addWidget(ok_button)
        dialog.setLayout(layout)
        ok_button.clicked.connect(dialog.accept)
        #buttonAbbrechen.clicked.connect(dialog.reject)

        dialog.resize(600, 400)
        result = dialog.exec_()
        #if result == QDialog.Accepted:
        #    eingabe = str(eingabe.text())
        #    print(eingabe)
        #else:
        #    print("Abgebrochen")

    def closeEvent(self, event):
        self.config.mainwindow_witdh = self.width()
        self.config.mainwindow_height = self.height()
        self.config.mainwindow_x = self.x()
        self.config.mainwindow_y = self.y()
        self.config.save()

        super(MainWindow, self).closeEvent(event)
