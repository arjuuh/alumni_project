from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.teacher_login, name='teacher_login'),
    path('dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('verify/', views.verify_alumni, name='verify_alumni'),
    path('approve/<int:user_id>/', views.approve_alumni, name='approve_alumni'),
    path('approved-alumni/', views.approved_alumni, name='approved_alumni'),
    path('post-job/', views.post_job, name='post_job'),
    path('post-event/', views.post_event, name='post_event'),
    path('alumni/<int:user_id>/', views.teacher_view_alumni, name='teacher_view_alumni'),
    path('reject/<int:user_id>/', views.reject_alumni, name='reject_alumni'),
    path("delete-job/<int:job_id>/", views.delete_job, name="delete_job"),
    path("delete-event/<int:event_id>/", views.delete_event, name="delete_event"),
    path('logout/', views.teacher_logout, name='teacher_logout'),
    
]