"""Tests for Flask-WeasyPrint."""

import pytest
from flask import Flask, json, jsonify, redirect, request
from flask_weasyprint import CSS, HTML, make_url_fetcher, render_pdf
from werkzeug.test import ClientRedirectError

from . import app, document_html


def test_url_fetcher():
    # A request context is required
    with pytest.raises(RuntimeError):
        make_url_fetcher()

    # But only for fist creating the fetcher, not for using it.
    with app.test_request_context(base_url='http://example.org/bar/'):
        fetcher = make_url_fetcher()

    result = fetcher('http://example.org/bar/')
    assert result['string'].strip().startswith(b'<html>')
    assert result['mime_type'] == 'text/html'
    assert result['encoding'] == 'utf-8'
    assert result['redirected_url'] == 'http://example.org/bar/foo/'

    result = fetcher('http://example.org/bar/foo/graph?data=1&labels=A')
    assert result['string'].strip().startswith(b'<svg xmlns=')
    assert result['mime_type'] == 'image/svg+xml'

    # Also works with a custom dispatcher
    def custom_dispatcher(url_string):
        return app, 'http://example.org/bar/', '/foo/graph?data=1&labels=A'
    with app.test_request_context(base_url='http://example.org/bar/'):
        fetcher = make_url_fetcher(dispatcher=custom_dispatcher)

    result = fetcher('test://')
    assert result['string'].strip().startswith(b'<svg xmlns=')
    assert result['mime_type'] == 'image/svg+xml'


def test_wrappers():
    with app.test_request_context(base_url='http://example.org/bar/'):
        # HTML can also be used with named parameters only:
        html = HTML(url='http://example.org/bar/foo/')
        css = CSS(url='http://example.org/bar/static/style.css')
    assert html.write_pdf(stylesheets=[css]).startswith(b'%PDF')


@pytest.mark.parametrize('url, filename, automatic, cookie', (
    ('/foo.pdf', None, None, None),
    ('/foo.pdf', None, None, 'cookie value'),
    ('/foo/', None, True, None),
    ('/foo/', 'bar.pdf', True, None),
    ('/foo/', 'bar.pdf', False, None),
))
def test_pdf(url, filename, automatic, cookie):
    if url.endswith('.pdf'):
        client = app.test_client()
        if cookie:
            client.set_cookie('', 'cookie', cookie)
        response = client.get('/foo.pdf')
    else:
        with app.test_request_context('/foo/'):
            response = render_pdf(
                HTML(string=document_html()),
                download_filename=filename,
                automatic_download=automatic)
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'
    assert response.data.startswith(b'%PDF')
    if cookie:
        assert cookie.encode('utf8') in response.data
    assert b'/URI (https://courtbouillon.org/)' in response.data
    disposition = response.headers.get('Content-Disposition')
    if filename:
        position = 'attachment' if automatic else 'inline'
        assert disposition == f'{position}; filename={filename}'
    else:
        assert disposition is None


def test_redirects():
    app = Flask(__name__)

    def add_redirect(old_url, new_url):
        app.add_url_rule(
            old_url, f'redirect_{old_url}', lambda: redirect(new_url))

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
    with pytest.raises(ClientRedirectError):
        fetcher('http://localhost/1')
    with pytest.raises(ValueError):
        fetcher('http://localhost/nonexistent')


def test_dispatcher():
    app = Flask(__name__)
    app.config['PROPAGATE_EXCEPTIONS'] = True

    @app.route('/')
    @app.route('/', subdomain='<subdomain>')
    @app.route('/<path:path>')
    @app.route('/<path:path>', subdomain='<subdomain>')
    def catchall(subdomain='', path=None):
        query_string = request.query_string.decode('utf8')
        app = [subdomain, request.script_root, request.path, query_string]
        return jsonify(app=app)

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
    assert_app('http://a.net/b/', '', '/b', '/')
    assert_app('http://a.net/b/c/d?e', '', '/b', '/c/d', 'e')
    assert_app('http://a.net:80/b/c/d?e', '', '/b', '/c/d', 'e')
    assert_dummy('http://a.net/other/prefix')
    assert_dummy('http://subdomain.a.net/b/')
    assert_dummy('http://other.net/b/')
    assert_dummy('http://a.net:8888/b/')
    assert_dummy('https://a.net/b/')

    # No SERVER_NAME config, explicit default port
    with app.test_request_context(base_url='http://a.net:80/b/'):
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


@pytest.mark.parametrize('url', (
    'http://example.net/Unïĉodé/pass !',
    'http://example.net/Unïĉodé/pass !'.encode('utf8'),
    'http://example.net/foo%20bar/p%61ss%C2%A0!',
    b'http://example.net/foo%20bar/p%61ss%C2%A0!',
))
def test_funky_urls(url):
    with app.test_request_context(base_url='http://example.net/'):
        fetcher = make_url_fetcher()
    assert fetcher(url)['string'] == 'pass !'.encode('utf8')
