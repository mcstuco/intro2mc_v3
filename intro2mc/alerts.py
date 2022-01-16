# def save_error(request, err):
#     request.session['error'] = err

# def get_error(request):
#     return request.session.get('error')

# def remove_errors(request):
#     del request.session['error']

# def get_and_remove_errors(request):
#     err = request.session.get('error')
#     del request.session['error']
#     return err

# def create_err(type, msg):
#     return {
#         'type': type,
#         'msg': msg
#     }

contact_instructors_txt = "Contact the instructors if you believe this was a mistake."

def access_denied_err(msg="You don't have access to this resource."):
    return ' '.join([msg, contact_instructors_txt])

def authencication_failed_err(msg="Could not authenticate your account."):
    # return create_err('Authentication Failed', msg)
    return ' '.join([msg, contact_instructors_txt])

def page_not_found_err(msg="This page does not exist."):
    # return create_err('Page not found', msg)
    return ' '.join([msg, contact_instructors_txt])
