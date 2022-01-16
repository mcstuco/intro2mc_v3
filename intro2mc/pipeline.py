from django.shortcuts import redirect

from intro2mc.alerts import *
from intro2mc.models import *

def auth_allowed(backend, details, response, *args, **kwargs):
    email = details.get('email')
    username = details.get('username')

    if not backend.auth_allowed(response, details):
        error = access_denied_err(
            f"Looks like your account ({email}) doesn't use a CMU domain.\
                 Please try again with a CMU email."
        )

        backend.strategy.session_set('error', error)
        return redirect('home')

    cfg = AppConfig().load()
    roster = list(filter(None, cfg.roster.split(',')))
    if username not in roster:
        error = access_denied_err(
            f"User {username} is not registered in the system."
        )

        backend.strategy.session_set('error', error)
        return redirect('home')
       
