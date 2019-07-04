import polib
import os

from django.core import management
from django.test import TestCase


class TestVinaigretteMakemessages(TestCase):
    def setUp(self):
        self.popath = 'locale/fr/LC_MESSAGES/django.po'

    def tearDown(self):
        os.remove(self.popath)

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
