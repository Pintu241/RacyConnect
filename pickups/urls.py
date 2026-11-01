from django.urls import path
from . import views

app_name = 'pickups'

urlpatterns = [
    path('', views.pickup_list_view, name='list'),
    path('create/', views.pickup_create_view, name='create'),
    path('available/', views.collector_available_pickups, name='available'),
    path('<str:reference_id>/', views.pickup_detail_view, name='detail'),
    path('<str:reference_id>/cancel/', views.pickup_cancel_view, name='cancel'),
    path('<str:reference_id>/accept/', views.collector_accept_pickup, name='accept'),
    path('<str:reference_id>/status/<str:new_status>/', views.collector_update_status, name='update_status'),
    path('<str:reference_id>/complete/', views.pickup_complete_view, name='complete'),
]
