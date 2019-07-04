# Copyright (c) Ecometrica. All rights reserved.
# Distributed under the BSD license. See LICENSE for details.
from __future__ import print_function
import io
import os
import re

import vinaigrette

from django.core.management.base import BaseCommand, CommandError
from django.core.management.commands import makemessages as django_makemessages
from django.utils.translation import ugettext

def _get_po_paths(locales=[]):
    """Returns paths to all relevant po files in the current project."""
    basedirs = [os.path.join('conf', 'locale'), 'locale']
    if os.environ.get('DJANGO_SETTINGS_MODULE'):
        from django.conf import settings
        basedirs.extend(settings.LOCALE_PATHS)

    # Gather existing directories.
    basedirs = set(map(os.path.abspath, filter(os.path.isdir, basedirs)))

    if not basedirs:
        raise CommandError("This script should be run from the Django SVN tree or your project or app tree, or with the settings module specified.")

    po_paths = []
    for basedir in basedirs:
        for locale in locales:
            basedir_locale = os.path.join(basedir, locale, 'LC_MESSAGES')
            for dirpath, dirnames, filenames in os.walk(basedir_locale):
                for f in filenames:
                    if f.endswith('.po'):
                        po_paths.append(os.path.join(dirpath, f))
    return po_paths

class Command(django_makemessages.Command):
    help = ("Runs over the entire source tree of the current directory and "
        "pulls out all strings marked for translation. It creates (or "
        "updates) a message file in the conf/locale (in the django tree) or "
        "locale (for project and application) directory. Also includes "
        "strings from database fields handled by vinaigrette.")

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument('--no-vinaigrette', default=True, action='store_false', dest='avec-vinaigrette',
            help="Don't include strings from database fields handled by vinaigrette."),
        parser.add_argument('--keep-obsolete', default=False, action='store_true', dest='keep-obsolete',
            help="Don't obsolete strings no longer referenced in code or Viniagrette's fields.")
        parser.add_argument('--keep-vinaigrette-temp', default=False, action='store_true', dest='keep-vinaigrette-temp',
            help="Keep the temporary vinaigrette-deleteme.py file.")

    requires_system_checks = True

    def handle(self, *args, **options):
        if not options.get('avec-vinaigrette'):
            return super(Command, self).handle(*args, **options)

        verbosity = int(options['verbosity'])
        vinfilepath = 'vinaigrette-deleteme.py'
        sources = ['', '']

        # Because Django makemessages isn't very extensible, we're writing a
        # fake Python file, calling makemessages, then deleting it after.
        with io.open(vinfilepath, 'w', encoding='utf8') as vinfile:
            vinfile.write(u'#coding:utf-8\n')
            if verbosity > 0:
                self.stdout.write('Vinaigrette is processing database values...')

            models = sorted(vinaigrette._REGISTRY.keys(), key=lambda m: m._meta.object_name)
            for model in models:
                strings_seen = set()
                modelname = "%s.%s" % (model._meta.app_label, model._meta.object_name)
                reg = vinaigrette._REGISTRY[model]
                fields = reg['fields']  # strings to be translated
                contexts = reg['contexts']  # Dict of string contexts, if available
                properties = reg['properties']
                # make query_fields a set to avoid duplicates
                # only these fields will be retrieved from the db instead of all model's field
                query_fields = set(fields)

                # if there are properties, we update the needed query fields and
                # update the string that will be translated
                if properties:
                    fields += properties.keys()
                    for prop in properties.itervalues():
                        query_fields.update(prop)

                manager = reg['manager'] if reg['manager'] else model._default_manager
                qs = manager.filter(reg['restrict_to']) if reg['restrict_to'] else manager.all()

                for instance in qs.order_by('pk').only('pk', *query_fields):
                    try:
                        idnum = int(instance.pk)
                    except (ValueError, TypeError):
                        idnum = 0
                    # iterate over fields to translate
                    for field in fields:
                        # In the reference comment in the po file, use the object's primary
                        # key as the line number, but only if it's an integer primary key
                        val = getattr(instance, field)

                        context = contexts.get(field, None)
                        if val and val not in strings_seen:
                            strings_seen.add(val)
                            sources.append('%s/%s:%s' % (modelname, field, idnum))
                            if context:
                                line = u'pgettext(%r, %r)\n' % (context, val.replace('\r', '').replace('%', '%%'))
                            else:
                                line = u'gettext(%r)\n' % val.replace('\r', '').replace('%', '%%')
                            vinfile.write(line)

        try:
            super(Command, self).handle(*args, **options)
        finally:
            if not options.get('keep-vinaigrette-temp'):
                os.unlink(vinfilepath)

        r_lineref = re.compile(r'%s:(\d+)' % re.escape(vinfilepath))
        def lineref_replace(match):
            try:
                return sources[int(match.group(1))]
            except (IndexError, ValueError):
                return match.group(0)

        # The PO file has been generated. Now, swap out the line-number
        # references to our fake python file for more descriptive
        # references.
        if options.get('all'):
            po_paths = _get_po_paths()
        else:
            locales = options.get('locale')

            # In django 1.6+ one or more locales can be specified, so we
            # make sure to handle both versions here.

            # Also, there is no simple way to differentiate a string from a
            # sequence of strings that works in both python2 (for str and
            # unicode) and python3 so we query for a string method on locales.
            if hasattr(locales, 'capitalize'):
                locales = [locales]

            po_paths = _get_po_paths(locales)

        if options.get('keep-obsolete'):
            obsolete_warning = ['#. %s\n' %
                ugettext('Obsolete translation kept alive with Viniagrette').encode('utf8'),
                '#: obsolete:0\n']

        for po_path in po_paths:
            po_file = open(po_path)
            new_contents = []
            lastline = ''
            for line in po_file:
                if line.startswith('#: '):
                    new_contents.append(r_lineref.sub(lineref_replace, line))
                else:
                    if (line.startswith('#, python-format')
                      and lastline.startswith('#: ')
                      and vinfilepath in lastline):
                        # A database string got labelled as being python-format;
                        # it shouldn't be. Skip the line.
                        continue
                    if options.get('keep-obsolete'):
                        if line in obsolete_warning:
                            # Don't preserve old obsolete warnings we inserted
                            continue
                        if line.startswith('#~ msgid '):
                            new_contents.extend(obsolete_warning)
                        if line.startswith('#~ '):
                            line = re.sub(r'^#~ ', '', line)

                    new_contents.append(line)
                lastline = line
            po_file.close()

            # Perhaps this should be done a little more atomically w/ renames?
            po_file = open(po_path, 'w')
            for line in new_contents:
                po_file.write(line)
            po_file.close()
