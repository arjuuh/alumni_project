from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from .models import Connection, Opportunity
from admin_module.models import SystemMetadata
from .models import AlumniProfile, AcademicDetails, ProfessionalDetails, ContactDetails, Post, AlumniEngagement
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Conversation, Message
from .models import Job
from django.contrib.auth import authenticate, login as auth_login, logout

from django.shortcuts import render

# 🔹 PUBLIC HOME PAGE (2nd image style)
def home(request):
    return render(request, "auth/home1.html")   # <-- new homepage

# 🔹 LOGIN PAGE (your stylish login)
def user_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user_obj = User.objects.get(email=email)

            user = authenticate(
                request,
                username=user_obj.username,
                password=password
            )

            if user is not None:
                metadata = SystemMetadata.objects.filter(user=user).first()

                if not metadata or metadata.status == "PENDING":
                    messages.warning(request, "Your account is waiting for approval.")
                    return redirect("waiting_approval")

                if metadata.status == "REJECTED":
                    messages.error(request, "Your account was rejected.")
                    return redirect("login")

                auth_login(request, user)
                return redirect("dashboard")

            else:
                messages.error(request, "Invalid credentials")
                return redirect("login")

        except User.DoesNotExist:
            messages.error(request, "User not found")
            return redirect("login")

    return render(request, "auth/home.html")


def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        department = request.POST.get("department")

        if password != confirm_password:
            return render(request, "auth/register.html", {"error": "Passwords do not match"})

        if User.objects.filter(username=username).exists():
            return render(request, "auth/register.html", {"error": "Username already exists"})

        if User.objects.filter(email=email).exists():
            return render(request, "auth/register.html", {"error": "Email already registered"})

        if not department:
            return render(request, "auth/register.html", {"error": "Please select your department"})

        user = User.objects.create_user(username=username, email=email, password=password)

        AlumniProfile.objects.get_or_create(
            user=user,
            defaults={"department": department}
        )

        SystemMetadata.objects.get_or_create(
            user=user,
            defaults={"status": "PENDING"}
        )

        login(request, user)
        return redirect("complete_profile")

    return render(request, "auth/register.html")

from .models import Connection   # make sure this import exists


@login_required
def dashboard(request):
    metadata = SystemMetadata.objects.filter(user=request.user).first()

    if not metadata or metadata.status != "APPROVED":
        return redirect("waiting_approval")

    # ── USER PROFILE DATA ──
    profile, _ = AlumniProfile.objects.get_or_create(user=request.user)
    professional = ProfessionalDetails.objects.filter(user=request.user).first()
    academic = AcademicDetails.objects.filter(user=request.user).first()
    contact = ContactDetails.objects.filter(user=request.user).first()

    # ── CREATE POST ──
    if request.method == "POST":
        content = request.POST.get("content")
        image = request.FILES.get("image")

        if content:
            Post.objects.create(
                user=request.user,
                content=content,
                image=image
            )
            messages.success(request, "Posted successfully!")
            return redirect("dashboard")
        else:
            messages.error(request, "Post content cannot be empty.")

    # ── POSTS FEED ──
    posts = Post.objects.all().order_by("-created_at")

    # ── CURRENT USER POST COUNT ──
    posts_count = Post.objects.filter(user=request.user).count()

    # ── FOLLOW COUNTS ──
    followers_count = Connection.objects.filter(following=request.user).count()
    following_count = Connection.objects.filter(follower=request.user).count()

    # ── NOTIFICATIONS (FOLLOWERS WHO FOLLOWED YOU) ──
    notification_followers = Connection.objects.filter(
        following=request.user
    ).select_related("follower").order_by("-id")

    notification_following_ids = Connection.objects.filter(
        follower=request.user
    ).values_list("following_id", flat=True)

    notification_count = Connection.objects.filter(
        following=request.user,
        is_read=False
    ).count()

    return render(request, "alumni/dashboard.html", {
        "profile": profile,
        "professional": professional,
        "academic": academic,
        "contact": contact,
        "posts": posts,
        "posts_count": posts_count,

        "followers_count": followers_count,
        "following_count": following_count,

        "notification_followers": notification_followers,
        "notification_following_ids": notification_following_ids,
        "notification_count": notification_count,
    })

