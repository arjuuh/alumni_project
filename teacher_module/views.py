from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User

from admin_module.models import SystemMetadata
from alumni_module.models import Opportunity, AlumniProfile, AcademicDetails, ProfessionalDetails, ContactDetails
from alumni_module.models import Notification
from .models import JobPost, EventPost, TeacherProfile
from django.core.mail import send_mail
from django.conf import settings


def teacher_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            teacher_profile = TeacherProfile.objects.filter(user=user).first()

            if teacher_profile:
                login(request, user)
                return redirect("teacher_dashboard")
            else:
                messages.error(request, "You are not authorized as a teacher.")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "teacher/teacher_login.html")


@login_required
def teacher_dashboard(request):
    teacher_profile = TeacherProfile.objects.filter(user=request.user).first()

    if not teacher_profile:
        return redirect("teacher_login")

    dept = teacher_profile.department

    pending_requests = SystemMetadata.objects.filter(
        status="PENDING",
        user__alumniprofile__department=dept
    ).select_related("user")[:5]

    pending_count = SystemMetadata.objects.filter(
        status="PENDING",
        user__alumniprofile__department=dept
    ).count()

    approved_count = SystemMetadata.objects.filter(
        status="APPROVED",
        user__alumniprofile__department=dept
    ).count()

    department_students_count = AlumniProfile.objects.filter(
        department=dept
    ).count()

    return render(request, "teacher/teacher_dashboard.html", {
        "teacher_profile": teacher_profile,
        "pending_requests": pending_requests,   # ✅ VERY IMPORTANT
        "pending_count": pending_count,
        "approved_count": approved_count,
        "department_students_count": department_students_count,
    })

@login_required
def verify_alumni(request):
    teacher_profile = TeacherProfile.objects.filter(user=request.user).first()

    if not teacher_profile:
        return redirect("teacher_login")

    pending = SystemMetadata.objects.filter(
        status="PENDING",
        user__alumniprofile__department=teacher_profile.department
    ).select_related("user")

    return render(request, "teacher/verify_alumni.html", {
        "pending": pending,
        "teacher_profile": teacher_profile,
    })





@login_required
def approve_alumni(request, user_id):
    teacher_profile = TeacherProfile.objects.filter(user=request.user).first()

    if not teacher_profile:
        return redirect("teacher_login")

    metadata = SystemMetadata.objects.filter(
        user_id=user_id,
        status="PENDING",
        user__alumniprofile__department=teacher_profile.department
    ).first()

    if not metadata:
        messages.error(request, "Student not found in your department.")
        return redirect("verify_alumni")

    # Approve alumni
    metadata.status = "APPROVED"
    metadata.save()

    # Send Email Notification
    user_email = metadata.user.email

    if user_email:
        send_mail(
            subject="Alumni Approval",
            message="Congratulations! Your alumni account has been approved successfully by the department.",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user_email],
            fail_silently=False,
        )

    messages.success(request, "Alumni approved successfully and email sent.")
    return redirect("verify_alumni")


@login_required
def approved_alumni(request):
    teacher_profile = TeacherProfile.objects.filter(user=request.user).first()

    if not teacher_profile:
        return redirect("teacher_login")

    approved = SystemMetadata.objects.filter(
        status="APPROVED",
        user__alumniprofile__department=teacher_profile.department
    ).select_related("user")

    return render(request, "teacher/approved_alumni.html", {
        "approved": approved,
        "teacher_profile": teacher_profile,
    })

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from alumni_module.models import (
    AlumniProfile,
    AcademicDetails,
    ProfessionalDetails,
    ContactDetails,
)

@login_required
def teacher_view_alumni(request, user_id):

    alumni_user = get_object_or_404(User, id=user_id)

    # SAFE GET OR EMPTY OBJECTS
    profile, _ = AlumniProfile.objects.get_or_create(user=alumni_user)
    academic, _ = AcademicDetails.objects.get_or_create(user=alumni_user)
    professional, _ = ProfessionalDetails.objects.get_or_create(user=alumni_user)
    contact, _ = ContactDetails.objects.get_or_create(user=alumni_user)

    context = {
        "alumni_user": alumni_user,
        "profile": profile,
        "academic": academic,
        "professional": professional,
        "contact": contact,
    }

    return render(request, "teacher/alumni_detail.html", context)


@login_required
def reject_alumni(request, user_id):
    teacher_profile = TeacherProfile.objects.filter(user=request.user).first()

    if not teacher_profile:
        return redirect("teacher_login")

    metadata = SystemMetadata.objects.filter(
        user_id=user_id,
        status="PENDING",
        user__alumniprofile__department=teacher_profile.department
    ).first()

    if not metadata:
        messages.error(request, "Student not found in your department.")
        return redirect("verify_alumni")

    # Reject alumni
    metadata.status = "REJECTED"
    metadata.save()

    # Send rejection email
    user_email = metadata.user.email

    if user_email:
        send_mail(
            subject="Alumni Application Rejected",
            message="We regret to inform you that your alumni registration has been rejected. Please contact the college for more details.",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user_email],
            fail_silently=False,
        )

    messages.error(request, "Alumni rejected and email sent.")
    return redirect("verify_alumni")

@login_required
def post_job(request):
    if request.method == "POST":
        title = request.POST.get("title")
        company = request.POST.get("company")
        location = request.POST.get("location", "")
        job_type = request.POST.get("job_type", "")
        apply_link = request.POST.get("apply_link", "")
        description = request.POST.get("description")
        deadline = request.POST.get("deadline")

        if title and company and description:
            JobPost.objects.create(
                posted_by=request.user,
                title=title,
                company=company,
                location=location,
                job_type=job_type,
                apply_link=apply_link,
                description=description,
                deadline=deadline,
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

from django.contrib.auth import logout
from django.shortcuts import redirect

def teacher_logout(request):
    logout(request)
    return redirect('teacher_login')


@login_required
def view_alumni(request, user_id):
    alumni_user = get_object_or_404(User, id=user_id)

    profile, _ = AlumniProfile.objects.get_or_create(user=alumni_user)
    academic, _ = AcademicDetails.objects.get_or_create(user=alumni_user)
    professional, _ = ProfessionalDetails.objects.get_or_create(user=alumni_user)
    contact, _ = ContactDetails.objects.get_or_create(user=alumni_user)

    context = {
        "alumni_user": alumni_user,
        "profile": profile,
        "academic": academic,
        "professional": professional,
        "contact": contact,
    }

    return render(request, "teacher/view_alumni.html", context)
