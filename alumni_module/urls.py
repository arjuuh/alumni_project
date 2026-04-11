from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),              # home1.html
    path('login/', views.user_login, name='login'), # home.html (login page)
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.user_logout, name='logout'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    #path('directory/', views.alumni_directory, name='alumni_directory'),
    path('profile/<int:user_id>/', views.view_profile, name='view_profile'),
    path('complete-profile/', views.complete_profile, name='complete_profile'),
    path('waiting/', views.waiting_approval, name='waiting_approval'),
    path("alumni/", views.alumni_list_view, name="alumni_list"),
    path('follow/<int:user_id>/', views.toggle_follow, name='toggle_follow'),
    path('notifications/read/', views.mark_notifications_read, name='mark_notifications_read'),
    path('jobs/', views.jobs, name='jobs'),
    path('events/', views.events, name='events'),
    path('jobs/<int:job_id>/', views.job_detail, name='job_detail'),
    path("events/<int:event_id>/", views.event_detail, name="event_detail"),
    path("messages/", views.messages_home, name="messages"),
    path("messages/<int:conv_id>/", views.messages_home, name="messages_conv"),
    path("messages/start/<int:user_id>/", views.start_conversation, name="start_conversation"),
    path("messages/send/", views.send_message, name="send_message"),
    path("messages/<int:conv_id>/fetch/", views.fetch_messages, name="fetch_messages"),
    path("messages/<int:conv_id>/clear/", views.clear_chat, name="clear_chat"),
    path("post/<int:post_id>/delete/", views.delete_post, name="delete_post"),
    path("post/<int:post_id>/edit/", views.edit_post, name="edit_post"),
    path("connections/followers/", views.followers_list, name="followers_list"),
    path("connections/following/", views.following_list, name="following_list"),
    path("send-otp/", views.send_otp, name="send_otp"),
    path("verify-otp/", views.verify_otp, name="verify_otp"),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path("jobs/", views.jobs_view, name="jobs"),
    path("jobs/<int:job_id>/", views.job_detail, name="job_detail"),
    path("alumni-jobpost/", views.alumni_jobpost, name="alumni_jobpost"),
    path("alumni/delete-job/<int:job_id>/", views.alumni_delete_job, name="alumni_delete_job"),
    path('alumni-eventpost/', views.alumni_eventpost, name='alumni_eventpost'),
    path('events/', views.events_view, name='events'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    path('delete-event/<int:event_id>/', views.alumni_delete_event, name='alumni_delete_event'),


]