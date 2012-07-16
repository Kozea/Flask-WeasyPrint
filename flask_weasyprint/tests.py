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
import urlparse

import cairo
from flask import Flask, redirect
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
        assert result['string'].strip().startswith('<!doctype html>')
        assert result['mime_type'] == 'text/html'
        assert result['encoding'] == 'utf-8'
        assert result['redirected_url'] == 'http://example.org/bar/foo/'

        result = fetcher('http://example.org/bar/foo/graph?data=1&labels=A')
        assert result['string'].strip().startswith('<svg xmlns=')
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
        assert result['string'] == 'Ok'
        assert result['redirected_url'] == 'http://localhost/d'
        self.assertRaises(ClientRedirectError, fetcher, 'http://localhost/1')
        self.assertRaises(ValueError, fetcher, 'http://localhost/nonexistent')


if __name__ == '__main__':
    unittest.main()
