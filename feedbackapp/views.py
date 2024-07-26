from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login
from .models import FailedLoginAttempts,Faculty,Branches,Departments,Section,StudyingYear,Student,Exam,Question,QuestionOption,Subject,User,Feedback
import uuid
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError 
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.db import models
from django.contrib.auth import logout
from django.db.models import Avg

MAX_FAILED_ATTEMPTS = 3
def set_device_cookie(response, device_id):
    response.set_cookie('device_id', device_id, max_age=365*24*60*60)

def get_device_id(request):
    return request.COOKIES.get('device_id', str(uuid.uuid4()))

def is_device_blocked(device_id):
    try:
        failed_attempt = FailedLoginAttempts.objects.get(device_id=device_id)
        if failed_attempt.is_active:
            return True
    except FailedLoginAttempts.DoesNotExist:
        return False
    return False

def adminlogin(request):
    if request.method == 'POST':
        device_id = get_device_id(request)
        if is_device_blocked(device_id):
            return render(request, 'adminlogin.html', {'blocked': True, 'error_message': 'Your device is permanently blocked due to multiple failed login attempts.'})

        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_superuser or (user.is_staff and not user.is_active):
                FailedLoginAttempts.objects.filter(device_id=device_id).update(attempts=0, is_active=False)
                response = redirect('adminpage')
                set_device_cookie(response, device_id)
                login(request, user)
                return response
            else:
                return render(request, 'adminlogin.html', {'error_message': 'You do not have permission to access the admin page.'})
        else:
            failed_attempt, created = FailedLoginAttempts.objects.get_or_create(device_id=device_id)
            if not created:
                failed_attempt.attempts += 1
                failed_attempt.save()
                if failed_attempt.attempts >= MAX_FAILED_ATTEMPTS:
                    failed_attempt.is_active = True
                    failed_attempt.save()
                    return render(request, 'adminlogin.html', {'blocked': True, 'error_message': 'Your device is permanently blocked due to multiple failed login attempts.'})
            else:
                failed_attempt.attempts = 1
                failed_attempt.save()
            return render(request, 'adminlogin.html', {'error_message': 'Invalid username or password'})
    else:
        response = render(request, 'adminlogin.html')
        if 'device_id' not in request.COOKIES:
            device_id = get_device_id(request)
            set_device_cookie(response, device_id)
        return response

@login_required(login_url='/adminlogin/')
def adminpage(request):
    return render(request,'adminpage.html')

@login_required(login_url='/adminlogin/')
def adddepartments(request):
    if request.method == 'POST':
        if request.POST.get('form_type') == 'adddepartmentsform':
            department_name = request.POST.get('departmentname')
            department_code = request.POST.get('departmentcode')
            department_image = request.FILES.get('departmentimage')
            try:
                check_department=Departments.objects.filter(department_code=department_code)
                if check_department:
                    return JsonResponse({'success': False, 'error': f'Department with id {department_code} already exists'})
                department = Departments.objects.create(
                    department_code=department_code,
                    department_name=department_name,
                    department_logo=department_image
                )
                if department:
                    return JsonResponse({'success': True})
                else:
                    return JsonResponse({'success': False, 'error': 'Failed to add department.'})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method or form type.'})
@login_required(login_url='/adminlogin/')
def get_departments(request):
    if request.method == 'POST':
        departments = Departments.objects.all()
        department_data = []
        for department in departments:
            department_data.append({
                'name': department.department_name,
                'code': department.department_code,
                'logo': department.department_logo.url if department.department_logo else None,
            })
        return JsonResponse(department_data, safe=False)
    return JsonResponse({'success': False, 'error': 'Invalid request method or form type.'})
@login_required(login_url='/adminlogin/')
@require_POST
def savedepartmentchanges(request):
    try:
        data = json.loads(request.body)
        department_code = data.get('department_code')
        department_name = data.get('department_name')
        
        current_department = Departments.objects.get(department_code=department_code)
        current_department.department_name = department_name
        current_department.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required(login_url='/adminlogin/')
@require_POST
def deletedepartment(request):
    try:
        data=json.loads(request.body)
        department_code=data.get('department_code')
        current_department=Departments.objects.get(department_code=department_code)
        current_department.delete()
        return JsonResponse({'success':True})
    except Departments.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Department not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required(login_url='/adminlogin/')
def adminfaculty(request):
    return render(request,'adminfaculty.html')

@login_required(login_url='/adminlogin/')
@csrf_exempt
def get_faculty(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        department_code = data.get('department_code')
        if Departments.objects.filter(department_code=department_code).exists():
            faculties = Faculty.objects.filter(department__department_code=department_code)
            department = Departments.objects.get(department_code=department_code)
            get_department_name = department.department_name  
            get_department_image=department.department_logo.url if department.department_logo else None,
            faculty_list = [
                {
                    'name': faculty.faculty_name,
                    'facultyid': faculty.faculty_id,
                    'departmentname': faculty.department.department_name,
                    'departmentcode': faculty.department.department_code,
                    'img': faculty.faculty_image.url if faculty.faculty_image else None
                } 
                for faculty in faculties
            ]
            return JsonResponse({
                'faculty': faculty_list, 
                'department_name': get_department_name,
                'department_image':get_department_image
            }, safe=False)
        else:
            return JsonResponse({'error': 'No faculty found for this department.'}, status=404)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)
@login_required(login_url='/adminlogin/')
@csrf_exempt
def addfaculty(request):
    if request.method=='POST':
        if request.POST.get('form_type') == 'addfacultyform':
            facultyname=request.POST.get('facultyname')
            registenumber=request.POST.get('registernumber')
            department=request.POST.get('department')
            faculty_image=request.POST.get('facultyimage')
            try:
                check_faculty=Faculty.objects.filter(faculty_id =registenumber)
                if check_faculty:
                    return JsonResponse({'success': False, 'error': f'Faculty with id {registenumber} already exists'})
                try:
                    department = Departments.objects.get(department_code=department) 
                except Departments.DoesNotExist:
                    return JsonResponse({'success': False, 'error': 'Invalid department selected.'})
                hashed_password = make_password(registenumber)
                faculty = Faculty.objects.create(
                    faculty_id=registenumber,
                    faculty_name=facultyname,
                    department=department,
                    faculty_image=faculty_image,
                    username=registenumber, 
                    password=hashed_password,
                    role='faculty'
                )
                if faculty:
                    return JsonResponse({'success': True})
                else:
                    return JsonResponse({'success': False, 'error': 'Failed to add Faculty.'})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method or form type.'})

