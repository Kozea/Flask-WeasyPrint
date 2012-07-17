.. module:: flask_weasyprint

.. include:: ../README.rst


Installation
------------

Once you `have WeasyPrint installed <http://weasyprint.org/install/>`_
and working, just install the extension with pip::

    $ pip install Flask-WeasyPrint


Quickstart
----------

Just import :func:`~flask_weasyprint.HTML` and :func:`~flask_weasyprint.CSS`
from ``flask_weasyprint`` rather than ``weasyprint``, and use them from
within a Flask :ref:`request context <flask:request-context>`.
:func:`render_pdf` is a helper function to make a :class:`~flask.Response`
with the correct MIME type.

``hello.py`` is a simple Flask application:

.. code-block:: python

    from flask import Flask, render_template, url_for
    from flask_weasyprint import HTML, render_pdf

    app = Flask(__name__)

    @app.route('/', defaults={'name': 'World'):
    @app.route('/hello/<name>/'):
    def hello_html(name):
        return render_template('hello.html', name=name)

    @app.route('/hello_<name>.pdf'):
    def hello_pdf(name):
        # Make a PDF from another view
        return render_pdf(url_for('hello_html', name=name))

    # Alternatively, if the PDF does not have a matching HTML page:

    @app.route('/hello_<name>.pdf'):
    def hello_pdf(name):
        # Make a PDF straight from HTML in a string.
        html = render_template('hello.html', name=name)
        return render_pdf(HTML(string=html))

In ``templates/hello.html``, the stylesheet is within the same app.
Flask-WeasyPrint will fetch at the Python level it without going through
the network. The same would apply to images that could even by dynamic:

.. code-block:: html+jinja

    <!doctype html>
    <title>Hello</title>
    <link rel=stylesheet href="{{ url_for('static', filename='style.css') }}" />

    <p>Hello, {{ name }}!</p>
    <nav><a href="{{ url_for('hello_pdf', name=name) }}">Get as PDF</a></nav>

In ``static/style.css``, web browsers ignore the parts in ``@page`` and
``@media print`` when rendering to screen:

.. code-block:: css

    body { font: 2em Fontin, serif }
    nav { font-size: .7em }

    @page { size: A5; margin: 1cm }
    @media print {
        nav { display: none }
    }


API
---

.. autofunction:: make_url_fetcher
.. autofunction:: HTML(guess=None, **kwargs)
.. autofunction:: CSS(guess=None, **kwargs)
.. autofunction:: render_pdf


Changelog
---------

Version 0.1
~~~~~~~~~~~

Not released yet.

First public release.
