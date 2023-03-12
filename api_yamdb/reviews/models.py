from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password

from .constants import (SCORE_CHOICES, ROLE_CHOICES,
                        CODE_LENGTH)


class CustomUserManager(BaseUserManager):
    def create_user(
        self,
        username,
        email,
        password='',
        bio='',
        role='user',
        first_name='',
        last_name=''
    ):
        if username is None:
            raise TypeError('Users must have a username.')

        if email is None:
            raise TypeError('Users must have an email address.')

        user = self.model(
            username=username,
            email=self.normalize_email(email),
            confirmation_code=self.make_random_password(length=CODE_LENGTH),
            password=password,
            role=role,
            bio=bio,
            first_name=first_name,
            last_name=last_name
        )
        user.save()

        return user

    def create_superuser(
        self,
        username,
        email,
        password=None,
        bio='',
        role='admin',
        first_name='',
        last_name=''
    ):
        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(
            username=username,
            email=email,
            password=make_password(password),
            role=role,
            bio=bio,
            first_name=first_name,
            last_name=last_name
        )
        user.is_superuser = True
        user.is_staff = True
        user.email_user(
            subject='confirmation_code',
            message=user.confirmation_code,
            fail_silently=False
        )
        user.save()

        return user


class User(AbstractUser):
    email = models.EmailField(blank=False, unique=True)
    bio = models.TextField(blank=True, null=True)
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='user',
        )
    confirmation_code = models.CharField(max_length=CODE_LENGTH, blank=True, )
    
    objects = CustomUserManager()

    def __str__(self):
        return self.username


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
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['pub_date']
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author'),
                name='unique_review'
            ),
        ]

    def __str__(self):
        return self.text

class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    pub_date = models.DateTimeField(auto_now_add=True)
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments'
    )

    class Meta:
        ordering = ['pub_date']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text
