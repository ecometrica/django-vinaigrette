import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()
    
setup(
    name = "django-vinaigrette",
    version = "0.1.0",
    packages = ['vinaigrette'],
    description = "Translate Django model data using gettext",
    author = "Ecometrica",
    author_email = "info@ecometrica.ca",
    maintainer = "Michael Mulley",
    maintainer_email = "michael@michaelmulley.com",
    url = "http://github.com/ecometrica/django-vinaigrette/",
    keywords = ["django", "translation", "gettext", 
        "internationalization", "i18n", "database", "model"],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX",
        "Topic :: Software Development :: Internationalization",
        "Framework :: Django",
        "Framework :: Django :: 1.2",
        ],
    long_description = read('README.rst'),
)