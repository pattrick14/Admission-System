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


pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'

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
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)  # Construct the absolute file path
        
        # Create an Application instance and save it
        application = Application(user=user)
        application.save()

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
            application=application,
            applNo=applNo,
            meritfile=new_file_name,
            file_path=new_file_path
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
                                               'dform':dform, 'file_path': new_file_path, 'jee_present':jee_present})
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
        output_path = generate_pdf(user)
        return render(request, 'success.html', {'output_path':output_path})
    else:
        print("NooNOO")
        Application.objects.create(user=user)
        output_path = generate_pdf(user)
        return render(request, 'success.html', {'output_path':output_path})


def export_data(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="applications.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Application ID',
        'Student Name',
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

        writer.writerow([
            application.id,
            student.studentname,
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
            upload_doc.meritfile
        ])

    return response


# def export_data(request):
#     applications = Application.objects.all()
#     data = []
#     for application in applications:
#         student = application.student
#         cet_exam = application.cet_exam
#         jee_exam = application.jee_exam
#         upload_doc = application.upload_doc
        
#         row = {
#             'Student Name': student.studentname,
#             'Email': student.email,
#             'Mobile': student.mobile,
#             'Address': student.address,
#             'Parent Name': student.pname,
#             'Parent Number': student.pnumber,
#             'MH Merit': student.mhMerit,
#             'AI Merit': student.aiMerit,
#             'Agreed': student.agreed,
#             'CET Physics': cet_exam.cetPhysics,
#             'CET Chemistry': cet_exam.cetChemistry,
#             'CET Mathematics': cet_exam.cetMathematics,
#             'CET Percentile': cet_exam.cetPercentile,
#             'JEE Physics': jee_exam.jeePhysics,
#             'JEE Chemistry': jee_exam.jeeChemistry,
#             'JEE Mathematics': jee_exam.jeeMathematics,
#             'JEE Percentile': jee_exam.jeePercentile,
#             'Application Number': upload_doc.applNo,
#             'Merit File': upload_doc.meritfile,
#         }
#         data.append(row)
    
#     df = pd.DataFrame(data)
#     response = HttpResponse(content_type='application/ms-excel')
#     response['Content-Disposition'] = 'attachment; filename="student_data.xlsx"'
#     df.to_excel(response, index=False)
#     return response

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
        output_path=r"media/" + f"filled_{upload_doc.applNo}.pdf"

        # Fill the PDF template
        fill_template(
            template_path=r"templates/PDFTemplate.png",
            output_path=output_path,
            text_data=text_data,
            coordinates=coordinates,
            font_name=font_name,
            font_size=font_size,
            )
        return output_path
        # # Serve the PDF file for download
        # with open(output_path, 'rb') as pdf_file:
        #     response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        #     response['Content-Disposition'] = f'attachment; filename="filled_{upload_doc.applNo}.pdf"'
        #     return response
        
    except Exception as e:
        print(f"Error generating PDF: {e}")
