# Copyright (c) Ecometrica. All rights reserved.
# Distributed under the BSD license. See LICENSE for details.

import codecs
from optparse import make_option
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
    
    option_list = django_makemessages.Command.option_list + (
        make_option('--no-vinaigrette', default=True, action='store_false', dest='avec-vinaigrette',
            help="Don't include strings from database fields handled by vinaigrette."),
        make_option('--keep-obsolete', default=False, action='store_true', dest='keep-obsolete',
            help="Don't obsolete strings no longer referenced in code or Viniagrette's fields.")
    )
    
    help = "Runs over the entire source tree of the current directory and pulls out all strings marked for translation. It creates (or updates) a message file in the conf/locale (in the django tree) or locale (for project and application) directory. Also includes strings from database fields handled by vinaigrette."
    requires_model_validation = True
    
    def handle(self, *args, **options):
        if not options.get('avec-vinaigrette'):
            return super(Command, self).handle(*args, **options)
        
        verbosity = int(options.get('verbosity'))
        vinfilepath = 'vinaigrette-deleteme.py'
        sources = ['', '']
        
        # Because Django makemessages isn't very extensible, we're writing a
        # fake Python file, calling makemessages, then deleting it after.
        vinfile = codecs.open(vinfilepath, 'w', encoding='utf8')
        try:
            vinfile.write('#coding:utf-8\n')
            if verbosity > 0:
                print 'Vinaigrette is processing database values...'
            
            for model in sorted(vinaigrette._registry.keys(),
              key=lambda m: m._meta.object_name):
                strings_seen = set()
                modelname = model._meta.object_name
                reg = vinaigrette._registry[model]
                fields = reg['fields']
                manager = reg['manager'] if reg['manager'] else model._default_manager
                qs = manager.filter(reg['restrict_to']) if reg['restrict_to'] \
                    else manager.all()
            
                for instance in qs.order_by('pk').values('pk', *fields):
                    # In the reference comment in the po file, use the object's primary
                    # key as the line number, but only if it's an integer primary key
                    idnum = instance.pop('pk')
                    idnum = idnum if isinstance(idnum, (int, long)) or idnum.isdigit() else 0
                    for (fieldname, val) in instance.items():
                        if val and val not in strings_seen:
                            strings_seen.add(val)
                            sources.append('%s/%s:%s' % (modelname, fieldname, idnum))
                            vinfile.write(
                                'gettext(%r)\n' 
                                % val.replace('\r', '').replace('%', '%%')
                            )
        finally:
            vinfile.close()
        
        try:
            super(Command, self).handle(*args, **options)
        finally:
            os.unlink(vinfilepath)
        
        r_lineref = re.compile(r'%s:(\d+)' % re.escape(vinfilepath))
        def lineref_replace(match):
            try:
                return sources[int(match.group(1))]
            except IndexError, ValueError:
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
            if isinstance(locales, basestring):
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
