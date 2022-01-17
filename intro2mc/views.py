from xml.etree.ElementInclude import include
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.core.cache import cache
from django.contrib import messages
from django.utils import timezone

import requests
import logging
import uuid

from intro2mc.alerts import *
from intro2mc.forms import *
from intro2mc.models import *

import qrcode
import qrcode.image.svg
from io import BytesIO

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
    
    context['videos'] = [{
        'videoURL': 'https://www.youtube.com/embed/QeaoV7ESihg'
    }] * 10

    messages.info(request, 'This website is still in development. Let us know if you found any bugs')

    return render(request, 'index.html', context)

@login_required()
def register_ign(request):
    context = get_default_context()
    try:
        student = Student.objects.get(andrewID=request.user.username)
        form = StudentForm(instance=student)
    except Exception as e: # expected
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
            student.IGN = form["IGN"].value()
            student.save()
            messages.success(request, 'Your in-game name has been successfully registered.')
            return redirect('account')
        else:
            messages.error(request, 'Registration failed')
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

    try:
        student = Student.objects.get(andrewID=request.user.username)
    except Exception as e:
        return redirect('registration')

    context['student'] = student
    return render(request, 'account.html', context)

@login_required()
def attendance(request, id=None):
    context = get_default_context()
    id_key = 'attendance_id'
    cfg = AppConfig().load()
    today = timezone.now().date()
    if request.user.is_superuser:
        sess, _ = ClassSession.objects.get_or_create(
            term=cfg.currSemester, 
            date=today
        )
        sess.save()

        id = str(uuid.uuid4())
        cache.set(id_key, id)
        print(cache.get(id_key))

        qr_code = generate_qrcode(request.build_absolute_uri(f"/attendance/{id}"))
        context["svg"] = qr_code
        return render(request, 'attendance.html', context)

    if id is None:
        messages.error(request, access_denied_err())
        return redirect('home')
    if cache.get(id_key) != id:
        return redirect('404')
    
    try:
        sess = ClassSession.objects.get(
            term=cfg.currSemester, 
            date=today
        )
    except Exception as e:
        messages.error(request, generic_err("Unable to find a class session for today.", e))
        return redirect('home')
    
    try:
        student = Student.objects.get(andrewID=request.user.username)
    except Exception as e:
        messages.error(request, generic_err("Unable to find student.", e))
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

########### util methods ###########
def get_default_context():
    context = {}
    return context

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
