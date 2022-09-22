from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from posts.models import User


class UsersURLTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='NoName')
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_users_urls_correct_response(self):
        """Проверка доступности страниц приложения Users
        для всех и ответа 404 от несуществующих страниц.

        """
        urls_users = {
            reverse('users:signup'): HTTPStatus.OK,
            reverse('users:login'): HTTPStatus.OK,
            reverse('users:logout'): HTTPStatus.OK,
            reverse('users:password_reset_form'): HTTPStatus.OK,
            reverse('users:password_reset_done'): HTTPStatus.OK,
            reverse('users:password_reset_complete'): HTTPStatus.OK,
            '/auth/fake_page/': HTTPStatus.NOT_FOUND,
            '/auth/password_change/fake_page/': HTTPStatus.NOT_FOUND,
            '/auth/password_reset/fake_page/': HTTPStatus.NOT_FOUND,
            '/auth/reset/fake_page/': HTTPStatus.NOT_FOUND,
        }
        for reverse_name, expected_value in urls_users.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(
                    response.status_code, expected_value,
                    f'страница {reverse_name} не отвечает'
                )

    def test_users_urls_correct_response_authorized(self):
        """Проверка доступности страниц смены пароля
        для авторизованного пользователя.

        """
        urls_users = {
            reverse('users:password_change_form'): HTTPStatus.OK,
            reverse('users:password_change_done'): HTTPStatus.OK,
        }
        for reverse_name, expected_value in urls_users.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(
                    response.status_code, expected_value,
                    f'страница {reverse_name} не отвечает'
                )

    def test_users_urls_redirect_guest(self):
        """Проверка редиректа со страниц смены пароля
        для не авторизированного пользователя.

        """
        urls_users = {
            reverse(
                'users:password_change_form'
            ): '/auth/login/?next=/auth/password_change/',
            reverse(
                'users:password_change_done'
            ): '/auth/login/?next=/auth/password_change/done/',
        }
        for reverse_name, url in urls_users.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertRedirects(response, url)

    def test_users_pages_uses_correct_template(self):
        """Проверка шаблона для страницы приложения Users."""
        self.assertTemplateUsed(
            self.guest_client.get(reverse('users:signup')),
            'users/signup.html',
            'не найден шаблон страницы "/auth/signup/"'
        )
