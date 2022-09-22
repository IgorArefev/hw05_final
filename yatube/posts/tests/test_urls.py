from http import HTTPStatus

from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName')
        cls.user2 = User.objects.create_user(username='NoName2')
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='t_slug',
            description='Тестовое описание группы',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовое поле поста',
        )
        cls.url_index = reverse(
            'posts:index'
        )
        cls.url_profile = reverse(
            'posts:profile', kwargs={'username': f'{cls.user}'}
        )
        cls.url_group = reverse(
            'posts:group_list', kwargs={'slug': f'{cls.group.slug}'}
        )
        cls.url_post = reverse(
            'posts:post_detail', kwargs={'post_id': f'{cls.post.id}'}
        )
        cls.url_create = reverse(
            'posts:post_create'
        )
        cls.url_edit = reverse(
            'posts:post_edit', kwargs={'post_id': f'{cls.post.id}'}
        )
        cls.url_login = reverse(
            'users:login'
        )
        cls.url_fake = '/fake_page/'
        cls.ok = HTTPStatus.OK
        cls.not_found = HTTPStatus.NOT_FOUND

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client2 = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client2.force_login(self.user2)
        cache.clear()

    def test_posts_urls_correct_response(self):
        """Проверка доступности страниц приложения Posts
        для всех и ответа 404 от несуществующих страниц.

        """
        urls_posts = {
            self.url_index: self.ok,
            self.url_group: self.ok,
            self.url_profile: self.ok,
            self.url_post: self.ok,
            self.url_fake: self.not_found,
        }
        for reverse_name, expected_value in urls_posts.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(
                    response.status_code, expected_value,
                    f'страница {reverse_name} не отвечает'
                )

    def test_posts_urls_correct_response_authorized(self):
        """Проверка доступности страниц приложения Posts
        для авторизованного автора.

        """
        urls_posts = {
            self.url_edit: self.ok,
            self.url_create: self.ok,
        }
        for reverse_name, expected_value in urls_posts.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(
                    response.status_code, expected_value,
                    f'страница {reverse_name} не отвечает'
                )

    def test_posts_urls_redirect_authorized(self):
        """Проверка редиректа со страницы редактирования чужого поста
        для авторизованного пользователя.

        """
        response = self.authorized_client2.get(
            self.url_edit, follow=True
        )
        self.assertRedirects(response, self.url_post)

    def test_posts_urls_redirect_anonymous(self):
        """Проверка редиректа анонимного пользователя
        со страницы '/posts/<int:post_id>/edit/' и '/create/'.

        """
        redirect_urls = {
            self.url_edit: f'{self.url_login}?next={self.url_edit}',
            self.url_create: f'{self.url_login}?next={self.url_create}',
        }
        for reverse_name, url in redirect_urls.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name, follow=True)
                self.assertRedirects(response, url)

    def test_posts_urls_uses_correct_template(self):
        """Проверка шаблонов для страниц приложения Posts."""
        template_urls_posts = {
            self.url_create: 'posts/create_post.html',
            self.url_group: 'posts/group_list.html',
            self.url_index: 'posts/index.html',
            self.url_post: 'posts/post_detail.html',
            self.url_edit: 'posts/create_post.html',
            self.url_profile: 'posts/profile.html',
        }
        for reverse_name, template in template_urls_posts.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(
                    response, template,
                    f'не найден шаблон страницы {reverse_name}'
                )
