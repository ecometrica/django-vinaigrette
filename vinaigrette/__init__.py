# Copyright (c) Ecometrica. All rights reserved.
# Distributed under the BSD license. See LICENSE for details.
import re

from django.db.models.signals import pre_save, post_save
from django.utils.translation import ugettext, pgettext

# TODO: Deprecated. Remove in next major version
from .middleware import VinaigretteAdminLanguageMiddleware as VinaigrettteAdminLanguageMiddleware

VERSION = "1.1.1"
DOUBLE_PERCENTAGE_RE = re.compile(u'%(?!\()')

_REGISTRY = {}


class VinaigretteError(Exception):
    pass


def _vinaigrette_pre_save(sender, instance, **kwargs):
    setattr(instance, '_vinaigrette_saving', True)


def _vinaigrette_post_save(sender, instance, **kwargs):
    delattr(instance, '_vinaigrette_saving')


def register(model, fields, restrict_to=None, manager=None, properties=None, contexts=None):
    """Tell vinaigrette which fields on a Django model should be translated.

    Arguments:
    model -- The relevant model class
    fields -- A list or tuple of field names. e.g. ['name', 'nickname']
    restrict_to -- Optional. A django.db.models.Q object representing the subset
        of objects to collect translation strings from.
    manager -- Optional. A reference to a manager -- e.g. Person.objects -- to use
        when collecting translation strings.
    properties -- A dictionary of "read only" properties that are composed by more that one field
                  e.g. {'full_name': ['first_name', 'last_name']}
    contexts -- A dictionary including any (pgettext) context that may need
                to be applied to each field.
                e.g. {'name': 'db category name', 'description': 'db detailed category description'}

    Note that both restrict_to and manager are only used when collecting translation
    strings. Gettext lookups will always be performed on relevant fields for all
    objects on registered models.
    """
    if not contexts:
        contexts = {}

    global _REGISTRY
    _REGISTRY[model] = {
        'fields': fields,
        'contexts': contexts,
        'restrict_to': restrict_to,
        'manager': manager,
        'properties': properties,
    }

    for field in fields:
        setattr(model, field, VinaigretteDescriptor(field, contexts.get(field, None)))
    model.untranslated = lambda self, fieldname: self.__dict__[fieldname]

    pre_save.connect(_vinaigrette_pre_save, sender=model)
    post_save.connect(_vinaigrette_post_save, sender=model)


class VinaigretteDescriptor(object):

    def __init__(self, name, context=None):
        self.name = name
        self.context = context

    def __get__(self, obj, type=None):
        if obj:
            key = obj.__dict__[self.name]
        else:
            return object.__getattribute__(type, self.name)
        if not key:
            return key
        if getattr(obj, '_vinaigrette_saving', False):
            return key

        # We double over all the keys to mimic how {% trans %} works
        key = DOUBLE_PERCENTAGE_RE.sub(u'%%', key)
        if self.context:
            text = pgettext(self.context, key)
        else:
            text = ugettext(key)
        return text.replace('%%', '%')

    def __set__(self, obj, value):
        obj.__dict__[self.name] = value
