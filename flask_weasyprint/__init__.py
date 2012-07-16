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
from flask import request, current_app
from werkzeug.test import ClientRedirectError


VERSION = '0.1'
__all__ = ['VERSION', 'make_url_fetcher', 'HTML', 'CSS', 'render_pdf']


def make_url_fetcher():
    url_root = request.url_root
    client = current_app.test_client()
    def flask_url_fetcher(url):
        redirect_chain = set()
        while 1:
            if not url.startswith(url_root):
                return weasyprint.default_url_fetcher(url)
            response = client.get(url[len(url_root):], base_url=url_root)
            if response.status_code == 200:
                return dict(
                    string=response.data,
                    mime_type=response.mimetype,
                    encoding=response.charset,
                    redirected_url=url)
            # The test client can follow redirects, but do it ourselves
            # to get access to the redirected URL.
            elif response.status_code in (301, 302, 303, 305, 307):
                redirect_chain.add(url)
                url = response.location
                if url in redirect_chain:
                    raise ClientRedirectError('loop detected')
            else:
                raise ValueError('Flask-WeasyPrint got HTTP status %s for %s'
                                 % (response.status, url))
    return flask_url_fetcher


def _wrap(class_):
    def wrapper(*args, **kwargs):
        if args:
            guess = args[0]
            args = args[1:]
        else:
            guess = kwargs.pop('guess', None)
        if guess is not None and not hasattr(guess, 'read'):
            # Assume a (possibly relative) URL
            guess = urlparse.urljoin(request.url, guess)
        kwargs['url_fetcher'] = make_url_fetcher()
        return class_(guess, *args, **kwargs)
    wrapper.__name__ = class_.__name__
    return wrapper

HTML = _wrap(weasyprint.HTML)
CSS = _wrap(weasyprint.CSS)


def render_pdf(url, stylesheets=None):
    pdf = HTML(url).write_pdf(stylesheets=stylesheets)
    return current_app.response_class(pdf, mimetype='application/pdf')
