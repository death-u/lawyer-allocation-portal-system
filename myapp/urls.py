from django.urls import path
from . import views
urlpatterns = [
    path('', views.login_view, name='login'),
    path('registration/', views.reg_clients, name='reg_clients'),
    path('client-dashboard/', views.client_dashboard, name='client_dashboard'),
    path('lawyer-dashboard/', views.lawyer_dashboard, name='lawyer_dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('submit_case/', views.submit_case, name='submit_case'),
    path('resolve-case/<int:case_id>/', views.resolve_case, name='resolve_case'),
    path('take-case/<int:case_id>/', views.take_case, name='take_case'),
    path('case/<int:case_id>/', views.case_detail, name='case_detail'),
    path('case/<int:case_id>/delete/', views.delete_case, name='delete_case'),
    path('update-profile/', views.update_profile, name='update_profile'),
]
