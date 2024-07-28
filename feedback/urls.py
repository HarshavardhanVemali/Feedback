from django.contrib import admin
from django.urls import path
from feedbackapp import views
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'), 
    path('studentlogin/',views.studentlogin,name='studentlogin'),
    path('adminlogin/',views.adminlogin,name='adminlogin'),
    path('facultylogin/',views.facultylogin,name='facultylogin.html'),
    path('adminpage/', views.adminpage, name='adminpage'),
    path('adminfaculty/',views.adminfaculty,name='adminfaculty'),
    path('adddepartments/',views.adddepartments,name='adddepartments'),
    path('getdepartments/',views.get_departments,name='getdepartments'),
    path('savedepartmentchanges/',views.savedepartmentchanges,name='savedepartmentchanges'),
    path('deletedepartment/',views.deletedepartment,name='deletedepartment'),
    path('getfaculty/',views.get_faculty,name='getfaculty'),
    path('subadminfaculty.html', TemplateView.as_view(template_name='subadminfaculty.html'), name='subadminfaculty'),
    path('addfaculty/',views.addfaculty,name='addfaculty'),
    path('savefacultychanges/',views.savefacultychanges,name='savefacultychanges'),
    path('deletefaculty/',views.deletefaculty,name='deletefaculty'),
    path('adminbranches/',views.adminbranches,name='adminbranches'),
    path('adminstudents/',views.adminstudents,name='adminstudents'),
    path('adminsections.html', TemplateView.as_view(template_name='adminsections.html'), name='adminsections'),
    path('adminsections/',views.adminsections,name='adminsections'),
    path('addbranches/',views.addbranches,name='addbranches'),
    path('getbranches/',views.get_branches,name='getbranches'),
    path('savebranchchanges/',views.savebranchchanges,name='savebranchchanges'),
    path('deletebranch/',views.deletebranch,name='deletebranch'),
    path('addyear/',views.addyear,name='addyear'),
    path('getyears/',views.getyears,name='getyears'),
    path('saveyearchanges/',views.saveyearchanges,name='saveyearchanges'),
    path('deleteyear/',views.deleteyear,name='deleteyear'),
    path('addsections/',views.addsections,name='addsections'),
    path('getsections/',views.get_sections,name='getsections'),
    path('savesectionchanges/',views.savesectionchanges,name='savesectionchanges'),
    path('deletesection/',views.deletesection,name='deletesection'),
    path('adminaddstudents/',views.adminaddstudents,name='adminaddstudents'),
    path('getstudents/',views.getstudents,name='getstudents'),
    path('adminaddstudents.html', TemplateView.as_view(template_name='adminaddstudents.html'), name='adminaddstudents'),
    path('addsingleuser/',views.addsingleuser,name='addsingleuser'),
    path('addmultipleusers/',views.addmultipleusers,name='addmultipleusers'),
    path('savestudentchanges/',views.savestudentchanges,name='savestudentchanges'),
    path('deletestudent/',views.deletestudent,name='deletestudent'),
    path('adminfeedback/',views.adminfeedback,name='adminfeedback'),
    path('getactivefeedbackexams/',views.getactivefeedbackexams,name='getactivefeedbackexams'),
    path('addfeedbackexam/',views.addfeedbackexam,name='addfeedbackexam'),
    path('updateexam/',views.updateExam,name='updateexam'),
    path('deleteExam/',views.deleteExam,name='deleteExam'),
    path('adminaddquestions/',views.adminaddquestions,name='adminaddquestions'),
    path('adminaddquestions.html', TemplateView.as_view(template_name='adminaddquestions.html'), name='adminaddquestions'),
    path('getmaximumoptions/',views.getmaximumoptions,name='getmaximumoptions'),
    path('getquestions/',views.getquestions,name='getquestions'),
    path('addquestion/',views.addquestion,name='addquestion'),
    path('savequestions/',views.savequestions,name='savequestions'),
    path('deletequestion/',views.deletequestion,name='deletequestion'),
    path('getsubjects/',views.getsubject,name='getsubjects'),
    path('addsubject/',views.addsubject,name='addsubject'),
    path('savesubjectchanges/',views.savesubjectchanges,name='savesubjectchanges'),
    path('deletesubject/',views.deletesubject,name='deletesubject'),
    path('activatefeedback/',views.activatefeedback,name='activatefeedback'),
    path('adminfeedbackofsubject/',views.adminfeedbackofsubject,name='adminfeedbackofsubject'),
    path('changequestionsforthesection/',views.changequestionsforthesection,name='changequestionsforthesection'),
    path('adminlogout/',views.admin_logout_view,name='adminlogout'),
    path('studentlogin/',views.studentlogin,name='studentlogin'),
    path('studentlogout/',views.student_logout_view,name='studentlogout'),
    path('getstudentsforexam/', views.getstudentsforexam, name='getstudentsforexam'),
    path('getsubjectsatstudent/',views.getsubjectsatstudent,name='getsubjectsatstudent'),
    path('feedbackpage/',views.feedbackpage,name='feedbackpage'),
    path('get_student_wise_analysis/',views.get_student_wise_analysis,name='get_student_wise_analysis'),
    path('get_question_wise_analysis/',views.get_question_wise_analysis,name='get_question_wise_analysis'),
    path('get_student_comments/',views.get_student_comments,name='get_student_comments'),
    path('downloadoverallreport/',views.downloadoverallreport,name='downloadoverallreport'),
    path('downloadoverallreporthtml/',views.downloadoverallreporthtml,name='downloadoverallreporthtml'),
    path('getsubjectdetails/',views.getsubjectdetails,name='getsubjectdetails'),
    path('getdepartmentdeatils/',views.getdepartmentdeatils,name='getdepartmentdeatils'),
    path('submitfeedback/',views.submitfeedback,name='submitfeedback'),
    path('getquestionsforfeedback/',views.getquestionsforfeedback,name='getquestionsforfeedback'),
    path('facultypage/',views.facultypage,name='facultypage'),
    path('getsubjectsoffaculty/',views.get_subjects_of_faculty,name='getsubjectsoffaculty'),
    path('facultyfeedbackofsubject/',views.facultyfeedbackofsubject,name='facultyfeedbackofsubject'),
    path('get_overall_rating/',views.get_overall_rating,name='get_overall_rating'),
    path('facultylogout',views.faculty_logout_view,name='facultylogout'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

