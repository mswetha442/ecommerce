from django.urls import path
from . import views

urlpatterns = [

    path("", views.dashboard, name="dashboard"),
    path("products/", views.product_list, name="product_list"),
    path("products/add/", views.add_product, name="add_product"),
    path("products/edit/<int:id>/", views.edit_product, name="edit_product"),
    path("products/delete/<int:id>/", views.delete_product, name="delete_product"),
    path("categories/", views.category_list, name="category_list"),
    path("categories/add/", views.add_category, name="add_category"),
    path("categories/edit/<int:id>/", views.edit_category, name="edit_category"),
    path("categories/delete/<int:id>/", views.delete_category, name="delete_category"),
    path("orders/", views.order_list, name="order_list"),
    path("orders/<int:id>/", views.admin_order_details, name="admin_order_details"),
    path("customers/", views.customer_list, name="customer_list"),
    path("customers/<int:id>/", views.customer_details, name="customer_details"),
    path("reports/sales/", views.sales_report, name="sales_report"),
    path("logout/",views.admin_logout,name="admin_logout"),
]