# coding: utf8
"""
    flask_weasyprint.test_app
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Demonstration and testing application for Flask-WeasyPrint.

    :copyright: (c) 2012 by Simon Sapin.
    :license: BSD, see LICENSE for more details.

"""

from flask import (Flask, render_template, request, abort, redirect, url_for,
                   Response)

try:
    unicode
except NameError:  # Python 3
    unicode = str


def run():
    """A more involved application, with a dynamic SVG graph.

    Run it with ``python -m flask_weasyprint.test_app`` or have a look
    at the source code.

    """
    app.run(debug=True)
# This function exits mostly to make a "view source" link in the docs.


# Disable the Flask’s default static file handling. (See below.)
app = Flask(__name__, static_folder=None)


### This is a pretty standard Flask app with a dynamic SVG graph.
### Of course the data here is always the same, but in a real app
### it could come from a database or be computed on the fly.
### We could also make prettier graphs with Pygal: http://pygal.org/


@app.config.from_object
class Config:
    GRAPH_COLORS = ['#0C3795', '#752641', '#E47F00']


@app.route('/')
def index():
    return redirect(url_for('document_html'))


@app.route('/foo/')
def document_html():
    return render_template(
        'document.html', data=[42, 27.3, 63], labels=['Lorem', 'ipsum', 'sit'])


@app.route('/foo/graph')
def graph():
    svg = render_template(
        'graph.svg',
        # Turn ?data=3,2,1&labels=A,B,C into
        # [(0, ('A', 3, color0)), (1, ('B', 2, color1)), (2, ('C', 1, color2))]
        series=enumerate(zip(
            request.args['labels'].split(','),
            map(float, request.args['data'].split(',')),
            app.config['GRAPH_COLORS'])))
    return svg, 200, {'Content-Type': 'image/svg+xml'}


### The code specific to Flask-WeasyPrint follows. Pretty simple, eh?

from flask_weasyprint import render_pdf, HTML


@app.route('/foo.pdf')
def document_pdf():
    return render_pdf(url_for('index'))


@app.route('/foo.png')
def document_png():
    # We didn’t bother to make a ``render_png`` helper
    # but of course you can still use WeasyPrint’s PNG output.
    return Response(HTML('/').write_png(), mimetype='image/png')


### End of code specific to Flask-WeasyPrint.


### The templates and static files are inlined here and served from memory.
### This is a bit unusual but allows us to keep this app in a single file.
### We could just as well use normal templates and static files.

from jinja2 import DictLoader

app.jinja_env.loader = DictLoader({
    'document.html': '''
        <!doctype html>
        <title>Test document</title>
        <link rel=stylesheet href="{{ url_for('static',
                                              filename='style.css') }}" />
        <body>
        <section>
            <h1><a href="http://packages.python.org/Flask-WeasyPrint/">
                Flask-WeasyPrint</a> demo</h1>
            <nav>Get this document <a href="/foo.pdf">as PDF</a> or
                 <a href="/foo.png">as PNG</a>.</nav>
            <p>This vector graph was generated dynamically:</p>
            <img src=graph?data={{ data|join(',')
                }}&amp;labels={{ labels|join(',') }}>
        </section>
    ''',

    'graph.svg': '''
        <svg xmlns="http://www.w3.org/2000/svg"
             width="1600" height="1000" viewBox="0 0 160 100">
        <style>
            text { text-anchor: middle; font-size: 10px }
        </style>
        {% for i, (label, value, color) in series %}
            <rect x="{{ 10 + i * 50 }}" y="{{ 75 - value }}"
                  width="40" height="{{ value }}"
                  fill="{{ color }}" stroke="#333" rx="5" ry="5" />
            <text x="{{ 30 + i * 50 }}" y="90">{{ label }}</text>
        {% endfor %}
        </svg>
    ''',
})


STATIC_FILES = {'style.css': ('text/css', '''
    html { font-family: Fontin Sans, sans-serif }
    section { width: 80%; margin: 2em auto }
    a { color: inherit }
    img { width: 100%; max-width: 600px; box-sizing: border-box;
         border: 1px solid #888; }

    /* Print-specific styles, ignored when rendering to screen: */
    @page { size: A5; margin: 1cm }
    @media print { nav { display: none } }
''')}


@app.route('/static/<path:filename>')
def static(filename):
    if filename in STATIC_FILES:
        content_type, body = STATIC_FILES[filename]
        return body, 200, {'Content-Type': content_type}
    else:
        abort(404)


@app.route(u'/Unïĉodé/<stuff>')
@app.route(u'/foo bar/<stuff>')
def funky_urls(stuff):
    return unicode(stuff)


if __name__ == '__main__':
    run()
