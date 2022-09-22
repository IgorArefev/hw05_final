from http import HTTPStatus

from django.test import TestCase


class CustomErrorsClass(TestCase):
    def test_404error_page(self):
        response = self.client.get('/fake_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
