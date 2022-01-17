from django import template

register = template.Library()

@register.filter
# Returns bootstrap classes for a django message tag
def get_alert_bsclass(tag):
    alert_bsclass = {
        "error": "alert alert-danger alert-dismissible show",
        "info": "alert alert-primary alert-dismissible show",
        "success": "alert alert-success alert-dismissible show",
        "warning": "alert alert-warning alert-dismissible show"
    }
    alert_bsclass.setdefault("alert alert-secondary alert-dismissible show")
    return alert_bsclass[tag]
