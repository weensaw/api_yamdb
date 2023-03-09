from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Category, Comment, Genre, Review, Title

from .models import Category, Comment, Genre, Review, Title

User = get_user_model()


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


class CustomUserSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username',
                  'bio', 'email', 'role')


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['email'] = user.email
        token['roles'] = user.roles
        return token


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,
                                     required=True,
                                     validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'password',
                  'password_confirm', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = get_user_model().objects.create_user(**validated_data)
        return user


class CommentSerializer(serializers.ModelSerializer):
    review = serializers.SlugRelatedField(
        read_only=True,
        slug_field='id',
    )

    class Meta:
        fields = ('id', 'review', 'text', 'author', 'pub_date')
        model = Comment
