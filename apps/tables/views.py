from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .models import Table
from .serializers import TableSerializer, TableStatusUpdateSerializer
from core.responses import success_response, StandardResultsSetPagination
from core.mixins import FilterSortMixin, StandardResponseMixin


class TableViewSet(FilterSortMixin, StandardResponseMixin, viewsets.ModelViewSet):
    """ViewSet for Table CRUD operations"""
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    search_fields = ['table_number', 'location']

    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get all available tables"""
        tables = Table.objects.filter(status='available')
        serializer = TableSerializer(tables, many=True)
        return success_response(data=serializer.data, msg='Available tables retrieved successfully')

    @action(detail=False, methods=['get'])
    def occupied(self, request):
        """Get all occupied tables"""
        tables = Table.objects.filter(status='occupied')
        serializer = TableSerializer(tables, many=True)
        return success_response(data=serializer.data, msg='Occupied tables retrieved successfully')

    @action(detail=False, methods=['get'])
    def reserved(self, request):
        """Get all reserved tables"""
        tables = Table.objects.filter(status='reserved')
        serializer = TableSerializer(tables, many=True)
        return success_response(data=serializer.data, msg='Reserved tables retrieved successfully')

    @action(detail=True, methods=['patch'], url_path='update-status')
    def update_status(self, request, pk=None):
        """Update table status"""
        table = self.get_object()
        serializer = TableStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        table.status = serializer.validated_data['status']
        table.save()

        response_serializer = TableSerializer(table)
        return success_response(data=response_serializer.data, msg='Table status updated successfully')

    @action(detail=True, methods=['get'])
    def orders(self, request, pk=None):
        """Get all orders for a table"""
        table = self.get_object()
        # Import here to avoid circular import
        from apps.orders.models import Order
        from apps.orders.serializers import OrderSerializer

        orders = Order.objects.filter(table=table)
        serializer = OrderSerializer(orders, many=True)
        return success_response(data=serializer.data, msg='Table orders retrieved successfully')

