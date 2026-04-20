from django.shortcuts import render, redirect, get_object_or_404 
from alumni_module.models import AlumniProfile
from teacher_module.models import TeacherProfile
from alumni_module.models import Job, Event

def admin_dashboard(request):
    total_alumni = AlumniProfile.objects.count()
    total_teachers = TeacherProfile.objects.count()
    total_jobs = Job.objects.count()
    total_events = Event.objects.count()

    context = {
        'total_alumni': total_alumni,
        'total_teachers': total_teachers,
        'total_jobs': total_jobs,
        'total_events': total_events,
    }
    return render(request, 'admin/dashboard.html', context)

def manage_alumni(request):
    alumni = AlumniProfile.objects.all()
    return render(request, 'admin/manage_alumni.html', {'alumni': alumni})



def manage_jobs(request):
    jobs = Job.objects.all()
    return render(request, 'admin/manage_jobs.html', {'jobs': jobs})

def delete_job(request, id):
    job = Job.objects.get(id=id)
    job.delete()
    return redirect('manage_jobs')

def manage_events(request):
    events = Event.objects.all()
    return render(request, 'admin/manage_events.html', {'events': events})



def manage_teachers(request):
    teachers = TeacherProfile.objects.all()
    return render(request, 'admin/manage_teachers.html', {'teachers': teachers})




def add_job(request):
    if request.method == 'POST':
        Job.objects.create(
            title=request.POST['title'],
            company=request.POST['company'],
            location=request.POST['location'],
            description=request.POST['description']
        )
        return redirect('manage_jobs')
    return render(request, 'admin/add_job.html')


def edit_job(request, id):
    job = get_object_or_404(Job, id=id)

    if request.method == 'POST':
        job.title = request.POST['title']
        job.company = request.POST['company']
        job.location = request.POST['location']
        job.description = request.POST['description']
        job.save()
        return redirect('manage_jobs')

    return render(request, 'admin/edit_job.html', {'job': job})


def delete_job(request, id):
    job = get_object_or_404(Job, id=id)
    job.delete()
    return redirect('manage_jobs')

def add_event(request):
    if request.method == 'POST':
        Event.objects.create(
            name=request.POST['name'],
            date=request.POST['date'],
            location=request.POST['location'],
            description=request.POST['description']
        )
        return redirect('manage_events')
    return render(request, 'admin/add_event.html')


def edit_event(request, id):
    event = get_object_or_404(Event, id=id)

    if request.method == 'POST':
        event.name = request.POST['name']
        event.date = request.POST['date']
        event.location = request.POST['location']
        event.description = request.POST['description']
        event.save()
        return redirect('manage_events')

    return render(request, 'admin/edit_event.html', {'event': event})


def delete_event(request, id):
    event = get_object_or_404(Event, id=id)
    event.delete()
    return redirect('manage_events')

def delete_teacher(request, id):
    teacher = get_object_or_404(TeacherProfile, id=id)
    teacher.delete()
    return redirect('manage_teachers')


def delete_alumni(request, id):
    alumni = get_object_or_404(AlumniProfile, id=id)
    alumni.delete()
    return redirect('manage_alumni')
