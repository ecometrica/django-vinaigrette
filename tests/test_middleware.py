from __future__ import print_function

try:
    import unittest.mock as mock
except ImportError:
    import mock

from django.conf import settings
from django.test import TestCase, modify_settings
from django.test.client import RequestFactory
from django.utils import translation


from vinaigrette.middleware import VinaigretteAdminLanguageMiddleware


class TestVinaigretteMiddleware(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.get_response_mock = mock.Mock()
        self.middleware = VinaigretteAdminLanguageMiddleware(self.get_response_mock)

    def test_regular_page_uses_user_language(self):
        with translation.override('fr'):
            request = self.factory.get("/")
            self.middleware(request)
            assert translation.get_language() == 'fr'

    def test_admin_uses_default_language(self):
        with translation.override('fr'):
            request = self.factory.get("/admin/")
            self.middleware(request)
            assert translation.get_language() == settings.LANGUAGE_CODE


@modify_settings(
    MIDDLEWARE={
        'append': 'vinaigrette.middleware.VinaigretteAdminLanguageMiddleware',
    },
)
class TestRequest(TestCase):

    def test_regular_page_request(self):
        response = self.client.get('/', HTTP_ACCEPT_LANGUAGE='fr')
        assert response.status_code == 200
        assert translation.get_language() == 'fr'

    def test_admin_page_request(self):
        # test against the admin login page to avoid redirects
        response = self.client.get('/admin/login/', HTTP_ACCEPT_LANGUAGE='fr')
        assert response.status_code == 200
        assert translation.get_language() == 'en'

    def test_admin_page_request_with_override(self):
        with translation.override('fr'):
            # test against the admin login page to avoid redirects
            response = self.client.get('/admin/login/')
            assert response.status_code == 200
            assert translation.get_language() == 'en'
