from django.test import Client, TestCase
from django.urls import reverse

from posts.models import User


class UserCreateTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_create_user(self):
        """Проверка, добавляется ли новый пользователь в базу данных"""
        users_count = User.objects.count()
        form_data = {
            'first_name': 'First',
            'last_name': 'Last',
            'username': 'NoName',
            'email': 'test@test.ru',
            'password1': 'zaq!@wsx',
            'password2': 'zaq!@wsx',
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertTrue(
            User.objects.filter(
                first_name='First',
                last_name='Last',
                username='NoName',
                email='test@test.ru'
            ).exists()
        )
