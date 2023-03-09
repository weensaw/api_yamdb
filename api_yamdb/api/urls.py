from django.urls import include, path
from rest_framework import routers

from .views import (CategoryViewSet, CommentViewSet,
                    GenreViewSet, ObtainTokenView,
                    RegisterView, ReviewViewSet, TitleViewSet, UserViewSet)

router_v1 = routers.DefaultRouter()
router_v1.register(
    'categories',
    CategoryViewSet,
    basename='categories'
)
router_v1.register(
    'genre',
    GenreViewSet,
    basename='genre'
)
router_v1.register(
    'titles',
    TitleViewSet,
    basename='titles'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)
router_v1.register('users', UserViewSet, basename='users')


urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1', include('djoser.urls')),
    path('v1', include('djoser.urls.jwt')),
    path('v1/auth/signup/', RegisterView.as_view()),
    path('v1/auth/token/', ObtainTokenView.as_view()),
    path('v1/users/me/', UserViewSet.as_view({'patch': 'partial_update'})),
]
