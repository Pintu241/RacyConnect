from django.urls import path
from . import views

app_name = 'scrap'

urlpatterns = [
    path('categories/', views.category_list_view, name='list'),
    path('categories/<slug:slug>/', views.category_detail_view, name='detail'),
    path('api/rates/', views.api_get_rates, name='api_rates'),
    path('manage/', views.category_manage_list, name='manage'),
    path('manage/create/', views.category_create_view, name='create'),
    path('manage/<int:pk>/edit/', views.category_edit_view, name='edit'),
]
