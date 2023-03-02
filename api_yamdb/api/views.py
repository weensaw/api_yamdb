from rest_framework import viewsets

from .models import Category, Genre, Title
from .serializers import (CategorySerializer, GenreSerializer,
                          TitleGetSerializer, TitlePostSerializer)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    search_fields = ['=name', ]


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    search_fields = ['=name', ]


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    
    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleGetSerializer
        return TitlePostSerializer