@login_required(login_url='/adminlogin/')
@require_POST
def savefacultychanges(request):
    try:
        data = json.loads(request.body)
        facultyid = data.get('faculty_id')
        faculty_name = data.get('faculty_name')
        current_faculty = Faculty.objects.get(faculty_id=facultyid)
        current_faculty.faculty_name=faculty_name
        current_faculty.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required(login_url='/adminlogin/')
@require_POST
def deletefaculty(request):
    try:
        data=json.loads(request.body)
        facultyid = data.get('faculty_id')
        current_faculty = Faculty.objects.get(faculty_id=facultyid)
        if current_faculty:
            current_faculty.delete()
            return JsonResponse({'success':True})
    except Departments.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Faculty not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required(login_url='/amdinlogin/')
def adminbranches(request):
    year_number = request.GET.get('year')

    context = {
         'year_number': year_number,
     }
    return render(request, 'adminbranches.html', context)

@login_required(login_url='/adminlogin/')
def adminstudents(request):
    return render(request,'adminstudents.html')

@login_required(login_url='/adminlogin/')
@csrf_exempt
def addyear(request):
    if request.method=='POST':
        if request.POST.get('form_type') == 'addyearsform':
            yearnumber=request.POST.get('yearnumber')
            yearname=request.POST.get('yearname')
            academicyear=request.POST.get('academicyear')
            try:
                check_year=StudyingYear.objects.filter(studying_year =yearnumber)
                if check_year:
                    return JsonResponse({'success': False, 'error': f'{yearnumber} already exists'})
                year = StudyingYear.objects.create(
                    studying_year=yearnumber,
                    studying_year_name=yearname,
                    academic_year=academicyear
                )
                if year:
                    return JsonResponse({'success': True})
                else:
                    return JsonResponse({'success': False, 'error': 'Failed to add Year.'})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method or form type.'})

login_required(login_url='/adminlogin/')
def getyears(request):
    if request.method == 'POST':
        years = StudyingYear.objects.all()
        year_data = []
        for year in years:
            year_data.append({
                'year_number': year.studying_year,
                'year_name': year.studying_year_name,
                'academic_year':year.academic_year
            })
        return JsonResponse(year_data, safe=False)
    return JsonResponse({'success': False, 'error': 'Invalid request method or form type.'})

login_required(login_url='/adminlogin/')
@csrf_exempt
def saveyearchanges(request):
    try:
        data=json.loads(request.body)
        year_number=data.get('year_number')
        new_year_number=data.get('new_year_number')
        year_name=data.get('year_name')
        academic_year=data.get('academic_year')
        current_year = StudyingYear.objects.get(studying_year=year_number)
        if current_year:
            current_year.studying_year=new_year_number
            current_year.studying_year_name=year_name
            current_year.academic_year=academic_year
            current_year.save()
        return JsonResponse({'success':True})
    except Departments.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Year not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required(login_url='/adminlogin/')
@csrf_exempt
def deleteyear(request):
    try:
        data=json.loads(request.body)
        year_number=data.get('year_number')
        current_year = StudyingYear.objects.get(studying_year=year_number)
        if current_year:
            current_year.delete()
        return JsonResponse({'success':True})
    except Departments.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Year not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required(login_url='/adminlogin/')
@csrf_exempt
def addbranches(request):
    if request.method == 'POST':
        if request.POST.get('form_type') == 'addbranchesform':
            branch_code = request.POST.get('branchcode')
            branch_name = request.POST.get('branchname')
            department_code = request.POST.get('department')
            year_number = request.POST.get('year_number')

            if not (branch_code and branch_name and department_code and year_number):
                return JsonResponse({'success': False, 'error': 'Missing required fields'}, status=400)
            try:
                department = Departments.objects.get(department_code=department_code)
                studying_year = StudyingYear.objects.get(studying_year=year_number)
                if Branches.objects.filter(branch_code=branch_code, studying_year=studying_year).exists():
                    return JsonResponse({'success': False, 'error': f'Branch with code {branch_code} already exists in this year.'})
                branch = Branches.objects.create(
                    branch_code=branch_code,
                    branch_name=branch_name,
                    department=department,
                    studying_year=studying_year
                )
                return JsonResponse({'success': True})
            except (Departments.DoesNotExist, StudyingYear.DoesNotExist) as e:
                return JsonResponse({'success': False, 'error': str(e)}, status=404)
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method or form type.'})

@login_required(login_url='/adminlogin/')
@csrf_exempt
def get_branches(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        year_number = data.get('year_number')

        if year_number is not None: 
            try:
                year_number = int(year_number)
                branches = Branches.objects.filter(
                    studying_year__studying_year=year_number
                )
                branch_data = [{
                    'code': branch.branch_code, 
                    'name': branch.branch_name, 
                    'department': branch.department.department_name,
                    'year_number': branch.studying_year.studying_year
                } for branch in branches]
                return JsonResponse(branch_data, safe=False)
            except ValueError:
                return JsonResponse({'success': False, 'error': 'Invalid year number.'})
        else:
            return JsonResponse({'success': False, 'error': 'Year number and department code are required.'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method.'})
@login_required(login_url='/adminlogin/')
@require_POST
def savebranchchanges(request):
    try:
        data = json.loads(request.body)
        branch_code = data.get('branch_code') 
        branch_name = data.get('branch_name')
        year_number = data.get('year_number')
        current_branch = Branches.objects.get(branch_code=branch_code, studying_year__studying_year=year_number)
        current_branch.branch_name = branch_name
        current_branch.save()

        return JsonResponse({'success': True})
    except Branches.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Branch not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required(login_url='/adminlogin/')
@require_POST
def deletebranch(request):
    try:
        data = json.loads(request.body)
        branch_code = data.get('branch_code')
        year_number = data.get('year_number')
        current_branch = Branches.objects.get(branch_code=branch_code, studying_year__studying_year=year_number)
        current_branch.delete()
        return JsonResponse({'success': True})
    except Branches.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Branch not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required(login_url='/adminlogin/')
def adminsections(request):
    return render(request, 'adminsections.html')

@login_required(login_url='/adminlogin/')
@require_POST
@csrf_exempt
def addsections(request):
    if request.method == 'POST':
        if request.POST.get('form_type') == 'addsectionsform':
            section_name = request.POST.get('sectionname')
            section_number = request.POST.get('sectionnumber')
            branch_code = request.POST.get('branch_code')
            year_number = request.POST.get('year_number')
            if not (section_name and section_number and branch_code and year_number):
                return JsonResponse({'success': False, 'error': 'Missing required fields'}, status=400)
            try:
                branch = Branches.objects.get(branch_code=branch_code, studying_year__studying_year=year_number)
                studying_year = StudyingYear.objects.get(studying_year=year_number)
                if Section.objects.filter(section_number=section_number, branch=branch).exists():
                    return JsonResponse({'success': False, 'error': 'Section already exists in this branch.'})
                Section.objects.create(
                    section_name=section_name,
                    section_number=section_number,
                    studying_year=studying_year,
                    branch=branch,
                )
                return JsonResponse({'success': True})
            except (Branches.DoesNotExist, StudyingYear.DoesNotExist) as e:
                return JsonResponse({'success': False, 'error': str(e)}, status=404)
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)}, status=500)
        else:
            return JsonResponse({'success': False, 'error': 'Invalid request.'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request.'})

@login_required(login_url='/adminlogin/')
@require_POST
def get_sections(request):
    try:
        data = json.loads(request.body)
        branch_code = data.get('branch_code')
        year_number = data.get('year_number')

        if branch_code and year_number: 
            sections = Section.objects.filter(
                branch__branch_code=branch_code,
                branch__studying_year__studying_year=year_number 
            )
            sections_list = [{
                'section_name': section.section_name, 
                'section_number': section.section_number,
                'year_number': section.studying_year.studying_year,
                'branch_code': section.branch.branch_code
            } for section in sections]
            return JsonResponse(sections_list, safe=False)
        else:
            return JsonResponse({'success': False, 'error': 'Branch code and year number are required.'}, status=400)

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON.'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required(login_url='/adminlogin/')
@require_POST
@csrf_exempt
def savesectionchanges(request):
    try:
        data = json.loads(request.body)
        section_number = data.get('section_number')
        section_name = data.get('section_name')
        year_number = data.get('year_number')
        branch_code = data.get('branch_code')

        if not (section_name and section_number and year_number and branch_code):
            return JsonResponse({'success': False, 'error': 'Missing required fields'}, status=400)

        current_section = Section.objects.get(
            section_number=section_number,
            branch__branch_code=branch_code,
            branch__studying_year__studying_year=year_number
        )

        current_section.section_name = section_name
        current_section.save()
        return JsonResponse({'success': True})

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Section.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'No section found.'}, status=404)

