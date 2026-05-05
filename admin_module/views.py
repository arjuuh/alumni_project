from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_POST
from django.db import transaction

# ================= MODELS =================
from .models import SystemMetadata

from alumni_module.models import (
    Post,
    Job,
    Event,
    Opportunity,
    AlumniProfile,
    AcademicDetails,
    ProfessionalDetails,
    ContactDetails
)

from teacher_module.models import JobPost, EventPost


# ================= ADMIN LOGIN =================
def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            return redirect("admin_dashboard")
        else:
            messages.error(request, "Invalid admin credentials")

    return render(request, "admin_module/login.html")


# ================= DASHBOARD =================
@login_required
@login_required
def admin_dashboard(request):

    total_alumni = SystemMetadata.objects.filter(
        status="APPROVED",
        user__is_superuser=False,
        user__is_staff=False
    ).count()

    pending_alumni = SystemMetadata.objects.filter(
        status="PENDING",
        user__is_superuser=False,
        user__is_staff=False
    ).count()

    total_posts = Post.objects.count()

    total_jobs = Job.objects.count() + JobPost.objects.count()

    total_events = Event.objects.count() + EventPost.objects.count()

    return render(request, "admin_module/dashboard.html", {
        "total_alumni": total_alumni,
        "pending_alumni": pending_alumni,
        "total_posts": total_posts,
        "total_jobs": total_jobs,
        "total_events": total_events,
    })  

# ================= ALUMNI MANAGEMENT =================
@login_required
def manage_alumni(request):

    alumni = SystemMetadata.objects.select_related("user").filter(
        user__is_superuser=False,
        user__is_staff=False
    ).order_by("-id")

    return render(request, "admin_module/manage_alumni.html", {
        "alumni": alumni
    })


@login_required
def approve_alumni_admin(request, user_id):
    metadata = get_object_or_404(SystemMetadata, user_id=user_id)
    metadata.status = "APPROVED"
    metadata.save()

    messages.success(request, "Alumni approved")
    return redirect("manage_alumni")


@login_required
def reject_alumni_admin(request, user_id):
    metadata = get_object_or_404(SystemMetadata, user_id=user_id)
    metadata.status = "REJECTED"
    metadata.save()

    messages.error(request, "Alumni rejected")
    return redirect("manage_alumni")




# ================= ALUMNI DETAIL =================
@login_required
def alumni_detail_admin(request, user_id):

    user = get_object_or_404(User, id=user_id)

    return render(request, "admin_module/alumni_detail.html", {
        "alumni_user": user,
        "profile": AlumniProfile.objects.filter(user=user).first(),
        "academic": AcademicDetails.objects.filter(user=user).first(),
        "professional": ProfessionalDetails.objects.filter(user=user).first(),
        "contact": ContactDetails.objects.filter(user=user).first(),
        "metadata": SystemMetadata.objects.filter(user=user).first(),
    })


# ================= POSTS =================
@login_required
def manage_posts(request):
    posts = Post.objects.all().order_by("-created_at")

    return render(request, "admin_module/manage_posts.html", {
        "posts": posts
    })


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.delete()

    messages.success(request, "Post deleted successfully")
    return redirect("manage_posts")


# ================= JOBS =================
@login_required
def manage_jobs(request):

    alumni_jobs = Job.objects.all()
    teacher_jobs = JobPost.objects.all()

    jobs = sorted(
        list(alumni_jobs) + list(teacher_jobs),
        key=lambda x: x.created_at,
        reverse=True
    )

    return render(request, "admin_module/manage_jobs.html", {
        "jobs": jobs
    })


@login_required
def job_detail_admin(request, job_id):

    job = Job.objects.filter(id=job_id).first()
    model_type = "job"

    if not job:
        job = JobPost.objects.filter(id=job_id).first()
        model_type = "jobpost"

    if not job:
        messages.error(request, "Job not found")
        return redirect("manage_jobs")

    # Normalize posted_by field
    posted_by = None

    if model_type == "job":
        posted_by = getattr(job, "posted_by", None)
    else:
        posted_by = getattr(job, "user", None) or getattr(job, "posted_by", None)

    return render(request, "admin_module/job_detail.html", {
        "job": job,
        "posted_by": posted_by
    })

@require_POST
@login_required
def delete_job(request, job_id):

    job = Job.objects.filter(id=job_id).first() or JobPost.objects.filter(id=job_id).first()

    if job:
        job.delete()

    return redirect("manage_jobs")




# ================= EVENTS =================
@login_required
def manage_events(request):

    alumni_events = Event.objects.all()
    teacher_events = EventPost.objects.all()

    events = sorted(
        list(alumni_events) + list(teacher_events),
        key=lambda x: getattr(x, "created_at", x.id),
        reverse=True
    )

    return render(request, "admin_module/manage_events.html", {
        "events": events
    })


@login_required
def event_detail_admin(request, event_id):

    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        try:
            event = EventPost.objects.get(id=event_id)
        except EventPost.DoesNotExist:
            return redirect("manage_events")

    return render(request, "admin_module/event_detail.html", {
        "event": event
    })


@require_POST
@login_required
def delete_event(request, event_id):

    event = None

    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        try:
            event = EventPost.objects.get(id=event_id)
        except EventPost.DoesNotExist:
            event = None

    if event:
        event.delete()

    return redirect("manage_events")


# ================= LOGOUT =================
def logout_view(request):
    logout(request)
    return redirect("home1")


# ================= HOME =================
def home1(request):
    return render(request, "auth/home1.html")