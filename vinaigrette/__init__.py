# Copyright (c) Ecometrica. All rights reserved.
# Distributed under the BSD license. See LICENSE for details.

import re

from django.db.models.signals import pre_save, post_save
from django.utils.translation import ugettext, ugettext_lazy

class VinaigretteError(Exception):
    pass
    
_registry = {}

DOUBLE_PERCENTAGE_RE = re.compile(u'%(?!\()')

def _vinaigrette_pre_save(sender, instance, **kwargs):
    setattr(instance, '_vinaigrette_saving', True)
    
def _vinaigrette_post_save(sender, instance, **kwargs):
    delattr(instance, '_vinaigrette_saving')

def register(model, fields, restrict_to=None, manager=None):
    """Tell vinaigrette which fields on a Django model should be translated.
    
    Arguments:
    model -- The relevant model class
    fields -- A list or tuple of field names. e.g. ['name', 'nickname']
    restrict_to -- Optional. A django.db.models.Q object representing the subset
        of objects to collect translation strings from.
    manager -- Optional. A reference to a manager -- e.g. Person.objects -- to use
        when collecting translation strings.
        
    Note that both restrict_to and manager are only used when collecting translation
    strings. Gettext lookups will always be performed on relevant fields for all
    objects on registered models.
    """
    
    global _registry
    _registry[model] = {
        'fields': fields,
        'restrict_to': restrict_to,
        'manager': manager
    }
    for field in fields:
        setattr(model, field, VinaigretteDescriptor(field))
    model.untranslated = lambda self, fieldname: self.__dict__[fieldname]
    
    pre_save.connect(_vinaigrette_pre_save, sender=model)
    post_save.connect(_vinaigrette_post_save, sender=model)

class VinaigretteDescriptor(object):
    
    def __init__(self, name):
        self.name = name

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
        return ugettext(key).replace('%%', '%')

    def __set__(self, obj, value):
        obj.__dict__[self.name] = value
