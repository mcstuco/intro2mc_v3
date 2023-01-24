"""webapps URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from django.contrib.auth.views import LogoutView
from intro2mc import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('syllabus/', views.syllabus, name='syllabus'),
    path('server-map/', views.map, name='map'),
    path('student-portal', views.account, name='account'),
    path('', include('social_django.urls', namespace='social')),
    path('logout/', LogoutView.as_view(template_name="index.html"), name='logout'),
    path('attendance/', views.attendance, name='attendance'),
    path('assignments/', views.assignments, name='assignments'),
    path('records/', views.records, name='records'),
    path('registration', views.register_ign, name='registration'),
    path('admin-panel/', views.admin_panel, name="adminpanel"),
    path('admin-panel/<str:action>', views.admin_panel, name="adminpanel-action"),
    path('404', views.page_not_found, name='404')
]

handler404 = 'intro2mc.views.page_not_found'