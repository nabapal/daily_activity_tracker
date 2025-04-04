# activity/urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('dashboard/', views.user_dashboard, name='dashboard'),
    path('lead-dashboard/', views.team_lead_dashboard, name='team_lead_dashboard'),
    path('admin-dashboard/', views.super_admin_dashboard, name='super_admin_dashboard'),
    path('activity/<int:activity_id>/', views.activity_detail, name='activity_detail'),
    path('assign-activity/', views.assign_activity, name='assign_activity'),
    path('export-report/', views.export_report, name='export_report'),
    path('', views.home, name='home'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
]
