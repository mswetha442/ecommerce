from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_page, name='logout'),

    path('cart/', views.cart_page, name='cart'),
    path('fav/', views.add_to_favourite, name='fav'),
    path('favviewpage/', views.favviewpage, name='favviewpage'),

    path('remove_cart/<int:cid>', views.remove_cart, name='remove_cart'),
    path('remove_fav/<int:fid>/', views.remove_fav, name='remove_fav'),

    path('collections/', views.collections, name='collections'),
    path('collections/<str:name>/', views.collectionsview, name='collectionsview'),
    path(
        'collections/<str:cname>/<str:pname>/',
        views.product_details,
        name='product_details'
    ),

    path('addtocart/', views.add_to_cart, name='addtocart'),
    path('updatecart/', views.update_cart, name='updatecart'),

    path('checkout/', views.checkout, name='checkout'),

    path('my-orders/', views.my_orders, name='my_orders'),
    path('my-orders/<int:oid>/', views.order_details, name='order_details'),
    path(
    'download-invoice/<int:oid>/',
    views.download_invoice,
    name='download_invoice'
    ), 
    path(
        'order-success/<int:order_id>/',
        views.order_success,
        name='order_success'
    ),

    path(
        'cancel-order/<int:id>/',
        views.cancel_order,
        name='cancel_order'
    ),
]