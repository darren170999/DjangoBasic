from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveDestroyAPIView
from rest_framework import viewsets
from rest_framework.views import APIView
import datetime
from django.http import HttpResponse
from django.contrib.auth.models import User, Group
from .models import Category, Cart, MenuItem, Order, OrderItem
from .serializers import UserSerializer, MenuItemSerializer, CartItemSerializer, CartMenuItemSerializer, OrderSerializer, OrderItemSerializer

def index(request):
    return HttpResponse("test?")

def isManager(user):
    if user.groups.filter(name='Manager').exists():
        return True
    return False

@api_view(['POST'])
def user_signup_view(request):
    user_data = UserSerializer(data=request.data)
    if user_data.is_valid():
        user_data.save()
        username = user_data.validated_data['username']
        print(username)
        user = User.objects.get(username=username)

        Group.objects.get(name='Customer').user_set.add(user)
    return Response({'status': 'success'}, 201)

class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request):
        if isManager(request.user):
            return super().create(request)
        else:
            return Response({'status': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

    def update(self, request, pk=None):
        if isManager(request.user):
            return super().update(request, pk)
        else:
            return Response({'status': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

    def partial_update(self, request, pk=None):
        if isManager(request.user):
            return super().partial_update(request, pk)
        else:
            return Response({'status': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, pk=None):
        if isManager(request.user):
            return super().destroy(request, pk)
        else:
            return Response({'status': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

class ManagerGroupManagementView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        if not isManager(request.user):
            return Response({'status': 'Unauthorized'}, 403)

        managers = User.objects.filter(groups__name='Manager')
        print(managers)
        serialized_data = UserSerializer(managers, many=True)
        return Response(serialized_data.data, 200)

    def create(self, request):
        if not isManager(request.user):
            return Response({'status': 'Unauthorized'}, 403)

        user_data = request.data
        try:
            user = User.objects.get(username=user_data['username'])
            group = Group.objects.get(name='Manager')
            user.groups.clear()
            user.groups.add(group)
        except User.DoesNotExist:
            return Response({'status': 'failed'}, 400)
        return Response({'status': 'success'}, 201)

    def destroy(self, request, pk):
        if not isManager(request.user):
            return Response({'status': 'Unauthorized'}, 403)

        user = User.objects.get(pk=pk)

        if isManager(user):
            user.groups.clear()
            Group.objects.get(name='Customer').user_set.add(user)
            return Response(status=200)
        else:
            return Response(status=404)

class DeliveryCrewGroupManagementView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        if not isManager(request.user):
            return Response({'status': 'Unauthorized'}, 403)

        delivery_crew = User.objects.filter(groups__name='Delivery crew')

        serialized_data = UserSerializer(delivery_crew, many=True)
        return Response(serialized_data.data, 200)

    def create(self, request):
        if not isManager(request.user):
            return Response({'status': 'Unauthorized'}, 403)

        user_data = request.data
        try:
            user = User.objects.get(username=user_data['username'])
            group = Group.objects.get(name='Delivery crew')
            user.groups.clear()
            user.groups.add(group)
        except User.DoesNotExist:
            return Response({'status': 'failed'}, 400)
        return Response({'status': 'success'}, 201)

    def destroy(self, request, pk):
        if not isManager(request.user):
            return Response({'status': 'Unauthorized'}, 403)

        user = User.objects.get(pk=pk)

        if isManager(user):
            user.groups.clear()
            Group.objects.get(name='Customer').user_set.add(user)
            return Response(status=200)
        else:
            return Response(status=404)

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def cart_managment_view(request):
    if request.method == 'GET':
        try:
            cart_items = Cart.objects.get(user=request.user)
            cart_items = CartItemSerializer(cart_items)
            return Response(cart_items.data, 200)
        except Cart.DoesNotExist:
            return Response(400)
    elif request.method == 'POST':
        cart_data = CartMenuItemSerializer(data=request.data)
        if cart_data.is_valid():
            quantity = cart_data.validated_data['quantity']
            menuitem = MenuItem.objects.get(
                title=cart_data.validated_data['menuitem']['title'])
            if menuitem.featured:
                cart = Cart.objects.create(
                    user=request.user, menuitem=menuitem, quantity=quantity, unit_price=menuitem.price,
                    price=(menuitem.price*quantity))

            return Response({'status': 'success'}, 201)
    elif request.method == 'DELETE':
        Cart.objects.filter(user=request.user).delete()
        return Response(200)

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def order_management_view(request):
    user = request.user

    if request.method == "GET":
        if request.user.groups.filter(name='Manager').exists():
            context = {
                'orders':[],
            }
            orders = Order.objects.all()
            for order in orders:
                order_item = OrderItem.objects.get(order=order)
                order_data = OrderSerializer(order)
                order_item_data = OrderItemSerializer(order_item)
                order_data = {
                    'order': order_data.data,
                    'order_item': order_item_data.data
                }
                context['orders'].append(order_data)

            return Response(context, 200)
        elif request.user.groups.filter(name='Delivery crew').exists():
            context = {
                'orders': [],
            }
            orders = Order.objects.filter(delivery_crew=user)
            for order in orders:
                order_item = OrderItem.objects.get(order=order)
                order_data = OrderSerializer(order)
                order_item_data = OrderItemSerializer(order_item)
                order_data = {
                    'order': order_data.data,
                    'order_item': order_item_data.data
                }
                context['orders'].append(order_data)

            return Response(context, 200)
        elif request.user.groups.filter(name='Customer').exists():
            context = {
                'orders': [],
            }
            orders = Order.objects.filter(user=user)
            for order in orders:
                order_item = OrderItem.objects.get(order=order)
                order_data = OrderSerializer(order)
                order_item_data = OrderItemSerializer(order_item)
                order_data = {
                    'order': order_data.data,
                    'order_item': order_item_data.data
                }
                context['orders'].append(order_data)

            return Response(context, 200)
        else:
            return Response(403)
    elif request.method == "POST":
        if request.user.groups.filter(name='Customer').exists():
            order_date = datetime.date.today()
            user_cart = Cart.objects.get(user=user)
            total = user_cart.quantity * user_cart.menuitem.price
            order = Order.objects.create(
                user=user,
                total=total,
                date=order_date
            )

            order_item = OrderItem.objects.create(
                order=order,
                menuitem=user_cart.menuitem,
                quantity=user_cart.quantity,
                unit_price=user_cart.unit_price,
                price=user_cart.price
            )

            user_cart.delete()
            return Response({'status': 'success'}, 201)
        else:
            return Response(403)

@api_view(['GET', 'POST', 'DELETE','PUT','PATCH'])
@permission_classes([IsAuthenticated])
def single_order_management_view(request,pk):
    if request.user.groups.filter(name='Customer').exists():
        if request.method == "GET":
            order = Order.objects.get(pk=pk)
            if order.user == request.user:
                order_items = OrderItem.objects.filter(order=order)
                order_items_data = OrderItemSerializer(order_items,many=True).data
                return Response(order_items_data,200)
            else:
                return Response(403)
        if request.method in ['PUT','PATCH']:
            delivery_crew_username = request.POST.get('username')
            order_status = request.POST.get('status')
            
            order = Order.objects.get(pk=pk)
            if delivery_crew_username:
                delivery_crew = User.objects.get(username=delivery_crew_username)
            if order_status != None:
                order.delivery_crew = delivery_crew
                order.status = order_status
            return Response(201)

    if request.user.groups.filter(name='Manager').exists():
        if request.method == "DELETE":
            Order.objects.filter(pk=pk).delete()
        return Response(200)

    if request.user.groups.filter(name='Delivery crew').exists():
        if request.method == "PATCH":
            order_status = request.POST.get('status')
            Order.objects.filter(pk=pk).update(status=order_status)
            return Response(200)
    return Response(400)