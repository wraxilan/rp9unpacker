#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Utilities for rp9 file handling
#

import gettext
import os
import sys
import traceback
import io

from xml.etree import ElementTree
from pathlib import Path
from zipfile import ZipFile
from PyQt5.QtGui import QImage

localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locales')
translate = gettext.translation('rp9util', localedir, fallback=True)
_ = translate.gettext


class Rp9UtilException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class Rp9Media:
    def __init__(self):
        self.type = None
        self.priority = None
        self.name = None


class Rp9Help:
    def __init__(self):
        self.priority = None
        self.name = None
        self.text = None


class Rp9Image:
    def __init__(self):
        self.priority = None
        self.name = None
        self.image = None


class Rp9Info:
    def __init__(self):
        self.description_title = None
        self.description_publisher = None
        self.description_type = None
        self.description_genre = None
        self.description_year = None
        self.description_language = None
        self.description_rating = None
        self.description_systemrom = None
        self.configuration_system = None
        self.media = []
        self.embedded_help = []
        self.embedded_images = []


def get_info(file, load_extras=False):
    try:
        with ZipFile(str(file)) as zipfile:
            with zipfile.open('rp9-manifest.xml') as manifest:
                info = Rp9Info()
                __parse_manifest(ElementTree.parse(manifest).getroot(), info)
                __look_for_default_extras(zipfile, info)
                if load_extras:
                    __load_help(zipfile, info)
                    __load_images(zipfile, info)
                return info

    except Exception:
        sys.stderr.write('Could not rp9 file: \'' + str(file) + '\'\n')
        traceback.print_exc(file=sys.stderr)
        raise Rp9UtilException(_('This is not a valid rp9 file!'))


def __parse_manifest(root, info):
    application = root.find('{http://www.retroplatform.com}application')
    if application is not None:
        description = application.find('{http://www.retroplatform.com}description')
        if description is not None:
            system = description.find('{http://www.retroplatform.com}system-filename')
            if system is None or system.text != 'Amiga':
                raise Rp9UtilException(_('This is not a Amiga rp9 file!'))
            __parse_description(description, info)
        configuration = application.find('{http://www.retroplatform.com}configuration')
        if configuration is not None:
            __parse_configuration(configuration, info)
        media = application.find('{http://www.retroplatform.com}media')
        if media is not None:
            __parse_media(media, info)
        extras = application.find('{http://www.retroplatform.com}extras')
        if extras is not None:
            __parse_extras(extras, info)


def __parse_configuration(configuration, info):
    system = configuration.find('{http://www.retroplatform.com}system')
    if system is not None:
        info.configuration_system = system.text


def __parse_description(description, info):
    for child in description:
        if child.tag == '{http://www.retroplatform.com}title':
            info.description_title = child.text
        elif child.tag == '{http://www.retroplatform.com}entity':
            info.description_publisher = child.text
        elif child.tag == '{http://www.retroplatform.com}type':
            info.description_type = child.text
        elif child.tag == '{http://www.retroplatform.com}genre':
            info.description_genre = child.text
        elif child.tag == '{http://www.retroplatform.com}year':
            info.description_year = child.text
        elif child.tag == '{http://www.retroplatform.com}language':
            info.description_language = child.text
        elif child.tag == '{http://www.retroplatform.com}rating':
            info.description_rating = child.text
        elif child.tag == '{http://www.retroplatform.com}systemrom':
            info.description_systemrom = child.text


def __parse_media(media, info):
    children = media.getchildren()
    length = len(children)
    for i in range(length):
        child = children[i]
        media = Rp9Media()
        info.media.append(media)
        media.type = str(child.tag)
        if media.type.startswith('{http://www.retroplatform.com}'):
            media.type = media.type[len('{http://www.retroplatform.com}'):]
        media.priority = child.attrib.get('priority', '0')
        media.name = child.text


