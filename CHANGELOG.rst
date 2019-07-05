Release Notes
=============

1.2.1
-----

* Fix Python 2 support for makemessages

  * Add a test for makemessages


1.2.0
--------

* Added an optional contexts parameter for the register function, for
  providing translation context for model fields.

* Update middleware to the 1.10+ style

  * Maintains backwards-compat with 1.9 and below

    * Will now work in either ``MIDDLEWARE_CLASSES`` or ``MIDDLEWARE``

  * Deprecates ``VinaigrettteAdminLanguageMiddleware`` for ``VinaigretteAdminLanguageMiddleware``

    * Users should change to ``vinaigrette.middleware.VinaigretteAdminLanguageMiddleware``
    * ``vinaigrette.VinaigrettteAdminLanguageMiddleware`` will continue to work until next major version

* Adds tox and pytest for development and testing

1.1.1
-----

* Update contact info

1.1.0
-----

* Django 2.0 support

1.0.1
-----

* Remembered to update version properly

1.0.0
-----

* Add the ``--keep-vinaigrette-temp`` option which keeps the temporary file containing the generated list of translations
* Added support for Django 1.9
* Remove support for Django versions < 1.8

0.5.0
-----

* Can specify properties to use instead of database field names in .register() function.

0.4.0
-----

* Support for Django 1.7

0.3.0
-----

* Support for python 3.3.

0.2.0
-----

* Bug fix for the --all option, it now works again.
* New VinaigrettteAdminLanguageMiddleware middleware.

0.1.3
-----

* Support for Django 1.6.
