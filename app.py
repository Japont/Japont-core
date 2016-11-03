#! python3

import json
import zipfile
from datetime import timezone
from io import BytesIO
from logging import getLogger
from os import environ, path
from os.path import abspath
from time import time
from zipfile import ZipFile

import japont
from Crypto.Hash import SHA512
from flask import Flask, Response, jsonify, make_response, request, send_file
from flask_cors import CORS
from werkzeug.contrib.cache import SimpleCache

# Init
logger = getLogger(__name__)
app = Flask(__name__, static_url_path='')
cors = CORS(app, intercept_exceptions=False, resources={r'/api/*': {}})
cache = SimpleCache()


@app.route('/')
def root():
    return app.send_static_file('index.html')


@app.route('/api/fonts', methods=['GET'])
def get_font_list():
    font_list = [
        path.splitext(font_path)[0]
        for font_path in app.config['font_list']
    ]
    response = make_response(jsonify(font_list))
    return response


@app.route('/api/fonts/<path:request_font_path>', methods=['GET'])
def response_font_zip_from_cache(request_font_path):
    if not request.args.get('hash'):
        raise ValueError()

    if request.if_modified_since:
        if_modified_since = \
            request.if_modified_since.replace(tzinfo=timezone.utc).timestamp()

    if (
        request.if_modified_since and
        int(app.config['server_updated_date']) <= int(if_modified_since)
    ):
        response = Response()
        response.status_code = 304
    else:
        font_file_path = \
            japont.search_font_path(request_font_path, app.config['font_list'])
        hash_key = '{}_{}'.format(
            font_file_path, request.args.get('hash').lower())
        if not cache.has(hash_key):
            raise IOError()

        response = send_file(
            BytesIO(cache.get(hash_key)),
            mimetype='application/zip',
            as_attachment=True,
            attachment_filename='font.zip')

    response.cache_control.must_revalidate = True
    response.cache_control.no_cache = True
    response.cache_control.max_age = 0
    response.expires = time()
    response.last_modified = app.config['server_updated_date']

    return response


@app.route('/api/fonts/<path:request_font_path>', methods=['POST'])
def generate_font_zip(request_font_path):
    # valid check
    if not request.data:
        raise ValueError()

    font_file_path = \
        japont.search_font_path(request_font_path, app.config['font_list'])
    request_data = {
        'file_path': font_file_path,
        'text': request.data.decode('utf-8'),
    }

    # Cache
    hashcalc = SHA512.new()
    hashcalc.update(request.data)
    text_hash = hashcalc.hexdigest().lower()
    hash_key = '{}_{}'.format(request_data['file_path'], text_hash)
    if cache.has(hash_key):
        response = Response()
        response.status_code = 201
        response.location = request.base_url + '?hash={}'.format(text_hash)

    # file
    basefile_path = abspath(
        path.join(app.config['fonts_dir'], request_data['file_path']))

    # valid check
    if not (basefile_path.find(app.config['fonts_dir']) == 0):
        raise ValueError('Path is invalid.')
    if not path.isfile(basefile_path):
        raise IOError('Font is not found.')

    # create fontname
    export_familyname = japont.generate_fontname()

    export_filename = '{}.woff'.format(export_familyname)

    # subsetting
    with BytesIO() as font_buff:
        japont.subset_font(
            basefile_path=basefile_path,
            buff=font_buff,
            text=request_data['text'])
        font_bytes = font_buff.getvalue()

    # info.json
    font_info = japont.load_font_info(basefile_path)

    # make license
    license = japont.generate_license(
        font_path=basefile_path,
        export_familyname=export_familyname,
        request_data=request_data['text'],
        post_url=request.base_url,
        owner=app.config['owner'],
        font_info=font_info)

    # make zip
    with BytesIO() as zip_buff:
        zip_archive = ZipFile(zip_buff, mode='w',
                              compression=app.config['zip_compression'])
        zip_archive.writestr(export_filename, font_bytes)
        zip_archive.writestr('LICENSE', license)
        zip_archive.writestr('info.json', json.dumps(font_info))
        zip_archive.close()
        zip_buff.seek(0)

        cache.set(hash_key, zip_buff.getvalue())

    response = Response()
    response.status_code = 201
    response.location = request.base_url + '?hash={}'.format(text_hash)

    return response


@app.route('/api', defaults={'path': ''})
@app.route('/api/<path:path>')
def api_path_not_found(path):
    response = jsonify(error='Invalid url')
    response.status_code = 400
    return response


@app.errorhandler(ValueError)
def handle_invalid_value(error):
    logger.exception(error)
    response = jsonify(error='Invalid value')
    response.status_code = 400
    return response


@app.errorhandler(IOError)
def handle_not_found(error):
    logger.exception(error)
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
app.config['owner'] = environ.get('SERVER_OWNER', 'Anonymous')
app.config['root_dir'] = path.dirname(__file__)
app.config['fonts_dir'] = abspath(path.join(
    app.config['root_dir'], environ.get('FONTS_DIR_PATH', './fonts')))
app.config['font_list'] = japont.load_font_list(app.config['fonts_dir'])
app.config['server_updated_date'] = time()

if environ.get('ZIP_COMPRESSION_TYPE', 'ZIP_STORED') in {
    'ZIP_STORED', 'ZIP_DEFLATED', 'ZIP_BZIP2', 'ZIP_LZMA'
}:
    app.config['zip_compression'] = \
        getattr(zipfile, environ.get('ZIP_COMPRESSION_TYPE', 'ZIP_STORED'))

if __name__ == '__main__':
    port = int(environ.get('PORT', 8000))
    host = environ.get('BIND_IP', '0.0.0.0')
    app.run(host=host, port=port)
