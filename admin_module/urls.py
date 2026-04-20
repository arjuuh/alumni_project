from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('alumni/', views.manage_alumni, name='manage_alumni'),
    path('jobs/', views.manage_jobs, name='manage_jobs'),
    path('events/', views.manage_events, name='manage_events'),
    path('teachers/', views.manage_teachers, name='manage_teachers'),
    path('alumni/delete/<int:id>/', views.delete_alumni, name='delete_alumni'),

    # JOBS
    path('jobs/add/', views.add_job, name='add_job'),
    path('jobs/edit/<int:id>/', views.edit_job, name='edit_job'),
    path('jobs/delete/<int:id>/', views.delete_job, name='delete_job'),

    # EVENTS
    path('events/add/', views.add_event, name='add_event'),
    path('events/edit/<int:id>/', views.edit_event, name='edit_event'),
    path('events/delete/<int:id>/', views.delete_event, name='delete_event'),

    # TEACHER
    path('teachers/delete/<int:id>/', views.delete_teacher, name='delete_teacher'),

]