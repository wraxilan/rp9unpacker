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
from PyQt5.QtWidgets import QLabel, QPlainTextEdit, QMainWindow, QDialog, QLineEdit, QPushButton, QWidget, QHBoxLayout, QVBoxLayout, QAction, QSizePolicy
from PyQt5.QtGui import QIcon, QPixmap, QTextCursor
from PyQt5.QtCore import pyqtSlot, Qt


localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locales')
translate = gettext.translation('gui', localedir, fallback=True)
_ = translate.gettext

images_path = Path(__file__).parents[0].joinpath('images')
resources_path = Path(__file__).parents[0].joinpath('resources')


class MainWindow(QMainWindow):

    def __init__(self, *args):
        QMainWindow.__init__(self, *args)
        self.setWindowTitle(_('rp9UnpAckEr for FS-UAE ' + const.VERSION))
        self.setWindowIcon(QIcon(str(images_path.joinpath('amigaball.png'))))

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
        dialog = QDialog(self)
        #eingabe = QLineEdit(dialog)
        # ok_button = QPushButton('OK', dialog)
        #layout.addWidget(ok_button)

        dlglyt = QVBoxLayout()
        dialog.setLayout(dlglyt)

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
        l1 = QLabel(_('rp9UnpAckEr for FS-UAE ' + const.VERSION))
        l1.setStyleSheet("font: bold")
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
        dlglyt.addWidget(textedit)

        button = QWidget()
        buttonlyt = QHBoxLayout()
        button.setLayout(buttonlyt)
        dlglyt.addWidget(button)
        ok_button = QPushButton('OK', dialog)
        # ok_button.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        buttonlyt.addStretch()
        buttonlyt.addWidget(ok_button)
        buttonlyt.addStretch()

        dialog.resize(550, 400)
        ok_button.setFocus()
        ok_button.clicked.connect(dialog.accept)
        dialog.exec_()

        #
        # result = dialog.exec_()
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
