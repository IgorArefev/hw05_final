import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName')
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='t_slug',
            description='Тестовое описание группы',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовое поле поста',
            group=cls.group,
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
        cls.url_login = reverse('users:login')
        cls.url_create = reverse('posts:post_create')
        cls.url_edit = reverse(
            'posts:post_edit', kwargs={'post_id': f'{cls.post.id}'}
        )
        cls.url_profile = reverse(
            'posts:profile', kwargs={'username': f'{cls.user}'}
        )
        cls.url_post = reverse(
            'posts:post_detail', kwargs={'post_id': f'{cls.post.id}'}
        )
        cls.url_comment = reverse(
            'posts:add_comment', kwargs={'post_id': f'{cls.post.id}'}
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def tearDown(self):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        self.uploaded.seek(0)

    def test_create_post(self):
        """Проверка, добавляется ли новый пост в базу данных
        с соответствующими полями и происходит ли редирект.

        """
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Новый пост',
            'group': self.group.id,
            'image': self.uploaded
        }
        response = self.authorized_client.post(
            self.url_create,
            data=form_data,
            follow=True,
        )
        new_post = Post.objects.all().first()
        self.assertRedirects(response, self.url_profile)
        self.assertEqual(
            Post.objects.count(),
            posts_count + 1,
            'новый пост не добавился в базу'
        )
        self.assertEqual(
            new_post.text,
            form_data['text'],
            'текст поста не сохранился'
        )
        self.assertEqual(
            new_post.group.id,
            form_data['group'],
            'группа поста не сохранилась'
        )
        self.assertEqual(
            new_post.image,
            'posts/' + self.uploaded.name,
            'картинка поста не сохранилась'
        )
        self.assertEqual(
            new_post.author,
            self.post.author,
            'ошибка с автором поста'
        )

    def test_post_edit(self):
        """Проверка, редактируется ли существующий пост в базе данных
        и происходит ли редирект."""
        posts_count = Post.objects.count()
        old_post = self.post.id
        form_data = {
            'text': 'Отредактированная запись',
            'group': self.group.id,
            'image': self.uploaded
        }
        response = self.authorized_client.post(
            self.url_edit,
            data=form_data,
            follow=True,
        )
        edited_post = Post.objects.get(id=old_post)
        self.assertRedirects(response, self.url_post)
        self.assertEqual(
            Post.objects.count(),
            posts_count,
            'при редактировании создался новый пост'
        )
        self.assertEqual(
            edited_post.text,
            form_data['text'],
            'текст поста не редактируется'
        )
        self.assertEqual(
            edited_post.group.id,
            form_data['group'],
            'группа поста не редактируется'
        )
        self.assertEqual(
            edited_post.image,
            'posts/' + self.uploaded.name,
            'картинка поста не сохранилась'
        )
        self.assertEqual(
            edited_post.author,
            self.post.author,
            'ошибка с автором поста при редактировании'
        )

    def test_guest_client_cant_create_post(self):
        """Проверка, добавляется ли новый пост в базу данных
        от неавторизованного пользователя и происходит ли редирект.

        """
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Новый пост',
            'group': self.group.pk,
        }
        response = self.guest_client.post(
            self.url_create,
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            self.url_login + '?next=' + self.url_create
        )
        self.assertEqual(
            Post.objects.count(),
            posts_count,
            'не авторизированный пользователь может создать пост'
        )

    def test_guest_client_cant_comment_post(self):
        """Проверка, добавляется ли новый комментарий в базу данных
        от неавторизованного пользователя и происходит ли редирект.

        """
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Новый коммент',
        }
        response = self.guest_client.post(
            self.url_comment,
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            self.url_login + '?next=' + self.url_comment
        )
        self.assertEqual(
            Comment.objects.count(),
            comments_count,
            'не авторизированный пользователь может создать коммент'
        )

    def test_create_comment(self):
        """Проверка, добавляется ли новый комментарий
        от авторизированного пользователя в базу данных
        и происходит ли редирект.

        """
        comments_count = Comment.objects.count()
        old_post = self.post.id
        form_data = {
            'text': 'Новый комментарий',
        }
        response = self.authorized_client.post(
            self.url_comment,
            data=form_data,
            follow=True,
        )
        commented_post = Comment.objects.get(post_id=old_post)
        self.assertRedirects(response, self.url_post)
        self.assertEqual(
            Comment.objects.count(),
            comments_count + 1,
            'новый комментарий не добавился в базу'
        )
        self.assertEqual(
            commented_post.text,
            form_data['text'],
            'текст комментария не сохранился'
        )
        self.assertEqual(
            commented_post.author,
            self.post.author,
            'ошибка с автором комментария'
        )
