from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.conf import settings
import os
import pytesseract
from .forms import StudentForm, JEE_ExamForm, CET_ExamForm
from .models import UploadDoc, Application, Student, JEE_Exam, CET_Exam
from .utils import extract_info, perform_ocr, fill_template
import csv
import re
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import default_storage

if os.name == 'nt':  # For Windows
    pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'
else:  # For Linux (Ubuntu)
    pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

# Create your views here.
@login_required
def upload_file(request):
    user=request.user

    # Check if the user has already submitted an application
    if Application.objects.filter(user=user).exists():
        print("User already present")
        return redirect('success_page')  # Redirect to a success page if already submitted
    
    if request.method == 'POST' and 'meritfile' in request.FILES:
        uploaded_file = request.FILES['meritfile']
        # file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)
        file_name = uploaded_file.name
        # file_path = os.path.join(settings.MEDIA_ROOT, file_name)  # Construct the absolute file path
        
        # Create an Application instance and save it
        application = Application(user=user)
        application.save()
        
        # Save the file locally with its original uploaded name
        local_file_path = os.path.join(settings.MEDIA_ROOT, file_name)
        with open(local_file_path, 'wb+') as local_file:
            for chunk in uploaded_file.chunks():
                local_file.write(chunk)


        # Perform OCR on the locally saved file
        text, image_file_path = perform_ocr(local_file_path)

        # Extract information from the OCR output
        info = extract_info(text)
        # print(info)  # Debugging: Print extracted information

        # Extract application number from the extracted info
        applNo = info.get('ApplicationID', '')

        # Rename the local file based on the extracted application number
        if applNo:
            new_file_name = f"{applNo}.pdf"
            new_local_file_path = os.path.join(settings.MEDIA_ROOT, new_file_name)
            
            os.rename(local_file_path, new_local_file_path)

        # Upload the renamed file to S3
        with open(new_local_file_path, 'rb') as local_file:
            file_name_in_s3 = default_storage.save(new_file_name, local_file)
            new_file_url = default_storage.url(file_name_in_s3)

        # Delete the local file after uploading to S3
        if os.path.exists(new_local_file_path):
            os.remove(new_local_file_path)
        # Delete the processed image from local storage
        if os.path.exists(image_file_path):
            os.remove(image_file_path)
            print(f"Deleted temporary image file: {image_file_path}")
        else:
            print(f"File not found: {image_file_path}")
        #  # Save file to S3 instead of local storage
        # file_name_in_s3 = default_storage.save(file_name, uploaded_file)
        # file_url = default_storage.url(file_name_in_s3)

        # # You can download the file for local processing if needed
        # local_file_path = os.path.join(settings.MEDIA_ROOT, file_name)
        # with default_storage.open(file_name_in_s3, 'rb') as s3_file:
        #     with open(local_file_path, 'wb+') as local_file:
        #         for chunk in s3_file.chunks():
        #             local_file.write(chunk)

        # # with open(file_path, 'wb+') as destination:
        # #     for chunk in uploaded_file.chunks():
        # #         destination.write(chunk)

        # text = pytesseract.image_to_string(cv2.imread(file_path))
        # text = perform_ocr(local_file_path)
        # print(text)
        # Function to extract information from OCR output
        # info = extract_info(text)
        # print(info) #find the error
        
        # applNo = info.get('ApplicationID', '')

        # Save the file with the application number as the filename
        # new_file_name = f"{applNo}.pdf"
        # new_file_path = os.path.join(settings.MEDIA_ROOT, new_file_name)
        # os.rename(file_path, new_file_path)  # Rename the file

        #  # Rename the file in S3 with the application number
        # new_file_name = f"{applNo}.pdf"
        # new_file_name_in_s3 = f"{new_file_name}"
        # new_file_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{new_file_name}"

        #  # Save the renamed file to S3
        # with open(local_file_path, 'rb') as local_file:
        #     default_storage.save(new_file_name_in_s3, local_file)

        # # Optionally, delete the old file from S3
        # # default_storage.delete(file_name_in_s3)

        # # Ensure the local file is properly closed before attempting to delete it
        # # os.remove(local_file_path)

        dform = UploadDoc.objects.create(
            application=application,
            applNo=applNo,
            meritfile=new_file_name,
            file_path=new_file_url
        )
        dform.save()

        # Check if the document is a Final Merit List document
        is_final_merit_list = re.search(r'Final Merit Status|Final Merit List', text)
        is_provisional = re.search(r'Provisional', text)
        if is_final_merit_list:
            print("The document is a Final Merit List document.")
            final = "The document is a Final Merit List document."
        if is_provisional:
            print("The document is not a Final Merit List document.")

        jee_present = info.get('JEE Present', '')

        sform = StudentForm(initial={
            'studentname': request.POST.get('studentname'),
            'gender': request.POST.get('gender'),
            'category': info.get('Category'),
            'email': request.POST.get('email'),
            'mobile': request.POST.get('mobile'),
            'address': request.POST.get('address'),
            'pname' : request.POST.get('pname'),
            'pnumber' : request.POST.get('pnumber'),
            'mhMerit' : info.get('State General Merit No', ''),
            'aiMerit'  : info.get('All India Merit No', ''),
            'agreed' : request.POST.get('agreed'),
            'applNo': applNo,
            # Add other fields from info dictionary
            })
        # print(form)


        cetform = CET_ExamForm(initial={
            'cetPhysics': info.get('CET_Physics', ''),
            'cetChemistry': info.get('CET_Chemistry',''),
            'cetMathematics': info.get('CET_Mathematics', ''),
            'cetPercentile': info.get('CET_Total', ''),
        })

        jeeform = JEE_ExamForm(initial={
            'jeePhysics' : info.get('JEE_Physics', ''),
            'jeeChemistry': info.get('JEE_Chemistry',''),
            'jeeMathematics': info.get('JEE_Mathematics', ''),
            'jeePercentile': info.get('JEE_Total', ''),
        })
        
        return render(request, 'output.html', {'application':application, 'final':final, 'sform': sform, 'cetform':cetform, 'jeeform':jeeform,
                                               'dform':dform, 'file_path': new_file_url, 'jee_present':jee_present})
    else:
        sform = StudentForm()
        cetform = CET_ExamForm()
        jeeform = JEE_ExamForm()
        dform = UploadDoc()

    return render(request, 'test.html')

