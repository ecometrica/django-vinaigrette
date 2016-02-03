import os
from setuptools import setup, find_packages

description = "Translate Django model data using gettext"
cur_dir = os.path.dirname(__file__)
try:
    long_description = open(os.path.join(cur_dir, 'README.rst')).read()
except:
    long_description = description

setup(
    name = "django-vinaigrette",
    version = "1.0.0",
    packages = find_packages(),
    description = description,
    author = "Ecometrica",
    author_email = "dev@ecometrica.com",
    maintainer = "Rory Geoghegan",
    maintainer_email = "rory.geoghegan@ecometrica.com",
    url = "http://github.com/ecometrica/django-vinaigrette/",
    keywords = ["django", "translation", "gettext",
        "internationalization", "i18n", "database", "model"],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX",
        "Topic :: Software Development :: Internationalization",
        "Framework :: Django",
        ],
    long_description = long_description,
)
