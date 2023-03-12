from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CategoryPagination(PageNumberPagination):
    page_size = 2

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'results': data,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            
        })