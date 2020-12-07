from django.contrib import admin
from django.urls import path

from session_manager.views import *
from teambeat import views as app_views

urlpatterns = [
    path('', app_views.Dashboard.as_view(), name='dashboard'),
    path('api/dashboard/', app_views.DashboardAPI.as_view(), name='dashboard_refresh_api'),
    path('api/usersearch/', app_views.UserSearchAPI.as_view(), name='api_user_search'),
    path('teams/new/', app_views.CreateTeam.as_view(), name='teams_create'),
    path('teams/<str:team_uuid>/set-status/', app_views.SetStatus.as_view(), name='teams_set_status'),
    path('teams/admin/<str:team_uuid>/dashboard/', app_views.TeamAdminDashboard.as_view(), name='team_admin_dashboard'),
    path('teams/admin/<str:team_uuid>/dashboard/api/<str:api_target>/', app_views.TeamAdminDashboardAPI.as_view(), name='team_admin_dashboard_api'),
    path('teams/lead/<str:team_uuid>/dashboard/', app_views.TeamLeadDashboard.as_view(), name='team_lead_dashboard'),
    path('admin/', admin.site.urls),
    path('register/', CreateUserView.as_view(), name='session_manager_register'),
    path('login/', LoginUserView.as_view(), name='session_manager_login'),
    path('logout/', LogOutUserView.as_view(), name='session_manager_logout'),
    path('resetpassword/', ResetPasswordWithTokenView.as_view(), name='session_manager_token_reset_password'),
    path('profile/resetpassword/', ResetPasswordFromProfileView.as_view(), name='session_manager_profile_reset_password'),
    path('profile/', Index.as_view(), name='session_manager_profile'),
]
