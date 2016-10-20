#! python3

import re
import uuid
from datetime import datetime
from glob import glob
from os import path

import yaml
from fontTools import subset
from fontTools.ttLib import TTFont
from jinja2 import Environment, FileSystemLoader

jinja2_env = Environment(
    loader=FileSystemLoader(path.join(path.dirname(__file__), 'templates')))


def load_font_list(root_dir):
    dirs = glob(path.join(root_dir, '[!.]*'))
    font_list = {}
    for dir_path in dirs:
        if not path.isdir(dir_path):
            continue
        dir_name = path.basename(dir_path)
        font_list[dir_name] = [
            path.relpath(x, dir_path)
            for x in glob(path.join(dir_path, '*'))
            if re.search(r'\.(ttf|woff)$', x)
        ]
        font_list[dir_name].sort()
    return font_list


def generate_fontname():
    name = 'JPT-{random_str}'.format(random_str=uuid.uuid4().hex.upper())
    return name


def subset_font(basefile_path, exportfile_path, text):
    subset.main([
        basefile_path,
        "--output-file={}".format(exportfile_path),
        "--flavor=woff",
        "--text={}".format(text),
        "--name-IDs=''",
        "--no-name-legacy"
    ])
    return


def generate_license(
    font_path, export_familyname,
    request_data, url_root, owner
):
    font_dir = path.dirname(font_path)
    config_filepath = path.join(font_dir, 'config.yaml')
    if not path.isfile(config_filepath):
        raise Exception()

    fd = open(config_filepath, 'r')
    config = yaml.safe_load(fd)
    fd.close()

    if not (
        'license' in config and
        'filename' in config['license'] and
        'type' in config['license']
    ):
        raise Exception()

    license_text = ''
    for license_file in config['license']['filename']:
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
        url=config.get('url', ''),
        form_url='{}/api/font'.format(url_root),
        request=request_data)

    return license_comment
