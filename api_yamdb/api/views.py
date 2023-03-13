from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models.aggregates import Avg

from rest_framework import filters, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (AllowAny, IsAdminUser,
                                        IsAuthenticated)
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenViewBase

from reviews.models import (Category, Comment, Genre,
                            Review, Title, User)
from .filters import TitleFilter
from .mixins import CDLViewSet
from .paginations import CategoryPagination
from .permissions import (IsAdmin, IsAdminUserOrReadOnly,
                          AuthorOrHasRoleOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, RegisterSerializer,
                          ReviewSerializer, TitleGetSerializer,
                          TitlePostSerializer, TokenSerializer,
                          UserSerializer)
from .utils import generate_confirmation_code


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
        rating=Avg('reviews__score')).order_by('-year')
    permission_classes = [IsAdminUserOrReadOnly, ]
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = TitleFilter
    filterset_fields = ('genre', 'category', 'year', 'name')
    pagination_class = PageNumberPagination

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


class RegisterView(views.APIView):
    permission_classes = [AllowAny, ]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.data['username']
            email = serializer.data['email']
            user, _ = User.objects.get_or_create(username=username,
                                                 email=email)
            user.email_user(
                subject='Confirmation_code для YaMDB',
                message=f'Сonfirmation_code {user.confirmation_code}',
                fail_silently=False
            )
            user.confirmation_code = generate_confirmation_code()
            user.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenView(TokenViewBase):
    permission_classes = (AllowAny,)
    serializer_class = TokenSerializer
