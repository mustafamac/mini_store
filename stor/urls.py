# في ملف urls.py الخاص بالتطبيق
from django.urls import path
from . import views

app_name = 'stor'

urlpatterns = [
    path('', views.index, name='index'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('contact/', views.contact, name='contact'),
    path('products/', views.product_list, name='product_list'),
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-success/<str:order_id>/', views.order_success, name='order_success'),
]