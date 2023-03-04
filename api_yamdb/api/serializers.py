from rest_framework import serializers

from .models import Category, Genre, Review, Title


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


class TitleGetSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category'
        )
        model = Title


class TitlePostSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category'
        )
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    title = serializers.SlugRelatedField(
        read_only=True,
        slug_field='id',
    )

    class Meta:
        fields = ('id', 'title', 'text', 'score', 'pub_date')
        model = Review
