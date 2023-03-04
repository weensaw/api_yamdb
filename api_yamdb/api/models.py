from django.contrib.auth.models import AbstractUser

from django.db import models


ADMIN = 'admin'
MODERATOR = 'moderator'
USER = 'user'
ROLES = [
    (ADMIN, 'Administrator'),
    (MODERATOR, 'Moderator'),
    (USER, 'User'),
]


class User(AbstractUser):
    username = models.CharField(
        verbose_name='Псевдоним пользователя',
        max_length=150,
        unique=True,
    )

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=254,
        unique=True,
    )

    first_name = models.CharField(
        verbose_name='Имя пользователя',
        max_length=150,
    )

    last_name = models.CharField(
        verbose_name='Фамилия пользователя',
        max_length=150,
    )

    bio = models.TextField(
        verbose_name='Биография',
        null=True,
        blank=True,
    )

    role = models.CharField(
        verbose_name='Роль',
        max_length=30,
        choices=ROLES,
        default=USER
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'    


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

    # class Meta:
    #     verbose_name = 'Категория'
    #     verbose_name_plural = 'Категории'


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

    # class Meta:
    #     verbose_name = 'Жанр'
    #     verbose_name_plural = 'Жанры'


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
    
    # class Meta:
    #     verbose_name = 'Произведение'
    #     verbose_name_plural = 'Произведения'
