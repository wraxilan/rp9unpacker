#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# The config handling
#

import json
import platform
import subprocess
import sys
import tempfile
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

        self.fsuae_command = 'fs-uae'
        self.fsuae_documents_dir = ''
        self.fsuae_rp9_dir = ''
        self.temp_dir = ''
        self.workbench_135_hd = ''
        self.workbench_211_hd = ''
        self.workbench_311_hd = ''

        # determine default values for linux
        self.temp_dir = tempfile.gettempdir()
        if 'Linux' == platform.system():
            try:
                command = subprocess.getoutput('which fs-uae')
                if command is not None and len(command) > 0:
                    if Path(command).is_file():
                        self.fsuae_command = command

                docs = subprocess.getoutput('xdg-user-dir DOCUMENTS')
                if docs is not None and len(docs) > 0:
                    docspath = Path(docs).joinpath('FS-UAE')
                    if docspath.is_dir():
                        self.fsuae_documents_dir = str(docspath)
                        self.fsuae_rp9_dir = str(docspath.joinpath('Amiga Forever'))

            except Exception:
                sys.stderr.write('Could not determine the system file layout!\n')
                traceback.print_exc(file=sys.stderr)

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

        fs_uae = data.get('fs-uae', None)
        if fs_uae is not None:
            self.fsuae_command = fs_uae.get('command', self.fsuae_command)
            self.fsuae_documents_dir = fs_uae.get('documents-dir', self.fsuae_documents_dir)
            self.fsuae_rp9_dir = fs_uae.get('rp9-dir', self.fsuae_rp9_dir)
            self.temp_dir = fs_uae.get('temp-dir', self.temp_dir)
            self.workbench_135_hd = fs_uae.get('workbench_135_hd', self.workbench_135_hd)
            self.workbench_211_hd = fs_uae.get('workbench_211_hd', self.workbench_211_hd)
            self.workbench_311_hd = fs_uae.get('workbench_311_hd', self.workbench_311_hd)

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
        fs_uae = {
            'command': self.fsuae_command,
            'documents-dir': self.fsuae_documents_dir,
            'rp9-dir': self.fsuae_rp9_dir,
            'temp-dir': self.temp_dir,
            'workbench_135_hd': self.workbench_135_hd,
            'workbench_211_hd': self.workbench_211_hd,
            'workbench_311_hd': self.workbench_311_hd,
        }
        data = {
            'mainwindow': mainwin,
            'filemanager': filemanager,
            'fs-uae': fs_uae,
        }

        configfile = Path.home().joinpath('.rp9unpacker')
        strfile = str(configfile)
        with open(strfile, 'w') as outfile:
            json.dump(data, outfile, indent=4)
