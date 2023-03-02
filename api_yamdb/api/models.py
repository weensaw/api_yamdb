from django.db import models


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
        on_delete=models.PROTECT,
        related_name='genre'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='categories'
    )

    def __str__(self):
        return self.name
