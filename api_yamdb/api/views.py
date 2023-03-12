from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.db.models.aggregates import Avg

from rest_framework import filters, status, viewsets
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenViewBase

from reviews.models import Category, Comment, Genre, Review, Title, User
from .mixins import CDLViewSet
from .filters import TitleFilter
from .paginations import CategoryPagination
from .permissions import IsAdmin, IsAdminUserOrReadOnly, AuthorOrHasRoleOrReadOnly 
from .serializers import (CategorySerializer, CommentSerializer, 
                          GenreSerializer, RegisterSerializer,
                          ReviewSerializer, TitleGetSerializer,
                          TitlePostSerializer, TokenSerializer, UserSerializer)
#from .utils import generate_confirmation_code


class CategoryViewSet(CDLViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter, ]
    search_fields = ['=name', ]
    permission_classes = [IsAdminUserOrReadOnly, ]
    lookup_field = 'slug'
    pagination_class = CategoryPagination


class GenreViewSet(CDLViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    search_fields = ['=name', ]
    permission_classes = [IsAdminUserOrReadOnly, ]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')).all()
    permission_classes = [IsAdminUserOrReadOnly, ]
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = TitleFilter
    filterset_fields = ('genre', 'category', 'year', 'name')

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleGetSerializer
        return TitlePostSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [AuthorOrHasRoleOrReadOnly, ]

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [AuthorOrHasRoleOrReadOnly, ]

    def get_queryset(self):
        review = get_object_or_404(
            Review, 
            id=self.kwargs['review_id'],
            title__id=self.kwargs['title_id'])
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review, 
            id=self.kwargs['review_id'],
            title__id=self.kwargs['title_id'])
        serializer.save(author=self.request.user, review=review)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser | IsAdmin]
    lookup_field = 'username'
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', ]
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(methods=['get', 'patch'], detail=False,
            permission_classes=[IsAuthenticated],
            url_path='me', url_name='me')
    def me(self, request):
        if request.method == 'GET':
            serializer = UserSerializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'PATCH':
            user = User.objects.get(username=request.user.username)
            data = request.data.copy()
            data['role'] = user.role
            serializer = UserSerializer(request.user,
                                        data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'DELETE':
            raise MethodNotAllowed(method='DELETE')


class RegisterView(CreateModelMixin, RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny| IsAdmin]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
                serializer.data,
                status=status.HTTP_200_OK,
                headers=headers
        )

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.data)
        username = serializer.data["username"]
        user = get_object_or_404(User, username=username)
        user.email_user(
            subject='Confirmation_code для YaMDB',
            message=f'Сonfirmation_code {user.confirmation_code}',
            fail_silently=False
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class TokenView(TokenViewBase):
    permission_classes = (AllowAny,)
    serializer_class = TokenSerializer
