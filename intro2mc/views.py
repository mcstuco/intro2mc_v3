from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.core.cache import cache
from django.contrib import messages
from django.utils import timezone
from django.conf import settings

from io import BytesIO
from mcstatus import MinecraftServer
import requests
import logging
import uuid
import os
import json
import qrcode
import qrcode.image.svg

from intro2mc.alerts import *
from intro2mc.forms import *
from intro2mc.models import *

GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)
USERINFO_ENDPOINT_KEY = "userinfo_endpoint"

STATUS_NO_CONTENT = 204

logger = logging.getLogger(__name__)

def home(request):
    context = get_default_context()
    context['user'] = request.user
    if 'error' in request.session:
        messages.error(request, request.session["error"])
        del request.session["error"]
    
    context['videos'] = Video.objects.all()

    messages.info(request, 'This website is still in development. Let us know if you found any bugs')

    return render(request, 'index.html', context)

@login_required()
def register_ign(request):
    context = get_default_context()
    try:
        student = Student.objects.get(andrewID=request.user.username)
        form = StudentForm(instance=student)
    except Exception as e:
        try:
            userinfo = fetch_userinfo(request)
            student = Student(
                andrewID=userinfo["andrew_id"],
                name=userinfo["first_name"],
                picture=userinfo["picture"],
            )
            form = StudentForm()
        except Exception as e:
            logout(request)
            messages.error(request, authencication_failed_err('Something went wrong, please log in again.'))
            return redirect('home')

    context["student"] = student
    context['form'] = form
    if request.method == 'POST':           
        form = StudentForm(request.POST)
        if form.is_valid():
            student.IGN = form.cleaned_data["IGN"]
            student.save()
            messages.success(request, 'Your in-game name has been successfully registered.')
            return redirect('account')
        else:
            context['form'] = form
            return render(request, 'registration.html', context)

    return render(request, 'registration.html', context)

def page_not_found(request, exception=None):
    messages.error(request, "This page does not exist.")
    return redirect('home')

def syllabus(request):
    cfg = AppConfig().load()
    if cfg.syllabus is not None and cfg.syllabus != '':
        return redirect(cfg.syllabus)
    return redirect('home')

@login_required()
def map(request):
    cfg = AppConfig().load()
    if cfg.serverMapURL is not None and cfg.serverMapURL != '':
        return redirect(cfg.serverMapURL)
    return redirect('home')

@login_required()
def account(request):
    context = get_default_context()
    if request.user.is_superuser:
        return redirect('adminpanel')

    try: student = Student.objects.get(andrewID=request.user.username)
    except Exception as e:
        return redirect('registration')

    cfg = AppConfig().load()

    try:
        server = MinecraftServer.lookup(cfg.serverAddress)
        status = server.status()
        players = status.players.online
    except Exception as e:
        print(e)
        players = None

    context['student'] = student
    context['server'] = {
        'address': cfg.serverAddress,
        'players': players,
    }
    return render(request, 'account.html', context)

@login_required()
def attendance(request, id=None):
    context = get_default_context()
    id_key = 'attendance_id'
    cfg = AppConfig().load()
    today = timezone.localtime(timezone.now()).date()
    if request.user.is_superuser:
        sess, created = ClassSession.objects.get_or_create(
            term=cfg.currSemester, 
            date=today
        )
        sess.save()

        if created: messages.info(request, 'New class session created.')

        id = cache.get(id_key)
        if id == None:
            id = str(uuid.uuid4())
            cache.set(id_key, id)

        url = request.build_absolute_uri(f"/attendance/{id}")
        qr_code = generate_qrcode(url)
        context["svg"] = qr_code
        context["url"] = url
        return render(request, 'attendance.html', context)

    try: student = Student.objects.get(andrewID=request.user.username)
    except Exception as e:
        messages.error(request, generic_err("Unable to find student.", e))
        return redirect('registration')

    if id is None:
        sessions = ClassSession.objects.filter(term=cfg.currSemester).order_by('date')
        classes = []
        absences = 0
        for s in sessions:
            # check if class is on Tuesday
            if s.date.weekday() != 1: continue

            cls = {'date': str(s.date)}
            try:
                att = Attendance.objects.get(student=student, term=cfg.currSemester, classSession=s)
                if att.excused: cls['status'] = 'Excused'
                else: cls['status'] = 'Present'
            except Exception as e:
                if s.date < timezone.localtime(student.created_at).date(): cls['status'] = 'N/A'
                else: 
                    cls['status'] = 'Absent'
                    absences += 1
            classes.append(cls)

        context = {
            'student': student,
            'classes': classes,
            'absences': absences,
        }
        
        return render(request, 'attendance.html', context)

    if cache.get(id_key) != id: return redirect('404')
    
    try:
        sess = ClassSession.objects.get(
            term=cfg.currSemester, 
            date=today
        )
    except Exception as e:
        messages.error(request, generic_err("Unable to find a class session for today.", e))
        return redirect('home')

    
    attendance, created = Attendance.objects.get_or_create(
        student=student,
        term=cfg.currSemester,
        classSession=sess
    )
    if created:
        attendance.save()
        messages.success(request, 'Your attendance has been recorded.')
    else:
        messages.warning(request, 'You have already signed in.')

    return redirect('account')