@login_required
def save_forms(request):
    user = request.user
    id = (Application.objects.get(user=user)).id
    application = Application.objects.get(id=id)

    if request.method == 'POST':
        sform = StudentForm(request.POST)
        cetform = CET_ExamForm(request.POST)
        jeeform = JEE_ExamForm(request.POST)
        dform = UploadDoc(request.POST, request.FILES)

        sform.instance.application = application
        cetform.instance.application = application
        jeeform.instance.application = application
        # dform.instance.application = application

        if all([sform.is_valid(), cetform.is_valid()]):
            sform.save()
            cetform.save()
        if (jeeform.is_valid()):
            jeeform.save()
        return redirect('success_page')  # Redirect to a success page after saving the data
    return render(request, 'output.html', {'sform': sform, 
                                           'cetform':cetform, 'jeeform':jeeform, 
                                           'dform': dform})

@login_required
def success_view(request):
    user = request.user
    
    if Application.objects.filter(user=user).exists():
        application = Application.objects.get(user=user)
        output_filename = f"filled_{application.uploaddoc.applNo}.pdf"  # Ensure uploaddoc is related to Application
        s3_file_name = f"filled_forms/{output_filename}"
        
        # Check if the PDF already exists in S3
        if default_storage.exists(s3_file_name):
            # If the file exists, get the URL
            s3_pdf_url = default_storage.url(s3_file_name)
        else:
            # If the file does not exist, generate a new PDF
            s3_pdf_url = generate_pdf(user)
        
        return render(request, 'success.html', {'output_path': s3_pdf_url})
    else:
        print("NooNOO")
        Application.objects.create(user=user)
        s3_pdf_url = generate_pdf(user)
        return render(request, 'success.html', {'output_path':s3_pdf_url})


