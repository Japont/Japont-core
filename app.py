#! python3

import zipfile
from io import BytesIO
from logging import getLogger
from os import environ, path, remove
from os.path import abspath
from time import time
from zipfile import ZipFile

import japont
from flask import Flask, jsonify, make_response, request, send_file
from flask_cors import CORS

# Init
logger = getLogger(__name__)
app = Flask(__name__, static_url_path='')
cors = CORS(app, intercept_exceptions=False, max_age=31536000,
            resources={r'/api/*': {}}, expose_headers=['ETag'])


@app.route('/')
def root():
    return app.send_static_file('index.html')


@app.route('/api/fonts', methods=['GET'])
def get_font_list():
    response = make_response(
        jsonify(app.config['font_list']))
    return response


@app.route('/api/font/<path:font_path>', methods=['POST'])
def generate_font_zip(font_path):
    # valid check
    if not request.data:
        raise ValueError()

    request_data = {
        'file_path': font_path,
        'text': request.data.decode('utf-8'),
    }

    # file
    basefile_path = abspath(
        path.join(app.config['fonts_dir'], request_data['file_path']))

    # valid check
    if not (basefile_path.find(app.config['fonts_dir']) == 0):
        raise ValueError()
    if not path.isfile(basefile_path):
        raise IOError()

    # create fontname
    export_familyname = japont.generate_fontname()

    export_filename = '{}.woff'.format(export_familyname)
    export_path = path.join('/tmp', export_filename)

    # subsetting
    japont.subset_font(
        basefile_path=basefile_path,
        exportfile_path=export_path,
        text=request_data['text'])

    # make license
    license = japont.generate_license(
        font_path=basefile_path,
        export_familyname=export_familyname,
        request_data=request_data['text'],
        url_root=request.url_root,
        owner=app.config['owner'])

    # make zip
    zip_buff = BytesIO()
    zip_archive = \
        ZipFile(zip_buff, mode='w', compression=app.config['zip_compression'])
    zip_archive.write(export_path, arcname=export_filename)
    zip_archive.writestr('LICENSE', license)
    zip_archive.close()
    remove(export_path)

    zip_buff.seek(0)
    response = send_file(
        zip_buff,
        mimetype='application/zip',
        as_attachment=True,
        attachment_filename='font.zip')
    response.status_code = 201

    return response


@app.route('/api', defaults={'path': ''})
@app.route('/api/<path:path>')
def api_path_not_found(path):
    response = jsonify(error='Invalid url')
    response.status_code = 400
    return response


@app.errorhandler(ValueError)
def handle_invalid_value(error):
    response = jsonify(error='Invalid value')
    response.status_code = 400
    return response


@app.errorhandler(IOError)
def handle_not_found(error):
    response = jsonify(error='Not found')
    response.status_code = 404
    return response


@app.errorhandler(Exception)
def handle_error(error):
    logger.exception(error)
    response = jsonify(error='Internal error')
    response.status_code = 500
    return response


@app.after_request
def add_x_robots_tag(response):
    response.headers['X-Robots-Tag'] = \
        environ.get('X_ROBOTS_TAG', 'noindex, nofollow')
    return response

# config
app.config['owner'] = environ.get('PUBLISHER', 'Anonymous')
app.config['root_dir'] = path.dirname(__file__)
app.config['fonts_dir'] = abspath(
    path.join(app.config['root_dir'], environ.get('FONTS_PATH', './fonts')))
app.config['font_list'] = japont.load_font_list(app.config['fonts_dir'])
app.config['server_updated_date'] = hex(int(time()))[2:]

if environ.get('ZIP_COMPRESSION_TYPE', 'ZIP_STORED') in {
    'ZIP_STORED', 'ZIP_DEFLATED', 'ZIP_BZIP2', 'ZIP_LZMA'
}:
    app.config['zip_compression'] = \
        getattr(zipfile, environ.get('ZIP_COMPRESSION_TYPE', 'ZIP_STORED'))

if __name__ == '__main__':
    port = int(environ.get('PORT', 8000))
    host = environ.get('BIND_IP', '0.0.0.0')
    app.run(host=host, port=port)
