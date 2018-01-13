#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# rp9UnpAckEr main file
#

import gui
import sys

from PyQt5.QtWidgets import QApplication


def main(argv):
    app = QApplication(argv)
    mainwindow = gui.MainWindow()
    mainwindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main(sys.argv)
