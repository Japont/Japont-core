#! python3

import re
import uuid
from datetime import datetime
from glob import glob
from os import path

import yaml
from fontTools.subset import Options, Subsetter, load_font, save_font
from fontTools.ttLib import TTFont
from jinja2 import Environment, FileSystemLoader

jinja2_env = Environment(
    loader=FileSystemLoader(path.join(path.dirname(__file__), 'templates')))


def load_font_list(search_dir, root_dir=None):
    if root_dir is None:
        root_dir = search_dir
    dirs = glob(path.join(search_dir, '[!.]*'))
    font_list = []
    for dir_path in dirs:
        if not path.isdir(dir_path):
            continue
        font_list.extend(load_font_list(dir_path, root_dir))
        font_list.extend([
            path.relpath(filename, root_dir)
            for filename in glob(path.join(dir_path, '*'))
            if re.search(r'\.(ttf|woff|otf)$', filename)
        ])
    font_list.sort()
    return font_list


def generate_fontname():
    name = 'JPT-{random_str}'.format(random_str=uuid.uuid4().hex.upper())
    return name


def subset_font(basefile_path, buff, text):
    options = Options()
    options.name_IDs = []
    options.obfuscate_names = True
    options.flavor = 'woff'

    font = load_font(basefile_path, options)
    subsetter = Subsetter(options=options)
    subsetter.populate(text=text)
    subsetter.subset(font)
    save_font(font, buff, options)

    font.close()
    buff.seek(0)
    return


def generate_license(
    font_path, export_familyname,
    request_data, post_url, owner
):
    font_dir = path.dirname(font_path)
    config_filepath = path.join(font_dir, 'info.yml')
    if not path.isfile(config_filepath):
        raise Exception('{} is not found.'.format(config_filepath))

    fd = open(config_filepath, 'r')
    config = yaml.safe_load(fd)
    fd.close()

    if not (
        'license' in config and
        'files' in config['license'] and
        'type' in config['license']
    ):
        raise Exception('license section is not set completely.')

    license_text = ''
    for license_file in config['license']['files']:
        license_file_path = path.join(font_dir, license_file)
        license_text += "\n" + open(license_file_path, 'r').read()
        license_text += "\n----------------------------\n"

    license_template = jinja2_env.get_template(
        path.join('./LICENSES', config['license']['type']))

    license_comment = license_template.render(
        license=license_text,
        export_name=export_familyname,
        original_name=TTFont(font_path)['name'].names[1],
        year=datetime.today().year,
        owner=owner,
        url=config.get('website', ''),
        post_url=post_url,
        request_data=request_data)

    return license_comment
