from django.utils.translation import ugettext, ugettext_lazy

class VinaigretteError(Exception):
    pass
    
_registry = {}

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

class VinaigretteDescriptor(object):
    
    def __init__(self, name):
        self.name = name

    def __get__(self, obj, type=None):
        key = obj.__dict__[self.name]
        if not key:
            return key
        return ugettext(key)

    def __set__(self, obj, value):
        obj.__dict__[self.name] = value