@login_required
def records(request):
    context = get_default_context()
    if not request.user.is_superuser:
        messages.error(request, access_denied_err())
        return redirect('home')
    cfg = AppConfig().load()

    # Get relevant student, class, and assignment objects
    assignments = Assignment.objects.filter(term=cfg.currSemester, userSubmittable=True).order_by('created_at')
    sessions = ClassSession.objects.filter(term=cfg.currSemester).order_by('date')
    classes = []
    for s in sessions:
        if s.date.weekday() == 1:
            classes.append(s)
    students = Student.objects.all().order_by('andrewID')

    ### Attendance ###
    # header row of table
    dates = []
    for c in classes:
        dates.append(c.date)

    # one student per row
    attendanceinfos = []
    for s in students:
        sname = str(s)
        absences = 0
        info = []
        for c in classes:
            try:
                att = Attendance.objects.get(student=s, term=cfg.currSemester, classSession=c)
                if att.excused: info.append('Excused')
                else: info.append('Present')
            except Exception as e:
                if c.date < timezone.localtime(s.created_at).date(): info.append('N/A')
                else:
                    info.append('Absent')
                    absences += 1
        attendanceinfos.append({'info':info,'name':sname,'absences':absences})

    ### Assignments ###
    # header row of table
    hwnames = []
    for a in assignments:
        hwnames.append(a.name)

    # one row per student
    assignmentinfos = []
    for s in students:
        sname = str(s)
        missing = 0
        info = []
        for a in assignments:
            submission = None
            try: 
                submission = (Submission.objects.filter(
                    assignment=a,
                    student=s,
                ).order_by('-updated_at') or [None])[0]
            except Exception as e: print(e)
            if submission is None or submission.grade == 'R':
                missing += 1
            info.append(submission)
        assignmentinfos.append({'info':info,'name':sname,'missing':missing})

    # render
    context = {
        'dates': dates,
        'attendanceinfos': attendanceinfos,
        'hwnames': hwnames,
        'assignmentinfos': assignmentinfos,
    }
    return render(request, 'records.html', context)


@login_required()
def admin_panel(request, action=None):
    context = get_default_context()
    if not request.user.is_superuser:
        messages.error(request, access_denied_err())
        return redirect('home')

    if action == 'semester':
        if request.method == 'POST':
            form = AppCfgForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('adminpanel')
        else:
            cfg = AppConfig().load()
            form = AppCfgForm(instance=cfg)
            context['form'] = form
        return render(request, 'semester.html', context)
    
    if action == 'whitelist':
        roster = get_roster()
        wl_file = os.path.join(settings.SERVER_DIR, 'whitelist.json')
        with open(wl_file, 'r') as f: whitelist = json.load(f)

        count = 0
        for s in Student.objects.all():
            if s.andrewID in roster:
                if s.uuid == None or s.uuid == '':
                    try:
                        id = fetch_uuid(s.IGN)
                    except Exception as e:
                        messages.error(request, f'Error fetching uuid for {s.andrewID} ({s.IGN}) [{str(e)}]')
                    else:
                        s.uuid = str(uuid.UUID(id))
                        s.save()
                if not any(d['uuid'] == s.uuid for d in whitelist):
                    count += 1
                    whitelist.append({
                        'uuid': s.uuid,
                        'name': s.IGN,
                    })

        with open(wl_file, 'w') as f: json.dump(whitelist, f, indent=2)

        messages.info(request, f'Added {count} people to the server whitelist')
 
        return redirect('adminpanel')

    return render(request, 'admin-panel.html', context)

@login_required()
def assignments(request):
    context = get_default_context()
    cfg = AppConfig().load()

    try: student = Student.objects.get(andrewID=request.user.username)
    except Exception as e:
        messages.error(request, generic_err("Unable to find student.", e))
        return redirect('registration')

    ass = Assignment.objects.filter(term=cfg.currSemester, userSubmittable=True).order_by('-created_at')
    context['assignments'] = []
    for a in ass:
        submission = None
        try: 
            submission = (Submission.objects.filter(
                assignment=a, 
                student=student, 
            ).order_by('-updated_at') or [None])[0]
        except Exception as e: print(e)

        context['assignments'].append({
            'name': a.name,
            'desc': a.description,
            'submission': submission,
        })

    return render(request, 'assignments.html', context)

########### util methods ###########
def get_default_context():
    context = {}
    return context

def get_roster():
    cfg = AppConfig.load()
    return set(filter(None, cfg.roster.split(',')))

def fetch_userinfo(request):
    social = request.user.social_auth.get(provider='google-oauth2')
    access_token = social.extra_data['access_token']
    
    google_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    userinfo_endpoint = google_cfg[USERINFO_ENDPOINT_KEY]
    
    response = requests.get(userinfo_endpoint, params={'access_token': access_token}).json()
    logger.info(msg=response)
    if 'error' in response:
        raise Exception(response.get('error'))

    userinfo = {
        'first_name': response.get('given_name'),
        'andrew_id': request.user.username,
        'picture': response.get('picture'),
    }
    return userinfo

def fetch_uuid(ign):
    response = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{ign}")
    if response.status_code == STATUS_NO_CONTENT:
        raise Exception('Unable to retrieve uuid for this username')

    response_json = response.json()
    if 'error' in response_json:
        raise Exception(response_json.get('error'))

    return response_json.get('id')

def generate_qrcode(url, size=30):
    img = qrcode.make(url, 
                      image_factory=qrcode.image.svg.SvgImage, 
                      box_size=size)
    stream = BytesIO()
    img.save(stream)
    svg = stream.getvalue().decode()
    return svg
