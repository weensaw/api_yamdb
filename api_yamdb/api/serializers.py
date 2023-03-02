from rest_framework import serializers

from .models import Category, Genre, Title


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'slug')
        lookup_field = 'slug'
        model = Genre


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'slug')
        lookup_field = 'slug'
        model = Category


class TitleSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category'
        )
        model = Title