@login_required(login_url='/adminlogin/')
@csrf_exempt
@require_POST
def deletesection(request):
    try:
        data = json.loads(request.body)
        section_number = data.get('section_number')
        year_number = data.get('year_number')
        branch_code = data.get('branch_code')

        section = Section.objects.get(
            section_number=section_number,
            branch__branch_code=branch_code,
            branch__studying_year__studying_year=year_number 
        )
        section.delete()
        return JsonResponse({'success': True})

    except Section.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Section not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required(login_url='/adminlogin/')
def adminaddstudents(request):
    return render(request,'adminaddstudents.html')

@login_required(login_url='/adminlogin/') 
@csrf_exempt
@require_POST
def getstudents(request):
    try:
        data = json.loads(request.body)
        branch_code = data.get('branch_code')
        year_number = data.get('year_number')
        section_number = data.get('section_number')
        students = Student.objects.filter(
            branch__branch_code=branch_code, 
            studying_year__studying_year=year_number,
            section__section_number=section_number
        )
        student_data = [{
            'student_id': student.student_id,
            'student_name': student.student_name,
            'studying_year': student.studying_year.studying_year_name,  
            'department': student.department.department_name,         
            'branch': student.branch.branch_name,
            'section': student.section.section_name,
        } for student in students]
        return JsonResponse({'students': student_data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required(login_url='/adminlogin/') 
@csrf_exempt
@require_POST
def addsingleuser(request):
    if request.method == 'POST':
        if request.POST.get('form_type') == 'addsingleusersform':
            student_name = request.POST.get('studentname')
            register_number = request.POST.get('registernumber')
            branch_code = request.POST.get('branch_code')
            year_number = request.POST.get('year_number')
            section_number = request.POST.get('section_number')
            if not (student_name and register_number and branch_code and year_number and section_number):
                return JsonResponse({'success': False, 'error': 'Missing required fields'}, status=400)
            if Student.objects.filter(student_id=register_number).exists():
                return JsonResponse({'success': False, 'error': 'Student with this Register Number already exists.'}, status=400)
            try:
                branch = Branches.objects.get(
                    branch_code=branch_code, 
                    studying_year__studying_year=year_number
                )
                section = Section.objects.get(section_number=section_number, branch=branch)
                if branch.department != section.branch.department:
                    return JsonResponse({'success': False, 'error': 'Inconsistent department between branch and section.'}, status=400)
                hashed_password = make_password(register_number) 
                student = Student.objects.create(
                    student_id=register_number,
                    student_name=student_name,
                    studying_year=branch.studying_year,
                    department=branch.department, 
                    branch=branch,
                    section=section,
                    username=register_number,
                    role='student',
                    password=hashed_password
                )
                return JsonResponse({'success': True})
            except (Branches.DoesNotExist, Section.DoesNotExist) as e:
                return JsonResponse({'success': False, 'error': str(e)}, status=404)
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=400)

@login_required(login_url='/adminlogin/')
@csrf_exempt
@require_POST
def addmultipleusers(request):
    if request.method == 'POST':
        if request.POST.get('form_type') == 'addmultipleusersform':
            sequence_number = request.POST.get('sequencenumber')
            starting_number = int(request.POST.get('startingnumber'))
            ending_number = int(request.POST.get('endingnumber'))
            student_names = request.POST.get('studentnames').split("\n")
            branch_code = request.POST.get('branch_code')
            year_number = request.POST.get('year_number')
            section_number = request.POST.get('section_number')
            if len(student_names) != (ending_number - starting_number + 1):
                return JsonResponse({'success': False, 'error': 'Number of students and given student names do not match.'})
            if not (student_names and sequence_number and starting_number and ending_number and branch_code and year_number and section_number):
                return JsonResponse({'success': False, 'error': 'Missing required fields'}, status=400)
            try:
                branch = Branches.objects.get(
                    branch_code=branch_code,
                    studying_year__studying_year=year_number
                )
                section = Section.objects.get(section_number=section_number, branch=branch)
                if branch.department != section.branch.department:
                    return JsonResponse({'success': False, 'error': 'Inconsistent department between branch and section.'}, status=400)
                for i in range(starting_number, ending_number + 1):
                    student_id = f'{sequence_number}{i:02}'
                    student_name = student_names[i - starting_number]
                    if Student.objects.filter(student_id=student_id).exists():
                        return JsonResponse({'success': False, 'error': f'Student with Register Number {student_id} already exists.'}, status=400)
                    hashed_password = make_password(student_id)
                    student = Student.objects.create(
                        student_id=student_id,
                        student_name=student_name,
                        studying_year=branch.studying_year,
                        department=branch.department,
                        branch=branch,
                        section=section,
                        username=student_id,
                        role='student',
                        password=hashed_password
                    )
                return JsonResponse({'success': True})
            except (Branches.DoesNotExist, Section.DoesNotExist) as e:
                return JsonResponse({'success': False, 'error': str(e)}, status=404)
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=400)
@login_required(login_url='/adminlogin/')
@csrf_exempt
@require_POST
def savestudentchanges(request):
    try:
        data = json.loads(request.body)
        student_id=data.get('student_id')
        student_name=data.get('student_name')

        if not (student_id and student_name):
            return JsonResponse({'success': False, 'error': 'Missing required fields'}, status=400)

        student = Student.objects.get(
            student_id=student_id
        )
        student.student_name=student_name
        student.save()
        return JsonResponse({'success': True})

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Section.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'No Student found.'}, status=404)

