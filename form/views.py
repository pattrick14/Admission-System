from django.shortcuts import render, redirect
# from django.http import JsonResponse
from django.conf import settings
import os
import pytesseract
from .forms import StudentForm, ParentForm, ExamForm, MeritForm, AgreeForm 
from .models import UploadDoc
from .utils import extract_info, perform_ocr
import cv2
import re

pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'

# Create your views here.
def upload_file(request):
    if request.method == 'POST' and 'meritfile' in request.FILES:
        uploaded_file = request.FILES['meritfile']
        # file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)
        file_name = uploaded_file.name
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)  # Construct the absolute file path


        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        # text = pytesseract.image_to_string(cv2.imread(file_path))
        text = perform_ocr(file_path)
        # Function to extract information from OCR output
        info = extract_info(text)
        print(info) #find the error

        applNo = info.get('ApplicationID', '')

        # Save the file with the application number as the filename
        new_file_name = f"{applNo}.pdf"
        new_file_path = os.path.join(settings.MEDIA_ROOT, new_file_name)
        os.rename(file_path, new_file_path)  # Rename the file

        dform = UploadDoc.objects.create(
            applNo=applNo,
            meritfile=new_file_name,
            file_path=new_file_path
        )
        dform.save()

        # dform = UploadDoc(initial={
        #     'applNo': info.get('ApplicationID', ''),
        #     'meritfile': new_file_name, 
        #     'file_path':new_file_path,
        # })
        # dform.save()


        sform = StudentForm(initial={
            'studentname': request.POST.get('studentname'),
            'email': request.POST.get('email'),
            'mobile': request.POST.get('mobile'),
            'address': request.POST.get('address'),
            # Add other fields from info dictionary
            })
        # print(form)
        pform = ParentForm(initial={
            'pname' : request.POST.get('pname'),
            'pnumber' : request.POST.get('pnumber'),
        })

        eform = ExamForm(initial={
            'cetPhysics': info.get('CET_Physics', ''),
            'cetChemistry': info.get('CET_Chemistry',''),
            'cetMathematics': info.get('CET_Mathematics', ''),
            'cetPercentile': info.get('CET_Total', ''),
            'jeePhysics' : info.get('JEE_Physics', ''),
            'jeeChemistry': info.get('JEE_Chemistry',''),
            'jeeMathematics': info.get('JEE_Mathematics', ''),
            'jeePercentile': info.get('JEE_Total', ''),
        })

        
        mform = MeritForm(initial={
            'mhMerit' : info.get('State General Merit No', ''),
            'aiMerit'  : info.get('All India Merit No', ''),
        })

        aform = AgreeForm(initial={

        })
        return render(request, 'output.html', {'sform': sform, 'pform':pform, 'eform':eform, 
                                               'dform':dform, 'mform':mform, 'aform':aform, 
                                               'file_path': new_file_path})
    else:
        sform = StudentForm()
        pform = ParentForm()
        eform = ExamForm()
        dform = UploadDoc()
        mform = MeritForm()
        aform = AgreeForm()

    return render(request, 'test.html')

def save_forms(request):
    if request.method == 'POST':
        sform = StudentForm(request.POST)
        pform = ParentForm(request.POST)
        eform = ExamForm(request.POST)
        dform = UploadDoc(request.POST, request.FILES)
        mform = MeritForm(request.POST)
        aform = AgreeForm(request.POST)

        if all([sform.is_valid(), pform.is_valid(), eform.is_valid(), mform.is_valid(), aform.is_valid()]):
            sform.save()
            pform.save()
            eform.save()
            mform.save()
            aform.save()
            return redirect('success_page')  # Redirect to a success page after saving the data
    return render(request, 'output.html', {'sform': sform, 'pform': pform, 'eform': eform, 'dform': dform, 'mform': mform, 'aform': aform})

def success_view(request):
    return render(request, 'success.html')
