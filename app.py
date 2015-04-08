#! python
# coding: utf-8

import os, re, sys, time, random, json, base64, yaml, threading, httplib, dotenv
from os import path, listdir, remove
from os.path import relpath, isfile, exists, abspath, dirname, basename
from glob import glob
from datetime import datetime
from subprocess import Popen, PIPE
from flask import (
  Flask, request, render_template, Response, jsonify, make_response)

app = Flask(__name__)
app.debug = True

env_file = abspath(path.join('/tmp', '.env'))
if not os.path.exists(env_file):
    f = open(env_file, 'w')
    f.write('')
    f.close()
dotenv.load_dotenv(env_file)

@app.before_request
def before_request():
    if not os.environ.has_key('HEROKU_URL'):
        os.environ['HEROKU_URL'] = request.headers['HOST']
        dotenv.set_key(env_file, 'HEROKU_URL', os.environ['HEROKU_URL'])
        t = threading.Thread(target=ping_me)
        t.start()
    return

@app.route('/')
def index():
    response = make_response(render_template(
      'index.html',
      HEROKU_URL=os.environ['HEROKU_URL']))
    if (os.environ['HEROKU_URL']) != 'japont.herokuapp.com':
        response.headers['X-Robots-Tag'] = 'noindex, nofollow';
    return response

@app.route('/japont.js')
def library_js():
    response = make_response(render_template(
      'japont.js',
      HEROKU_URL=os.environ['HEROKU_URL']))
    response.headers['Content-Type'] = "application/javascript"
    response.headers['Access-Control-Allow-Origin'] = "*"
    return response

@app.route('/fontlist.json')
def fontlist():
    response = make_response(jsonify(**app.config['font_list']))
    response.headers['Content-Type'] = "application/javascript"
    response.headers['Access-Control-Allow-Origin'] = "*"
    return response

@app.route('/font.css', methods=['POST'])
def fontcss():
    try:
        json_data = json.loads(request.data)
        # valid check
        if not isinstance(json_data, dict):
            raise ValueError()
        if False in {
            json_data.has_key('text'),
            json_data.has_key('fontName')
        }:
            raise ValueError()
        if False in {
            isinstance(json_data['text'], unicode),
            isinstance(json_data['fontName'], unicode)
        }:
            raise ValueError()

        # font_filename
        font_dir = path.join(app.config['root_dir'], 'fonts')
        font_filename = json_data['fontName']
        font_filepath = path.join(font_dir, font_filename)
        font_filepath = abspath(font_filepath)

        # valid check
        if not font_filepath.find(abspath(font_dir)) == 0:
            raise ValueError()
        if not isfile(font_filepath):
            raise IOError()

        # export_filename
        tmp_dir = '/tmp'
        unixtime = int(time.time())
        random_str = "".join([
            random.choice("1234567890ABCDEF") for x in xrange(10)
        ])

        export_basename = "JPT-{unixtime}{random_str}".format(
            unixtime=unixtime,
            random_str=random_str)
        if (not isinstance(json_data['fontFamily'], unicode)) or \
           (json_data['fontFamily'] == u''):
            json_data['fontFamily'] = export_basename

        export_filename = "%s.woff" % export_basename
        export_filepath = path.join(tmp_dir, export_filename)
        export_filepath = abspath(export_filepath)

        # make script
        chars = list()
        char_list = list(json_data['text'])
        for char in char_list:
            chars.append(ord(char))

        script = render_template(
            "generate.py",
            chars=json.dumps(chars),
            fontpath=font_filepath,
            exportpath=export_filepath)

        fontforge = Popen(
            "fontforge -lang=py -script",
            shell=True, stdin=PIPE, stdout=PIPE)
        fontforge.stdin.write(script)
        fontforge.stdin.close()
        fontforge.wait()

        fontforge_stdout = fontforge.stdout.read()
        fontforge.stdout.close()
        font_familyname = fontforge_stdout.split('\n')[0]

        export_data = open(export_filepath).read()
        export_base64 = base64.b64encode(export_data)
        remove(export_filepath)

        # make license
        font_origin_url = ""
        license_files = license_type = None
        font_config_path = path.join(dirname(font_filepath), 'config.yaml')
        if isfile(font_config_path):
            f = open(font_config_path, 'r')
            font_config = yaml.safe_load(f)
            f.close()
            if font_config.has_key('url'):
                font_origin_url = font_config['url']
            if font_config.has_key('license'):
                if font_config['license'].has_key('filename'):
                    license_files = font_config['license']['filename']
                if font_config['license'].has_key('type'):
                    license_type = font_config['license']['type']

        if True in {
          license_files is None,
          license_type is None
        }:
            raise Exception()

        license_text = ""
        for license_file in license_files:
            license_file = path.join(dirname(font_filepath), license_file)
            license_text += "\n" + open(license_file).read()
            license_text += "\n----------------------------\n"
        license_comment = render_template(
            'LICENSES/%s' % license_type,
            license=license_text,
            export_name=export_basename,
            font_name=font_familyname,
            year=datetime.today().year,
            owner=app.config['owner'],
            font_url=font_origin_url,
            text=json_data['text'])

    except ValueError:
        response = Response()
        response.status_code = 400
        response.headers['Access-Control-Allow-Origin'] = "*"
        return response
    except IOError:
        response = Response()
        response.status_code = 404
        response.headers['Access-Control-Allow-Origin'] = "*"
        return response
    except Exception:
        response = Response()
        response.status_code = 500
        response.headers['Access-Control-Allow-Origin'] = "*"
        return response

    response = make_response(render_template(
      'font.css',
      export_base64=export_base64,
      font_family=json_data['fontFamily'],
      license=license_comment))
    response.headers['Access-Control-Allow-Origin'] = "*"

    return response

def load_font_list():
    font_dirs = listdir(path.join(app.config['root_dir'], 'fonts'))
    font_list = {}
    for dirname in font_dirs:
        dirpath = path.join(app.config['root_dir'], 'fonts', dirname)
        font_list[dirname] = [relpath(x, dirpath) for x in glob(path.join(dirpath, '*')) if re.search(r"\.(ttf|woff)$", x)]
        font_list[dirname].sort()
    return font_list

def ping_me():
    if os.environ.has_key('HEROKU_URL'):
        conn = httplib.HTTPSConnection(os.environ['HEROKU_URL'])
        conn.request('HEAD', '/')
    t = threading.Timer(5*60, ping_me)
    t.start()
    return

# config
app.config['owner'] = u'3846masa'
app.config['root_dir'] = dirname(__file__)
app.config['font_list'] = load_font_list()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
