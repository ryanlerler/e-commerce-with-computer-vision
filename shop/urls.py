from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('add_product/', views.add_product, name='add_product'),
    path('cart/', views.cart, name='cart'),
    path('add_to_cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('process_image/<int:product_id>/', views.process_image, name='process_image'),
]
