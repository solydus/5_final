from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()

ZNAK_15 = 15


class Group(models.Model):
    text = models.TextField(verbose_name='текст')
    title = models.CharField(max_length=200,
                             verbose_name='Название')
    slug = models.SlugField(unique=True, max_length=50,
                            verbose_name='Номер')
    description = models.TextField(verbose_name='Описание')

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации')
    group = models.ForeignKey(Group,
                              models.SET_NULL,
                              blank=True,
                              null=True,
                              verbose_name='Группа',
                              related_name='posts')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               verbose_name='Автор',
                               related_name='posts')
    image = models.ImageField("Картинка", upload_to="posts/", blank=True)

    def get_absolute_url(self):
        return f'/posts/{self.id}'

    class Meta:
        verbose_name = "Посты"
        ordering = ("-pub_date",)

    def __str__(self):
        return self.text[:ZNAK_15]


class Comment(models.Model):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             verbose_name='Статья',
                             related_name='comments')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               verbose_name='Автор комментария',
                               related_name='comments')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации')
    text = models.TextField(verbose_name='Текст комментария')


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='unique_following'
            )
        ]
