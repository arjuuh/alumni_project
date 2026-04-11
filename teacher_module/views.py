from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from admin_module.models import SystemMetadata
from alumni_module.models import Opportunity, AlumniProfile, AcademicDetails, ProfessionalDetails, ContactDetails
from .models import JobPost, EventPost
from alumni_module.models import Notification

@login_required
def teacher_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            return redirect('teacher_dashboard')
        else:
            messages.error(request, "Invalid teacher credentials")

    return render(request, 'teacher/teacher_login.html')


@login_required
def teacher_dashboard(request):

    pending_requests = SystemMetadata.objects.filter(status="PENDING")

    verified_count = SystemMetadata.objects.filter(status="APPROVED").count()
    pending_count = pending_requests.count()
    total_alumni = SystemMetadata.objects.count()

    return render(request, "teacher/teacher_dashboard.html", {
        "pending_requests": pending_requests,
        "verified_count": verified_count,
        "pending_count": pending_count,
        "total_alumni": total_alumni,
    })

@login_required
def verify_alumni(request):
    pending = SystemMetadata.objects.filter(status="PENDING").select_related("user")
    return render(request, "teacher/verify_alumni.html", {"pending": pending})


from django.contrib import messages

@login_required
def approve_alumni(request, user_id):
    user = get_object_or_404(User, id=user_id)

    metadata, _ = SystemMetadata.objects.get_or_create(user=user)
    metadata.status = "APPROVED"
    metadata.save()

    # ✅ success message
    messages.success(request, "Alumni approved successfully")

    # ✅ redirect to dashboard
    return redirect("teacher_dashboard")



def approved_alumni(request):
    approved = SystemMetadata.objects.filter(status="APPROVED")
    return render(request, "teacher/approved_alumni.html", {"approved": approved})


@login_required
def teacher_view_alumni(request, user_id):
    user = get_object_or_404(User, id=user_id)

    profile = AlumniProfile.objects.filter(user=user).first()
    academic = AcademicDetails.objects.filter(user=user).first()
    professional = ProfessionalDetails.objects.filter(user=user).first()
    contact = ContactDetails.objects.filter(user=user).first()
    metadata = SystemMetadata.objects.filter(user=user).first()

    return render(request, "teacher/alumni_detail.html", {
        "alumni_user": user,
        "profile": profile,
        "academic": academic,
        "professional": professional,
        "contact": contact,
        "metadata": metadata,
    })

@login_required
def reject_alumni(request, user_id):
    user = get_object_or_404(User, id=user_id)

    metadata, _ = SystemMetadata.objects.get_or_create(user=user)
    metadata.status = "REJECTED"
    metadata.save()

    messages.error(request, "Alumni rejected")

    return redirect("teacher_dashboard")

@login_required
def post_job(request):
    if request.method == "POST":
        title = request.POST.get("title")
        company = request.POST.get("company")
        location = request.POST.get("location", "")
        job_type = request.POST.get("job_type", "")
        apply_link = request.POST.get("apply_link", "")
        description = request.POST.get("description")

        if title and company and description:
            JobPost.objects.create(
                posted_by=request.user,
                title=title,
                company=company,
                location=location,
                job_type=job_type,
                apply_link=apply_link,
                description=description,
            )
            messages.success(request, "Job posted successfully.")
            return redirect("post_job")   # ✅ stay on post job page

        messages.error(request, "Please fill all required fields.")

    # ✅ IMPORTANT: send teacher's posted jobs to template (for delete list)
    teacher_jobs = JobPost.objects.filter(
        posted_by=request.user
    ).order_by("-id")

    return render(request, "teacher/post_job.html", {
        "teacher_jobs": teacher_jobs
    })

@login_required
def post_event(request):
    if request.method == "POST":
        title = request.POST.get("title")
        organizer = request.POST.get("organizer", "")
        location = request.POST.get("location", "")
        event_type = request.POST.get("event_type", "")
        event_date = request.POST.get("event_date")
        event_time = request.POST.get("event_time", "")
        registration_link = request.POST.get("registration_link", "")
        description = request.POST.get("description")

        if title and event_date and description:
            EventPost.objects.create(
                posted_by=request.user,
                title=title,
                organizer=organizer,
                location=location,
                event_type=event_type,
                event_date=event_date,
                event_time=event_time if event_time else None,
                registration_link=registration_link,
                description=description,
            )
            messages.success(request, "Event posted successfully.")
            return redirect("post_event")

        messages.error(request, "Please fill all required fields.")

    teacher_events = EventPost.objects.filter(
        posted_by=request.user
    ).order_by("-id")

    return render(request, "teacher/post_event.html", {
        "teacher_events": teacher_events
    })

@login_required
def delete_job(request, job_id):
    job = get_object_or_404(JobPost, id=job_id, posted_by=request.user)

    job.delete()
    messages.success(request, "Job deleted successfully.")

    return redirect("teacher_dashboard")

@login_required
def delete_event(request, event_id):
    event = get_object_or_404(EventPost, id=event_id, posted_by=request.user)

    event.delete()
    messages.success(request, "Event deleted successfully.")

    return redirect("teacher_dashboard")





