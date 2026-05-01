from django.urls import path
from .views import logout_view
from . import views

urlpatterns = [

    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('login/', views.admin_login, name='admin_login'),

    # alumni management
    path('alumni/', views.manage_alumni, name='manage_alumni'),
    path('approve/<int:user_id>/', views.approve_alumni_admin, name='approve_alumni_admin'),
    path('reject/<int:user_id>/', views.reject_alumni_admin, name='reject_alumni_admin'),
    path('delete/<int:user_id>/', views.delete_alumni, name='delete_alumni'),
    path('alumni/<int:user_id>/', views.alumni_detail_admin, name='alumni_detail_admin'),

    # posts
    path('posts/', views.manage_posts, name='manage_posts'),
    path('delete-post/<int:post_id>/', views.delete_post, name='admin_delete_post'),
    # jobs
    path('jobs/', views.manage_jobs, name='manage_jobs'),
    path('jobs/<int:job_id>/', views.job_detail_admin, name='job_detail_admin'),
    path('jobs/delete/<int:job_id>/', views.delete_job, name='delete_job'),

    # events
    path('events/', views.manage_events, name='manage_events'),
    path('events/<int:event_id>/', views.event_detail_admin, name='event_detail_admin'),
    path('events/delete/<int:event_id>/', views.delete_event, name='delete_event'),

    path('logout/', views.logout_view, name='admin_logout'),
    path('', views.home1, name='home1'),

]