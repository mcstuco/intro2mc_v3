from django.db import models

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
    serverAddress = models.CharField(max_length=200)
    # All andrew ids on the roster, separated by ','
    roster = models.TextField(blank=True)

class HasTimeStamps(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

######## Attendance ########
class Student(HasTimeStamps):
    andrewID = models.CharField(max_length=200, primary_key=True)
    name = models.CharField(max_length=200, default='')
    picture = models.CharField(max_length=200)
    IGN = models.CharField(max_length=200)
    uuid = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.andrewID} [{self.IGN}]'

class ClassSession(HasTimeStamps):
    date = models.DateField(primary_key=True)
    term = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.term}-{self.date}'

class Attendance(HasTimeStamps):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.PROTECT)
    term = models.CharField(max_length=200)
    classSession = models.ForeignKey(ClassSession, on_delete=models.PROTECT)
    excused = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.student} {self.classSession}'

######## Website contents ########
class Video(HasTimeStamps):
    videoURL = models.CharField(max_length=200, primary_key=True)
    description = models.TextField(blank=True)

class Meme(HasTimeStamps):
    imageURL = models.CharField(max_length=200, primary_key=True)
    description = models.TextField(blank=True)

class Resource(HasTimeStamps):
    id = models.AutoField(primary_key=True)
    URL = models.CharField(max_length=200)
    imageURL = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

######## Assignments ########
class Assignment(HasTimeStamps):
    id = models.AutoField(primary_key=True)
    term = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    userSubmittable = models.BooleanField(default=False)
    gradeReleased = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.term}-{self.name}'

class Submission(HasTimeStamps):
    id = models.AutoField(primary_key=True)
    assignment = models.ForeignKey(Assignment, on_delete=models.PROTECT)
    student = models.ForeignKey(Student, on_delete=models.PROTECT)
    details = models.TextField(blank=True)
    grade = models.CharField(max_length=1, default='U')

    def __str__(self):
        return f'{self.assignment}-{self.student}'