@login_required
def edit_profile(request):
    profile, _ = AlumniProfile.objects.get_or_create(user=request.user)
    academic, _ = AcademicDetails.objects.get_or_create(user=request.user)
    professional, _ = ProfessionalDetails.objects.get_or_create(user=request.user)
    contact, _ = ContactDetails.objects.get_or_create(user=request.user)
    engagement, _ = AlumniEngagement.objects.get_or_create(user=request.user)

    if request.method == "POST":
       # Personal
        profile.first_name = request.POST.get('first_name', '')
        profile.last_name = request.POST.get('last_name', '')
        profile.gender = request.POST.get('gender', '')
        profile.address = request.POST.get('address', '')
        profile.city = request.POST.get('city', '')
        profile.state = request.POST.get('state', '')
        profile.country = request.POST.get('country', '')
        profile.postal_code = request.POST.get('postal_code', '')

        #PHOTO UPLOAD
        if request.FILES.get('photo'):
            profile.photo = request.FILES['photo']

        profile.save()

        # Academic
        academic.student_id = request.POST.get('student_id', '')
        academic.degree = request.POST.get('degree', '')
        academic.department = request.POST.get('department', '')
        admission = request.POST.get('year_of_admission')
        academic.year_of_admission = int(admission) if admission else None
        graduation = request.POST.get('year_of_graduation')
        academic.year_of_graduation = int(graduation) if graduation else None
        academic.achievements = request.POST.get('achievements', '')
        academic.save()

        # Professional
        professional.current_designation = request.POST.get('current_designation', '')
        professional.current_company = request.POST.get('current_company', '')
        professional.industry = request.POST.get('industry', '')
        year_exp = request.POST.get('year_of_experience')
        professional.year_of_experience = int(year_exp) if year_exp else 0
        professional.company_location = request.POST.get('company_location', '')
        professional.linkedin_profile = request.POST.get('linkedin_profile', '')
        professional.career_highlights = request.POST.get('career_highlights', '')
        professional.save()

        # Contact (keep same as login email)
        contact.email = request.user.email
        contact.phone_number = request.POST.get('phone_number', '')
        contact.alternate_phone = request.POST.get('alternate_phone', '')
        contact.save()

        # Engagement (checkbox fix)
        engagement.membership_status = request.POST.get('membership_status', '')
        events = request.POST.get('events_attended')
        engagement.events_attended = int(events) if events else None
        engagement.mentorship_interest = request.POST.get('mentorship_interest') == 'on'
        engagement.donation_amount = request.POST.get('donation_amount') or None
        engagement.volunteer_activities = request.POST.get('volunteer_activities', '')
        engagement.newsletter_subscription = request.POST.get('newsletter_subscription') == 'on'
        engagement.save()

        return redirect('dashboard')

    return render(request, 'alumni/edit_profile.html', {
        'profile': profile,
        'academic': academic,
        'professional': professional,
        'contact': contact,
        'engagement': engagement,
    })


"""@login_required
def alumni_directory(request):
    query = request.GET.get('q')
    department = request.GET.get('department')

    # Only approved users (SystemMetadata)
    approved_users = SystemMetadata.objects.filter(
        status="APPROVED"
    ).values_list('user', flat=True)

    profiles = AlumniProfile.objects.filter(user__in=approved_users)

    if query:
        profiles = profiles.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )

    if department:
        profiles = profiles.filter(
            user__academicdetails__department__icontains=department
        )

    return render(request, 'alumni/alumni_directory.html', {
        'profiles': profiles
    })"""



from .models import Connection   # make sure this import exists

@login_required
def view_profile(request, user_id):

    approved = SystemMetadata.objects.filter(
        user_id=user_id,
        status="APPROVED"
    ).first()

    if not approved:
        return redirect('alumni_list')

    profile = AlumniProfile.objects.filter(user_id=user_id).first()
    academic = AcademicDetails.objects.filter(user_id=user_id).first()
    professional = ProfessionalDetails.objects.filter(user_id=user_id).first()
    contact = ContactDetails.objects.filter(user_id=user_id).first()

    # follow status
    is_following = Connection.objects.filter(
        follower=request.user,
        following_id=user_id
    ).exists()

    # stats
    followers_count = Connection.objects.filter(
        following_id=user_id
    ).count()

    following_count = Connection.objects.filter(
        follower_id=user_id
    ).count()

    posts_count = Post.objects.filter(
        user_id=user_id
    ).count()

    # ✅ GET USER POSTS
    user_posts = Post.objects.filter(
        user_id=user_id
    ).order_by("-created_at")

    return render(request, 'alumni/view_profile.html', {
        'profile': profile,
        'academic': academic,
        'professional': professional,
        'contact': contact,
        'is_following': is_following,

        'followers_count': followers_count,
        'following_count': following_count,
        'posts_count': posts_count,

        # important for posts section
        'user_posts': user_posts,
    })

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction

