# Flask-WeasyPrint documentation build configuration file.

import flask_weasyprint

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    'sphinx.ext.autodoc', 'sphinx.ext.intersphinx',
    'sphinx.ext.autosectionlabel']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'Flask-WeasyPrint'
copyright = 'Simon Sapin and contributors'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The full version, including alpha/beta/rc tags.
release = flask_weasyprint.__version__

# The short X.Y version.
version = release

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'monokai'

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'sphinx_rtd_theme'

html_theme_options = {
    'collapse_navigation': False,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = []

# These paths are either relative to html_static_path
# or fully qualified paths (eg. https://...)
html_css_files = [
    'https://www.courtbouillon.org/static/docs.css',
]

# Output file base name for HTML help builder.
htmlhelp_basename = 'flaskweasyprintdoc'

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    ('index', 'flask_weasyprint', 'Flask-WeasyPrint Documentation',
     ['Simon Sapin and contributors'], 1)
]

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [(
    'index', 'Flask-WeasyPrint', 'Flask-WeasyPrint Documentation',
    'Simon Sapin', 'Flask-WeasyPrint',
    'Generate PDF files out of your Flask website', 'Miscellaneous'),
]

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'flask': ('https://flask.palletsprojects.com/en/2.1.x/', None),
    'weasyprint': ('https://doc.courtbouillon.org/weasyprint/stable/', None),
}
