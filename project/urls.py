from django.contrib import admin
from django.urls import path

from session_manager.views import *
from teambeat.views import organization_admin_views
from teambeat.views import user_views
from teambeat.views import team_admin_views
from teambeat.views import team_lead_views


urlpatterns = [
    path('', user_views.Dashboard.as_view(), name='dashboard'),
    path('organization/new/', organization_admin_views.CreateOrganization.as_view(), name='create_organization'),
    path('organization/invitations/<str:org_uuid>/handle/', organization_admin_views.HandleOrganizationInvitation.as_view(), name='handle_organization_invitation'),
    path('organization/select/', user_views.SetOrganization.as_view(), name='set_organization'),
    path('organization/add-user/', organization_admin_views.AddUserToOrganization.as_view(), name='add_user_to_organization'),
    path('organization/admin/', organization_admin_views.OrganizationAdminDashboard.as_view(), name='organization_admin_dashboard'),
    path('organization/admin/api/<str:api_target>/', organization_admin_views.OrganizationAdminDashboardAPI.as_view(), name='organization_admin_dashboard_api'),
    path('api/dashboard/', user_views.DashboardAPI.as_view(), name='dashboard_refresh_api'),
    path('api/usersearch/', user_views.UserSearchAPI.as_view(), name='api_user_search'),
    path('teams/new/', team_admin_views.CreateTeam.as_view(), name='teams_create'),
    path('teams/<str:team_uuid>/set-status/', user_views.SetStatus.as_view(), name='teams_set_status'),
    path('teams/admin/<str:team_uuid>/dashboard/', team_admin_views.TeamAdminDashboard.as_view(), name='team_admin_dashboard'),
    path('teams/admin/<str:team_uuid>/dashboard/api/<str:api_target>/', team_admin_views.TeamAdminDashboardAPI.as_view(), name='team_admin_dashboard_api'),
    path('teams/lead/<str:team_uuid>/dashboard/', team_lead_views.TeamLeadDashboard.as_view(), name='team_lead_dashboard'),
    path('admin/', admin.site.urls),
    path('register/', CreateUserView.as_view(), name='session_manager_register'),
    path('login/', LoginUserView.as_view(), name='session_manager_login'),
    path('logout/', LogOutUserView.as_view(), name='session_manager_logout'),
    path('resetpassword/', ResetPasswordWithTokenView.as_view(), name='session_manager_token_reset_password'),
    path('profile/resetpassword/', ResetPasswordFromProfileView.as_view(), name='session_manager_profile_reset_password'),
    path('profile/', user_views.Profile.as_view(), name='session_manager_profile'),
]
