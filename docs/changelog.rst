Changelog
=========


Version 1.1.0
~~~~~~~~~~~~~

Released on 2023-10-03.

Drop support of Python 3.7, support Python 3.12. Requires Flask >= 2.3.0 and
WeasyPrint >= 53.0.

Allow extra rendering options in render_pdf().


Version 1.0.0
~~~~~~~~~~~~~

Released on 2022-08-18.

Drop support of Python 2, only support Python 3.7+. This requires Flask >=
2.0.0 and WeasyPrint 43.0.

Resend cookies of the original request received by Flask if a request is then
sent by WeasyPrint.


Version 0.6
~~~~~~~~~~~

Released on 2019-03-11.

Add an option to enable/disable automatic download.


Version 0.5
~~~~~~~~~~~

Released on 2015-03-27.

Don't crash on URLs with no hostname, including 'data:' URLs.


Version 0.4
~~~~~~~~~~~

Released on 2013-06-13.

Add Python 3.3 support. This requires Flask >= 0.10 and Werkzeug >= 0.9.


Version 0.3
~~~~~~~~~~~

Released on 2013-02-27.

Fix Unicode %-encoded URLs.


Version 0.2
~~~~~~~~~~~

Released on 2012-07-23.

Add URL dispatchers and make Flask-WeasyPrint do the right thing with
apps that use subdomains (when the ``SERVER_NAME`` config is set).


Version 0.1
~~~~~~~~~~~

Released on 2012-07-19.

First public release.
