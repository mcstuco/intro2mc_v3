from django import forms
import intro2mc.models as models
import re

class AppCfgForm(forms.ModelForm):
    class Meta:
        model = models.AppConfig
        fields = '__all__'
        labels = {
            'currSemester': 'Semester'
        }
    
    def clean_roster(self):
        data = self.cleaned_data['roster'].lower()
        roster = set(re.findall(r'\w+', data))
        return ','.join(roster)
   
    def clean_currSemester(self):
        return self.cleaned_data['currSemester'].lower()

class StudentForm(forms.ModelForm):
    class Meta:
        model = models.Student
        fields = ['IGN', 'discord']
    
    def clean_IGN(self):
        ign = self.cleaned_data['IGN']
        if len(ign) > 16:
            raise forms.ValidationError("IGNs cannot exceed 16 characters")
        if not re.match("^[\w]+$", ign):
            raise forms.ValidationError("Illegal characters detected. Only a-z, A-Z, 0-9 and _ are allowed.")
        return ign

class ExcuseForm(forms.ModelForm):
    class Meta:
        model = models.Attendance
        fields = ['student', 'classSession', 'reason']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'classSession': forms.Select(attrs={'class': 'form-control'}),
            'reason': forms.TextInput(attrs={'class': 'form-control bg-white'})
        }
