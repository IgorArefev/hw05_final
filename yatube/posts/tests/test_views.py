import datetime
import shutil
import tempfile
from math import ceil

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Follow, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PaginatorTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName')
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='t_slug',
            description='Тестовое описание группы',
        )
        for post_id in range(1, 15):
            cls.posts = Post.objects.bulk_create([
                Post(
                    author=cls.user,
                    text='Тестовое поле поста',
                    group=cls.group
                )
            ])
        cls.url_index = reverse(
            'posts:index'
        )
        cls.url_profile = reverse(
            'posts:profile', kwargs={'username': f'{cls.user}'}
        )
        cls.url_group = reverse(
            'posts:group_list', kwargs={'slug': f'{cls.group.slug}'}
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        cache.clear()

    def _posts_per_page(self, value, page=1):
        """Считает количество постов на заданной странице."""
        pages = ceil(value / settings.PAGINATOR_VALUE)
        if pages > page:
            return settings.PAGINATOR_VALUE
        if pages <= 1:
            return value
        n = value % settings.PAGINATOR_VALUE
        return n

    def test_index_group_profile_pages_contain_N_posts(self):
        """Проверяет количество постов на первой и второй странице
        по адресам index, group_list и profile.

        """
        posts_per_page = [
            (
                self.url_index,
                self._posts_per_page(Post.objects.count())
            ),
            (
                self.url_index + '?page=2',
                self._posts_per_page(Post.objects.count(), 2)
            ),
            (
                self.url_group,
                self._posts_per_page(
                    len(Post.objects.filter(group=self.group.id))
                )
            ),
            (
                self.url_group + '?page=2',
                self._posts_per_page(
                    len(Post.objects.filter(group=self.group.id)), 2
                )
            ),
            (
                self.url_profile,
                self._posts_per_page(
                    len(Post.objects.filter(author=self.user))
                )
            ),
            (
                self.url_profile + '?page=2',
                self._posts_per_page(
                    len(Post.objects.filter(author=self.user)), 2
                )
            )
        ]
        for url, posts in posts_per_page:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(
                    len(response.context['page_obj']),
                    posts,
                    f'На странице "{url}" неверное количество постов'
                )


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName')
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='t_slug',
            description='Тестовое описание группы',
        )
        cls.gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовое поле поста',
            group=cls.group
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

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def _context_page_obj(self, url):
        """Проверка контекста page_obj."""
        response = self.authorized_client.get(url)
        post_object = response.context['page_obj'][0]
        text = post_object.text
        author = post_object.author.username
        pub_date = post_object.pub_date.today().date()
        group = post_object.group.title
        image = post_object.image
        context = {
            'text': text,
            'author': author,
            'pub_date': pub_date,
            'group': group,
            'image': image,
            'response': response,
        }
        return context

    def _context_create_edit(self, url):
        """Проверка полей форм create и edit"""
        response = self.authorized_client.get(url)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        return response

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self._context_page_obj(self.url_index)
        self.assertEqual(response['group'], self.group.title)
        self.assertEqual(response['text'], self.post.text)
        self.assertEqual(response['author'], self.user.username)
        self.assertEqual(response['image'], self.post.image)
        self.assertEqual(
            response['pub_date'], datetime.datetime.today().date()
        )

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self._context_page_obj(self.url_group)
        group_object = response['response'].context['group']
        group_title = group_object.title
        group_description = group_object.description
        self.assertEqual(group_title, self.group.title)
        self.assertEqual(group_description, self.group.description)
        self.assertEqual(response['author'], self.user.username)
        self.assertEqual(response['text'], self.post.text)
        self.assertEqual(response['image'], self.post.image)
        self.assertEqual(
            response['pub_date'], datetime.datetime.today().date()
        )

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self._context_page_obj(self.url_profile)
        author_object = response['response'].context['author']
        posts_count = author_object.posts.count()
        author = author_object.username
        self.assertEqual(author, self.user.username)
        self.assertEqual(response['group'], self.group.title)
        self.assertEqual(response['text'], self.post.text)
        self.assertEqual(response['image'], self.post.image)
        self.assertEqual(
            response['pub_date'], datetime.datetime.today().date()
        )
        self.assertEqual(
            posts_count, len(Post.objects.filter(author=self.user))
        )

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.url_post)
        post_object = response.context['post']
        pub_date = post_object.pub_date.today().date()
        posts_count = post_object.author.posts.count()
        author = post_object.author.username
        text = post_object.text
        image = post_object.image
        group_title = post_object.group.title
        self.assertEqual(group_title, self.group.title)
        self.assertEqual(pub_date, datetime.datetime.today().date())
        self.assertEqual(author, self.user.username)
        self.assertEqual(image, self.post.image)
        self.assertEqual(
            posts_count, len(Post.objects.filter(author=self.user))
        )
        self.assertEqual(text, self.post.text)

    def test_create_post_show_correct_context(self):
        """Шаблон creat_post сформирован с правильным контекстом."""
        self._context_create_edit(self.url_create)

    def test_post_edit_show_correct_context(self):
        """Шаблон creat_post сформирован с правильным контекстом."""
        response = self._context_create_edit(self.url_edit)
        post_id = response.context['post'].id
        is_edit = response.context['is_edit']
        self.assertEqual(post_id, self.post.id)
        self.assertTrue(is_edit)

    def test_posts_views_uses_correct_template(self):
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

    def test_index_cache(self):
        """Проверка работы кеширования страницы index."""
        response_1 = self.authorized_client.get(self.url_index)
        old_content = response_1.content
        Post.objects.create(
            text='Test',
            author=self.user
        )
        response_2 = self.authorized_client.get(self.url_index)
        cache_content = response_2.content
        self.assertEqual(old_content, cache_content)
        cache.clear()
        response_3 = self.authorized_client.get(self.url_index)
        new_content = response_3.content
        self.assertNotEqual(old_content, new_content)


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Author')
        cls.follower = User.objects.create_user(username='Follower')
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовое поле поста'
        )
        cls.url_login = reverse('users:login')
        cls.url_index = reverse('posts:index')
        cls.url_follow_index = reverse('posts:follow_index')
        cls.url_profile = reverse(
            'posts:profile', kwargs={'username': f'{cls.author}'}
        )
        cls.url_follow = reverse(
            'posts:profile_follow', kwargs={'username': f'{cls.author}'}
        )
        cls.url_unfollow = reverse(
            'posts:profile_unfollow', kwargs={'username': f'{cls.author}'}
        )

    def setUp(self):
        self.guest_client = Client()
        self.follower_client = Client()
        self.author_client = Client()
        self.follower_client.force_login(self.follower)
        self.author_client.force_login(self.author)
        cache.clear()

    def test_follow_authorized(self):
        """Проверка, может ли авторизованный пользователь подписываться
        на других пользователей и происходит ли редирект.

        """
        count_follow_old = Follow.objects.count()
        response = self.follower_client.post(self.url_follow)
        follow = Follow.objects.all().last()
        self.assertRedirects(response, self.url_profile)
        self.assertEqual(Follow.objects.count(), count_follow_old + 1)
        self.assertEqual(follow.author_id, self.author.id)
        self.assertEqual(follow.user_id, self.follower.id)

    def test_follow_guest(self):
        """Проверка, может ли не авторизованный пользователь подписываться
        на других пользователей и происходит ли редирект.

        """
        count_follow_old = Follow.objects.count()
        response = self.guest_client.post(self.url_follow)
        self.assertRedirects(
            response,
            self.url_login + '?next=' + self.url_follow
        )
        self.assertEqual(Follow.objects.count(), count_follow_old)

    def test_follow_self(self):
        """Проверка, может ли авторизованный пользователь подписываться
        на самого себя и происходит ли редирект.

        """
        count_follow = Follow.objects.count()
        response = self.author_client.post(self.url_follow)
        self.assertRedirects(response, self.url_index)
        self.assertEqual(Follow.objects.count(), count_follow)

    def test_unfollow_authorized(self):
        """Проверка, может ли авторизованный пользователь удалять
        из подписок других пользователей и происходит ли редирект.

        """
        Follow.objects.create(
            user=self.follower,
            author=self.author)
        count_follow = Follow.objects.count()
        response = self.follower_client.post(self.url_unfollow)
        self.assertRedirects(response, self.url_profile)
        self.assertEqual(Follow.objects.count(), count_follow - 1)

    def test_unfollow_none(self):
        """Проверка, может ли авторизованный пользователь удалять
        из подписок пользователей на которых не подписан
        и происходит ли редирект.

        """
        count_follow = Follow.objects.count()
        response = self.follower_client.post(self.url_unfollow)
        self.assertRedirects(response, self.url_index)
        self.assertEqual(Follow.objects.count(), count_follow)

    def test_authorized_see_right_follow_index_if_follow(self):
        """Проверка, появляются ли записи пользователя
        в ленте тех, кто на него подписан.

        """
        Follow.objects.create(
            user=self.follower,
            author=self.author
        )
        response = self.follower_client.get(self.url_follow_index)
        self.assertIn(self.post, response.context['page_obj'].object_list)

    def test_authorized_see_right_follow_index_if_not_follow(self):
        """Проверка, не появляются ли записи пользователя
        в ленте тех, кто на него не подписан.

        """
        response = self.follower_client.get(self.url_follow_index)
        self.assertNotIn(self.post, response.context['page_obj'].object_list)
