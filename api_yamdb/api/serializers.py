from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404


from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework.validators import UniqueTogetherValidator
#from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Comment, Genre, Review, Title, User
#from .utils import generate_confirmation_code


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug')
        lookup_field = 'slug'
        model = Genre


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug')
        lookup_field = 'slug'
        model = Category


class TitleGetSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(required=True)
    description = serializers.CharField(
        required=False
    )
    rating = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        fields = (
            'id', 'name', 'year', 'description',
            'genre', 'category', 'rating'
        )
        model = Title


class TitlePostSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug', many=True, queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )

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
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    def validate(self, data):
        title_id = self.context['view'].kwargs.get('title_id')
        author = self.context.get('request').user
        title = get_object_or_404(Title, id=title_id)
        if self.context.get('request').method != 'PATCH':
            if title.reviews.filter(author=author).exists():
                raise serializers.ValidationError(
                    '"Вы уже оставили отзыв на данное произведение"'
                )
        return data

    class Meta:
        fields = ('id', 'title', 'text', 'author', 'score', 'pub_date')
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    pub_date = serializers.DateTimeField(
        read_only=True
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username',
                  'bio', 'email', 'role')


class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate(self, data):
        username=data.get("username"),
        email=data.get("email")      
        if User.objects.filter(username=username).exists():
            user1 = User.objects.filter(username=username)
            user2 = User.objects.filter(email=email)
            if user1 != user2:
                raise serializers.ValidationError('Имя не соотвествуюет email')
        return data

    def validate_username(self, username):
        if username == 'me':
            raise serializers.ValidationError(
                'Сочетание "me" нельзя использовать в качестве никнейма.'
            )
        return username
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.email_user(
                subject='Confirmation_code для YaMDB',
                message=f'Сonfirmation_code {user.confirmation_code}',
                fail_silently=False
            )
        return {
            'email': user.email,
            'username': user.username,
        }


class TokenSerializer(serializers.ModelSerializer, TokenObtainPairSerializer):

    def __init__(self, instance=None, data=..., **kwargs):
        super().__init__(instance, data, **kwargs)
        self.fields['password'].required = False

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')

    def validate(self, attrs):
        authenticate_kwargs = {
            self.username_field: attrs[self.username_field],
        }
        confirm_code = None
        if 'request' in self.context:
            authenticate_kwargs['request'] = self.context['request']
            confirm_code = self.context['request'].data['confirmation_code']

        self.user = authenticate(**authenticate_kwargs)

        if self.user is None:
            raise NotFound(
                'Пользователя не существует.'
            )

        if self.user.confirmation_code != confirm_code:
            raise serializers.ValidationError(
                'Не верный confirmation_code.'
            )

        access = AccessToken.for_user(self.user)

        return {
            'token': str(access)
        }