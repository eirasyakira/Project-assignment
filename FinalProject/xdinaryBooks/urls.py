from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('profile/', views.profile, name='profile'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('search/', views.search, name='search'),
    path('add_to_cart/<str:book_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<str:book_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/', views.view_cart, name='cart'),
    path('purchase/', views.process_purchase, name='purchase'),
    path('book/<str:book_id>/', views.book_detail, name='book_detail'),
    path('orders/', views.view_orders, name='view_orders'),
    path('order_confirmation/<uuid:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('submit_review/<str:book_id>/', views.submit_review, name='submit_review'),
    path('my_purchases/', views.my_purchases, name='my_purchases'),
]