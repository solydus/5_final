from django.test import TestCase

from ..models import Group, Post, User, ZNAK_15


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create(
            username='igoshevs',
            email='igoshevs@gmail.com',
            password='igoshevs123',
        )
        cls.group = Group.objects.create(
            title='тест заголовка группы',
            slug='test-group',
            description='тест описания группы',
        )
        cls.post = Post.objects.create(
            group=cls.group,
            text='Тест публикации',
            author=cls.test_user,
        )

    def setUp(self):
        self.post = PostModelTest.post
        self.group = PostModelTest.group

    def test_models_have_correct_object_names(self):
        """__str__ в порядке """
        vals = (
            (str(self.post), self.post.text[:ZNAK_15]),
            (str(self.group), self.group.title),
        )
        for value, expected in vals:
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def verbose_name(self):
        """verbose_name в порядке"""
        field_verboses = {
            "text": "Текст",
            "group": "Группа",
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.post._meta.get_field(value).verbose_name, expected
                )

    def help_text(self):
        """help_text в порядке"""
        post = PostModelTest.post
        field_help_texts = {
            "text": "",
            "group": "",
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(post._meta.get_field(value).help_text,
                                 expected)
