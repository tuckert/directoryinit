from django.urls import path
from . import views

urlpatterns = [
    path('thankyou/', views.ThankYouView.as_view(), name='thank-you'),
    path('create/', views.CreateDirectoryView.as_view(), name='create-directory'),
    path('delete/<slug>/', views.DeleteDirectoryView.as_view(), name='delete-directory'),
    path('invitation/detail/<pk>/', views.InvitationDetailView.as_view(), name='invitation'),
    path('invitation/<uidb64>/<token>', views.InvitationUsageView.as_view(), name='use-invitation'),

    path('', views.ListDirectoryView.as_view(), name='list-directories'),
    path('<slug>/create-invitation/', views.CreateInvitationView.as_view(), name='create-invitation'),
    path('<slug>/create-invitation/<tenant>/', views.CreateInvitationView.as_view(), name='create-invitation-from-tenant'),
    path('<slug>/', views.DetailDirectoryView.as_view(), name='view-directory'),
    path('<slug>/tenants/', views.TenantListView.as_view(), name='list-tenants'),
    path('<slug>/tenant/<pk>', views.TenantDetailView.as_view(), name='tenant-view'),
    path('<slug>/tenant/<pk>/invitations', views.ListInvitationView.as_view(), name='view-tenant-invitations'),
    path('<slug>/invitations/', views.ListInvitationView.as_view(), name='view-directory-invitations'),
    path('<slug>/edit/', views.UpdateDirectoryView.as_view(), name='edit-directory'),

]
