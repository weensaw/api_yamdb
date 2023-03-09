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
    name = models.CharField(max_length=50)
    slug = models.SlugField(
        max_length=50,
        unique=True
    )


class Genre(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(
        max_length=50,
        unique=True
    )


class Title(models.Model):
    name = models.CharField(max_length=120)
    year = models.IntegerField()
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
        on_delete=models.PROTECT,
        related_name='categories'
    )

    def __str__(self):
        return self.name


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
