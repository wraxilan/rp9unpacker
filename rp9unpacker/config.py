#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# The config handling
#

import json
import sys
import traceback

from pathlib import Path


class Config:

    def __init__(self):
        self.mainwindow_witdh = 800
        self.mainwindow_height = 600
        self.mainwindow_x = 0
        self.mainwindow_y = 0

        self.current_dir = Path.home()
        self.show_hidden = False

    def load(self):
        configfile = Path.home().joinpath('.rp9unpacker')
        if configfile.exists():
            strfile = str(configfile)
            try:
                with open(strfile) as json_data_file:
                    self.__parsedata(json.load(json_data_file))

            except Exception:
                sys.stderr.write('Could not read config file: \'' + strfile + '\'\n')
                traceback.print_exc(file=sys.stderr)

    def __parsedata(self, data):
        mainwin = data.get('mainwindow', None)
        if mainwin is not None:
            self.mainwindow_witdh = mainwin.get('witdh', self.mainwindow_witdh)
            self.mainwindow_height = mainwin.get('height', self.mainwindow_height)
            self.mainwindow_x = mainwin.get('x', self.mainwindow_x)
            self.mainwindow_y = mainwin.get('y', self.mainwindow_y)

        filemanager = data.get('filemanager', None)
        if filemanager is not None:
            filename = filemanager.get('current-dir', None)
            if filename is not None:
                curdir = Path(filename)
                if curdir.is_dir():
                    self.current_dir = curdir
            self.show_hidden = filemanager.get('show-hidden', self.show_hidden)

    def save(self):
        mainwin = {
            'witdh': self.mainwindow_witdh,
            'height': self.mainwindow_height,
            'x': self.mainwindow_x,
            'y': self.mainwindow_y,
        }
        filemanager = {
            'current-dir': str(self.current_dir),
            'show-hidden': self.show_hidden,
        }
        data = {
            'mainwindow': mainwin,
            'filemanager': filemanager,
        }

        configfile = Path.home().joinpath('.rp9unpacker')
        strfile = str(configfile)
        with open(strfile, 'w') as outfile:
            json.dump(data, outfile, indent=4)
