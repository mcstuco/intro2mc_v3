from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User as UserModel
from django.contrib.auth import logout
from django.core.cache import cache
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from django.http import HttpResponseForbidden, HttpResponseNotFound, HttpResponse

from mcstatus import MinecraftServer
import requests
import logging
import uuid
import json
import string
import random
import datetime

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

        if not form.is_valid():
            context['form'] = form
            return render(request, 'registration.html', context)

        try:
            case_correct_username, id = fetch_mojang_userinfo(form.cleaned_data["IGN"])
        except Exception as e:
            messages.error(request, f'Error fetching uuid for {form.cleaned_data["IGN"]}. Try clicking the Submit button again. If it still does not work, it is usually means that you entered a nonexistent username.')
            return render(request, 'registration.html', context)
        else:
            student.uuid = str(uuid.UUID(id))
            student.IGN = case_correct_username
            student.discord = form.cleaned_data["discord"]
            student.save()

            messages.success(request, 'You have been successfully registered.')
            return redirect('account')

    return render(request, 'registration.html', context)

@login_required
def invite(request):
    context = get_default_context()
    if not request.user.is_superuser:
        messages.error(request, access_denied_err())
        return redirect('home')
    cfg = AppConfig().load()

    if request.method == 'POST':
        form = InviteForm(request.POST)
        if form.is_valid():
            try:
                case_correct_username, uid = fetch_mojang_userinfo(form.cleaned_data["IGN"])
            except Exception as e:
                messages.error(request, f'Error fetching uuid for {form.cleaned_data["IGN"]}. Try clicking the Submit button again. If it still does not work, it is usually means that you entered a nonexistent username.')
            else:
                invited, created = InvitedStudent.objects.get_or_create(
                    IGN=case_correct_username,
                    uuid=str(uuid.UUID(uid)),
                    invitedBy=form.cleaned_data['invitedBy']
                )
                if created:
                    invited.save()
                    messages.success(request, f'{case_correct_username} has been successfully whitelisted.')
                else:
                    messages.warning(request, f'{case_correct_username} has already been invited by {form.invitedBy}.')
        context['form'] = form
    else:
        context['form'] = InviteForm()

    context['invited_students'] = []
    for s in InvitedStudent.objects.all().order_by('-created_at'):
        context['invited_students'].append(s)
    return render(request, 'invite.html', context)

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
def attendance(request):
    context = get_default_context()
    cfg = AppConfig().load()

    if request.user.is_superuser:
        sessions = ClassSession.objects.filter(term=cfg.currSemester).order_by('date')
        classes = []
        for s in sessions:
            classes.append(s)

        context["classes"] = classes
        return render(request, 'attendance.html', context)

    try:
        student = Student.objects.get(andrewID=request.user.username)
    except Exception as e:
        messages.error(request, generic_err("Unable to find student.", e))
        return redirect('registration')

    if request.method == 'POST':
        try:
            sess = ClassSession.objects.get(code=request.POST.get("code").upper(), term=cfg.currSemester, accepting=True)
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
        except Exception as e:
            messages.error(request, authencication_failed_err("Invalid or expired attendance code."))

    sessions = ClassSession.objects.filter(term=cfg.currSemester).order_by('date')
    classes = []
    absences = 0
    for s in sessions:
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

@login_required
def excuse(request):
    context = get_default_context()
    if not request.user.is_superuser:
        messages.error(request, access_denied_err())
        return redirect('home')
    cfg = AppConfig().load()

    if request.method == 'POST':
        try:
            stu = Student.objects.get(andrewID=request.POST['student'])
            sess = ClassSession.objects.get(date=request.POST['classSession'])
            att, created = Attendance.objects.get_or_create(
                student=stu,
                term=cfg.currSemester,
                classSession=sess
            )
            att.reason = request.POST['reason']
            att.excused = True
            att.save()
            if created:
                messages.success(request, 'Student excused.')
            else:
                messages.success(request, 'Attendance updated.')
        except Exception as e:
            messages.error(request, generic_err("Unable to find student or class session.", e))

    context['form'] = ExcuseForm()
    context['excused_absences'] = []
    for att in Attendance.objects.filter(excused=True).order_by('-updated_at'):
        d = {}
        d['date'] = att.updated_at
        d['session'] = att.classSession.date
        d['student'] = att.student
        d['reason'] = att.reason
        context['excused_absences'].append(d)
    return render(request, 'excuse.html', context)

