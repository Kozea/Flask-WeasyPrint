# coding: utf8
"""
    flask_weasyprint
    ~~~~~~~~~~~~~~~~

    Flask-WeasyPrint: Make PDF in your Flask app with WeasyPrint.

    :copyright: (c) 2012 by Simon Sapin.
    :license: BSD, see LICENSE for more details.

"""

import urlparse

import weasyprint
import flask


VERSION = '0.1'


def make_url_fetcher():
    url_root = flask.request.url_root
    client = flask.current_app.test_client()
    def flask_url_fetcher(fetched_url):
        if not fetched_url.startswith(url_root):
            return weasyprint.default_url_fetcher(fetched_url)
        response = client.get(fetched_url[len(url_root):], base_url=url_root)
        if response.status_code == 200:
            return dict(
                string=response.data,
                mime_type=response.mimetype,
                encoding=response.charset,
                redirected_url=fetched_url)
        if response.status_code in (301, 302, 303, 305, 307):
            return flask_url_fetcher(response.location)
        raise ValueError('Flask-WeasyPrint got HTTP status %i for %s'
                         % (response.status_code, fetched_url))
    return flask_url_fetcher


def HTML(*args, **kwargs):
    if args:
        guess = args[0]
        args = args[1:]
    else:
        guess = kwargs.pop('guess', None)
    if guess is not None and not hasattr(guess, 'read'):
        # Assume a (possibly relative) URL as a string
        guess = urlparse.urljoin(flask.request.url, guess)
    kwargs['url_fetcher'] = make_url_fetcher()
    return weasyprint.HTML(guess, *args, **kwargs)


def render_pdf(url, stylesheets=None):
    pdf = HTML(url).write_pdf(stylesheets=stylesheets)
    return flask.current_app.response_class(pdf, mimetype='application/pdf')


def render_png(url, stylesheets=None, resolution=None):
    png = HTML(url).write_png(stylesheets=stylesheets, resolution=resolution)
    return flask.current_app.response_class(png, mimetype='image/png')
