from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import Product
from .serializers import ProductSerializer


class CustomPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    filterset_fields = {
        'price': ['gte', 'lte', 'exact'],
        'in_stock': ['exact'],
    }

    search_fields = ['name', 'description']

    ordering_fields = ['price', 'created_at']
    ordering = ['-created_at']

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        data = serializer.data
        data['extra_info'] = {
            'message': 'Это дополнительные данные для конкретного продукта',
            'discount_available': True if instance.price > 1000 else False
        }

        return Response(data)

    @action(detail=False, methods=['get'])
    def discounted(self, request):
        products = self.get_queryset().filter(price__gte=1000)
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)