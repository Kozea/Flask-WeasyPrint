.. module:: flask_weasyprint

.. include:: ../README.rst


Installation
------------

Once you `have WeasyPrint installed <http://weasyprint.readthedocs.io/en/latest/install.html>`_
and working, just install the extension with pip::

    $ pip install Flask-WeasyPrint


Introduction
------------

Let’s assume you have a Flask application serving an HTML document at
http://example.net/hello/ with a print-ready CSS stylesheet. WeasyPrint
can render this document to PDF:

.. code-block:: python

    from weasyprint import HTML
    pdf = HTML('http://example.net/hello/').write_pdf()

WeasyPrint will fetch the stylesheet, the images as well as the document itself
over HTTP, just like a web browser would. Of course, going through the network
is a bit silly if WeasyPrint is running on the same server as the application.
Flask-WeasyPrint can help:

.. code-block:: python

    from my_flask_application import app
    from flask_weasyprint import HTML
    with app.test_request_context(base_url='http://example.net/'):
        # /hello/ is resolved relative to the context’s URL.
        pdf = HTML('/hello/').write_pdf()

Just import :func:`~flask_weasyprint.HTML` or :func:`~flask_weasyprint.CSS`
from ``flask_weasyprint`` rather than ``weasyprint``, and use them from
within a Flask :ref:`request context <flask:request-context>`.
For URLs below the application’s root URL, Flask-WeasyPrint will short-circuit
the network and make the request at the WSGI level, without leaving the
Python process.

Note that from a Flask view function you already are in a request context and
thus do not need :meth:`~flask.Flask.test_request_context`.


An example app
--------------

Here is a simple *hello world* application that uses Flask-WeasyPrint:

.. code-block:: python

    from flask import Flask, render_template, url_for
    from flask_weasyprint import HTML, render_pdf

    app = Flask(__name__)

    @app.route('/hello/', defaults={'name': 'World'})
    @app.route('/hello/<name>/')
    def hello_html(name):
        return render_template('hello.html', name=name)

    @app.route('/hello_<name>.pdf')
    def hello_pdf(name):
        # Make a PDF from another view
        return render_pdf(url_for('hello_html', name=name))

    # Alternatively, if the PDF does not have a matching HTML page:

    @app.route('/hello_<name>.pdf')
    def hello_pdf(name):
        # Make a PDF straight from HTML in a string.
        html = render_template('hello.html', name=name)
        return render_pdf(HTML(string=html))

``templates/hello.html``:

.. code-block:: html+jinja

    <!doctype html>
    <title>Hello</title>
    <link rel=stylesheet href="{{ url_for('static', filename='style.css') }}" />

    <p>Hello, {{ name }}!</p>
    <nav><a href="{{ url_for('hello_pdf', name=name) }}">Get as PDF</a></nav>

``static/style.css``:

.. code-block:: css

    body { font: 2em Fontin, serif }
    nav { font-size: .7em }

    @page { size: A5; margin: 1cm }
    @media print {
        nav { display: none }
    }


:func:`render_pdf` helps making a :class:`~flask.Response` with the correct
MIME type. You can give it an URL or an ``HTML`` object.

In the HTML you can use :func:`~flask.url_for` or relative URLs.
Flask-WeasyPrint will do the right thing to fetch resources and make
hyperlinks absolute in the PDF output.

In CSS, ``@page`` and ``@media print`` can be used to have print-specific
styles. Here the "Get as PDF" link is not displayed in the PDF itself,
although it still exists in the HTML.

.. autofunction:: flask_weasyprint.test_app.run


API
---

.. autofunction:: make_flask_url_dispatcher
.. autofunction:: make_url_fetcher(dispatcher=None, next_fetcher=weasyprint.default_url_fetcher)
.. autofunction:: HTML(guess=None, **kwargs)
.. autofunction:: CSS(guess=None, **kwargs)
.. autofunction:: render_pdf


Changelog
---------

.. include:: ../CHANGES
