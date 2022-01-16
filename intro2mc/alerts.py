contact_instructors_txt = "Contact the instructors if you believe this was a mistake."

def access_denied_err(msg="You don't have access to this resource."):
    return ' '.join([msg, contact_instructors_txt])

def authencication_failed_err(msg="Could not authenticate your account."):
    return ' '.join([msg, contact_instructors_txt])

def page_not_found_err(msg="This page does not exist."):
    return ' '.join([msg, contact_instructors_txt])
