#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# The config handling
#

import json
import sys

from pathlib import Path


class Config:

    def __init__(self):
        self.mainwindow_witdh = 800
        self.mainwindow_height = 600
        self.mainwindow_x = 0
        self.mainwindow_y = 0

    def load(self):
        configfile = Path.home().joinpath('.rp9unpacker')
        if configfile.exists():
            strfile = str(configfile)
            try:
                with open(strfile) as json_data_file:
                    self.__parsedata(json.load(json_data_file))

            except IOError as e:
                sys.stderr.write('Could not read config file: \'' + strfile + '\'\n')
                sys.stderr.write(str(e))
                sys.stderr.write('\n')
                sys.stderr.flush()

    def __parsedata(self, data):
        mainwin = data['mainwindow']
        if mainwin is not None:
            self.mainwindow_witdh = self.__parseint(mainwin['witdh'], self.mainwindow_witdh)
            self.mainwindow_height = self.__parseint(mainwin['height'], self.mainwindow_height)
            self.mainwindow_x = self.__parseint(mainwin['x'], self.mainwindow_x)
            self.mainwindow_y = self.__parseint(mainwin['y'], self.mainwindow_y)

    @staticmethod
    def __parseint(val, defval):
        if val is not None:
            return int(val)
        else:
            return defval

    def save(self):
        mainwin = {
            'witdh': self.mainwindow_witdh,
            'height': self.mainwindow_height,
            'x': self.mainwindow_x,
            'y': self.mainwindow_y,
        }
        data = {'mainwindow': mainwin}

        configfile = Path.home().joinpath('.rp9unpacker')
        strfile = str(configfile)
        with open(strfile, 'w') as outfile:
            json.dump(data, outfile, indent=4)
