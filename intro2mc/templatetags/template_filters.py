from django import template

register = template.Library()

@register.filter
def get_alert_bsclass(tag):
    alert_bsclass = {
        "error": "alert alert-danger alert-dismissible show",
        "info": "alert alert-primary alert-dismissible show",
        "success": "alert alert-success alert-dismissible show"
    }
    alert_bsclass.setdefault("alert alert-secondary alert-dismissible show")
    return alert_bsclass[tag]