def export_data(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="applications.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Application ID',
        'Student Name',
        'Gender',
        'Category',
        'Email',
        'Mobile',
        'Address',
        'Parent Name',
        'Parent Number',
        'MH Merit',
        'AI Merit',
        'Agreed',
        'CET Physics',
        'CET Chemistry',
        'CET Mathematics',
        'CET Percentile',
        'JEE Physics',
        'JEE Chemistry',
        'JEE Mathematics',
        'JEE Percentile',
        'Application Number',
        'Merit File'
    ])

    applications = Application.objects.all()
    for application in applications:
        student = Student.objects.get(application=application)
        cet_exam = CET_Exam.objects.get(application=application)
        upload_doc = UploadDoc.objects.get(application=application)
        try:
            jee_exam = JEE_Exam.objects.get(application=application)
        except ObjectDoesNotExist:
            jee_exam = None

        # Generate the URL for the uploaded merit file
        merit_file_url = default_storage.url(upload_doc.meritfile.name)

        writer.writerow([
            application.id,
            student.studentname,
            student.gender,
            student.category,
            student.email,
            student.mobile,
            student.address,
            student.pname,
            student.pnumber,
            student.mhMerit,
            student.aiMerit,
            student.agreed,
            cet_exam.cetPhysics,
            cet_exam.cetChemistry,
            cet_exam.cetMathematics,
            cet_exam.cetPercentile,
            jee_exam.jeePhysics if jee_exam else "Null",
            jee_exam.jeeChemistry if jee_exam else "Null",
            jee_exam.jeeMathematics if jee_exam else "Null",
            jee_exam.jeePercentile if jee_exam else "Null",
            upload_doc.applNo,
            merit_file_url
        ])

    return response



def generate_pdf(user):
    """
    Generate a PDF file for the given user.
    Args:
        user (User): The logged-in user.
    Returns:
        None
    """

    try:
        # Fetch the application data for the logged-in user
        applications = Application.objects.all()
        for application in applications:
            student = Student.objects.get(application=application)
            cet_exam = CET_Exam.objects.get(application=application)
            upload_doc = UploadDoc.objects.get(application=application)
            try:
                jee_exam = JEE_Exam.objects.get(application=application)
            except ObjectDoesNotExist:
                jee_exam = None

        # Prepare the context with the fetched data
        text_data = [
            student.studentname,
            student.gender,
            student.category,
            student.email,
            student.mobile,
            student.address,
            student.pname,
            student.pnumber,
            student.mhMerit,
            student.aiMerit,
            upload_doc.applNo,
            # upload_doc.meritfile,
            cet_exam.cetPhysics,
            cet_exam.cetChemistry,
            cet_exam.cetMathematics,
            cet_exam.cetPercentile,
            student.studentname,
            jee_exam.jeePhysics if jee_exam else "Null",
            jee_exam.jeeChemistry if jee_exam else "Null",
            jee_exam.jeeMathematics if jee_exam else "Null",
            jee_exam.jeePercentile if jee_exam else "Null",
        ]

        coordinates = [
            (560, 838),  # name
            (560, 910),  #gender
            (560, 1004), #category
            (560, 1078),  # email
            (560, 1150),  # mobile
            (1845, 1002),  # address
            (1845, 833),  # pname
            (1845, 920),  # pnumber
            (643, 2133),  # mhmerit
            (1570, 2133),  # aimerit
            (692, 1497),  # appl_no
            # (, ),  # merit_file
            (680, 1660),  # cet_physics
            (680, 1730),  # cet_chemistry
            (680, 1806),  # cet_mathematics
            (680, 1895),  # cet_percentile
            (432, 2515),  # AgreeName
            (1785, 1670),  # jee_physics
            (1785, 1743),  # jee_chemistry
            (1785, 1820),  # jee_mathematics
            (1785, 1895),  # jee_percentile
        ]

        # Define font and font size
        font_name = "Times-Roman"
        font_size = 30
        # Generate the output path for the local file
        output_filename = f"filled_{upload_doc.applNo}.pdf"
        output_path = os.path.join(settings.MEDIA_ROOT, output_filename)

        # Fill the PDF template
        fill_template(
            template_path=r"templates/PDFTemplate.png",
            output_path=output_path,
            text_data=text_data,
            coordinates=coordinates,
            font_name=font_name,
            font_size=font_size,
            )
        
          # Upload the filled PDF to S3
        with open(output_path, 'rb') as pdf_file:
            s3_file_name = f"filled_forms/{output_filename}"  # You can customize the S3 path
            s3_file_url = default_storage.save(s3_file_name, pdf_file)

        # Get the URL for the uploaded PDF
        s3_file_url = default_storage.url(s3_file_name)

        print(s3_file_url)
        # Optionally, delete the local file after uploading to S3
        os.remove(output_path)

        return s3_file_url
        # return output_path
        # # Serve the PDF file for download
        # with open(output_path, 'rb') as pdf_file:
        #     response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        #     response['Content-Disposition'] = f'attachment; filename="filled_{upload_doc.applNo}.pdf"'
        #     return response
        
    except Exception as e:
        print(f"Error generating PDF: {e}")
