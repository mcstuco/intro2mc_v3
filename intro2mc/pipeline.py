from django.http.response import HttpResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from django.shortcuts import render, redirect

def auth_allowed(backend, details, response, *args, **kwargs):
    email = details.get('email')
    username = details.get('username')
    error = {
        'type': 'Authentication Failed'
    }

    if not backend.auth_allowed(response, details):
        error['msg'] = f"Looks like your account ({email}) doesn't have a CMU domain.\
                 Please try again with a CMU email."

        backend.strategy.session_set('error', error)
        return redirect('home')

    # TODO: implement username validation
    if username == '':
        error['msg'] = f"User {username} are not registered in the system."

        backend.strategy.session_set('error', error)
        return redirect('home')
       
