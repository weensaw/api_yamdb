from django.shortcuts import get_object_or_404
#from django.contrib.auth.password_validation import validate_password
from djoser.serializers import UserSerializer
from rest_framework import serializers
#from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Category, Comment, Genre, Review, Title, User


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class EmailAuthSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField(max_length=100)

    def validate(self, data):
        user = get_object_or_404(
            User, confirmation_code=data['confirmation_code'],
            username=data['username']
        )
        return get_tokens_for_user(user)


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
    rating = serializers.IntegerField(
        source='reviews__score__avg', read_only=True
    )
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category'
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
        read_only=True)

    class Meta:
        fields = ('id', 'title', 'text', 'author', 'score', 'pub_date')
        model = Review

    def validate(self, data):
        super().validate(data)

        if self.context['request'].method != 'POST':
            return data

        user = self.context['request'].user
        title_id = (
            self.context['request'].parser_context['kwargs']['title_id']
        )
        if Review.objects.filter(author=user, title__id=title_id).exists():
            raise serializers.ValidationError(
                    "Вы уже оставили отзыв на данное произведение")
        return data


class CommentSerializer(serializers.ModelSerializer):
    review = serializers.SlugRelatedField(
        read_only=True,
        slug_field='id',
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True)

    class Meta:
        fields = ('id', 'review', 'text', 'author', 'pub_date')
        model = Comment


class CustomUserSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username',
                  'bio', 'email', 'role')


#class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    
#    @classmethod
#   def get_token(cls, user):
#        token = super().get_token(user)
        #token['username'] = user.username
        #token['email'] = user.email
        #token['confirmation_code'] = user.confirmation_code
        #token['roles'] = user.roles
#        return token


class RegisterSerializer(serializers.ModelSerializer):
    #password = serializers.CharField(write_only=True,
    #                                 required=True,
    #                                 validators=[validate_password])
    #password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    #def validate(self, attrs):
    #    if attrs['password'] != attrs['password_confirm']:
    #        raise serializers.ValidationError("Passwords do not match")
    #    return attrs

    #def create(self, validated_data):
    #    validated_data.pop('password_confirm')
    #    user = get_user_model().objects.create_user(**validated_data)
    #    return user
