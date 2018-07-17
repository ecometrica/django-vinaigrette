from django.conf import settings
from django.urls import reverse
from django.utils.translation import activate


class VinaigretteAdminLanguageMiddleware(object):
    """
    Use this middleware to ensure the admin is always running under the
    default language, to prevent vinaigrette from clobbering the registered
    fields with the user's picked language in the change views. Also make
    sure that this is after any LocaleMiddleware like classes.
    """

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        self.process_request(request)
        return self.get_response(request)

    def is_admin_request(self, request):
        """Returns True if this request is for the admin views"""
        return request.path.startswith(reverse('admin:index'))

    def process_request(self, request):
        if self.is_admin_request(request):
            # We are in the admin site
            activate(settings.LANGUAGE_CODE)
