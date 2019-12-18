import polib
import os

from django.core import management
from django.test import TestCase
from django.utils import translation


class TestVinaigretteMakemessages(TestCase):
    def setUp(self):
        self.popath = 'locale/fr/LC_MESSAGES/django.po'
        self.mopath = 'locale/fr/LC_MESSAGES/django.mo'
        self.popathen = 'locale/en/LC_MESSAGES/django.po'
        self.mopathen = 'locale/en/LC_MESSAGES/django.mo'

    def tearDown(self):
        if os.path.exists(self.popath):
            os.remove(self.popath)

        if os.path.exists(self.mopath):
            os.remove(self.mopath)

        if os.path.exists(self.popathen):
            os.remove(self.popathen)

        if os.path.exists(self.mopathen):
            os.remove(self.mopathen)

    def test_happy_path(self):
        management.call_command('makemessages', locale=('fr',))
        pofile = polib.pofile(self.popath)
        expected = {
            u'Vinaigrette': [(u'dressings.Dressing/name', u'1')],
            u'Ranch': [(u'dressings.Dressing/name', u'2')],
            u'Thousand Island': [(u'dressings.Dressing/name', u'3')],
        }
        actual = {poentry.msgid: poentry.occurrences for poentry in pofile}
        self.assertDictContainsSubset(expected, actual)

    def test_same_result_after_compilemessages(self):
        """
        Ensures that makemessages is not affected by a current compiled message
        file.
        """
        # makemessages without translations being active
        with translation.override(None):
            management.call_command('makemessages', locale=('en',))

        if os.path.exists(self.mopathen):
            os.remove(self.mopathen)

        # Fill some translations
        pofileen = polib.pofile(self.popathen)

        for entry in pofileen:
            if entry.msgid == u'Vinaigrette':
                entry.msgstr = u'blub'

        pofileen.save(self.popathen)

        # compilemessages
        management.call_command('compilemessages', locale=('en',))

        # Reload the catalog (clear catalog, then re-activate; rather hacky).
        translation.trans_real.gettext_module._translations.clear()
        translation.trans_real._translations.clear()
        translation._trans._translations.clear()
        translation._trans.catalog()._catalog.clear()
        translation.activate('en')

        # makemessages with translations being active
        management.call_command('makemessages', locale=('en',))

        # Did it work?
        expected = {
            u'Vinaigrette': ('blub', [(u'dressings.Dressing/name', u'1')]),
            u'Ranch': ('', [(u'dressings.Dressing/name', u'2')]),
            u'Thousand Island': ('', [(u'dressings.Dressing/name', u'3')]),
        }

        pofileen2 = polib.pofile(self.popathen)
        actual = {}

        for poentry in pofileen2:
            if not poentry.obsolete:
                actual[poentry.msgid] = (poentry.msgstr, poentry.occurrences)

        for k, v in expected.items():
            self.assertEqual(v, actual.get(k, None))