@login_required(login_url='/adminlogin/')
@csrf_exempt
@require_POST
def deletestudent(request):
    try:
        data = json.loads(request.body)
        student_id=data.get('student_id')
        student = Student.objects.get(
            student_id=student_id
        )
        student.delete()
        return JsonResponse({'success': True})
    except Section.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Student not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    
@login_required(login_url='/adminlogin/')
def adminfeedback(request):
    return render(request,'adminfeedback.html')

@login_required(login_url='/adminlogin/')
@csrf_exempt
@require_POST
def getactivefeedbackexams(request):
    if request.method == 'POST':
        try:
            exams = Exam.objects.all()
            exams_data = [{'exam_name': exam.feedback_exam_name, 'exam_code': exam.feedback_exam_code,'maximumoptions':exam.max_options_per_question} for exam in exams]
            return JsonResponse(exams_data, safe=False)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

@login_required(login_url='/adminlogin/')
@csrf_exempt
@require_POST
def getmaximumoptions(request):
    if request.method == 'POST':
        try:
            data=json.loads(request.body)
            exam_code=data.get('exam_code')
            exams = Exam.objects.get(feedback_exam_code=exam_code)
            maximumoptions=exams.max_options_per_question
            return JsonResponse({'success':True,'maximum_options':maximumoptions})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})



@login_required(login_url='/adminlogin/')
@csrf_exempt
@require_POST
def addfeedbackexam(request):
    if request.method == 'POST':
        if request.POST.get('form_type') == 'addfeedbacksform':
            exam_name = request.POST.get('examname')
            exam_number = request.POST.get('examcode')
            maximumoptions=request.POST.get('maximumoptions')
            if not (exam_name and exam_number and maximumoptions):
                return JsonResponse({'success': False, 'error': 'Missing required fields'}, status=400)
            
            if Exam.objects.filter(feedback_exam_code=exam_number).exists():
                return JsonResponse({'success': False, 'error': 'Exam with this code already exists.'}, status=400)

            try:
                Exam.objects.create(feedback_exam_code=exam_number, feedback_exam_name=exam_name,max_options_per_question=maximumoptions)
                return JsonResponse({'success': True})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
        return JsonResponse({'success': False, 'error': 'Invalid form type.'})
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

@login_required(login_url='/adminlogin/')
@csrf_exempt
@require_POST
def updateExam(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            exam_code = data.get('exam_code')
            new_name = data.get('new_name')

            exam = Exam.objects.get(feedback_exam_code=exam_code)
            exam.feedback_exam_name = new_name
            exam.save()

            return JsonResponse({'success': True})
        except Exam.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Exam not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)

@login_required(login_url='/adminlogin/')
@csrf_exempt
@require_POST
def deleteExam(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            exam_code = data.get('exam_code')

            exam = Exam.objects.get(feedback_exam_code=exam_code)
            exam.delete() 

            return JsonResponse({'success': True})
        except Exam.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Exam not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)

@login_required(login_url='/adminlogin/')
@csrf_exempt
@require_POST
def adminaddquestions(request):
    return render(request,'adminaddquestions.html')

@login_required(login_url='/adminlogin/')
@csrf_exempt
@require_POST
def getquestions(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            exam_code = data.get('exam_code')
            if not exam_code:
                return JsonResponse({'success': False, 'error': 'Missing required fields'}, status=400)
            try:
                exam = Exam.objects.get(feedback_exam_code=exam_code) 
                questions = Question.objects.filter(exam=exam)
                questions_data = []
                for question in questions:
                    question_data = {
                        'question_number': question.question_number,
                        'question_text': question.question_text,
                        'options': []  
                    }
                    options = QuestionOption.objects.filter(question=question)
                    for option in options:
                        option_data = {
                            'option_number': option.option_number,
                            'option_text': option.option_text,
                            'option_score': option.option_score
                        }
                        question_data['options'].append(option_data) 
                    questions_data.append(question_data)
                return JsonResponse({'success': True, 'questions': questions_data})
            except Exam.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Exam not found.'}, status=404)
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)}, status=500)
        except Exam.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Exam not found.'}, status=404)
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)

