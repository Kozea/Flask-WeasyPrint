"""Demonstration and testing application for Flask-WeasyPrint."""

from flask import Flask, abort, redirect, render_template, request, url_for

# Disable the Flask’s default static file handling. (See below.)
app = Flask(__name__, static_folder=None)


# This is a pretty standard Flask app with a dynamic SVG graph. Of course the
# data here is always the same, but in a real app it could come from a database
# or be computed on the fly.


@app.config.from_object
class Config:
    GRAPH_COLORS = ['#0C3795', '#752641', '#E47F00']


@app.route('/')
def index():
    return redirect(url_for('document_html'))


@app.route('/foo/')
def document_html():
    return render_template(
        'document.html', data=[42, 27.3, 63], labels=['Lorem', 'ipsum', 'sit'],
        cookie=request.cookies.get('cookie'))


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


# The code specific to Flask-WeasyPrint follows. Pretty simple, eh?

from flask_weasyprint import render_pdf  # noqa


@app.route('/foo.pdf')
def document_pdf():
    return render_pdf(url_for('index'))

# End of code specific to Flask-WeasyPrint.


# The templates and static files are inlined here and served from memory. This
# is a bit unusual but allows us to keep this app in a single file. We could
# just as well use normal templates and static files.

from jinja2 import DictLoader  # noqa

app.jinja_env.loader = DictLoader({
    'document.html': '''<html>
        {% set data = data | join(',') %}
        {% set labels = labels | join(',') %}
        <title>Test document{% if cookie %}{{ cookie }}{% endif %}</title>
        <link rel=stylesheet
              href="{{ url_for('static', filename='style.css') }}" />
        <section>
            <h1><a href="https://courtbouillon.org/">Flask-WeasyPrint</a></h1>
            <nav>Get this document <a href="/foo.pdf">as PDF</a>.</nav>
            <p>This vector graph was generated dynamically:</p>
            <img src="graph?data={{ data }}&amp;labels={{ labels }}">
        </section>
    ''',

    'graph.svg': '''
        <svg xmlns="http://www.w3.org/2000/svg"
             width="1600" height="1000" viewBox="0 0 160 100">
        {% for i, (label, value, color) in series %}
            <rect x="{{ 10 + i * 50 }}" y="{{ 75 - value }}"
                  width="40" height="{{ value }}"
                  fill="{{ color }}" stroke="#333" rx="5" ry="5" />
            <text x="{{ 30 + i * 50 }}" y="90"
                  text-anchor="middle" font-size="10px">{{ label }}</text>
        {% endfor %}
        </svg>
    ''',
})


STATIC_FILES = {'style.css': ('text/css', '''
    html { font-family: sans-serif }
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
    else:  # pragma: no cover
        abort(404)


@app.route(u'/Unïĉodé/<stuff>')
@app.route(u'/foo bar/<stuff>')
def funky_urls(stuff):
    return stuff


if __name__ == '__main__':  # pragma: no cover
    app.run(debug=True)
