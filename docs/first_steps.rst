First Steps
===========


Installation
------------

The easiest way to use Flask-WeasyPrint is to install it in a Python `virtual
environment`_. When your virtual environment is activated, you can then install
Flask-WeasyPrint with pip_::

    pip install flask_weasyprint

This will also automatically install Flask-WeasyPrint’s dependencies, Flask_
and WeasyPrint_. Check the relative documentations if you have installationt
problems with these packages.

.. _virtual environment: https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/
.. _pip: https://pip.pypa.io/
.. _Flask: https://flask.palletsprojects.com/
.. _WeasyPrint: https://doc.courtbouillon.org/weasyprint/


Introduction
------------

Let’s assume you have a Flask application serving an HTML document at
http://example.net/hello/ with a print-ready CSS stylesheet. WeasyPrint can
render this document to PDF:

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

Just import :func:`flask_weasyprint.HTML` or :func:`flask_weasyprint.CSS`
from ``flask_weasyprint`` rather than ``weasyprint``, and use them from within
a Flask :doc:`request context <flask:reqcontext>`. For URLs below the
application’s root URL, Flask-WeasyPrint will short-circuit the network and
make the request at the WSGI level, without leaving the Python process.

Note that from a Flask view function you already are in a request context and
thus do not need :meth:`flask.Flask.test_request_context`.
