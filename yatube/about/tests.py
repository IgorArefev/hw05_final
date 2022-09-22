from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class AboutURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_urls_correct_response(self):
        """Проверка доступности страниц приложения About."""
        urls_about = {
            reverse('about:author'): HTTPStatus.OK,
            reverse('about:tech'): HTTPStatus.OK,
            '/about/fake_page/': HTTPStatus.NOT_FOUND,
        }
        for reverse_name, expected_value in urls_about.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(
                    response.status_code, expected_value,
                    f'страница {reverse_name} не отвечает'
                )

    def test_about_urls_uses_correct_template(self):
        """Проверка шаблонов для страниц приложения About."""
        template_urls_about = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }
        for reverse_name, template in template_urls_about.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(
                    response, template,
                    f'не найден шаблон страницы {reverse_name}'
                )
