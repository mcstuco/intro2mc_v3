from re import sub
from django import template

register = template.Library()

@register.filter
# Returns bootstrap classes for a django message tag
def get_alert_bsclass(tag):
    default = "alert alert-secondary alert-dismissible show"
    alert_bsclass = {
        "error": "alert alert-danger alert-dismissible show",
        "info": "alert alert-primary alert-dismissible show",
        "success": "alert alert-success alert-dismissible show",
        "warning": "alert alert-warning alert-dismissible show"
    }
    return alert_bsclass.get(tag.lower(), default)

@register.filter
# Returns bootstrap classes for an attendance record
def get_attendance_bsclass(status):
    attendance_bsclass = {
        "n/a": "text-muted",
        "absent": "text-danger",
        "present": "text-success",
        "excused": "text-warning"
    }
    return attendance_bsclass.get(status.lower(), '')

@register.filter
def get_attendance_faclass(status):
    attendance_faclass = {
        "n/a": "fas fa-check-circle text-muted",
        "absent": "fas fa-exclamation-circle text-danger",
        "present": "fas fa-check-circle text-success",
        "excused": "fas fa-check-circle text-warning"
    }
    return attendance_faclass.get(status.lower(), '')

@register.filter
# Returns fontawesome classes for an assignment's status
def get_hwstatus_faclass(submission):
    default = "fas fa-exclamation-circle text-warning"
    hwstatus_faclass = {
        "u": "fas fa-check-circle text-muted",
        "p": "fas fa-check-circle text-success",
        "r": "fas fa-redo-alt text-danger",
    }
    if not submission: return default
    return hwstatus_faclass.get(submission.grade.lower(), default)

@register.filter
# Returns the tooltip message for an assignment status
def get_hwstatus_tooltip(submission):
    default = "No Submission"
    hwstatus_tooltip = {
        "u": "Submitted",
        "p": "Pass",
        "r": "Redo",
    }
    if not submission: return default
    return hwstatus_tooltip.get(submission.grade.lower(), default)

@register.filter
# Returns the number of missing submissions in a list
def count_missing_ass(assignments):
    return len([a for a in assignments if not a['submission'] or a['submission'].grade.lower() == 'r'])

@register.filter
# Returns the readable string for a grade letter
def get_grade_str(grade):
    grade_mapping = {
        'u': 'not graded',
        'p': 'pass',
        'r': 'redo'
    }
    return grade_mapping.get(grade.lower(), '')

@register.filter
# Returns bootstrap classes for a letter grade
def get_grade_bsclass(grade):
    grade_bsclass = {
        'u': 'badge badge-secondary',
        'p': 'badge badge-success',
        'r': 'badge badge-danger',
    }
    return grade_bsclass.get(grade.lower(), '')