from rest_framework import serializers
from .models import Order, OrderItem, OrderItemTopping
from apps.tables.serializers import TableSerializer
from apps.menu.serializers import ProductVariantSerializer, ToppingSerializer


class OrderItemToppingSerializer(serializers.ModelSerializer):
    """Serializer for OrderItemTopping model"""
    topping_name = serializers.CharField(source='topping.name', read_only=True)
    topping_details = ToppingSerializer(source='topping', read_only=True)

    class Meta:
        model = OrderItemTopping
        fields = ['id', 'order_item', 'topping', 'topping_name', 'topping_details',
                  'quantity', 'price', 'created_at']
        read_only_fields = ['id', 'price', 'created_at']


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for OrderItem model"""
    variant_details = ProductVariantSerializer(source='variant', read_only=True)
    product_name = serializers.CharField(source='variant.product.name', read_only=True)
    size = serializers.CharField(source='variant.get_size_display', read_only=True)
    toppings = OrderItemToppingSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'variant', 'variant_details', 'product_name', 'size',
                  'quantity', 'price', 'notes', 'toppings', 'total_price',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'price', 'created_at', 'updated_at']

    def get_total_price(self, obj):
        return obj.get_total_price()


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order model"""
    table_details = TableSerializer(source='table', read_only=True)
    table_number = serializers.CharField(source='table.table_number', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    items_count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'table', 'table_details', 'table_number', 'user', 'user_name',
                  'status', 'status_display', 'notes', 'total_amount', 'items', 'items_count',
                  'created_at', 'updated_at', 'confirmed_at', 'served_at', 'completed_at']
        read_only_fields = ['id', 'user', 'total_amount', 'created_at', 'updated_at',
                           'confirmed_at', 'served_at', 'completed_at']

    def get_items_count(self, obj):
        return obj.items.count()


class OrderListSerializer(serializers.ModelSerializer):
    """Simplified serializer for order listing"""
    table_number = serializers.CharField(source='table.table_number', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    items_count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'table', 'table_number', 'user', 'user_name',
                  'status', 'status_display', 'total_amount', 'items_count',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'total_amount', 'created_at', 'updated_at']

    def get_items_count(self, obj):
        return obj.items.count()


class OrderStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating order status"""
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)

