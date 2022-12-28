from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from . import views

urlpatterns = [
    path('users', views.user_signup_view, name='signup'),
    path('menu-items', views.MenuItemViewSet.as_view({
        'get': 'list',
        'post': 'create',
    })),
    path('menu-items/<int:pk>', views.MenuItemViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy',
    })),
    path('groups/manager/users',views.ManagerGroupManagementView.as_view({
        'get':'list',
        'post':'create'
    })),
    path('groups/manager/users/<int:pk>',views.ManagerGroupManagementView.as_view({
        'delete':'destroy'
    })),
    path('groups/delivery-crew/users',views.DeliveryCrewGroupManagementView.as_view({
        'get':'list',
        'post':'create'
    })),
    path('groups/delivery-crew/users/<int:pk>',views.DeliveryCrewGroupManagementView.as_view({
        'delete':'destroy'
    })),
    path('cart/menu-items',views.cart_managment_view),
    path('orders',views.order_management_view),
    path('orders/<int:pk>',views.single_order_management_view),
]