from admin_module.models import SystemMetadata
from .models import (
    AlumniProfile,
    AcademicDetails,
    ProfessionalDetails,
    ContactDetails
)


@login_required
def complete_profile(request):

    metadata, _ = SystemMetadata.objects.get_or_create(user=request.user)

    if metadata.status == "APPROVED":
        return redirect("dashboard")

    if metadata.profile_completion == 100 and metadata.status == "PENDING":
        return redirect("waiting_approval")

    if request.method == "POST":
        try:
            with transaction.atomic():

                department = request.POST.get("department", "")

                # ===== PERSONAL PROFILE =====
                profile, _ = AlumniProfile.objects.get_or_create(
                    user=request.user
                )

                profile.first_name = request.POST.get("first_name", "")
                profile.last_name = request.POST.get("last_name", "")
                profile.gender = request.POST.get("gender", "")
                profile.date_of_birth = request.POST.get("date_of_birth") or None
                profile.address = request.POST.get("address", "")
                profile.city = request.POST.get("city", "")
                profile.state = request.POST.get("state", "")
                profile.country = request.POST.get("country", "")
                profile.postal_code = request.POST.get("postal_code", "")
                profile.department = department   # ✅ IMPORTANT FIX

                if request.FILES.get("photo"):
                    profile.photo = request.FILES.get("photo")

                profile.save()

                # ===== ACADEMIC DETAILS =====
                academic, _ = AcademicDetails.objects.get_or_create(
                    user=request.user
                )

                academic.student_id = request.POST.get("student_id", "")
                academic.degree = request.POST.get("degree", "")
                academic.department = department

                academic.year_of_admission = (
                    int(request.POST.get("year_of_admission"))
                    if request.POST.get("year_of_admission") else None
                )

                academic.year_of_graduation = (
                    int(request.POST.get("year_of_graduation"))
                    if request.POST.get("year_of_graduation") else None
                )

                academic.save()

                # ===== PROFESSIONAL DETAILS =====
                professional, _ = ProfessionalDetails.objects.get_or_create(
                    user=request.user
                )

                professional.current_designation = request.POST.get("current_designation", "")
                professional.current_company = request.POST.get("current_company", "")
                professional.industry = request.POST.get("industry", "")

                professional.year_of_experience = (
                    int(request.POST.get("year_of_experience"))
                    if request.POST.get("year_of_experience") else 0
                )

                professional.company_location = request.POST.get("company_location", "")
                professional.linkedin_profile = request.POST.get("linkedin_profile", "")

                professional.save()

                # ===== CONTACT DETAILS =====
                contact, _ = ContactDetails.objects.get_or_create(
                    user=request.user
                )

                contact.phone_number = request.POST.get("phone_number", "")
                contact.alternate_phone = request.POST.get("alternate_phone", "")
                contact.email = request.user.email

                contact.save()

                # ===== APPROVAL TRIGGER =====
                metadata.profile_completion = 100
                metadata.status = "PENDING"
                metadata.save()

                return redirect("waiting_approval")

        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect("complete_profile")

    return render(request, "alumni/complete_profile.html")

def waiting_approval(request):
    return render(request, "auth/waiting_approval.html")

from django.contrib.auth import logout


def user_logout(request):
    logout(request)
    return redirect("home")   # or your login page name

from django.db.models import Q
def alumni_list_view(request):
    q = request.GET.get("q", "").strip()

    alumni = AlumniProfile.objects.select_related("user").filter(
        user__is_staff=False,
        user__is_superuser=False,
        is_approved=True   # ✅ ADD THIS LINE
    )

    if q:
        alumni = alumni.filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(user__email__icontains=q)
        )

    following_ids = []
    if request.user.is_authenticated:
        following_ids = Connection.objects.filter(
            follower=request.user
        ).values_list("following_id", flat=True)

    return render(request, "alumni/alumni_list.html", {
        "alumni": alumni,
        "q": q,
        "following_ids": following_ids
    })

from django.http import JsonResponse

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@login_required
def mark_notifications_read(request):
    Connection.objects.filter(following=request.user, is_read=False).update(is_read=True)
    return redirect(request.META.get("HTTP_REFERER", "dashboard"))



from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

