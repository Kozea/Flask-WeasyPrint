# coding: utf8
"""
    flask_weasyprint.tests
    ~~~~~~~~~~~~~~~~~~~~~~

    Tests for Flask-WeasyPrint.

    :copyright: (c) 2012 by Simon Sapin.
    :license: BSD, see LICENSE for more details.

"""

import io
import struct
import unittest

import cairo
from flask import Flask, redirect, request, json, jsonify
from werkzeug.test import ClientRedirectError

from flask_weasyprint import make_url_fetcher, HTML, CSS, render_pdf
from flask_weasyprint.test_app import app, document_html


class TestFlaskWeasyPrint(unittest.TestCase):
    def test_url_fetcher(self):
        # A request context is required
        self.assertRaises(RuntimeError, make_url_fetcher)

        # But only for fist creating the fetcher, not for using it.
        with app.test_request_context(base_url='http://example.org/bar/'):
            fetcher = make_url_fetcher()

        result = fetcher('http://example.org/bar/')
        assert result['string'].strip().startswith(b'<!doctype html>')
        assert result['mime_type'] == 'text/html'
        assert result['encoding'] == 'utf-8'
        assert result['redirected_url'] == 'http://example.org/bar/foo/'

        result = fetcher('http://example.org/bar/foo/graph?data=1&labels=A')
        assert result['string'].strip().startswith(b'<svg xmlns=')
        assert result['mime_type'] == 'image/svg+xml'

    def test_wrappers(self):
        with app.test_request_context(base_url='http://example.org/bar/'):
            # HTML can also be used with named parameters only:
            html = HTML(url='http://example.org/bar/foo/')
            css = CSS(url='http://example.org/bar/static/style.css')
        assert hasattr(html, 'root_element')
        assert hasattr(css, 'rules')

    def test_pdf(self):
        client = app.test_client()
        response = client.get('/foo.pdf')
        assert response.status_code == 200
        assert response.mimetype == 'application/pdf'
        pdf = response.data
        assert pdf.startswith(b'%PDF')
        # The link is somewhere in an uncompressed PDF object.
        assert b'/URI (http://packages.python.org/Flask-WeasyPrint/)' in pdf

        with app.test_request_context('/foo/'):
            response = render_pdf(HTML(string=document_html()))
        assert response.mimetype == 'application/pdf'
        assert 'Content-Disposition' not in response.headers
        assert response.data == pdf

        with app.test_request_context('/foo/'):
            response = render_pdf(HTML(string=document_html()),
                                  download_filename='bar.pdf')
        assert response.mimetype == 'application/pdf'
        assert (response.headers['Content-Disposition']
                == 'attachment; filename=bar.pdf')
        assert response.data == pdf

        with app.test_request_context('/foo/'):
            response = render_pdf(HTML(string=document_html()),
                                  download_filename='bar.pdf',
                                  automatic_download=False)
        assert response.mimetype == 'application/pdf'
        assert (response.headers['Content-Disposition']
                == 'inline; filename=bar.pdf')
        assert response.data == pdf

    def test_png(self):
        client = app.test_client()
        response = client.get('/foo.png')
        assert response.status_code == 200
        image = cairo.ImageSurface.create_from_png(io.BytesIO(response.data))
        assert image.get_format() == cairo.FORMAT_ARGB32
        # A5 (148 * 210 mm) at the default 96 dpi
        assert image.get_width() == 560
        assert image.get_height() == 794
        stride = image.get_stride()
        data = image.get_data()

        def get_pixel(x, y):
            # cairo stores 32bit unsigned integers in *native* endianness
            uint32, = struct.unpack_from('=L', data, y * stride + x * 4)
            # The value is ARGB, 8bit per channel
            alpha = uint32 >> 24
            rgb = uint32 & 0xffffff
            assert alpha == 0xff
            return '#%06X' % (rgb)

        colors = [get_pixel(x, 320) for x in [180, 280, 380]]
        assert colors == app.config['GRAPH_COLORS']
        assert data[:4] == b'\x00\x00\x00\x00'  # Pixel (0, 0) is transparent

    def test_redirects(self):
        app = Flask(__name__)

        def add_redirect(old_url, new_url):
            app.add_url_rule(
                old_url, 'redirect_' + old_url, lambda: redirect(new_url))

        add_redirect('/a', '/b')
        add_redirect('/b', '/c')
        add_redirect('/c', '/d')
        app.add_url_rule('/d', 'd', lambda: 'Ok')

        add_redirect('/1', '/2')
        add_redirect('/2', '/3')
        add_redirect('/3', '/1')  # redirect loop

        with app.test_request_context():
            fetcher = make_url_fetcher()
        result = fetcher('http://localhost/a')
        assert result['string'] == b'Ok'
        assert result['redirected_url'] == 'http://localhost/d'
        self.assertRaises(ClientRedirectError, fetcher, 'http://localhost/1')
        self.assertRaises(ValueError, fetcher, 'http://localhost/nonexistent')

    def test_dispatcher(self):
        app = Flask(__name__)
        app.config['PROPAGATE_EXCEPTIONS'] = True

        @app.route('/')
        @app.route('/', subdomain='<sub>')
        @app.route('/<path:path>')
        @app.route('/<path:path>', subdomain='<sub>')
        def catchall(sub='', path=None):
            return jsonify(app=[sub, request.script_root, request.path,
                                request.query_string.decode('utf8')])

        def dummy_fetcher(url):
            return {'string': 'dummy ' + url}

        def assert_app(url, host, script_root, path, query_string=''):
            """The URL was dispatched to the app with these parameters."""
            assert json.loads(dispatcher(url)['string']) == {
                'app': [host, script_root, path, query_string]}

        def assert_dummy(url):
            """The URL was not dispatched, the default fetcher was used."""
            assert dispatcher(url)['string'] == 'dummy ' + url

        # No SERVER_NAME config, default port
        with app.test_request_context(base_url='http://a.net/b/'):
            dispatcher = make_url_fetcher(next_fetcher=dummy_fetcher)
        assert_app('http://a.net/b', '', '/b', '/')
        assert_app('http://a.net/b/', '', '/b', '/')
        assert_app('http://a.net/b/c/d?e', '', '/b', '/c/d', 'e')
        assert_app('http://a.net:80/b/c/d?e', '', '/b', '/c/d', 'e')
        assert_dummy('http://a.net/other/prefix')
        assert_dummy('http://subdomain.a.net/b/')
        assert_dummy('http://other.net/b/')
        assert_dummy('http://a.net:8888/b/')
        assert_dummy('https://a.net/b/')

        # Change the context’s port number
        with app.test_request_context(base_url='http://a.net:8888/b/'):
            dispatcher = make_url_fetcher(next_fetcher=dummy_fetcher)
        assert_app('http://a.net:8888/b', '', '/b', '/')
        assert_app('http://a.net:8888/b/', '', '/b', '/')
        assert_app('http://a.net:8888/b/cd?e', '', '/b', '/cd', 'e')
        assert_dummy('http://subdomain.a.net:8888/b/')
        assert_dummy('http://a.net:8888/other/prefix')
        assert_dummy('http://a.net/b/')
        assert_dummy('http://a.net:80/b/')
        assert_dummy('https://a.net/b/')
        assert_dummy('https://a.net:443/b/')
        assert_dummy('https://a.net:8888/b/')

        # Add a SERVER_NAME config
        app.config['SERVER_NAME'] = 'a.net'
        with app.test_request_context():
            dispatcher = make_url_fetcher(next_fetcher=dummy_fetcher)
        assert_app('http://a.net', '', '', '/')
        assert_app('http://a.net/', '', '', '/')
        assert_app('http://a.net/b/c/d?e', '', '', '/b/c/d', 'e')
        assert_app('http://a.net:80/b/c/d?e', '', '', '/b/c/d', 'e')
        assert_app('https://a.net/b/c/d?e', '', '', '/b/c/d', 'e')
        assert_app('https://a.net:443/b/c/d?e', '', '', '/b/c/d', 'e')
        assert_app('http://subdomain.a.net/b/', 'subdomain', '', '/b/')
        assert_dummy('http://other.net/b/')
        assert_dummy('http://a.net:8888/b/')

        # SERVER_NAME with a port number
        app.config['SERVER_NAME'] = 'a.net:8888'
        with app.test_request_context():
            dispatcher = make_url_fetcher(next_fetcher=dummy_fetcher)
        assert_app('http://a.net:8888', '', '', '/')
        assert_app('http://a.net:8888/', '', '', '/')
        assert_app('http://a.net:8888/b/c/d?e', '', '', '/b/c/d', 'e')
        assert_app('https://a.net:8888/b/c/d?e', '', '', '/b/c/d', 'e')
        assert_app('http://subdomain.a.net:8888/b/', 'subdomain', '', '/b/')
        assert_dummy('http://other.net:8888/b/')
        assert_dummy('http://a.net:5555/b/')
        assert_dummy('http://a.net/b/')

    def test_funky_urls(self):
        with app.test_request_context(base_url='http://example.net/'):
            fetcher = make_url_fetcher()

        def assert_pass(url):
            assert fetcher(url)['string'] == u'pass !'.encode('utf8')

        assert_pass(u'http://example.net/Unïĉodé/pass !')
        assert_pass(u'http://example.net/Unïĉodé/pass !'.encode('utf8'))
        assert_pass(u'http://example.net/foo%20bar/p%61ss%C2%A0!')
        assert_pass(b'http://example.net/foo%20bar/p%61ss%C2%A0!')

if __name__ == '__main__':
    unittest.main()
