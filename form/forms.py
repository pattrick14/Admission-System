from django import forms
from .models import Student, Parent, Exam, UploadDoc, Merit, Agree

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['studentname', 'email', 'mobile', 'address', ]
        
class ParentForm(forms.ModelForm):
    class Meta:
        model = Parent
        fields = ['pname', 'pnumber']

class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['cetPhysics', 'cetChemistry', 'cetMathematics', 'cetPercentile', 'jeePhysics', 'jeeChemistry', 'jeeMathematics', 'jeePercentile']

class UploadDoc(forms.ModelForm):
    class Meta:
        model = UploadDoc
        fields = ['applNo', 'meritfile']

class MeritForm(forms.ModelForm):
    class Meta:
        model = Merit
        fields = ['mhMerit', 'aiMerit']

class AgreeForm(forms.ModelForm):
    class Meta:
        model = Agree
        fields = []  # Add any fields if necessary

