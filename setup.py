import re
import os.path
from setuptools import setup, find_packages


VERSION = re.search(
    b"VERSION = '([^']+)'",
    open(os.path.join(os.path.dirname(__file__),
                      'flask_weasyprint', '__init__.py'),
         'rb').read()).group(1).decode('ascii')

README = open(os.path.join(os.path.dirname(__file__),
                           'README.rst'),
              'rb').read().decode('utf8')
__doc__ = README


setup(
    name='Flask-WeasyPrint',
    version=VERSION,
    url='https://github.com/SimonSapin/Flask-WeasyPrint',
    license='BSD',
    author='Simon Sapin',
    author_email='simon.sapin@exyr.org',
    description='Make PDF in your Flask app with WeasyPrint.',
    long_description=README,
    packages=find_packages(),
    test_suite='flask_weasyprint.tests',
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask',
        'WeasyPrint>=0.12',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
