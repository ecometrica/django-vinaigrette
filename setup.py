"""Translate Django model data using gettext"""
from setuptools import setup, find_packages

LONG_DESCRIPTION_FILES = ('README.rst', 'CHANGELOG.rst')


def yield_long_description_files():
    for description_file in LONG_DESCRIPTION_FILES:
        with open(description_file, 'r', 'utf-8') as f:
            yield f.read()


setup(
    name="django-vinaigrette",
    version="1.1.1",
    packages=find_packages(),
    description=__doc__,
    long_description='\n\n'.join(yield_long_description_files()),
    author="Ecometrica Ltd",
    author_email="dev@ecometrica.com",
    maintainer="Ecometrica Ltd",
    maintainer_email="software@ecometrica.com",
    url="https://github.com/ecometrica/django-vinaigrette/",
    keywords=[
        "django", "translation", "gettext",
        "internationalization", "i18n", "database", "model"
    ],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX",
        "Topic :: Software Development :: Internationalization",
        "Framework :: Django",
        "Framework :: Django :: 1.7",
        "Framework :: Django :: 1.8",
        "Framework :: Django :: 1.9",
    ],
)
