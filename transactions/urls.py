from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    path('', views.transaction_list_view, name='list'),
    path('<str:transaction_id>/', views.transaction_detail_view, name='detail'),
]
