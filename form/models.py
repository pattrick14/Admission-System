from django.db import models
from django.contrib.auth.models import User

class Application(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Application by {self.user.username}"

class UploadDoc(models.Model):
    application = models.OneToOneField(Application, on_delete=models.CASCADE)
    applNo = models.CharField(max_length=200, null=True)
    meritfile = models.FileField(upload_to='uploads/')
    file_path = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.applNo

class Student(models.Model):
    application = models.OneToOneField(Application, on_delete=models.CASCADE)
    studentname = models.CharField(max_length=100)
    gender = models.CharField(max_length=50, null=True, blank=True)
    category = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField()
    mobile = models.CharField(max_length=15)
    address = models.CharField(max_length=500)
    pname = models.CharField(max_length=100, null=True, blank=True)
    pnumber = models.CharField(max_length=15, null=True, blank=True)
    mhMerit = models.CharField(max_length=20, null=True, blank=True)
    aiMerit = models.CharField(max_length=20, null=True, blank=True)
    agreed = models.BooleanField(default=False)

class CET_Exam(models.Model):
    application = models.OneToOneField(Application, on_delete=models.CASCADE)
    cetPhysics = models.CharField(max_length=10)
    cetChemistry = models.CharField(max_length=10)
    cetMathematics = models.CharField(max_length=10)
    cetPercentile = models.CharField(max_length=10)

class JEE_Exam(models.Model):
    application = models.OneToOneField(Application, on_delete=models.CASCADE)
    jeePhysics = models.CharField(max_length=10)
    jeeChemistry = models.CharField(max_length=10)
    jeeMathematics = models.CharField(max_length=10)
    jeePercentile = models.CharField(max_length=10)