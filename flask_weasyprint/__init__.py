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
    """Return an function suitable as a ``url_fetcher`` in WeasyPrint.
    You generally don’t need to call this directly.

    This requires a Flask :ref:`request context <flask:request-context>`.
    The current application and its root URL (based on ``wsgi.url_scheme``,
    ``HTTP_HOST`` and ``SCRIPT_NAME``) are taken from this context when the
    fetcher is first created. The context is not needed when the fetcher
    is used (when rendering with WeasyPrint).

    Requests for URLs below the application’s root URL are made directly
    with Python calls as the WSGI level, without going through the network.
    Other URLs are fetched normally.

    """
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


def _wrapper(class_, *args, **kwargs):
    if args:
        guess = args[0]
        args = args[1:]
    else:
        guess = kwargs.pop('guess', None)
    if guess is not None and not hasattr(guess, 'read'):
        # Assume a (possibly relative) URL
        guess = urlparse.urljoin(request.url, guess)
    if 'string' in kwargs and 'base_url' not in kwargs:
        # Strings do not have an "intrinsic" base URL, use the request context.
        kwargs['base_url'] = request.url
    kwargs['url_fetcher'] = make_url_fetcher()
    return class_(guess, *args, **kwargs)


def HTML(*args, **kwargs):
    """Like `weasyprint.HTML()
    <http://weasyprint.org/using/#the-weasyprint-html-class>`_ but:

    * :func:`make_url_fetcher` is used to create an ``url_fetcher``
    * If ``guess`` is not a file object, it is an URL relative to the current
      request context.
      This means that you can just pass a result from :func:`flask.url_for`.
    * If ``string`` is passed, ``base_url`` defaults to the current
      request’s URL.

    This requires a Flask request context.

    """
    return _wrapper(weasyprint.HTML, *args, **kwargs)


def CSS(*args, **kwargs):
    return _wrapper(weasyprint.CSS, *args, **kwargs)
CSS.__doc__ = HTML.__doc__.replace('HTML', 'CSS').replace('html', 'css')


def render_pdf(html, stylesheets=None, download_filename=None):
    """Render a PDF to a response with the correct ``Content-Type`` header.

    :param html:
        Either a :class:`weasyprint.HTML` object or an URL to be passed
        to :func:`flask_weasyprint.HTML`. The latter case requires
        a request context.
    :param stylesheets:
        A list of user stylesheets, passed to
        :meth:`~weasyprint.HTML.write_pdf`
    :param download_filename:
        If provided, the ``Content-Disposition`` header is set so that most
        web browser will show the "Save as…" dialog with the value a default
        filename.
    :returns: a :class:`flask.Response` object.

    """
    if not hasattr(html, 'write_pdf'):
        html = HTML(html)
    pdf = html.write_pdf(stylesheets=stylesheets)
    response = current_app.response_class(pdf, mimetype='application/pdf')
    if download_filename:
        response.headers.add('Content-Disposition', 'attachment',
                             filename=download_filename)
    return response
