from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.core.cache import cache
from django.contrib import messages

import requests
import logging

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

logger = logging.getLogger(__name__)

def get_default_context():
    context = {}
    return context

def home(request):
    context = get_default_context()
    context['user'] = request.user
    if 'error' in request.session:
        messages.error(request, request.session["error"])
        del request.session["error"]
        # context['error'] = get_and_remove_errors(request)
    
    context['videos'] = [{
        'videoURL': 'https://www.youtube.com/embed/QeaoV7ESihg'
    }] * 10
    messages.error(request, 'test')
    messages.info(request, 'test')
    return render(request, 'index.html', context)

def page_not_found(request, exception=None):
    # save_error(request, page_not_found_err())
    messages.error(request, "This page does not exist.")
    return redirect('home')

def syllabus(request):
    cfg = AppConfig().load()
    if cfg.syllabus is not None and cfg.syllabus is not '':
        return redirect(cfg.syllabus)
    return redirect('home')

def map(request):
    cfg = AppConfig().load()
    if cfg.serverMapURL is not None and cfg.serverMapURL is not '':
        return redirect(cfg.serverMapURL)
    return redirect('home')

@login_required
def account(request):
    context = get_default_context()
    if request.user.is_superuser:
        return redirect('adminpanel')

    try:
        userinfo = fetch_userinfo(request)
    except Exception as e:
        logout(request)
        # save_error(request, authencication_failed_err('Something went wrong, please log in again.'))
        messages.error(request, authencication_failed_err('Something went wrong, please log in again.'))
        return redirect('home')

    context['userinfo'] = userinfo
    return render(request, 'account.html', context)

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

@login_required()
def attendance(request, id=None):
    if request.user.is_superuser:
        return render(request, 'attendance.html')

    if id is None:
        save_error(request, access_denied_err())
        return redirect('home')

    if cache.get('attendance_id') is None or cache.get('attendance_id') != id:
        return redirect('404')

@login_required()
def admin_panel(request, action=None):
    context = get_default_context()
    if not request.user.is_superuser:
        save_error(request, access_denied_err())
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

def generate_qrcode(url, size=20):
    img = qrcode.make(url, 
                      image_factory=qrcode.image.svg.SvgImage, 
                      box_size=size)
    stream = BytesIO()
    img.save(stream)
    svg = stream.getvalue().decode()
    return svg
