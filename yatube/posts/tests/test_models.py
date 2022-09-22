from django.test import TestCase

from posts.models import Comments, Group, Post, User


class PostModelTests(TestCase):
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
        )
        cls.comment = Comments.objects.create(
            author=cls.user,
            post=cls.post,
            text='Тестовое поле коммента',
        )

    def test_str_group_function(self):
        """Проверяем, что, у модели Group, корректно работает __str__."""
        self.assertEqual(
            self.group.title,
            str(self.group),
            'функция __str__ у модели Group работает неверно'
        )

    def test_str_post_function(self):
        """Проверяем, что, у модели Post, корректно работает __str__."""
        self.assertEqual(
            self.post.text[:15],
            str(self.post),
            'функция __str__ у модели Post работает неверно'
        )

    def test_str_comment_function(self):
        """Проверяем, что, у модели Comments, корректно работает __str__."""
        self.assertEqual(
            self.comment.text[:15],
            str(self.comment),
            'функция __str__ у модели Post работает неверно'
        )

    def test_group_verbose_name(self):
        """Проверяем, что, у модели Group,
        verbose_name в полях совпадает с ожидаемым.

        """
        field_verboses_group = {
            'title': 'Группа',
            'slug': 'Человекопонятный URL',
            'description': 'Описание группы',
        }
        for field, expected_value in field_verboses_group.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.group._meta.get_field(field).verbose_name,
                    expected_value,
                    'verbose_name модели Group не совпадает с ожидаемым'
                )

    def test_post_verbose_name(self):
        """Проверяем, что, у модели Post,
        verbose_name в полях совпадает с ожидаемым.

        """
        field_verboses_post = {
            'text': 'Текст',
            'pub_date': 'Дата публикации поста',
            'author': 'Автор поста',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses_post.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name,
                    expected_value,
                    'verbose_name модели Post не совпадает с ожидаемым'
                )

    def test_comments_verbose_name(self):
        """Проверяем, что, у модели Comments,
        verbose_name в полях совпадает с ожидаемым.

        """
        field_verboses_comments = {
            'post': 'Пост',
            'text': 'Комментарий',
            'author': 'Автор комментария',
            'created': 'Дата публикации комментария',
        }
        for field, expected_value in field_verboses_comments.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.comment._meta.get_field(field).verbose_name,
                    expected_value,
                    'verbose_name модели Post не совпадает с ожидаемым'
                )

    def test_group_help_text(self):
        """Проверяем, что, у модели Group,
        help_text в полях совпадает с ожидаемым.

         """
        field_help_group = {
            'title': 'Введите название группы',
            'slug': 'Используйте буквы латинского алфавита и символы "-", "_"',
            'description': 'Введите описание группы',
        }
        for field, expected_value in field_help_group.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.group._meta.get_field(field).help_text,
                    expected_value,
                    'help_text модели Group не совпадает с ожидаемым'
                )

    def test_post_help_text(self):
        """Проверяем, что, у модели Post,
        help_text в полях совпадает с ожидаемым.

        """
        field_help_post = {
            'text': 'Введите текст поста',
            'author': 'Выберите автора поста',
            'group': (
                'Группа, к которой будет относиться пост (необязательное поле)'
            ),
        }
        for field, expected_value in field_help_post.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text, expected_value,
                    'help_text модели Post не совпадает с ожидаемым'
                )

    def test_comments_help_text(self):
        """Проверяем, что, у модели Comments,
        help_text в полях совпадает с ожидаемым.

        """
        field_help_comments = {
            'text': 'Введите текст комментария',
            'author': 'Выберите автора комментария',
            'post': 'Выберите пост комментария',
        }
        for field, expected_value in field_help_comments.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.comment._meta.get_field(field).help_text,
                    expected_value,
                    'help_text модели Post не совпадает с ожидаемым'
                )
