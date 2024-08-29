from django import forms
from .models import Student, CET_Exam, UploadDoc, JEE_Exam, Application

# class ApplicationForm(forms.ModelForm):
#     class Meta:
#         model = Application
#         fields = ['student', 'cet_exam', 'jee_exam', 'upload_doc']

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['studentname','gender', 'category', 'email', 'mobile', 'address','pname', 'pnumber',
                  'mhMerit', 'aiMerit', 'agreed'
                  ]
        widgets={
            'agreed':forms.CheckboxInput(attrs={'required':True}),
        }
        def __init__(self, *args, **kwargs):
            super(StudentForm, self).__init__(*args, **kwargs)
            for field in self.fields.values():
                field.required = True #Sets all fields as required

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

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['user']

