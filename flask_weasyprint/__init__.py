"""Make PDF in your Flask app with WeasyPrint."""

from urllib.parse import urljoin, urlsplit

import weasyprint
from flask import current_app, has_request_context, request
from werkzeug.test import Client, ClientRedirectError, EnvironBuilder
from werkzeug.wrappers import Response

VERSION = __version__ = '1.0.0'
DEFAULT_PORTS = (('http', 80), ('https', 443))


def make_flask_url_dispatcher():
    """Return a URL dispatcher based on the current request context.

    You generally don’t need to call this directly.

    The :doc:`request context <flask:reqcontext>` is used when the dispatcher
    is first created but not afterwards. It is not required after this function
    has returned.

    Dispatch to the context’s app URLs below the context’s root URL. If the
    application has a ``SERVER_NAME`` :doc:`configuration <flask:config>`, also
    accept URLs that have that domain name or a subdomain thereof.

    """
    def parse_netloc(netloc):
        """Return (hostname, port)."""
        parsed = urlsplit(f'http://{netloc}')
        return parsed.hostname, parsed.port

    app = current_app._get_current_object()
    root_path = request.script_root

    server_name = app.config.get('SERVER_NAME')
    if server_name:
        hostname, port = parse_netloc(server_name)

        def accept(url):
            """Accept any URL scheme; also accept subdomains."""
            return url.hostname is not None and (
                url.hostname == hostname or
                url.hostname.endswith(f'.{hostname}'))
    else:
        scheme = request.scheme
        hostname, port = parse_netloc(request.host)

        def accept(url):
            """Do not accept subdomains."""
            return (url.scheme, url.hostname) == (scheme, hostname)

    def dispatch(url_string):
        if isinstance(url_string, bytes):
            url_string = url_string.decode('utf8')
        url = urlsplit(url_string)
        url_port = url.port
        if (url.scheme, url_port) in DEFAULT_PORTS:
            url_port = None
        if accept(url) and url_port == port and url.path.startswith(root_path):
            netloc = url.netloc
            if url.port and not url_port:
                netloc = netloc.rsplit(':', 1)[0]  # remove default port
            base_url = f'{url.scheme}://{netloc}{root_path}'
            path = url.path[len(root_path):]
            if url.query:
                path = f'{path}?{url.query}'
            # Ignore url.fragment
            return app, base_url, path

    return dispatch


def make_url_fetcher(dispatcher=None,
                     next_fetcher=weasyprint.default_url_fetcher):
    """Return an function suitable as a ``url_fetcher`` in WeasyPrint.

    You generally don’t need to call this directly.

    If ``dispatcher`` is not provided, :func:`make_flask_url_dispatcher` is
    called to get one. This requires a :doc:`request context
    <flask:reqcontext>`.

    Otherwise, it must be a callable that takes a URL and returns either
    :obj:`None` or a ``(wsgi_callable, base_url, path)`` tuple. For
    :obj:`None`, ``next_fetcher`` is used. (By default, fetch normally over the
    network.) For a tuple the request is made at the WSGI level.
    ``wsgi_callable`` must be a Flask application or another WSGI callable.
    ``base_url`` is the root URL for the application while ``path`` is the path
    within the application.

    Typically ``base_url + path`` is equivalent to the passed URL.

    """
    if dispatcher is None:
        dispatcher = make_flask_url_dispatcher()

    def flask_url_fetcher(url):
        redirect_chain = set()
        while True:
            result = dispatcher(url)
            if result is None:
                return next_fetcher(url)
            app, base_url, path = result
            client = Client(app, response_wrapper=Response)
            if has_request_context() and request.cookies:
                server_name = EnvironBuilder(
                    path, base_url=base_url).server_name
                for cookie_key, cookie_value in request.cookies.items():
                    client.set_cookie(server_name, cookie_key, cookie_value)
            response = client.get(path, base_url=base_url)
            if response.status_code == 200:
                return {
                    'string': response.data, 'mime_type': response.mimetype,
                    'encoding': response.charset, 'redirected_url': url}
            # The test client can follow redirects, but do it ourselves
            # to get access to the redirected URL.
            elif response.status_code in (301, 302, 303, 305, 307, 308):
                redirect_chain.add(url)
                url = urljoin(url, response.location)
                if url in redirect_chain:
                    raise ClientRedirectError('loop detected')
            else:
                raise ValueError(
                    'Flask-WeasyPrint got HTTP status '
                    f'{response.status} for {urljoin(base_url, path)}')

    return flask_url_fetcher


def _wrapper(class_, *args, **kwargs):
    if args:
        guess, args = args[0], args[1:]
    else:
        guess = kwargs.pop('guess', None)
    if guess is not None and not hasattr(guess, 'read'):
        # Assume a (possibly relative) URL
        guess = urljoin(request.url, guess)
    if 'string' in kwargs and 'base_url' not in kwargs:
        # Strings do not have an "intrinsic" base URL, use the request context.
        kwargs['base_url'] = request.url
    kwargs['url_fetcher'] = make_url_fetcher()
    return class_(guess, *args, **kwargs)


def HTML(*args, **kwargs):
    """Like :class:`weasyprint.HTML` but:

    * :func:`make_url_fetcher` is used to create an ``url_fetcher``
    * If ``guess`` is not a file object, it is a URL relative to the current
      request context. This means that you can just pass a result from
      :func:`flask.url_for`.
    * If ``string`` is passed, ``base_url`` defaults to the current
      request’s URL.

    This requires a Flask :doc:`request context <flask:reqcontext>`.

    """
    return _wrapper(weasyprint.HTML, *args, **kwargs)


def CSS(*args, **kwargs):
    return _wrapper(weasyprint.CSS, *args, **kwargs)


CSS.__doc__ = HTML.__doc__.replace('HTML', 'CSS')


def render_pdf(html, stylesheets=None, download_filename=None,
               automatic_download=True):
    """Render a PDF to a response with the correct ``Content-Type`` header.

    :param html:
        Either a :class:`weasyprint.HTML` object or a URL to be passed
        to :func:`flask_weasyprint.HTML`. The latter case requires
        a request context.
    :param list stylesheets:
        A list of user stylesheets, passed to
        :meth:`weasyprint.HTML.write_pdf`.
    :param str download_filename:
        If provided, the ``Content-Disposition`` header is set so that most
        web browser will show the "Save as…" dialog with the value as the
        default filename.
    :param bool automatic_download:
        If :obj:`True`, the browser will automatic download file.
    :returns: a :class:`flask.Response` object.

    """
    if not hasattr(html, 'write_pdf'):
        html = HTML(html)
    pdf = html.write_pdf(stylesheets=stylesheets)
    response = current_app.response_class(pdf, mimetype='application/pdf')
    if download_filename:
        response.headers.add(
            'Content-Disposition',
            'attachment' if automatic_download else 'inline',
            filename=download_filename)
    return response