@login_required
def records(request):
    context = get_default_context()
    if not request.user.is_superuser:
        messages.error(request, access_denied_err())
        return redirect('home')
    cfg = AppConfig().load()

    # Get relevant student, class, and assignment objects
    assignments = Assignment.objects.filter(term=cfg.currSemester).order_by('created_at')
    classes = ClassSession.objects.filter(term=cfg.currSemester).order_by('date')
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

@login_required()
def toggle_admin(request):
    if not request.user.is_staff:
        return HTTPResponseForbidden()
    user = UserModel.objects.get(username=request.user.username)
    user.is_superuser = not user.is_superuser
    user.save()
    messages.info(request, 'Admin status toggled.')
    return redirect('home')

########### API ###########

@login_required
def api(request, endpoint):
    cfg = AppConfig.load()

    if endpoint == 'rerollcode':
        if not request.user.is_superuser or request.method != 'POST':
            return HttpResponseForbidden()

        try:
            parseddate = parse_display_date(request.POST['date'])
            session = ClassSession.objects.get(date=parseddate)
            session.code = ''.join(random.choices(string.ascii_uppercase, k=4))
            session.save()
            return HttpResponse(session.code)

        except Exception as e:
            return HttpResponseNotFound()

    elif endpoint == 'togglesession':
        if not request.user.is_superuser or request.method != 'POST':
            return HttpResponseForbidden()

        try:
            parseddate = parse_display_date(request.POST['date'])
            session = ClassSession.objects.get(date=parseddate)

            if request.POST['action'] == 'open':
                session.accepting = True
            elif request.POST['action'] == 'close':
                session.accepting = False
            else:
                raise IllegalArgumentException('No such option '+request.POST['action'])

            session.save()
            return HttpResponse("Success!")

        except Exception as e:
            return HttpResponseNotFound()

    elif endpoint == 'newsession':
        if not request.user.is_superuser or request.method != 'POST':
            return HttpResponseForbidden()

        try:
            today = timezone.localtime(timezone.now()).date()
            sess, created = ClassSession.objects.get_or_create(
                term=cfg.currSemester,
                date=today
            )
            if created:
                sess.code = ''.join(random.choices(string.ascii_uppercase, k=4))
                sess.accepting = False
                sess.save()
                messages.info(request, 'New class session created.')
            else:
                messages.warning(request, 'Class already exists.')
            return HttpResponse()

        except Exception as e:
            return HttpResponseNotFound(str(e))

    elif endpoint == 'deletesession':
        if not request.user.is_superuser or request.method != 'POST':
            return HttpResponseForbidden()

        try:
            parseddate = parse_display_date(request.POST['date'])
            session = ClassSession.objects.get(date=parseddate)

            Attendance.objects.filter(classSession=session).delete()
            session.delete()
            messages.info(request, 'Successfully deleted class session.')
            return HttpResponse()

        except Exception as e:
            return HttpResponseNotFound()


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

def fetch_mojang_userinfo(ign):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }
    
    response = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{ign}", headers=headers, verify=True)
    if response.status_code == STATUS_NO_CONTENT:
        raise Exception('Unable to retrieve uuid for this username')

    response_json = response.json()
    if 'error' in response_json:
        raise Exception(response_json.get('error'))

    if 'id' not in response_json and 'name' not in response_json:
        raise Exception('User does not exist')

    return response_json.get('name'), response_json.get('id')

def parse_display_date(datestring):
    if '.' in datestring:
        return datetime.datetime.strptime(datestring, '%b. %d, %Y').date()
    else:
        return datetime.datetime.strptime(datestring, '%B %d, %Y').date()
