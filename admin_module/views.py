from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required


from .models import SystemMetadata
from alumni_module.models import Post, Job ,Event
from teacher_module.models import JobPost, EventPost
from alumni_module.models import Opportunity, AlumniProfile, AcademicDetails, ProfessionalDetails, ContactDetails



from django.contrib.auth import authenticate, login


def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:   # 🔥 ONLY ADMIN
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Invalid admin credentials")

    return render(request, "admin/login.html")
# ================= ADMIN DASHBOARD =================
@login_required
def admin_dashboard(request):

    total_alumni = SystemMetadata.objects.filter(status="APPROVED").count()
    pending_alumni = SystemMetadata.objects.filter(status="PENDING").count()

    total_posts = Post.objects.count()
    total_jobs = Job.objects.count() + JobPost.objects.count()
    total_events = EventPost.objects.count()

    return render(request, "admin/dashboard.html", {
        "total_alumni": total_alumni,
        "pending_alumni": pending_alumni,
        "total_posts": total_posts,
        "total_jobs": total_jobs,
        "total_events": total_events,
    })


# ================= ALUMNI MANAGEMENT =================
from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden

from .models import SystemMetadata
from alumni_module.models import AlumniProfile



@login_required
def manage_alumni(request):

    alumni = SystemMetadata.objects.select_related("user").filter(
        user__isnull=False,
        user__is_superuser=False,   # ❌ remove admin
        user__is_staff=False        # ❌ remove staff (teachers/admins)
    ).order_by("-id")

    return render(request, "admin/manage_alumni.html", {
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


from django.views.decorators.http import require_POST


@require_POST
@login_required
def delete_alumni(request, user_id):

    if not request.user.is_superuser:
        messages.error(request, "Permission denied")
        return redirect("admin_dashboard")

    if request.user.id == user_id:
        messages.error(request, "You cannot delete yourself")
        return redirect("manage_alumni")

    try:
        with transaction.atomic():

            # delete everything related FIRST
            Post.objects.filter(user_id=user_id).delete()
            Job.objects.filter(user_id=user_id).delete()
            AlumniProfile.objects.filter(user_id=user_id).delete()
            SystemMetadata.objects.filter(user_id=user_id).delete()

            # finally delete user
            User.objects.filter(id=user_id).delete()

        messages.success(request, "Alumni deleted successfully")

    except Exception as e:
        messages.error(request, f"Delete failed: {str(e)}")

    return redirect("manage_alumni")



@login_required
def alumni_detail_admin(request, user_id):

    user = get_object_or_404(User, id=user_id)

    profile = AlumniProfile.objects.filter(user=user).first()
    academic = AcademicDetails.objects.filter(user=user).first()
    professional = ProfessionalDetails.objects.filter(user=user).first()
    contact = ContactDetails.objects.filter(user=user).first()
    metadata = SystemMetadata.objects.filter(user=user).first()

    return render(request, "admin/alumni_detail.html", {
        "alumni_user": user,
        "profile": profile,
        "academic": academic,
        "professional": professional,
        "contact": contact,
        "metadata": metadata,
    })



# ================= POSTS =================

@login_required
def manage_posts(request):
    posts = Post.objects.all().order_by('-created_at')

    return render(request, "admin/manage_posts.html", {
        "posts": posts
    })

@login_required
def delete_post(request, post_id):

    post = get_object_or_404(Post, id=post_id)

    post.delete()

    messages.success(request, "Post deleted successfully")

    return redirect('manage_posts')


# ================= JOBS =================
from django.shortcuts import render, get_object_or_404, redirect
from alumni_module.models import Job   # adjust if your model is elsewhere



from teacher_module.models import JobPost
@login_required
def manage_jobs(request):
    alumni_jobs = Job.objects.all()
    teacher_jobs = JobPost.objects.all()

    jobs = list(alumni_jobs) + list(teacher_jobs)

    # sort by latest (assuming both have created_at)
    jobs = sorted(jobs, key=lambda x: x.created_at, reverse=True)

    return render(request, "admin/manage_jobs.html", {
        "jobs": jobs
    })




def job_detail_admin(request, job_id):

    job = Job.objects.filter(id=job_id).first()

    if not job:
        job = JobPost.objects.filter(id=job_id).first()

    if not job:
        return redirect('manage_jobs')  # safe fallback

    return render(request, "admin/job_detail.html", {
        "job": job
    })


from teacher_module.models import JobPost
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

@login_required
@require_POST
def delete_job(request, job_id):

    job = Job.objects.filter(id=job_id).first()

    if not job:
        job = JobPost.objects.filter(id=job_id).first()

    if not job:
        return redirect('manage_jobs')

    job.delete()
    return redirect('manage_jobs')
# ================= EVENTS =================
from teacher_module.models import EventPost
@login_required
def manage_events(request):
    alumni_events = Event.objects.all()
    teacher_events = EventPost.objects.all()

    # combine both
    events = list(alumni_events) + list(teacher_events)

    # sort manually (since different models)
    events = sorted(events, key=lambda x: x.id, reverse=True)

    return render(request, "admin/manage_events.html", {
        "events": events
    })

@login_required
def event_detail_admin(request, event_id):
    event = Event.objects.filter(id=event_id).first()

    if not event:
        event = EventPost.objects.filter(id=event_id).first()

    if not event:
        return HttpResponse("Event not found")

    return render(request, "admin/event_detail.html", {
        "event": event
    })


@login_required
def delete_event(request, event_id):

    event = Event.objects.filter(id=event_id).first()

    if not event:
        event = EventPost.objects.filter(id=event_id).first()

    if not event:
        return redirect('manage_events')

    event.delete()
    return redirect('manage_events')


from django.shortcuts import render

def home1(request):
    return render(request, "auth/home1.html")

from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect('home1')  # now this will work ✅