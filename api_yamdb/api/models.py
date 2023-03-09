from django.contrib.auth.models import AbstractUser
from django.db import models

from .constants import SCORE_CHOICES


class User(AbstractUser):
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    @property
    def is_admin(self):
        return self.is_staff

    @property
    def is_moderator(self):
        return self.groups.filter(name='moderators').exists()

    @property
    def is_user(self):
        return self.groups.filter(name='users').exists()


class Category(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=256
    )

    slug = models.SlugField(
        verbose_name='Идентификатор',
        max_length=50,
        unique=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=256
    )

    slug = models.SlugField(
        verbose_name='Идентификатор',
        max_length=50,
        unique=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Произведение'
    )

    year = models.IntegerField(
        verbose_name='Год издания'
    )

    description = models.TextField(
        max_length=250,
        blank=True
    )

    genre = models.ManyToManyField(
        Genre,
        related_name='genre'
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='categories'
    )

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'


class GenreTitle(models.Model):
    title = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        on_delete=models.CASCADE
    )

    genre = models.ForeignKey(
        Genre,
        verbose_name='Жанр',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.title}, в жанре {self.genre}'
    
    class Meta:
        verbose_name = 'Произведение и жанр'
        verbose_name_plural = 'Произведения и жанры'

class Review(models.Model):
    text = models.TextField()
    score = models.IntegerField(choices=SCORE_CHOICES, default=1)
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews'
    )
    pub_date = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    text = models.TextField()
    author = models.IntegerField()
    pub_date = models.DateTimeField(auto_now_add=True)
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments'
    )

