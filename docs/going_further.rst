Going Further
=============


Why Flask-WeasyPrint?
---------------------

Generating documents out of HTML and CSS can be useful in many cases, but one
of them is particularly useful: web applications.

Many web applications can benefit from generating both HTML and PDF files using
the same templates. Users way want to read blog articles online and
offline, customers may want to see invoices in their browsers and to keep them
as static files on their computers, applications are endless.

CSS has been designed in a way that enables web-designers to use the same
stylesheet for both browsers and paged documents. You can share most of the
layout while defining specific rules for each rendering modes.

Flask-WeasyPrint helps users to include WeasyPrint in Flask applications. It
avoids useless HTTP requests when it’s possible to bypass them and gives a nice
Flask-oriented API to define routes serving PDF files.

The same kind of module exists for Django_: Django-WeasyPrint_.

.. _Django: https://www.djangoproject.com/
.. _Django-WeasyPrint: https://github.com/fdemmer/django-weasyprint