def __parse_extras(extras, info):
    for document in extras.findall('{http://www.retroplatform.com}document'):
        if document.attrib.get('root', '') == 'embedded' and document.attrib.get('type', '') == 'help':
            if document.text.lower().endswith('.txt'):
                helpdoc = Rp9Help()
                info.embedded_help.append(helpdoc)
                helpdoc.priority = document.attrib.get('priority', '0')
                helpdoc.name = document.text

    for image in extras.findall('{http://www.retroplatform.com}image'):
        if image.attrib.get('root', '') == 'embedded':
            imgdoc = Rp9Image()
            info.embedded_images.append(imgdoc)
            imgdoc.priority = image.attrib.get('priority', '0')
            imgdoc.name = image.text


def __look_for_default_extras(zipfile, info):
    if not info.embedded_help:
        try:
            zipinfo = zipfile.getinfo('rp9-help-en.txt')
            if zipinfo is not None:
                helpdoc = Rp9Help()
                info.embedded_help.append(helpdoc)
                helpdoc.priority = '1'
                helpdoc.name = 'rp9-help-en.txt'
        except KeyError:
            pass

    if not info.embedded_images:
        try:
            zipinfo = zipfile.getinfo('rp9-preview.png')
            if zipinfo:
                imgdoc = Rp9Image()
                info.embedded_images.append(imgdoc)
                imgdoc.priority = '1'
                imgdoc.name = 'rp9-preview.png'
        except KeyError:
            pass


def __load_help(zipfile, info):
    for doc in info.embedded_help:
        try:
            with zipfile.open(doc.name) as text:
                doc.text = io.TextIOWrapper(io.BytesIO(text.read())).read()
        except KeyError:
            sys.stderr.write('Could not find embedded document: \'' + doc.name + '\'\n')
            traceback.print_exc(file=sys.stderr)


def __load_images(zipfile, info):
    for image in info.embedded_images:
        try:
            with zipfile.open(image.name) as file:
                image.image = QImage()
                image.image.loadFromData(file.read())
        except KeyError:
            sys.stderr.write('Could not find embedded image: \'' + image.name + '\'\n')
            traceback.print_exc(file=sys.stderr)


def __check_dir(temp_path):
    if temp_path.is_file():
        raise Rp9UtilException(_('The configured temp directory is an existing file!'))

    if not temp_path.is_dir():
        parent = temp_path.parent
        if parent.is_dir():
            temp_path.mkdir()
        else:
            raise Rp9UtilException(_('The configured temp directory doesn\'t exist!'))


def __delete_dir(path):
    for sub in path.iterdir():
        if sub.is_dir():
            __delete_dir(sub)
        else:
            sub.unlink()
    path.rmdir()


def run_from_temp(rp9_file, temp_dir):
    info = get_info(rp9_file)
    __check_dir(temp_dir)
    __extract_files(rp9_file, info, temp_dir, override=True)


def __extract_files(rp9_file, info, dir, override=False):
    if info.media is None or len(info.media) == 0:
        raise Rp9UtilException(_('The rp9 file as no media files!'))

    media_dir = None
    if info.description_title is None or len(info.description_title) == 0:
        name = rp9_file.name
        if name.lower().endswith('.rp9') and len(name) > 4:
            name = name[:-4]
            media_dir = dir.joinpath(name)
    else:
        media_dir = dir.joinpath(info.description_title)

    if media_dir.is_file():
        raise Rp9UtilException(_('Couldn\'t extract files! Directory already exists as file.'))

    if media_dir.is_dir() and override:
        __delete_dir(media_dir)
        media_dir.mkdir()
    else:
        media_dir.mkdir()

    with ZipFile(str(rp9_file)) as zipfile:
        for media in info.media:
            media_file = media_dir.joinpath(media.name)
            if not media_file.is_file() and not media_file.is_dir() and not media_file.is_symlink():
                zipfile.extract(media.name, media_dir)

    # write config
