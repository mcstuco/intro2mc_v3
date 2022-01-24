from django.contrib import admin
from intro2mc.models import *

# Register your models here.
class AttendanceAdmin(admin.ModelAdmin):
    fields = [field.name for field in Attendance._meta.concrete_fields]
    readonly_fields = ['id', 'created_at', 'updated_at']
    class Meta:
        model = Attendance

class ClassSessionAdmin(admin.ModelAdmin):
    fields = [field.name for field in ClassSession._meta.concrete_fields]
    readonly_fields = ['created_at', 'updated_at']
    class Meta:
        model = ClassSession

class MemeAdmin(admin.ModelAdmin):
    fields = [field.name for field in Meme._meta.concrete_fields]
    readonly_fields = ['created_at', 'updated_at']
    class Meta:
        model = Meme

class ResourceAdmin(admin.ModelAdmin):
    fields = [field.name for field in Resource._meta.concrete_fields]
    readonly_fields = ['created_at', 'updated_at']
    class Meta:
        model = Resource

class StudentAdmin(admin.ModelAdmin):
    fields = [field.name for field in Student._meta.concrete_fields]
    readonly_fields = ['created_at', 'updated_at']
    class Meta:
        model = Student

class VideoAdmin(admin.ModelAdmin):
    fields = [field.name for field in Video._meta.concrete_fields]
    readonly_fields = ['created_at', 'updated_at']
    class Meta:
        model = Video

class AssignmentAdmin(admin.ModelAdmin):
    fields = [field.name for field in Assignment._meta.concrete_fields]
    readonly_fields = ['id', 'created_at', 'updated_at']
    class Meta:
        model = Assignment

class SubmissionAdmin(admin.ModelAdmin):
    fields = [field.name for field in Submission._meta.concrete_fields]
    readonly_fields = ['id', 'created_at', 'updated_at']
    class Meta:
        model = Submission

admin.site.register(AppConfig)
admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(ClassSession, ClassSessionAdmin)
admin.site.register(Meme, MemeAdmin)
admin.site.register(Resource, ResourceAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Video, VideoAdmin)
admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(Submission, SubmissionAdmin)