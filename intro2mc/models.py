from django.db import models

######## Attendance ########
class Student(models.Model):
    andrewID = models.CharField(max_length=200, primary_key=True)
    name = models.CharField(max_length=200, default='')
    picture = models.CharField(max_length=200)
    IGN = models.CharField(max_length=200)

class ClassSession(models.Model):
    id = models.AutoField(primary_key=True)
    term = models.CharField(max_length=200)
    date = models.DateTimeField()

class Attendance(models.Model):
    andrewID = models.CharField(max_length=200, primary_key=True)
    term = models.CharField(max_length=200)
    classSession = models.ForeignKey(ClassSession, on_delete=models.PROTECT)
    excused = models.BooleanField(default=False)

######## Web app settings ########
# Adapted from https://www.rootstrap.com/blog/simple-dynamic-settings-for-django/
class Singleton(models.Model):

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super(Singleton, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
        
class AppConfig(Singleton):
    id = models.AutoField(primary_key=True)
    currSemester = models.CharField(max_length=200)
    syllabus = models.CharField(max_length=200)
    serverMapURL = models.CharField(max_length=200)
    # All andrew ids on the roster, separated by ','
    roster = models.TextField(blank=True)

######## Website contents ########
class Video(models.Model):
    id = models.AutoField(primary_key=True)
    videoURL = models.CharField(max_length=200)
    description = models.TextField(blank=True)

class Meme(models.Model):
    id = models.AutoField(primary_key=True)
    imageURL = models.CharField(max_length=200)
    description = models.TextField(blank=True)

class Resource(models.Model):
    id = models.AutoField(primary_key=True)
    URL = models.CharField(max_length=200)
    imageURL = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)