from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [

    # AUTH
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='logout'),

    # PROFILE
    path('dashboard/', views.dashboard, name='dashboard'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('profile/<int:user_id>/', views.view_profile, name='view_profile'),
    path('complete-profile/', views.complete_profile, name='complete_profile'),
    path('waiting/', views.waiting_approval, name='waiting_approval'),

    # ALUMNI LIST + FOLLOW
    path("alumni/", views.alumni_list_view, name="alumni_list"),
    path('follow/<int:user_id>/', views.toggle_follow, name='toggle_follow'),
    path('notifications/read/', views.mark_notifications_read, name='mark_notifications_read'),

    # POSTS
    path('delete-post/<int:post_id>/', views.delete_post, name='delete_post'),
    path("post/<int:post_id>/edit/", views.edit_post, name="edit_post"),

    # CONNECTIONS
    path("connections/followers/", views.followers_list, name="followers_list"),
    path("connections/following/", views.following_list, name="following_list"),

    # MESSAGES
    path("messages/", views.messages_home, name="messages"),
    path("messages/<int:conv_id>/", views.messages_home, name="messages_conv"),
    path("messages/start/<int:user_id>/", views.start_conversation, name="start_conversation"),
    path("messages/send/", views.send_message, name="send_message"),
    path("messages/<int:conv_id>/fetch/", views.fetch_messages, name="fetch_messages"),
    path("messages/<int:conv_id>/clear/", views.clear_chat, name="clear_chat"),

    # JOBS (MERGED)
    path("jobs/", views.jobs_view, name="jobs"),
    path("jobs/<int:job_id>/", views.job_detail, name="job_detail"),
    path("alumni-jobpost/", views.alumni_jobpost, name="alumni_jobpost"),
    path("alumni/delete-job/<int:job_id>/", views.alumni_delete_job, name="alumni_delete_job"),

    # EVENTS (MERGED)
    path('events/', views.events_view, name='events'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    path('alumni-eventpost/', views.alumni_eventpost, name='alumni_eventpost'),
    path('delete-event/<int:event_id>/', views.alumni_delete_event, name='alumni_delete_event'),

    # OTP
    path("send-otp/", views.send_otp, name="send_otp"),
    path("verify-otp/", views.verify_otp, name="verify_otp"),
    path('resend-otp/', views.resend_otp, name='resend_otp'),

    # PASSWORD RESET
    path('forgot-password/',
         auth_views.PasswordResetView.as_view(template_name='auth/password_reset_form.html'),
         name='password_reset'),

    path('forgot-password/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='auth/password_reset_done.html'),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='auth/password_reset_confirm.html'),
         name='password_reset_confirm'),

    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='auth/password_reset_complete.html'),
         name='password_reset_complete'),
]