@login_required
def toggle_follow(request, user_id):
    if request.user.id == user_id:
        return redirect("dashboard")

    connection = Connection.objects.filter(
        follower=request.user,
        following_id=user_id
    ).first()

    if connection:
        connection.delete()
    else:
        Connection.objects.create(
            follower=request.user,
            following_id=user_id
        )

    return redirect(request.META.get("HTTP_REFERER", "dashboard"))


@login_required
def followers_list(request):
    followers = Connection.objects.filter(
        following=request.user
    ).select_related(
        "follower", "follower__alumniprofile"
    ).order_by("-id")

    following_ids = set(
        Connection.objects.filter(
            follower=request.user
        ).values_list("following_id", flat=True)
    )

    return render(request, "alumni/followers_list.html", {
        "followers": followers,
        "following_ids": following_ids,
    })


@login_required
def following_list(request):
    following = Connection.objects.filter(
        follower=request.user
    ).select_related(
        "following", "following__alumniprofile"
    ).order_by("-id")

    return render(request, "alumni/following_list.html", {
        "following": following,
    })


from teacher_module.models import JobPost,EventPost

from teacher_module.models import JobPost
from .models import Job

@login_required
def jobs(request):
    teacher_jobs = JobPost.objects.all().order_by("-created_at")
    alumni_jobs = Job.objects.all().order_by("-created_at")

    jobs = sorted(
        list(teacher_jobs) + list(alumni_jobs),
        key=lambda x: x.created_at,
        reverse=True
    )

    return render(request, "alumni/jobs.html", {"jobs": jobs})


@login_required
def events(request):
    events = EventPost.objects.all().order_by("-id")
    return render(request, "alumni/events.html", {"events": events})

from django.shortcuts import get_object_or_404


from alumni_module.models import Job
from teacher_module.models import JobPost   # ⚠️ change this based on your app name
from django.shortcuts import render
from django.http import Http404

def job_detail(request, job_id):
    job = Job.objects.filter(id=job_id).first()
    source = "alumni"

    if not job:
        job = JobPost.objects.filter(id=job_id).first()
        source = "teacher"

    if not job:
        raise Http404("Job not found")

    return render(request, "alumni/job_detail.html", {
        "job": job,
        "source": source
    })

from alumni_module.models import Event   # if you create this
from teacher_module.models import EventPost
from django.shortcuts import render
from django.http import Http404

def event_detail(request, event_id):
    event = Event.objects.filter(id=event_id).first()
    source = "alumni"

    if not event:
        event = EventPost.objects.filter(id=event_id).first()
        source = "teacher"

    if not event:
        raise Http404("Event not found")

    return render(request, "alumni/event_detail.html", {
        "event": event,
        "source": source
    })
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Conversation, Message

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, OuterRef, Q, Subquery
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.db.models import Count, OuterRef, Q, Subquery, Prefetch

from .models import Conversation, Message
@login_required
def messages_home(request, conv_id=None):
    last_msg_qs = Message.objects.filter(
        conversation=OuterRef("pk")
    ).order_by("-created_at")

    conversations = (
        Conversation.objects
        .filter(participants=request.user)
        .annotate(
            unread_count=Count(
                "messages",
                filter=Q(messages__is_read=False) & ~Q(messages__sender=request.user)
            ),
            last_message_text=Subquery(last_msg_qs.values("text")[:1]),
            last_message_time=Subquery(last_msg_qs.values("created_at")[:1]),
        )
        .prefetch_related(
            Prefetch(
                "participants",
                queryset=User.objects.exclude(id=request.user.id)
            )
        )
        .order_by("-last_message_time", "-updated_at")
        .distinct()
    )

    for conv in conversations:
        conv.other_user = conv.participants.all().first()

    active_conv = None
    chat_messages = Message.objects.none()

    if conv_id:
        active_conv = get_object_or_404(
            Conversation.objects.prefetch_related("participants"),
            id=conv_id,
            participants=request.user
        )
        active_conv.other_user = active_conv.participants.exclude(id=request.user.id).first()

        chat_messages = active_conv.messages.select_related("sender").order_by("created_at")

        active_conv.messages.filter(
            is_read=False
        ).exclude(
            sender=request.user
        ).update(is_read=True)

    return render(request, "alumni/messages.html", {
        "conversations": conversations,
        "active_conv": active_conv,
        "chat_messages": chat_messages,
    })


