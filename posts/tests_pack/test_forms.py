from http import HTTPStatus
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group, User, Comment


class PostFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="igoshevs")
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_posts_create(self):
        """форма создает запись если авторизован"""
        posts_count = Post.objects.count()
        form_data = {"text": "Тестовый текст"}
        response = self.authorized_client.post(
            reverse("posts:create"), data=form_data, follow=True
        )
        self.assertRedirects(
            response, reverse("posts:profile",
                              kwargs={"username": self.user.username})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(Post.objects.filter(text="Тестовый текст").exists())
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit(self):
        """форма изменяет запись если """
        self.post = Post.objects.create(
            author=self.user,
            text='test_post_edit',
        )
        self.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='test_description',
        )
        posts_count = Post.objects.count()
        form_data = {'text': 'correct_text', 'group': self.group.id}
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=({self.post.id})),
            data=form_data,
            follow=True,
        )

        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(Post.objects.filter(text='correct_text').exists())
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_not_create(self):
        """форма не изменит запись если не авторизован"""
        self.post = Post.objects.create(
            author=self.user,
            text="test_text",
        )
        self.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='test_description',
        )
        posts_count = Post.objects.count()
        form_data = {"text": "Изменяем текст", "group": self.group.id}
        response = self.guest_client.post(
            reverse("posts:post_edit", args=({self.post.id})),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, str(reverse('users:login')
                             + '?next=' + reverse('posts:post_edit',
                                                  args=({self.post.pk}))))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertFalse(Post.objects.filter(text="Изменяем текст").exists())
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_comment_for_post_created_successfully(self):
        """Тест создания комментария авторизованным пользователем"""
        post = Post.objects.create(
            text='Тестовый текст',
            author=self.user
        )
        form_data = {
            'post': post,
            'author': self.user,
            'text': 'Тестовый комментарий'
        }
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True
        )
        self.assertTrue(post.comments.filter(text=form_data['text']).exists())

    def test_guest_client_cannot_create_comment_for_post(self):
        Post.objects.create(
            text='Тестовый текст',
            author=self.user
        )
        form_data = {
            'text': 'Тестовый комментарий',
            'author': self.guest_client,
        }
        post_id = Post.objects.count()
        comments_count = Comment.objects.count()
        self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': post_id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comments_count)
