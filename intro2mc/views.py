from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

import requests

import qrcode
import qrcode.image.svg
from io import BytesIO

GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)
USERINFO_ENDPOINT_KEY = "userinfo_endpoint"

# @login_required
def home(request):
    context = {
        'user': request.user,
    }
    if 'error' in request.session:
        context['error'] = request.session.get('error')
        del request.session['error']
    
    return render(request, 'index.html', context)

@login_required
def account(request):
    social = request.user.social_auth.get(provider='google-oauth2')
    access_token = social.extra_data['access_token']
    
    google_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    userinfo_endpoint = google_cfg[USERINFO_ENDPOINT_KEY]
    
    response = requests.get(userinfo_endpoint, params={'access_token': access_token}).json()
    print(response)
    context = {
        'first_name': response.get('given_name'),
        'andrew_id': request.user.username,
        'picture': response.get('picture'),
    }
    return render(request, 'account.html', context)

def generate_qrcode(url, size=20):
    img = qrcode.make(url, 
                      image_factory=qrcode.image.svg.SvgImage, 
                      box_size=size)
    stream = BytesIO()
    img.save(stream)
    svg = stream.getvalue().decode()
    return svg
