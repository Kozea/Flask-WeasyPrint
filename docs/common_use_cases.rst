Common Use Cases
================


Example Application
-------------------

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


:func:`flask_weasyprint.render_pdf` helps making a :class:`flask.Response` with
the correct MIME type. You can give it an URL or an ``HTML`` object.

In the HTML you can use :func:`flask.url_for` or relative URLs.
Flask-WeasyPrint will do the right thing to fetch resources and make hyperlinks
absolute in the PDF output.

In CSS, ``@page`` and ``@media print`` can be used to have print-specific
styles. Here the "Get as PDF" link is not displayed in the PDF itself, although
it still exists in the HTML.


Testing Application
-------------------

A custom application has been created to test Flask-WeasyPrint. It includes
separate code for the common Flask application and the Flask-WeasyPrint
specific part.

You can find it in `Flask-WeasyPrint’s repository`_.

.. _Flask-WeasyPrint’s repository: https://github.com/Kozea/Flask-WeasyPrint/blob/main/tests/__init__.py
