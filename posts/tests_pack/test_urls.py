from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(
            username='igoshevs',
            email='igoshevs@gmail.com',
            password='igoshevs123',
        )
        cls.group = Group.objects.create(
            slug='test_slug',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='test text',
        )

    def setUp(self):
        self.user = User.objects.create(username="TEST")
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_home_page(self):
        """ Главная страница доступна всем """
        response = self.guest_client.get(reverse('posts:home'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_author_page(self):
        """ Профиль автора """
        response = self.guest_client.get(reverse('posts:profile',
                                         kwargs={'username':
                                                 self.user.username}))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_page(self):
        """ Страница группы доступна всем """
        response = self.guest_client.get(reverse('posts:group_list',
                                                 kwargs={'slug': 'test_slug'}))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_detail(self):
        """ Страница поста доступна всем """
        response = self.guest_client.get(reverse('posts:posts_detail',
                                                 args=({self.post.id})))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_create_auth(self):
        """ Cоздание поста для авторизованного """
        response = self.authorized_client.get(reverse('posts:create'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_author(self):
        """ Страница редактирования только для автора """
        response = self.authorized_client.get(reverse('posts:post_edit',
                                              args=({self.post.id})))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_post_edit(self):
        """ редактирование post_edit выкидывает неавторизованного """
        response = self.guest_client.get(reverse('posts:post_edit',
                                         args=({self.post.id})))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_group_create(self):
        """ создание create выкидывает неавторизованного пользователя """
        response = self.guest_client.get(reverse('posts:create'))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_404(self):
        """ 404 отдает код 404 """
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