@login_required
def start_conversation(request, user_id):
    other = get_object_or_404(User, id=user_id)

    if other == request.user:
        return redirect("messages")

    existing = (
        Conversation.objects
        .filter(participants=request.user)
        .filter(participants=other)
        .distinct()
        .first()
    )

    if existing:
        return redirect("messages_conv", conv_id=existing.id)

    conv = Conversation.objects.create()
    conv.participants.add(request.user, other)
    return redirect("messages_conv", conv_id=conv.id)


@login_required
@require_POST
@csrf_protect
def send_message(request):
    conv_id = request.POST.get("conv_id")
    text = (request.POST.get("text") or "").strip()

    if not conv_id:
        return JsonResponse({"ok": False, "error": "conv_id missing"}, status=400)

    if not text:
        return JsonResponse({"ok": False, "error": "message empty"}, status=400)

    conv = get_object_or_404(Conversation, id=conv_id, participants=request.user)

    msg = Message.objects.create(
        conversation=conv,
        sender=request.user,
        text=text
    )

    conv.save(update_fields=["updated_at"])

    return JsonResponse({
        "ok": True,
        "id": msg.id,
        "text": msg.text,
        "created_at": msg.created_at.strftime("%I:%M %p"),
    })


@login_required
def fetch_messages(request, conv_id):
    conv = get_object_or_404(Conversation, id=conv_id, participants=request.user)

    after_id = request.GET.get("after", "0")
    try:
        after_id = int(after_id)
    except ValueError:
        after_id = 0

    msgs = (
        conv.messages
        .select_related("sender")
        .filter(id__gt=after_id)
        .order_by("id")[:50]
    )

    data = [{
        "id": m.id,
        "text": m.text,
        "sender_id": m.sender_id,
        "sender": m.sender.username,
        "created_at": m.created_at.strftime("%I:%M %p"),
    } for m in msgs]

    conv.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    return JsonResponse({"ok": True, "messages": data})
    return JsonResponse({"ok": True, "messages": data})
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # only owner or admin
    if post.user != request.user and not request.user.is_superuser:
        messages.error(request, "You are not allowed to delete this post.")
        return redirect("dashboard")

    if request.method == "POST":
        post.delete()
        messages.success(request, "Post deleted.")
    return redirect("dashboard")


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # only owner or admin
    if post.user != request.user and not request.user.is_superuser:
        messages.error(request, "You are not allowed to edit this post.")
        return redirect("dashboard")

    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        image = request.FILES.get("image")

        if not content:
            messages.error(request, "Post content cannot be empty.")
            return redirect("dashboard")

        post.content = content

        # optional: if user selects new image, replace old
        if image:
            post.image = image

        # optional: remove image checkbox
        if request.POST.get("remove_image") == "1":
            post.image = None

        post.save()
        messages.success(request, "Post updated.")
    return redirect("dashboard")


from .models import Notification

def follow_user(request, user_id):

    user_to_follow = User.objects.get(id=user_id)

    Connection.objects.create(
        follower=request.user,
        following=user_to_follow
    )

    Notification.objects.create(
        user=user_to_follow,
        sender=request.user,
        message=f"{request.user.username} started following you",
        notification_type="follow"
    )

    return redirect("dashboard")


from django.core.mail import send_mail
from django.shortcuts import render
from django.contrib.auth.models import User
from .models import EmailOTP
import random


