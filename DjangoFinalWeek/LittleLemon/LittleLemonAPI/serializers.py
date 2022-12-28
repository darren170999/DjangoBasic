from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Cart, MenuItem, Order, OrderItem
from rest_framework.fields import CurrentUserDefault

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {
            'id': {'read_only': True},
            'password': {'write_only': True},
        }

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"

class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price',
                  'featured', 'category', 'category_id']

class CartItemSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    menuitem = MenuItemSerializer()
    class Meta:
        model = Cart
        fields = ['user','menuitem','quantity','unit_price','price']
        extra_kwargs = {
            'price':{'read_only':True},
            'unit_price':{'read_only':True}
        }

class CartMenuItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)
    menuitem = MenuItemSerializer()

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['user','delivery_crew','status','total','date']

class OrderItemSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer()
    class Meta:
        model = OrderItem
        fields = "__all__"