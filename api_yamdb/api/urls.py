from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import UsernameAuthSerializer
from .views import (CategoryViewSet, CommentViewSet,
                    GenreViewSet, RegisterView,
                    ReviewViewSet, TitleViewSet, UserViewSet)


router_v1 = routers.DefaultRouter()
router_v1.register(
    'categories',
    CategoryViewSet,
    basename='categories'
)
router_v1.register(
    'genres',
    GenreViewSet,
    basename='genres'
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

router_v1_auth = [
    path('signup/', RegisterView.as_view()),
    path(
    'token/',
    TokenObtainPairView.as_view(serializer_class=UsernameAuthSerializer)
    ),
]


urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/', include(router_v1_auth)),
    #path('v1/users/me/', UserViewSet.as_view({'patch': 'partial_update'})),
]
