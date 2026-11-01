from django.urls import path
from . import views

app_name = 'recyclers'

urlpatterns = [
    path('marketplace/', views.recycler_marketplace, name='marketplace'),
    path('orders/', views.purchase_request_list, name='purchase_list'),
    path('orders/create/', views.purchase_request_create, name='purchase_create'),
    path('orders/<str:request_id>/', views.purchase_request_detail, name='purchase_detail'),
    path('orders/<str:request_id>/status/<str:new_status>/', views.purchase_status_update, name='status_update'),
]
