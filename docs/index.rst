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

.. code-block:: python

    from flask import Flask, render_template, url_for
    from flask_weasyprint import HTML, render_pdf

    app = Flask(__name__)

    @app.route('/lorem/ipsum_<int:lipsum_id>/'):
    def lipsum(lipsum_id):
        # A normal HTML view
        data = ...
        return render_template('lipsum.html', **data)

    @app.route('/lorem/ipsum_<int:lipsum_id>.pdf'):
    def lipsum_pdf(lipsum_id):
        # Make a PDF from another view
        return render_pdf(url_for('lipsum', lipsum_id=lipsum_id))

    # Alternatively, if the PDF does not have a matching HTML page:

    @app.route('/lorem/ipsum_<int:lipsum_id>.pdf'):
    def lipsum_pdf(lipsum_id):
        # Make a PDF straight from HTML in a string.
        data = ...
        return render_pdf(HTML(string=render_template('lipsum.html', **data)))


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