def send_otp(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            return render(request, "auth/register.html", {"error": "Passwords do not match"})

        if User.objects.filter(username=username).exists():
            return render(request, "auth/register.html", {"error": "Username already exists"})

        if User.objects.filter(email=email).exists():
            return render(request, "auth/register.html", {"error": "Email already registered"})

        otp = str(random.randint(100000, 999999))

        EmailOTP.objects.update_or_create(
            email=email,
            defaults={"otp": otp}
        )

        send_mail(
            "Your Alumni Portal Verification Code",
            f"Your verification code is {otp}",
            "yourgmail@gmail.com",
            [email],
            fail_silently=False,
        )

        # Store data in session
        request.session["username"] = username
        request.session["email"] = email
        request.session["password"] = password

        return render(request, "auth/verify_otp.html")

    return render(request, "auth/register.html")

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login
from .models import EmailOTP
from admin_module.models import SystemMetadata

def verify_otp(request):

    if request.method == "POST":

        otp_entered = request.POST.get("otp")
        email = request.session.get("email")

        record = EmailOTP.objects.filter(email=email).first()

        if record and record.otp == otp_entered:

            username = request.session.get("username")
            password = request.session.get("password")

            user, created = User.objects.get_or_create(
                username=username,
                defaults={"email": email}
            )

            if created:
                user.set_password(password)
                user.save()

            # ✅ CREATE METADATA (THIS IS MISSING)
            SystemMetadata.objects.get_or_create(user=user)

            login(request, user)

            record.delete()

            request.session.pop("email", None)
            request.session.pop("username", None)
            request.session.pop("password", None)

            # ❗ CHANGE THIS
            return redirect("complete_profile")

        else:
            return render(request, "auth/verify_otp.html", {
                "error": "Invalid OTP"
            })

    return render(request, "auth/verify_otp.html")


import random
from django.core.mail import send_mail
from django.shortcuts import render

def resend_otp(request):

    email = request.session.get("email")

    otp = str(random.randint(100000,999999))

    EmailOTP.objects.update_or_create(
        email=email,
        defaults={"otp": otp}
    )

    send_mail(
        "Your Alumni Portal Verification Code",
        f"Your new verification code is {otp}",
        "yourgmail@gmail.com",
        [email],
        fail_silently=False,
    )

    return render(request, "auth/verify_otp.html", {
        "error": "New OTP sent to your email"
    })

@login_required
def clear_chat(request, conv_id):
    if request.method != "POST":
        return JsonResponse({"ok": False}, status=400)

    conv = get_object_or_404(Conversation, id=conv_id, participants=request.user)

    # remove only current user from this conversation
    conv.participants.remove(request.user)

    # if nobody left, delete conversation
    if conv.participants.count() == 0:
        conv.delete()

    return JsonResponse({"ok": True})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Job


@login_required
def alumni_jobpost(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        company = request.POST.get("company", "").strip()
        location = request.POST.get("location", "").strip()
        job_type = request.POST.get("job_type", "").strip()
        apply_link = request.POST.get("apply_link", "").strip()
        description = request.POST.get("description", "").strip()

        if title and company and description:
            Job.objects.create(
                user=request.user,
                title=title,
                company=company,
                location=location,
                job_type=job_type,
                apply_link=apply_link,
                description=description,
            )
            messages.success(request, "Job posted successfully.")
            return redirect("alumni_jobpost")
        else:
            messages.error(request, "Please fill all required fields.")

    alumni_jobs = Job.objects.filter(user=request.user).order_by("-id")

    return render(request, "alumni/alumni_jobpost.html", {
        "alumni_jobs": alumni_jobs
    })

@login_required
def alumni_delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, user=request.user)

    job.delete()
    messages.success(request, "Job deleted successfully.")
    return redirect("alumni_jobpost")

def jobs_view(request):
    jobs = Job.objects.all().order_by("-id")
    return render(request, "alumni/jobs.html", {
        "jobs": jobs
    })

from .models import Event   # make sure this model exists

@login_required
def alumni_eventpost(request):
    if request.method == "POST":
        title = request.POST.get("title")
        organizer = request.POST.get("organizer")
        location = request.POST.get("location", "")
        event_type = request.POST.get("event_type", "")
        event_date = request.POST.get("event_date", "")
        event_time = request.POST.get("event_time", "")
        registration_link = request.POST.get("registration_link", "")
        description = request.POST.get("description")

        if title and organizer and description:
            EventPost.objects.create(
                posted_by=request.user,
                title=title,
                organizer=organizer,
                location=location,
                event_type=event_type,
                event_date=event_date if event_date else None,
                event_time=event_time if event_time else None,
                registration_link=registration_link,
                description=description,
            )
            messages.success(request, "Event posted successfully.")
            return redirect("alumni_eventpost")

        messages.error(request, "Please fill all required fields.")

    alumni_events = EventPost.objects.filter(
        posted_by=request.user
    ).order_by("-id")

    return render(request, "alumni/alumni_eventpost.html", {
        "alumni_events": alumni_events
    })


@login_required
def events_view(request):
    events = EventPost.objects.all().order_by("-id")
    return render(request, "alumni/events.html", {
        "events": events
    })


@login_required
def event_detail(request, event_id):
    event = get_object_or_404(EventPost, id=event_id)
    return render(request, "alumni/event_detail.html", {
        "event": event
    })

@login_required
def alumni_delete_event(request, event_id):
    event = get_object_or_404(EventPost, id=event_id, posted_by=request.user)
    event.delete()
    messages.success(request, "Event deleted successfully.")
    return redirect("alumni_eventpost")