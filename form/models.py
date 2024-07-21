from django.db import models

class Student(models.Model):
    studentname = models.CharField(max_length=100)
    email = models.EmailField()
    mobile = models.CharField(max_length=15)
    address = models.CharField(max_length=500)

class Parent(models.Model):
    pname = models.CharField(max_length=100)
    pnumber = models.CharField(max_length=15)

class CET_Exam(models.Model):
    cetPhysics = models.CharField(max_length=10)
    cetChemistry = models.CharField(max_length=10)
    cetMathematics = models.CharField(max_length=10)
    cetPercentile = models.CharField(max_length=10)

class JEE_Exam(models.Model):
    jeePhysics = models.CharField(max_length=10)
    jeeChemistry = models.CharField(max_length=10)
    jeeMathematics = models.CharField(max_length=10)
    jeePercentile = models.CharField(max_length=10)

class UploadDoc(models.Model):
    applNo = models.CharField(max_length=200)
    meritfile = models.FileField(upload_to='uploads/')
    file_path = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.applNo

class Merit(models.Model):
    mhMerit = models.CharField(max_length=20)
    aiMerit = models.CharField(max_length=20)

class Agree(models.Model):
    # Add fields if necessary
    pass





# # Create your models here.
# class studentData(models.Model):
#     studentname= models.CharField(max_length=100),
#     email = models.EmailField(),
#     mobile = models.CharField(max_length=10),
#     address = models.CharField(),
#     pname = models.CharField(max_length=100)

# class documentModel(models.Model):
#     title = models.CharField(max_length=100)
#     image = models.ImageField(upload_to=('images/'))

#     def __str__(self):
#         return self.title 