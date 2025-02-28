from django.contrib import admin
from django.urls import path, include
from commerce import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('detail/<slug:slug>/', views.product_details, name='product_details'),
    path('product_grid/', views.product_grid, name='product_grid'),
    path('add_product/', views.add_product, name='add_product'),
    path('edit_product/<int:pk>/', views.edit_product, name='edit_product'),
    path('delete_product/<int:pk>/', views.delete_product, name='delete_product'),
    path('product-comments/<int:pk>/', views.comment_view, name='comment_view'),
    path('customers/', views.customer_list, name='customer_list'),
    path('customer_detail/<int:pk>/', views.customer_details, name='customer_details'),
    path('customer_info/<int:pk>/', views.customer_info, name='customer_info'),
    path('add_customer/', views.add_customer, name='add_customer'),
    path('edit_customer/<int:pk>/', views.edit_customer, name='edit_customer'),
    path('delete_customer/<int:pk>/', views.delete_customer, name='delete_customer'),
    path('about/', views.about, name='about'),
    path('about_alibaba/', views.about_alibaba, name='about_alibaba'),
    path('order_list/', views.order_list, name='order_list'),
    path('order_detail/<int:order_id>/', views.order_details, name='order_details'),
    path('order/<int:order_id>/change-status/<str:new_status>/', views.change_order_status, name='change_order_status'),
    path('order/<int:product_id>/', views.order_product, name='order_product'),
    path("order-summary/", views.order_summary, name="order_summary"),
    path('add_order/', views.add_order, name='add_order'),
    path('order/<int:order_id>/delete/', views.delete_order, name='delete_order'),
    path('register/', views.register, name='register'),
    path("confirm-email/<str:token>/", views.confirm_email, name="confirm_email"),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('export/', views.export_page, name='export_page'),
    path('export/download/', views.export_data, name='export_data')
]