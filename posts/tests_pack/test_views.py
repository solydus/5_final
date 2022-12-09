import tempfile

from http import HTTPStatus
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache
from django.conf import settings


from posts.models import Post, Group, User
from ..views import POST_V

PAGEN = 13


class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.author = User.objects.create(username='igoshevs',
                                         email='igoshevs@gmail.com',
                                         password='igoshevs123',)
        cls.group = Group.objects.create(title='Тестовый заголовок',
                                         slug='test_group',
                                         description='Тестовое описание',)

        cls.user_2 = User.objects.create_user(username='NoName2')
        cls.POSTS_V = POST_V
        pict_pict = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(name='small.gif',
                                      content=pict_pict,
                                      content_type='image/gif')
        cls.picture = SimpleUploadedFile(
            name='small.gif',
            content=pict_pict,
            content_type='image/jpg'
        )
        cls.post = Post.objects.create(author=cls.author,
                                       group=cls.group,
                                       text='Тестовый текст',
                                       image=uploaded)
        cls.user = User.objects.create_user(username='NoName')

    def setUp(self):
        self.user = User.objects.create(username="TEST")
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_post_create_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:create'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_list_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:home'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.id
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        self.assertEqual(post_text_0, self.post.pk)
        self.assertEqual(post_author_0, self.author)
        self.assertEqual(post_group_0, self.group)

    def test_pages_use_correct_templates(self):
        """URL-адрес использует корректный шаблон."""
        templates_pages_names = {
            'posts/index.html': reverse('posts:home'),
            'posts/group_list.html': reverse(
                'posts:group_list', kwargs={'slug': 'test_group'}),
            'posts/profile.html': reverse(
                'posts:profile', kwargs={'username': self.author}),
            'posts/post_detail.html': reverse(
                'posts:posts_detail', kwargs={'post_id': 1}),
            'posts/create.html': reverse('posts:create'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.authorized_client = Client()
        cls.author = User.objects.create_user(username='NoName')
        cls.group = Group.objects.create(
            title='test_title',
            description='test_description',
            slug='test-slug'
        )

    def setUp(self):
        for post_temp in range(PAGEN):
            Post.objects.create(
                text=f'text{post_temp}', author=self.author, group=self.group
            )

    def test_first_page_contains_ten_records(self):
        templates_pages_names = {
            'posts/index.html': reverse('posts:home'),
            'posts/profile.html':
                reverse('posts:profile', kwargs={'username': self.author}),
            'posts/group_list.html':
                reverse('posts:group_list', kwargs={'slug': self.group.slug}),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(
                    len(response.context['page_obj']), POST_V
                )


class CacheIndex(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='posts_author',
        )

    def setUp(self):
        """авторизация пользователя"""
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cache(self):
        """тестируем кэш"""
        content = self.authorized_client.get(reverse('posts:home')).content
        Post.objects.create(
            text='Пост №1',
            author=self.user,
        )
        content_1 = self.authorized_client.get(reverse('posts:home')).content
        self.assertEqual(content, content_1)
        cache.clear()
        content_2 = self.authorized_client.get(reverse('posts:home')).content
        self.assertNotEqual(content_1, content_2)


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(
            username='posts_author',
        )
        cls.follower = User.objects.create(
            username='follower',
        )
        cls.post = Post.objects.create(
            author=FollowTest.author,
            text='Рандомный текст статьи',
        )

    def setUp(self):
        cache.clear()
        self.follower_client = Client()
        self.follower_client.force_login(self.follower)
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_follow_page(self):
        """подписываемся и отписываемся"""
        response = self.follower_client.get(reverse('posts:follow_index'))
        page_object = response.context.get('page_obj').object_list
        self.assertEqual((len(page_object)), 0)
        self.follower_client.get(reverse('posts:profile_follow',
                                 kwargs={'username': self.author.username}))
        response = self.follower_client.get(reverse('posts:follow_index'))
        self.assertEqual((len(response.context['page_obj'])), 1)
        page_object = response.context.get('page_obj').object_list[0]
        self.assertEqual(page_object.author, self.author)
        self.assertEqual(page_object.text, self.post.text)
        self.assertEqual(page_object.pub_date, self.post.pub_date)
        self.follower_client.get(reverse('posts:profile_unfollow',
                                 kwargs={'username': self.author.username}))
        response = self.follower_client.get(reverse('posts:follow_index'))
        page_object = response.context.get('page_obj').object_list
        self.assertEqual((len(page_object)), 0)

    def test_cant_following(self):
        response = self.author_client.get(reverse('posts:follow_index'))
        page_object = response.context.get('page_obj').object_list
        self.assertEqual((len(page_object)), 0)
        self.author_client.get(
            reverse('posts:profile_follow',
                    kwargs={
                        'username': self.author.username
                    })
        )
        response = self.author_client.get(reverse('posts:follow_index'))
        self.assertEqual((len(page_object)), 0)
