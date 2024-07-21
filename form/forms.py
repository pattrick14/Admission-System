from django import forms
from .models import Student, Parent, CET_Exam, UploadDoc, Merit, Agree, JEE_Exam

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['studentname', 'email', 'mobile', 'address', ]
        
class ParentForm(forms.ModelForm):
    class Meta:
        model = Parent
        fields = ['pname', 'pnumber']

class CET_ExamForm(forms.ModelForm):
    class Meta:
        model = CET_Exam
        fields = ['cetPhysics', 'cetChemistry', 'cetMathematics', 'cetPercentile']

class JEE_ExamForm(forms.ModelForm):
    class Meta:
        model = JEE_Exam
        fields = ['jeePhysics', 'jeeChemistry', 'jeeMathematics', 'jeePercentile']

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