@login_required
@csrf_exempt
@require_POST
def addquestion(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        exam_code = data.get('exam_code')
        question_number = data.get('question_number')
        question_text = data.get('question_text')
        options_data = data.get('options')
        try:
            exam = Exam.objects.get(feedback_exam_code=exam_code) 

            question = Question.objects.create(
                exam=exam,
                question_number=question_number,
                question_text=question_text
            )
            for option_data in options_data:
                QuestionOption.objects.create(
                    exam=exam,
                    question=question, 
                    option_number=option_data['option_number'],
                    option_text=option_data['option_text'],
                    option_score=option_data['option_score']
                )

            return JsonResponse({'success': True})
        
        except Exam.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Exam not found'})
        except ValidationError as e: 
            return JsonResponse({'success': False, 'error': e.message})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
@csrf_exempt
@require_POST
def savequestions(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        question_number = data.get('question_number')
        exam_code = data.get('exam_code')

        try:
            exam = Exam.objects.get(feedback_exam_code=exam_code)
            question = Question.objects.get(exam=exam, question_number=question_number)
            question.question_text = data.get('question_text')
            question.save()
            for option_data in data.get('options', []):
                option_number = option_data.get('option_number')
                option, created = QuestionOption.objects.get_or_create(
                    exam=exam, 
                    question=question, 
                    option_number=option_number
                )
                option.option_text = option_data.get('option_text')
                option.option_score = option_data.get('option_score')
                option.save()

            return JsonResponse({'success': True, 'message': 'Question updated successfully'})
        except Exam.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Exam not found'})
        except Question.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Question not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
@csrf_exempt
@require_POST
def deletequestion(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            question_number = data.get('question_number')
            exam_code = data.get('exam_code')
            if not question_number or not exam_code:
                return JsonResponse({'success': False, 'error': 'Missing required fields'}, status=400)
            exam = Exam.objects.get(feedback_exam_code=exam_code)
            question = Question.objects.get(exam=exam, question_number=question_number)
            question.delete()
            return JsonResponse({'success': True})
        except Exam.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Exam not found.'}, status=404)
        except Question.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Question not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)

@login_required(login_url='/adminlogin')
@csrf_exempt
@require_POST
def getsubject(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            branch_code = data.get('branch_code')
            year_number = data.get('year_number')
            section_number = data.get('section_number')
            branch = Branches.objects.get(branch_code=branch_code, studying_year__studying_year=year_number)
            section = Section.objects.get(section_number=section_number,branch__branch_code=branch_code,studying_year__studying_year=year_number)
            subjects = Subject.objects.filter(section=section, studying_year=year_number, branch=branch)
            subjects_data = []
            for subject in subjects:
                faculty = Subject.objects.get(subject_code=subject.subject_code,section=section,studying_year=year_number,branch=branch)
                faculty=faculty.faculty
                faculty_code = Faculty.objects.get(faculty_id=faculty) 
                faculty_name = faculty_code.faculty_name
                faculty_department = faculty_code.department.department_name
                subjects_data.append({
                    'subject_code': subject.subject_code,
                    'subject_name': subject.subject_name,
                    'subject_faculty_name': f"{faculty.username}({faculty_name})",
                    'subject_facultydepartment': faculty_department
                })

            return JsonResponse({'subjects': subjects_data}, safe=False)
        except Branches.DoesNotExist:
            return JsonResponse({'error': 'Branch not found.'}, status=404)
        except Section.DoesNotExist:
            return JsonResponse({'error': 'Section not found.'}, status=404)
        except Subject.DoesNotExist:
            return JsonResponse({'error': 'Subject not found.'}, status=404)
            return JsonResponse({'error': 'Invalid branch, year, or section.'}, status=400)


@login_required(login_url='/adminlogin/')
@csrf_exempt
@require_POST
def addsubject(request):
    if request.method=='POST':
        if request.POST.get('form_type') == 'addsubjectform':
            subjectname = request.POST.get('subjectname')
            subjectcode = request.POST.get('subjectcode')
            faculty_department = request.POST.get('facultydepartment')
            faculty_id = request.POST.get('faculty')
            branch_code = request.POST.get('branch_code')
            year_number = request.POST.get('year_number')
            section_number = request.POST.get('section_number')
            try:
                subject = Subject.objects.get(
                    subject_code=subjectcode,
                    branch__branch_code=branch_code,
                    studying_year__studying_year=year_number,
                    section__section_number=section_number
                )
                return JsonResponse({'error': 'Subject already exists in this section.'}, status=400)  
            except Subject.DoesNotExist:
                try:
                    branch = Branches.objects.get(branch_code=branch_code, studying_year__studying_year=year_number)
                    section = Section.objects.get(branch=branch, section_number=section_number)
                    faculty = Faculty.objects.get(faculty_id=faculty_id)
                    if faculty.department.department_code== faculty_department:
                        subject = Subject.objects.create(
                            subject_code=subjectcode,
                            subject_name=subjectname,
                            faculty=faculty,
                            branch=branch,
                            studying_year=branch.studying_year,
                            section=section
                        )
                        return JsonResponse({'success': True})
                    else:
                        return JsonResponse({'error': 'Faculty does not belong to the selected department.'}, status=400) 
                except (Branches.DoesNotExist, Section.DoesNotExist, Faculty.DoesNotExist):
                    return JsonResponse({'error': 'Invalid branch, year, section, or faculty.'}, status=400)


@login_required(login_url='/adminlogin')
@csrf_exempt
@require_POST
def savesubjectchanges(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            subject_code = data.get('subject_code')
            subject_name = data.get('subject_name')
            branch_code = data.get('branch_code')
            year_number = data.get('year_number')
            section_number = data.get('section_number')
            subject = Subject.objects.get(
                subject_code=subject_code,
                branch__branch_code=branch_code,
                studying_year__studying_year=year_number,
                section__section_number=section_number
            )
            subject.subject_name = subject_name
            subject.save()
            return JsonResponse({'success': True})
        except Subject.DoesNotExist:
            return JsonResponse({'error': 'Invalid subject code, branch, year, or section.'}, status=400)

@login_required(login_url='/adminlogin')
@csrf_exempt
@require_POST
def deletesubject(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            subject_code = data.get('subject_code')
            branch_code = data.get('branch_code')
            year_number = data.get('year_number')
            section_number = data.get('section_number')
            subject = Subject.objects.get(
                subject_code=subject_code,
                branch__branch_code=branch_code,
                studying_year__studying_year=year_number,
                section__section_number=section_number
            )
            subject.delete()
            return JsonResponse({'success': True})
        except Subject.DoesNotExist:
            return JsonResponse({'error': 'Invalid subject code, branch, year, or section.'}, status=400)
@login_required(login_url='/adminlogin')
@csrf_exempt
@require_POST
def activatefeedback(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            branch_code = data.get('branch_code')
            year_number = data.get('year_number')
            section_number = data.get('section_number')
            action = data.get('action')
            mid_term = int(data.get('mid_term'))

            branch = Branches.objects.get(branch_code=branch_code, studying_year__studying_year=year_number)
            section = Section.objects.get(branch=branch, section_number=section_number)
            subjects = Subject.objects.filter(
                section=section,
                studying_year=branch.studying_year,
            )
            if mid_term == 1:
                for subject in subjects:
                    if action == 'activate':
                        if subject.midterm1_active:
                            return JsonResponse({'error': f'Midterm 1 for all is already activated.'}, status=400)
                        elif subject.midterm2_active:
                            return JsonResponse({'error': f'Midterm 2 for all is active. Please deactivate Midterm 2 first.'}, status=400)
                        elif subject.midterm1_deactivate:
                            return JsonResponse({'error': f'Midterm 1 for all has been deactivated and cannot be activated again.'}, status=400)
                        else:
                            subject.midterm1_active = True
                            subject.midterm1_activated_at = timezone.now()
                            subject.save()
                    elif action == 'deactivate':
                        if not subject.midterm1_active:
                            return JsonResponse({'error': f'Midterm 1 for all is already deactivated.'}, status=400)
                        else:
                            subject.midterm1_active = False
                            subject.midterm1_deactivate = timezone.now()
                            subject.save()
                    else:
                        return JsonResponse({'error': 'Invalid action.'}, status=400)

            elif mid_term == 2:
                for subject in subjects:
                    if action == 'activate':
                        if subject.midterm2_active:
                            return JsonResponse({'error': f'Midterm 2 for all is already activated.'}, status=400)
                        elif subject.midterm1_active:
                            return JsonResponse({'error': f'Midterm 1 for all is active. Please deactivate Midterm 1 first.'}, status=400)
                        elif subject.midterm2_deactivate:
                            return JsonResponse({'error': f'Midterm 2 for all has been deactivated and cannot be activated again.'}, status=400)
                        else:
                            subject.midterm2_active = True
                            subject.midterm2_activated_at = timezone.now()
                            subject.save()
                    elif action == 'deactivate':
                        if not subject.midterm2_active:
                            return JsonResponse({'error': f'Midterm 1 for all is already deactivated.'}, status=400)
                        else:
                            subject.midterm1_active = False
                            subject.midterm2_deactivate = timezone.now()
                            subject.save()
                    else:
                        return JsonResponse({'error': 'Invalid action.'}, status=400)
                else:
                    return JsonResponse({'error': 'Invalid action.'}, status=400)

            else:
                return JsonResponse({'error': 'Invalid midterm value.'}, status=400)

            return JsonResponse({'success': True, 'message': f'Midterm {mid_term} {"activated" if action == "activate" else "deactivated"} successfully for all subjects.'})

        except (Branches.DoesNotExist, Section.DoesNotExist):
            return JsonResponse({'error': 'Invalid branch, year, or section.'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)

@login_required(login_url='/adminlogin/')
@csrf_exempt
@require_POST
def changequestionsforthesection(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            branch_code = data.get('branch_code')
            year_number = data.get('year_number')
            section_number = data.get('section_number')
            exam_code = data.get('exam_code')
            if not (branch_code and year_number and section_number and exam_code):
                return JsonResponse({'success': False, 'error': 'Require the missing fields'})

            branch = Branches.objects.get(branch_code=branch_code, studying_year__studying_year=year_number)
            section = Section.objects.get(branch=branch, section_number=section_number)
            exam = Exam.objects.get(feedback_exam_code=exam_code)
            
            if section:
                section.selected_exam = exam
                section.save() 
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'error': 'Invalid exam code value.'}, status=400)
        except (Branches.DoesNotExist, Section.DoesNotExist, Exam.DoesNotExist): 
            return JsonResponse({'error': 'Invalid branch, year, section, or exam code.'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)   

@login_required(login_url='/adminlogin/')
def adminfeedbackofsubject(request):
    return render(request,'adminfeedbackofsubject.html')

@login_required(login_url='/adminlogin/')
@csrf_exempt
@require_POST
def get_student_wise_analysis(request):
    if request.method == 'POST':    
        try:
            data = json.loads(request.body)
            branch_code = data.get('branch_code')
            year_of_study = data.get('year_of_study')
            subject_code = data.get('subject_code')
            section_code = data.get('section_number')
            mid_term = int(data.get('mid_term'))
            if not all([branch_code, year_of_study, subject_code, section_code, mid_term]):
                return JsonResponse({'error': 'Missing parameters'}, status=400)
            try:
                feedbacks = Feedback.objects.filter(
                    subject__subject_code=subject_code,
                    subject__studying_year__studying_year=year_of_study,
                    subject__section__section_number=section_code,
                    subject__branch__branch_code=branch_code,
                    mid_term=mid_term
                ).select_related('student', 'subject', 'subject__section__selected_exam')
                if not feedbacks:
                    return JsonResponse({'error': 'No feedback found for the given criteria.'}, status=404)
                analysis_data = []
                total_average_rating = 0 
                rating_count = 0
                for feedback in feedbacks:
                    student_data = {
                        'student_id': feedback.student.student.student_id,
                        'student_name': feedback.student.student.student_name,
                        'average_rating': getattr(feedback, f'mid_term_{mid_term}_rating', None),
                        'question_ratings': [] 
                    }
                    average_rating = getattr(feedback, f'mid_term_{mid_term}_rating', None)
                    if average_rating is not None:
                        total_average_rating += average_rating
                        rating_count += 1
                    selected_options = getattr(feedback, f'options_mid_term_{mid_term}', None)
                    exam = feedback.subject.section.selected_exam.feedback_exam_code
                    if selected_options:
                        try:
                            selected_options = eval(selected_options) 
                        except (SyntaxError, NameError):
                            return JsonResponse({'error': 'Invalid format for selected_options'}, status=400)
                        for question_number, option_number in selected_options.items():
                            question = Question.objects.get(exam=exam, question_number=int(question_number))
                            option = QuestionOption.objects.get(question=question, option_number=int(option_number))
                            student_data['question_ratings'].append({
                                'question_number': question.question_number,
                                'question_text': question.question_text,
                                'selected_option': option.option_text,
                                'rating': option.option_score
                            })

                    analysis_data.append(student_data)
                if rating_count > 0:
                    total_average_rating /= rating_count

                return JsonResponse({
                    'analysis_data': analysis_data, 
                    'total_average_rating': total_average_rating
                })

            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)

@login_required(login_url='/adminlogin/')
@csrf_exempt
@require_POST
def get_question_wise_analysis(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            branch_code = data.get('branch_code')
            year_of_study = data.get('year_of_study')
            subject_code = data.get('subject_code')
            section_code = data.get('section_number')
            mid_term = int(data.get('mid_term'))
            if not all([branch_code, year_of_study, subject_code, section_code, mid_term]):
                return JsonResponse({'error': 'Missing parameters'}, status=400)

            try:
                exam = Feedback.objects.filter(
                    subject__subject_code=subject_code,
                    subject__studying_year__studying_year=year_of_study,
                    subject__section__section_number=section_code,
                    subject__branch__branch_code=branch_code,
                    mid_term=mid_term
                ).select_related('subject__section__selected_exam').first().subject.section.selected_exam.feedback_exam_code
                all_feedbacks = Feedback.objects.filter(
                    subject__subject_code=subject_code,
                    subject__studying_year__studying_year=year_of_study,
                    subject__section__section_number=section_code,
                    subject__branch__branch_code=branch_code,
                    mid_term=mid_term
                ).select_related('student')
                questions = Question.objects.filter(exam=exam).prefetch_related('options')
                analysis_data = []

                for question in questions:
                    question_data = {
                        'question_number': question.question_number,
                        'question_text': question.question_text,
                        'options': {}
                    }
                    for option in question.options.all():
                        option_count = 0
                        for feedback in all_feedbacks:
                            selected_options = getattr(feedback, f'options_mid_term_{mid_term}', None)
                            if selected_options:
                                try:
                                    selected_options = eval(selected_options)
                                    if isinstance(selected_options, dict) and str(question.question_number) in selected_options and str(option.option_number) == selected_options[str(question.question_number)]:
                                        option_count += 1
                                except (SyntaxError, NameError):
                                    pass 

                        question_data['options'][option.option_text] = option_count

                    analysis_data.append(question_data)

                return JsonResponse({'analysis_data': analysis_data})

            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)
    
@login_required(login_url='/adminlogin/')
@csrf_exempt
@require_POST
def get_student_comments(request):
    if request.method == 'POST':    
        try:
            data = json.loads(request.body)
            branch_code = data.get('branch_code')
            year_of_study = data.get('year_of_study')
            subject_code = data.get('subject_code')
            section_code = data.get('section_number')
            mid_term = int(data.get('mid_term'))
            if not all([branch_code, year_of_study, subject_code, section_code, mid_term]):
                return JsonResponse({'error': 'Missing parameters'}, status=400)
            try:
                feedbacks = Feedback.objects.filter(
                    subject__subject_code=subject_code,
                    subject__studying_year__studying_year=year_of_study,
                    subject__section__section_number=section_code,
                    subject__branch__branch_code=branch_code,
                    mid_term=mid_term
                ).select_related('student', 'subject', 'subject__section__selected_exam')
                
                if not feedbacks:
                    return JsonResponse({'error': 'No feedback found for the given criteria.'}, status=404)

                analysis_data = []
                for feedback in feedbacks:
                    student_data = {
                        'student_id': feedback.student.student.student_id,
                        'student_name': feedback.student.student.student_name,
                        'comment': getattr(feedback, f'comments_mid_term_{mid_term}', None),
                    }
                    analysis_data.append(student_data)
                return JsonResponse({'analysis_data': analysis_data})
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)

@login_required(login_url="/adminlogin/")
def admin_logout_view(request):
    logout(request)
    return redirect('adminlogin')

#students

@login_required(login_url='/studentlogin/')
def index(request):
    student_name = request.session.get('student_name')
    register_number = request.session.get('register_number') 
    context = {
        'student_name': student_name,
        'register_number': register_number 
    }
    return render(request, 'index.html', context)

def studentlogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
            if user.role == 'student':
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    student = Student.objects.get(student_id=username)
                    request.session['student_name'] = student.student_name
                    request.session['register_number'] = student.student_id 
                    return redirect('index')
                else:
                    return render(request, 'studentlogin.html', {'error_message': 'Invalid username or password'})
            else:
                return render(request, 'studentlogin.html', {'error_message': 'Invalid User.'})
        except User.DoesNotExist:
            return render(request, 'studentlogin.html', {'error_message': 'User does not exist.'})

    return render(request, 'studentlogin.html')

@login_required(login_url='/studentlogin/')
@csrf_exempt
@require_POST
def getstudentsforexam(request):
    if request.method == 'POST':
        try:
            data=json.loads(request.body)
            student_id=data.get('student_id')
            if student_id:
                student = get_object_or_404(Student, student_id=student_id)
                student_data = {
                    'Register Number': student.student_id,
                    'Name': student.student_name,
                    'Semester':student.studying_year.studying_year_name,
                    'Academic Year':student.studying_year.academic_year, 
                    'Department': student.department.department_name,         
                    'Branch': student.branch.branch_name,
                    'Section': student.section.section_name,
                }
                return JsonResponse(student_data)
            else:
                return JsonResponse({'error': 'Missing student_id parameter.'}, status=400) 
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)

@login_required(login_url='/studentlogin/')
def feedbackpage(request):
    return render(request,'feedbackpage.html')

@login_required(login_url='/studentlogin/')
@csrf_exempt
@require_POST
def getsubjectsatstudent(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            student_id = data.get('student_id')
            if student_id:
                try:
                    student = Student.objects.get(student_id=student_id)
                    subjects = Subject.objects.filter(
                        section=student.section,
                        studying_year=student.studying_year,
                        branch=student.branch
                    )
                    active_subjects = subjects.filter(
                        models.Q(midterm1_active=True) | models.Q(midterm2_active=True)
                    )
                    if not active_subjects:
                        return JsonResponse({'success': False, 'error': 'No Active Feedbacks found right now, ask our Administrator to activate.'})
                    subject_list = []
                    for subject in active_subjects:
                        faculty = subject.faculty
                        faculty_code = faculty.faculty_name if hasattr(faculty, 'faculty_name') else faculty.username
                        faculty_get_code = Faculty.objects.get(faculty_id=faculty_code)
                        faculty_name = faculty_get_code.faculty_name
                        active_midterm = 1 if subject.midterm1_active else 2
                        feedback_submitted = Feedback.objects.filter(
                            student=student,
                            subject=subject,
                            **{f'is_submitted_mid_term_{active_midterm}': True} 
                        ).exists()

                        subject_list.append({
                            'subject_code': subject.subject_code,
                            'subject_name': subject.subject_name,
                            'faculty_code': faculty_code,
                            'faculty_name': faculty_name,
                            'feedback_submitted': feedback_submitted,
                            'active_midterm': active_midterm
                        })
                    return JsonResponse({'success': True, 'subjects': subject_list})
                except ObjectDoesNotExist:
                    return JsonResponse({'success': False, 'error': 'Student not found.'}, status=404)
            else:
                return JsonResponse({'success': False, 'error': 'Missing student_id parameter.'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@login_required(login_url='/studentlogin/')
def getsubjectdetails(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            subject_code = data.get('subject_code')
            student_id = data.get('student_id')
            if not (subject_code and student_id):
                return JsonResponse({'success': False, 'error': 'Missing subject code or student ID.'})
            student = Student.objects.get(student_id=student_id)
            subject = Subject.objects.get(subject_code=subject_code, section=student.section)
            faculty_name = subject.faculty.faculty_name if hasattr(subject.faculty, 'faculty_name') else subject.faculty.username

            return JsonResponse({
                'success': True,
                'subject_name': subject.subject_name,
                'faculty_name': faculty_name,
            })
        except (Student.DoesNotExist, Subject.DoesNotExist):
            return JsonResponse({'success': False, 'error': 'Invalid student or subject.'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method.'})

@login_required(login_url='/studentlogin/')
@csrf_exempt
@require_POST
def getquestionsforfeedback(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            subject_code = data.get('subject_code')
            student_id = data.get('student_id')

            if not (subject_code and student_id):
                return JsonResponse({'success': False, 'error': 'Missing subject code or student ID.'})

            student = Student.objects.get(student_id=student_id)
            subject = Subject.objects.get(subject_code=subject_code, section=student.section)
            exam = subject.section.selected_exam

            questions = Question.objects.filter(exam=exam).prefetch_related('options')
            questions_data = []
            for question in questions:
                options_data = []
                for option in question.options.all():
                    options_data.append({
                        'option_number': option.option_number,
                        'option_text': option.option_text,
                        'option_score': option.option_score,
                    })
                questions_data.append({
                    'question_number': question.question_number,
                    'question_text': question.question_text,
                    'options': options_data,
                })

            return JsonResponse({'success': True, 'questions': questions_data})

        except (Student.DoesNotExist, Subject.DoesNotExist):
            return JsonResponse({'success': False, 'error': 'Invalid student or subject.'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method.'})
    
@login_required(login_url='/studentlogin/')
def submitfeedback(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            subject_code = data.get('subject_code')
            student_id = data.get('student_id')
            selected_answers = data.get('selectedAnswers')
            comments = data.get('comments')  

            student = get_object_or_404(Student, student_id=student_id)
            subject = get_object_or_404(Subject, subject_code=subject_code, section=student.section)
            faculty = Faculty.objects.get(user_ptr_id=subject.faculty.id) 
            section = student.section

            if subject.midterm1_active and not subject.midterm2_active:
                active_midterm = 1
            elif subject.midterm2_active and not subject.midterm1_active:
                active_midterm = 2
            else:
                return JsonResponse({'success': False, 'error': 'No active midterm for this subject.'})
            try:
                feedback = Feedback.objects.get(student=student, subject=subject) 
            except Feedback.DoesNotExist:
                feedback = Feedback.objects.create(
                    student=student,
                    subject=subject,
                    faculty=faculty,
                    section=section,
                    mid_term=active_midterm
                )
            exam = subject.section.selected_exam 
            total_score = 0
            for question_number, option_number in selected_answers.items():
                option = get_object_or_404(
                    QuestionOption, 
                    question__question_number=int(question_number), 
                    option_number=int(option_number),
                    question__exam=exam
                )
                total_score += option.option_score

            average_rating = total_score / len(selected_answers) if selected_answers else 0

            if active_midterm == 1:
                if feedback.is_submitted_mid_term_1:
                    return JsonResponse({'success': False, 'error': 'Feedback already submitted for Mid-1.'})
                feedback.mid_term_1_rating = average_rating
                feedback.comments_mid_term_1 = comments
                feedback.options_mid_term_1 = selected_answers
                feedback.is_submitted_mid_term_1 = True 
                feedback.created_at_mid_term_1 = timezone.now()
                feedback.updated_at_mid_term_1 = timezone.now()
            elif active_midterm == 2:
                if feedback.is_submitted_mid_term_2:
                    return JsonResponse({'success': False, 'error': 'Feedback already submitted for Mid-2.'})
                feedback.mid_term_2_rating = average_rating
                feedback.comments_mid_term_2 = comments
                feedback.options_mid_term_2 = selected_answers
                feedback.is_submitted_mid_term_2 = True
                feedback.created_at_mid_term_2 = timezone.now()
                feedback.updated_at_mid_term_2 = timezone.now()

            feedback.save()
            return JsonResponse({'success': True, 'message': 'Feedback submitted successfully!'})

        except Exception as e: 
            return JsonResponse({'success': False, 'error': str(e)}) 
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method.'})

@login_required(login_url="/studentlogin/")
def student_logout_view(request):
    logout(request)
    return redirect('studentlogin')
 
#faculty

@login_required(login_url='/facultylogin/')
@csrf_exempt
def facultypage(request):
    faculty_name = request.session.get('faculty_name')
    register_number = request.session.get('register_number')
    context = {
        'faculty_name': faculty_name,
        'register_number': register_number,

    }
    return render(request, 'facultypage.html', context)

def facultylogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
            if user.role == 'faculty':
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    faculty = Faculty.objects.get(faculty_id=username)
                    request.session['faculty_name'] = faculty.faculty_name
                    request.session['register_number'] = faculty.faculty_id
                    return redirect('facultypage')
                else:
                    return render(request, 'facultylogin.html', {'error_message': 'Invalid username or password'})
            else:
                return render(request, 'facultylogin.html', {'error_message': 'Invalid User.'})
        except User.DoesNotExist:
            return render(request, 'facultylogin.html', {'error_message': 'User does not exist.'})

    return render(request, 'facultylogin.html')

@login_required(login_url='/facultylogin/')
def facultyfeedbackofsubject(request):
    return render(request,'facultyfeedbackofsubject.html')

@login_required(login_url='/facultylogin/')
@csrf_exempt
@require_POST
def get_overall_rating(request):
    try:
        data = json.loads(request.body)
        branch_code = data.get('branch_code')
        year_of_study = data.get('year_of_study')
        subject_code = data.get('subject_code')
        section_number = data.get('section_number')
        mid_term = int(data.get('mid_term'))

        if not all([branch_code, year_of_study, subject_code, section_number, mid_term]):
            return JsonResponse({'error': 'Missing parameters'}, status=400)

        try:
            branch = Branches.objects.get(branch_code=branch_code, studying_year=year_of_study)
            section = Section.objects.get(section_number=section_number, branch=branch)
            subject = Subject.objects.get(subject_code=subject_code, section=section)

            if mid_term == 1:
                rating_field = 'mid_term_1_rating'
            elif mid_term == 2:
                rating_field = 'mid_term_2_rating'
            else:
                return JsonResponse({'error': 'Invalid mid_term value.'}, status=400)

            overall_rating = Feedback.objects.filter(
                subject=subject,
                mid_term=mid_term
            ).aggregate(Avg(rating_field))[f'{rating_field}__avg']

            if overall_rating is None:
                overall_rating = 0

            return JsonResponse({'overall_rating': overall_rating})

        except (Branches.DoesNotExist, Section.DoesNotExist, Subject.DoesNotExist) as e:
            return JsonResponse({'error': str(e)}, status=404)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data.'}, status=400)

@login_required(login_url='/facultylogin/')
@csrf_exempt
def get_subjects_of_faculty(request):
    if request.method == 'GET':
        faculty_id = request.session.get('register_number')
        faculty=Faculty.objects.get(faculty_id=faculty_id)
        subjects = Subject.objects.filter(faculty=faculty) 

        subjects_data = [
            {
                'subject_code': subject.subject_code, 
                'subject_name': subject.subject_name,
                'studying_year': subject.studying_year.studying_year,
                'branch_code': subject.branch.branch_code,
                'section_number': subject.section.section_number,
                'branch_name': subject.branch.branch_name, 
                'section_name': subject.section.section_name,
                'studying_year_name': subject.studying_year.studying_year_name,
            }
            for subject in subjects
        ]
        return JsonResponse({'subjects': subjects_data})
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required(login_url="/facultylogin/")
def faculty_logout_view(request):
    logout(request)
    return redirect('facultylogin')

