from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from rest_framework import filters, generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from titles.models import Category, Comment, Genre, Review, Title, User
from .mixins import CDLViewSet, ReviewCommentMixin
from .permissions import IsAdmin, IsAdminUserOrReadOnly 
from .serializers import (CategorySerializer, CommentSerializer, 
                          GenreSerializer, RegisterSerializer,
                          ReviewSerializer, TitleGetSerializer,
                          TitlePostSerializer, UserSerializer)
from .utils import generate_confirmation_code
from api_yamdb.settings import NOREPLY_YAMDB_EMAIL


class CategoryViewSet(CDLViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    search_fields = ['=name', ]
    permission_classes = [IsAdminUserOrReadOnly, ]
    lookup_field = 'slug'


class GenreViewSet(CDLViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    search_fields = ['=name', ]
    permission_classes = [IsAdminUserOrReadOnly, ]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    permission_classes = [IsAdminUserOrReadOnly, ]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleGetSerializer
        return TitlePostSerializer


class ReviewViewSet(ReviewCommentMixin):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        serializer.save(author=self.request.user, title=title)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser | IsAdmin]
    lookup_field = 'username'
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', ]
    pagination_class = PageNumberPagination

    @action(methods=['get', 'patch'], detail=False,
            permission_classes=[IsAuthenticated],
            url_path='me', url_name='me')
    def me(self, request):
        if request.method == 'GET':
            serializer = UserSerializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'PATCH':
            serializer = UserSerializer(request.user,
                                        data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny| IsAdmin]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        confirmation_code = generate_confirmation_code()
        user.confirmation_code = confirmation_code
        user.save()
        
        send_mail(
            'Confirmation_code для YaMDB',
            f'Сonfirmation_code для работы с API YaMDB {confirmation_code}',
            NOREPLY_YAMDB_EMAIL,
            [f'{user.email}'],
            fail_silently=False,
        )
        
        return Response(serializer.data, status=status.HTTP_200_OK)


class CommentViewSet(ReviewCommentMixin):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAdminUserOrReadOnly, ]

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
