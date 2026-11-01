from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_index, name='index'),
    path('customer/', views.customer_dashboard, name='customer'),
    path('collector/', views.collector_dashboard, name='collector'),
    path('recycler/', views.recycler_dashboard, name='recycler'),
    path('admin/', views.admin_dashboard, name='admin'),
    path('admin/verify-collector/<int:profile_id>/', views.verify_collector_action, name='verify_collector'),
    path('admin/complaint/<int:complaint_id>/<str:new_status>/', views.update_complaint_status, name='update_complaint'),
]
