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
import subprocess

from xml.etree import ElementTree
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
        self.configuration_floppy_count = 0
        self.configuration_hdf_boot = None
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

    info.configuration_floppy_count = 0
    peripherals = configuration.findall('{http://www.retroplatform.com}peripheral')
    for peripheral in peripherals:
        if peripheral.attrib.get('type', '') == 'dd' and peripheral.text == 'floppy':
            info.configuration_floppy_count = info.configuration_floppy_count + 1

    boot = configuration.find('{http://www.retroplatform.com}boot')
    if boot is not None:
        if boot.attrib.get('type', '') == 'hdf':
            info.configuration_hdf_boot = boot.text


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
    config_file = __extract_and_write_config(rp9_file, info, temp_dir, override=True)

    subprocess.run(['fs-uae', str(config_file)])


def __extract_and_write_config(rp9_file, info, media_base_dir, override=False):

    # pre check
    if info.media is None or len(info.media) == 0:
        raise Rp9UtilException(_('The rp9 file as no media files!'))

    sorted_media = sorted(info.media, key=lambda m: m.priority)
    floppy_list = []
    hd_list = []
    for media in sorted_media:
        if media.type == 'floppy':
            floppy_list.append(media)
        elif media.type == 'harddrive':
            hd_list.append(media)
        else:
            raise Rp9UtilException(_('The rp9 file contains an unsupported media type!'))

    boot_hdfs = {
        '135': '/home/jens/Dokumente/FS-UAE/Hard Drives/workbench-135_org.hdf',
        '211': '/home/jens/Dokumente/FS-UAE/Hard Drives/workbench-211_org.hdf',
        '311': '/home/jens/Dokumente/FS-UAE/Hard Drives/workbench-311_org.hdf'
    }

    if info.configuration_hdf_boot is not None and len(info.configuration_hdf_boot) > 0 and \
            info.configuration_hdf_boot not in boot_hdfs:
        raise Rp9UtilException(_('The rp9 file contains an unsupported boot harddisk!'))

    # extract media
    media_name = None
    if info.description_title is None or len(info.description_title) == 0:
        name = rp9_file.name
        if name.lower().endswith('.rp9') and len(name) > 4:
            media_name = name[:-4]
    else:
        media_name = info.description_title

    media_dir = media_base_dir.joinpath(media_name)

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
    config_file = media_dir.joinpath(media_name + '.fs-uae')
    with open(str(config_file), 'w', encoding='utf-8') as config:
        config.write('# FS-UAE configuration saved by rp9UnpAckEr\n\n')
        config.write('[fs-uae]\n')

        # write mode
        models = {
            'a-500': 'A500',
            'a-500plus': 'A500+',
            'a-600': 'A600',
            'a-1000': 'A1000',
            'a-1200': 'A1200',
            'a-2000': 'A500',
            'a-3000': 'A3000',
            'a-4000': 'A4000/040'
        }

        if info.configuration_system not in models:
            print('Unknown amiga system: ' + info.configuration_system + ' Using default.')

        config.write('amiga_model = ')
        config.write(models.get(info.configuration_system, 'a-500'))
        config.write('\n')

        # write harddisks
        offset = 0
        if info.configuration_hdf_boot is not None and len(info.configuration_hdf_boot) > 0:
            config.write('hard_drive_0 = ')
            config.write(boot_hdfs.get(info.configuration_hdf_boot))
            config.write('\n')
            offset = 1

        length = len(hd_list)
        for i in range(length):
            config.write('hard_drive_' + str(i + offset))
            config.write(' = ')
            config.write(str(media_dir.joinpath(hd_list[i].name)))
            config.write('\n')

        # write floppies
        floppy_count = 1
        if info.configuration_floppy_count > 1:
            floppy_count = info.configuration_floppy_count

        length = len(floppy_list)
        if length > floppy_count:
            length = floppy_count
        for i in range(length):
            config.write('floppy_drive_' + str(i))
            config.write(' = ')
            config.write(str(media_dir.joinpath(floppy_list[i].name)))
            config.write('\n')
            config.write('floppy_drive_' + str(i))
            config.write('_sounds = off\n')

        config.write('floppy_drive_count = ')
        config.write(str(floppy_count))
        config.write('\n')
        config.write('floppy_drive_speed = 800\n')
        config.write('floppy_drive_volume_empty = 0\n')

        length = len(floppy_list)
        if length > 1:
            for i in range(length):
                config.write('floppy_image_' + str(i))
                config.write(' = ')
                config.write(str(media_dir.joinpath(floppy_list[i].name)))
                config.write('\n')

    return config_file
