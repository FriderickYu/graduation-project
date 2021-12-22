import random
import time
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import StudentInformation, TeacherInformation, User, ManagerInformation, CourseInformation, \
    Course_to_student, Department, Clbum, Course_to_clbum, Course_to_test, Test, Score
from .forms import UserForm
from django.http import HttpResponse, JsonResponse
import json
from .sendmessage import *
from django.core.paginator import Paginator
# filter() 等方法中的关键字参数查询都是一起进行“AND” 的。 如果需要执行更复杂的查询（例如OR 语句），使用Q 对象。
# Q 对象 (django.db.models.Q) 对象用于封装一组关键字参数。这些关键字参数就是上面“字段查询” 中所提及的那些。
from django.db.models import Q
import datetime
import numpy as np
import math
from pyecharts.charts import Bar, Line, Timeline, Page
from pyecharts import options as opts
import copy


# from apps.utils.email_send import send_register_email


# Create your views here.
def decorator(func):
    def innerfunc(request):
        try:
            username = request.session["username"]
        except Exception as e:
            return redirect("Myauth:登录")
        return func(request)

    return innerfunc


def findBack(request):
    return render(request, "Myauth/test.html")


def findBackpwd(request):
    em = request.GET.get("email")
    try:
        try:
            user = StudentInformation.objects.get(email=em)
            e = EmailManage(receivers=[user.email], username=user.student)
            e.sendEmail()
            return HttpResponse("1")
        except:
            try:
                user = TeacherInformation.objects.get(email=em)
                e = EmailManage(receivers=[user.email], username=user.teacher)
                e.sendEmail()
                return HttpResponse('1')
            except:
                user = ManagerInformation.objects.get(email=em)
                e = EmailManage(receivers=[user.email], username=user.manager)
                e.sendEmail()
                return HttpResponse('1')

    except:
        return HttpResponse("0")


def reSet(request):
    user = User.objects.get(pk=request.GET.get("username"))
    request.session['username'] = user.name
    return render(request, "Myauth/test1.html")


def reSetpwd(request):
    user = User.objects.get(name=request.session.get("username"))
    user.password = request.GET.get("password")
    user.save()
    del request.session['username']
    return JsonResponse({"usertype": user.user_type, "label": 1})


@decorator
def homepage(request):
    username = request.session.get('username')
    user = User.objects.get(name=username)
    if user.user_type == 1:
        studentinfo = StudentInformation.objects.get(student_id=username)
        return render(request, 'Myauth/homepage.html', {'studentinfo': studentinfo})


@decorator
def homepage_t(request):
    username = request.session.get('username')
    user = User.objects.get(name=username)
    if user.user_type == 2:
        teacherinfo = TeacherInformation.objects.get(teacher_id=username)
        return render(request, 'Myauth/homepage_t.html', {'teacherinfo': teacherinfo})


@decorator
def homepage_m(request):
    username = request.session.get('username')
    user = User.objects.get(name=username)
    if user.user_type == 0:
        managerinfo = ManagerInformation.objects.get(manager_id=username)
        return render(request, 'Myauth/homepage_m.html', {'managerinfo': managerinfo})


def user_login(request):
    return render(request, 'Myauth/login.html')


def verify_login(request):
    error_reaction = {"errorCode": 0, "errorsList": ''}
    if request.method == 'GET':
        username = request.GET.get('username')
        userpassword = request.GET.get('password')
        if username and userpassword:
            username = username.strip()
            try:
                user = User.objects.get(name=username)
                if user.password == userpassword:
                    if user.user_type == 1:
                        request.session['username'] = user.name
                        return JsonResponse(error_reaction)
                    elif user.user_type == 2:
                        error_reaction['errorCode'] = 2
                        request.session['username'] = user.name
                        return JsonResponse(error_reaction)
                    elif user.user_type == 0:
                        error_reaction['errorCode'] = 3
                        request.session['username'] = user.name
                        return JsonResponse(error_reaction)
                else:
                    error_reaction['errorCode'] = 1
                    error_reaction['errorsList'] = '你输入的密码错误！'
            except:
                error_reaction['errorCode'] = 1
                error_reaction['errorsList'] = '你输入的账号并不存在！'
        return JsonResponse(error_reaction)


# ----------------------------------------------------------------------------------以及modifypwd.html
@decorator
def modifypwd(request):
    user = User.objects.get(name=request.session['username'])
    label = 'Myauth/base.html'
    if user.user_type == 1:
        label
    elif user.user_type == 2:
        label = 'Myauth/base_t.html'
    else:
        label = 'Myauth/base_m.html'
    return render(request, 'Myauth/modifypwd.html', {"label": label, "type": user.user_type})


@decorator
def modify_information(request):
    username = request.session.get('username')
    user = User.objects.get(name=username)
    if user.user_type == 2:
        teacherinfo = TeacherInformation.objects.get(teacher_id=username)
        teacherinfo.phone = request.GET.get('tel')
        teacherinfo.email = request.GET.get('email')
        teacherinfo.save()
    elif user.user_type == 1:
        studentinfo = StudentInformation.objects.get(student_id=username)
        studentinfo.phone = request.GET.get('tel')
        studentinfo.email = request.GET.get('email')
        studentinfo.save()
    else:
        managerinfo = ManagerInformation.objects.get(manager_id=username)
        managerinfo.phone = request.GET.get('tel')
        managerinfo.email = request.GET.get('email')
        managerinfo.save()
    return JsonResponse({"label": "1"})


@decorator
def updatePwd(request):
    user = User.objects.get(name=request.session['username'])
    if (user.password == request.GET.get("oldpassword")):
        user.password = request.GET.get("newpassword")
        user.save()
        return JsonResponse({"usertype": user.user_type, "label": "1"})
    return JsonResponse({"label": "0"})


def login_out(request):
    logout(request)
    return redirect('Myauth:主页')


def exit(request):
    del request.session['username']
    return redirect('Myauth:登录')


def class_schedule(request):
    r_list = [c for c in Course_to_student.objects.filter(
        student=StudentInformation.objects.get(student=request.session.get("username")))]
    r_list += [c for c in Course_to_clbum.objects.filter(
        clbum=StudentInformation.objects.get(student=request.session.get("username")).clbum)]
    resultlist = []
    for data in r_list:
        teacher_name = data.course.teacher.name
        course_name = data.course.course_name
        course_label = data.course.course_label
        resultlist.append({
            'teacher_name': teacher_name,
            'course_name': course_name,
            'course_row': course_label % 100,
            'course_column': course_label // 100,
            'course_id': data.course.course_id,
            'course_room': data.course.course_room
        })
    return render(request, "Myauth/class_schedule.html", {'course_list': resultlist})


def class_schedule_t(request):
    r_list = CourseInformation.objects.filter(
        teacher=TeacherInformation.objects.get(teacher=request.session.get("username")))
    resultlist = []
    for data in r_list:
        resultlist.append({
            'teacher_name': data.teacher.name,
            'course_name': data.course_name,
            'course_row': data.course_label % 100,
            'course_column': data.course_label // 100,
            'course_id': data.course_id,
            'course_room': data.course_room
        })
    return render(request, "Myauth/class_schedule_t.html", {'course_list': resultlist})


def student_information(request):
    username = request.session.get('username')
    user = User.objects.get(name=username)
    if user.user_type == 1:
        studentinfo = StudentInformation.objects.get(student_id=username)
        studentinfo.clb = studentinfo.clbum.class_name
        studentinfo.department = studentinfo.clbum.department.department_name
        return render(request, 'Myauth/Student_Information.html', {'studentinfo': studentinfo})


def teacher_information(request):
    username = request.session.get('username')
    user = User.objects.get(name=username)
    if user.user_type == 2:
        # student = StudentInformation()
        # student.get_Gender_display()
        teacherinfo = TeacherInformation.objects.get(teacher_id=username)
        teacherinfo.depart = teacherinfo.department.department_name
        return render(request, 'Myauth/Teacher_Information.html', {'teacherinfo': teacherinfo})


def manager_information(request):
    username = request.session.get('username')
    user = User.objects.get(name=username)
    if user.user_type == 0:
        # student = StudentInformation()
        # student.get_Gender_display()
        managerinfo = ManagerInformation.objects.get(manager_id=username)
        return render(request, 'Myauth/Manager_Information.html', {'managerinfo': managerinfo})


def get_classschedule(request):
    pass


def input_course_m(request, pIndex='1'):
    datalist = TeacherInformation.objects.all()
    teacherlist = []
    for data in datalist:
        teacherlist.append({
            "teacher": data.teacher,
            "teacher_name": data.name
        })
    resultlist = CourseInformation.objects.all()
    p = Paginator(resultlist, 10)
    if pIndex == '':
        pIndex = '1'
    pIndex = int(pIndex)
    returnlist = p.page(pIndex)
    plist = p.page_range
    list2 = []
    departmentlist = []
    clbumlist = []
    for department in Department.objects.all():
        cl = []
        for clbum in Clbum.objects.filter(department=department):
            cl.append(clbum.class_name)
        departmentlist.append(department.department_name)
        clbumlist.append(cl)
    for data in returnlist:
        teacher = TeacherInformation.objects.get(teacher=data.teacher_id)
        data.teacher_id = teacher.name
        data.course_label = data.get_course_label_display()
        data.course_type = {1: "选修", 0: "必修"}[data.course_type]
        data.course_class = ','.join([clbum.clbum.class_name for clbum in Course_to_clbum.objects.filter(course=data)])
        list2.append(data)
    return render(request, 'Myauth/input_course_m.html',
                  {'teacherlist': teacherlist, 'departmentlist': departmentlist, 'clbumlist': clbumlist,
                   'returnlist': list2, 'plist': plist, 'pIndex': pIndex})


def search_course(request, pIndex='1'):
    if (request.GET.get("content", "") == ""):
        label = True
        resultlist = CourseInformation.objects.all()
    else:
        label = False
        resultlist = CourseInformation.objects.filter(course_name__contains=request.GET.get("content"))
    p = Paginator(resultlist, 10)
    if pIndex == '':
        pIndex = '1'
    pIndex = int(pIndex)
    returnlist = p.page(pIndex)
    plist = p.page_range
    list2 = []
    for data in returnlist:
        teacher = TeacherInformation.objects.get(teacher=data.teacher_id)
        data.teacher_id = teacher.name
        data.course_label = data.get_course_label_display()
        data.course_type = {1: "选修", 0: "必修"}[data.course_type]
        data.course_class = ','.join([clbum.clbum.class_name for clbum in Course_to_clbum.objects.filter(course=data)])
        list2.append(data)
    if label:
        return render(request, 'Myauth/search_course.html', {'returnlist': list2, 'plist': plist, 'pIndex': pIndex})
    else:
        r_list = []
        for data in list2:
            r_list.append({
                'course_id': data.course_id,
                'course_name': data.course_name,
                # 'course_week':data.course_week,
                'course_room': data.course_room,
                'credit': data.credit,
                'course_class': data.course_class,
                'course_label': data.course_label,
                'teacher_id': data.teacher_id
            })
        return JsonResponse({'returnlist': r_list})


@decorator
def add_course_index(request):
    return render(request, 'Myauth/add_course.html')


def add_course(request):
    teacher = TeacherInformation.objects.get(teacher=request.GET.get('teacher'))
    courselist = CourseInformation.objects.filter(teacher=teacher)
    label_list = []
    for data in courselist:
        label_list.append(data.course_label)
    label = request.GET.get("label")
    course_id_list = [course.course_id for course in CourseInformation.objects.all()]
    if (int(request.GET.get('applabel')) == 1 and request.GET.get('id') in course_id_list):
        return HttpResponse('3')
    try:
        course = CourseInformation.objects.get(course_id=request.GET.get("id"))
        if (int(label) in label_list and int(label) != course.course_label):
            return HttpResponse("2")
        course.teacher = teacher
        course.course_id = request.GET.get("id")
        course.course_type = {"选修": True, "必修": False}[request.GET.get("type")]
        course.course_name = request.GET.get("name")
        course.course_room = request.GET.get("room")
        course.credit = request.GET.get("credit")
        course.course_label = request.GET.get("label")
        course.save()
        for cb in Course_to_clbum.objects.filter(course=course):
            cb.delete()
        if ({"选修": True, "必修": False}[request.GET.get("type")] == False):
            Course_to_clbum(clbum=Clbum.objects.get(class_name=request.GET.get("class")), course=course).save()
        return HttpResponse("0")
    except:
        if (int(label) in label_list):
            return HttpResponse("2")
        course = CourseInformation()
        course.teacher = teacher
        course.course_id = request.GET.get("id")
        course.course_name = request.GET.get("name")
        # course.course_week = request.GET.get("week")
        course.course_room = request.GET.get("room")
        course.credit = request.GET.get("credit")
        course.course_label = request.GET.get("label")
        course.course_type = {"选修": True, "必修": False}[request.GET.get("type")]
        course.save()
        if ({"选修": True, "必修": False}[request.GET.get("type")] == False):
            Course_to_clbum(clbum=Clbum.objects.get(class_name=request.GET.get("class")), course=course).save()
        return HttpResponse("1")


def delete_course(request):
    try:
        course = CourseInformation.objects.get(course_id=request.GET.get("id"))
        c_list = Course_to_student.objects.filter(course=course)
        for c in c_list:
            c.delete()
        course.delete()
        return HttpResponse(1)
    except Exception as e:
        print(e)
        return HttpResponse(0)


def select_course(request, pIndex):
    r_list = Course_to_student.objects.filter(
        student=StudentInformation.objects.get(student=request.session.get("username")))
    resultlist = []
    for d in r_list:
        resultlist.append(d.course.course_id)
    resultlist = CourseInformation.objects.filter(~Q(course_id__in=resultlist)).filter(course_type=True)
    p = Paginator(resultlist, 10)
    if pIndex == '':
        pIndex = '1'
    pIndex = int(pIndex)
    returnlist = p.page(pIndex)
    plist = p.page_range
    list2 = []
    for data in returnlist:
        teacher = TeacherInformation.objects.get(teacher=data.teacher_id)
        data.teacher_id = teacher.name
        data.course_label = data.get_course_label_display()
        data.course_type = '选修'
        list2.append(data)
    return render(request, 'Myauth/select_course.html', {'returnlist': list2, 'plist': plist, 'pIndex': pIndex})


def student_save_course(request):
    id_list = request.GET.get("idlist")[:-1].split(",")
    r_list = Course_to_student.objects.filter(
        student=StudentInformation.objects.get(student=request.session.get("username")))
    resultlist = []
    for d in r_list:
        resultlist.append(d.course.course_label)
    for i in id_list:
        course = CourseInformation.objects.get(course_id=i)
        if (course.course_label in resultlist):
            return HttpResponse(0)
    student = StudentInformation.objects.get(student=request.session.get("username"))
    try:
        for id in id_list:
            relative = Course_to_student()
            relative.student = student
            relative.course = CourseInformation.objects.get(course_id=id)
            relative.save()
        return HttpResponse(1)
    except Exception as e:
        print(e)
        return HttpResponse(0)


def withdraw_course(request):
    try:
        idlist = request.GET.get("idlist")[:-1].split(",")
        student = StudentInformation.objects.get(student=User.objects.get(name=request.session.get('username')))
        for id in idlist:
            course = CourseInformation.objects.get(course_id=id)
            relative = Course_to_student.objects.filter(course=course, student=student)
            relative.delete()
        return HttpResponse(1)
    except:
        return HttpResponse(0)


def findPerson(request):
    try:
        teacher = TeacherInformation.objects.get(teacher=User.objects.get(name=request.GET.get('id')))
        return JsonResponse({'name': teacher.name, 'id': request.GET.get('id'), 'type': "老师"})
    except:
        try:
            student = StudentInformation.objects.get(student=User.objects.get(name=request.GET.get('id')))
            return JsonResponse({'name': student.name, 'id': request.GET.get('id'), 'type': "学生"})
        except:
            return HttpResponse('0')


def select_person(request):
    userlist = []
    for user in User.objects.filter(~Q(user_type=0)):
        if (user.user_type == 1):
            person = StudentInformation.objects.get(student=user.name)
        elif (user.user_type == 2):
            person = TeacherInformation.objects.get(teacher=user.name)
        user.user_type = user.get_user_type_display()
        user.currentname = person.name
        userlist.append(user)
    return render(request, 'Myauth/select_person.html', {"userlist": userlist})


def delete_teacher(request):
    try:
        # 逗号相隔，分离所有获取的账号(-1)
        idlist = request.GET.get('id').split(',')[:-1]
        for id in idlist:
            user = User.objects.get(name=id)
            teacher = TeacherInformation.objects.get(teacher=user)
            teacher.delete()
            user.delete()
        return HttpResponse(1)
    except:
        return HttpResponse(0)


def delete_student(request):
    try:
        idlist = request.GET.get('id').split(',')[:-1]
        for id in idlist:
            user = User.objects.get(name=id)
            student = StudentInformation.objects.get(student=user)
            course_student = Course_to_student.objects.filter(student=student)
            for course in course_student:
                course.delete()
            student.delete()
            user.delete()
        return HttpResponse(1)
    except:
        return HttpResponse(0)


def person_detail(request, username):
    user = User.objects.get(name=username)
    if (user.user_type == 1):
        person = StudentInformation.objects.get(student=user.name)
        person.department = person.clbum.department.department_name
        person.clb = person.clbum.class_name
        gender = list([list(x) for x in StudentInformation.Gender])
        department = [department.department_name for department in Department.objects.all()]
        return render(request, 'Myauth/person_detail.html', {"label": 0, "person": person,
                                                             "infolist": {'gender': gender,
                                                                          'department': department}})
    elif (user.user_type == 2):
        person = TeacherInformation.objects.get(teacher=user.name)
        gender = list([list(x) for x in TeacherInformation.Gender])
        person.depart = person.department.department_name
        department = [department.department_name for department in Department.objects.all()]
        rank = list([list(x) for x in TeacherInformation.Rank])
        return render(request, 'Myauth/person_detail.html', {"label": 1, "person": person,
                                                             "infolist": {'gender': gender, 'rank': rank,
                                                                          'department': department}})


def modify_Manager_Information(request):
    data = request.GET
    user = User.objects.get(name=data['oldid'])
    user.name = data['manager_id']
    user.save()
    request.session['username'] = user.name
    manager = ManagerInformation.objects.get(manager=data['oldid'])
    manager.manager = user
    manager.name = data['name']
    manager.sex = data['sex']
    manager.birthday = data['birthday']
    manager.phone = data['tel']
    manager.email = data['email']
    manager.save()
    if (data['oldid'] != data['manager_id']):
        user = User.objects.get(name=data['oldid'])
        user.delete()
    return JsonResponse({"label": "1"})


def modify_user(request):
    data = json.loads(request.GET.get('data'))

    label = request.GET.get('label')
    if label == '0':
        user = User.objects.get(name=data['person_student'])
        user.name = data['username']
        user.save()
        studentinfo = StudentInformation.objects.get(student=data['person_student'])
        studentinfo.student = user
        studentinfo.name = data['name']
        studentinfo.sex = data['sex']
        studentinfo.birthday = data['birthday']
        studentinfo.admission_date = data['admission_date']
        studentinfo.clbum = Clbum.objects.get(class_name=data['clbum'])
        studentinfo.phone = data['phone']
        studentinfo.email = data['email']
        studentinfo.save()
        if (data['username'] != data['person_student']):
            user = User.objects.get(name=data['person_student'])
            user.delete()
    elif (label == '1'):
        user = User.objects.get(name=data['person_teacher'])
        user.name = data['username']
        user.save()
        teacherinfo = TeacherInformation.objects.get(teacher=data['person_teacher'])
        teacherinfo.teacher = user
        teacherinfo.name = data['name']
        teacherinfo.sex = data['sex']
        teacherinfo.birthday = data['birthday']
        teacherinfo.department = Department.objects.get(department_name=data['department'])
        teacherinfo.admission_date = data['admission_date']
        teacherinfo.rank = data['rank']
        teacherinfo.phone = data['phone']
        teacherinfo.email = data['email']
        teacherinfo.save()
        if (data['username'] != data['person_teacher']):
            user = User.objects.get(name=data['person_teacher'])
            user.delete()
    return JsonResponse({"label": "1"})


def register(request):
    gender = list([x[0] for x in StudentInformation.Gender])
    department = [depart.department_name for depart in Department.objects.all()]
    rank = list([x[0] for x in TeacherInformation.Rank])
    return render(request, 'Myauth/register.html',
                  {'infolist': {'sex': gender, 'department': department, 'rank': rank}})


def in_excel(request):
    datalist = json.loads(request.POST.get("data"))
    print(datalist)
    label = 0
    if (list(datalist[0].keys())[0] != 'student_id'):
        label = 1
    resultlist = []
    for data in datalist:
        if label == 0:
            userlist = [user.name for user in User.objects.all()]
            user = User(user_type=1, name=data['student_id'], password=data['password'])
            if (data['student_id'] in userlist):
                resultlist.append(data['name'])
                continue
            user.save()
            try:
                department = Department.objects.get(department_name=data['department'])
            except:
                department = Department(department_name=data['department'])
                department.save()
            try:
                clbum = Clbum.objects.get(class_name=data['clbum'])
            except:
                clbum = Clbum(class_name=data['clbum'], department=department)
                clbum.save()
            student = StudentInformation(student=user, name=data['name'], sex=data['sex'],
                                         birthday=parseTime(data['birthday']),
                                         email=data['email'], admission_date=parseTime(data['admission_date']),
                                         clbum=clbum,
                                         phone=data['phone'])
            student.save()
        else:
            userlist = [user.name for user in User.objects.all()]
            user = User(user_type=2, name=data['teacher_id'], password=data['password'])
            if (data['teacher_id'] in userlist):
                resultlist.append(data['name'])
                continue
            user.save()
            try:
                department = Department.objects.get(department_name=data['department'])
            except:
                department = Department(department_name=data['department'])
                department.save()
            teacher = TeacherInformation(teacher=user, name=data['name'], sex=data['sex'],
                                         birthday=parseTime(data['birthday']),
                                         email=data['email'], admission_date=parseTime(data['admission_date']),
                                         rank=data['rank'], department=department, phone=data['phone'])
            teacher.save()
    return JsonResponse({'data': resultlist})


def signal_register(request):
    data = json.loads(request.POST.get('data'))
    userlist = [user.name for user in User.objects.all()]
    if (data['id'] in userlist):
        return HttpResponse('0')
    user = User(name=data['id'], password=data['password'], user_type=data['label'])
    user.save()
    try:
        if (data['label'] == 1):
            student = StudentInformation(student=user, name=data['name'], sex=data['sex'], birthday=data['birthday'],
                                         email=data['email'], admission_date=data['admission_date'],
                                         clbum=Clbum.objects.get(class_name=data['clbum']),
                                         phone=data['phone'])
            student.save()
        elif (data['label'] == 2):
            teacher = TeacherInformation(teacher=user, name=data['name'], sex=data['sex'], birthday=data['birthday'],
                                         email=data['email'], admission_date=data['admission_date'],
                                         rank=data['rank'],
                                         department=Department.objects.get(department_name=data['department']),
                                         phone=data['phone'])
            teacher.save()
        else:
            manager = ManagerInformation(manager=user, name=data['name'], sex=data['sex'], birthday=data['birthday'],
                                         email=data['email'],
                                         phone=data['phone'])
            manager.save()
        return HttpResponse('1')
    except Exception as e:
        print(e)
        user.delete()
        return HttpResponse('2')


def find_selected(request, pIndex):
    r_list = Course_to_student.objects.filter(
        student=StudentInformation.objects.get(student=request.session.get("username")))
    resultlist = [d.course.course_id for d in r_list]
    resultlist = CourseInformation.objects.filter(course_id__in=resultlist)
    p = Paginator(resultlist, 10)
    if pIndex == '':
        pIndex = '1'
    pIndex = int(pIndex)
    returnlist = p.page(pIndex)
    plist = p.page_range
    list2 = []
    for data in returnlist:
        teacher = TeacherInformation.objects.get(teacher=data.teacher_id)
        data.teacher_id = teacher.name
        data.course_label = data.get_course_label_display()
        list2.append(data)
    return render(request, 'Myauth/find_selected.html', {'returnlist': list2, 'plist': plist, 'pIndex': pIndex})


# 时间戳转时间
def getTime(timelabel, label: str) -> str:
    time_local = time.localtime(timelabel)
    return time.strftime("%Y{0}%m{0}%d".format(label), time_local)


def parseTime(timelabel):
    return datetime.datetime.strptime(timelabel, '%Y年%m月%d日')


def testmanage(request):
    coursecompletelist = Course_to_test.objects.all()
    c_list = [course.course_id for course in coursecompletelist]
    courselist = CourseInformation.objects.filter(course_type=False).filter(~Q(course_id__in=c_list))
    resultcourse = []
    selectlist = CourseInformation.objects.filter(course_type=True).filter(~Q(course_id__in=c_list))
    resultselect = []
    for course in courselist:
        course.clbum = ""
        for clbum in Course_to_clbum.objects.filter(course=course):
            course.clbum += clbum.clbum.class_name
        course.teacher_name = course.teacher.name
        course.course_label = course.get_course_label_display()
        resultcourse.append(course)
    for course in selectlist:
        course.teacher_name = course.teacher.name
        course.course_label = course.get_course_label_display()
        resultselect.append(course)
    return render(request, 'Myauth/test_manage.html', {'clbumlist': resultcourse, 'selectlist': resultselect})


def add_test(request):
    try:
        test = Test(starttime=request.GET.get('starttime'), endtime=request.GET.get('endtime'))
        test.save()
        Course_to_test(course=CourseInformation.objects.get(course_id=request.GET.get('course_id')), test=test).save()
        return HttpResponse('1')
    except Exception as e:
        print(e)
        return HttpResponse('0')


def select_test_info(request):
    coursecompletelist = Course_to_test.objects.all()
    c_list = [course.course_id for course in coursecompletelist]
    testlist = Test.objects.all()
    courselist = CourseInformation.objects.filter(course_type=False).filter(course_id__in=c_list)
    resultcourse = []
    selectlist = CourseInformation.objects.filter(course_type=True).filter(course_id__in=c_list)
    resultselect = []
    for course in courselist:
        course.clbum = ""
        for clbum in Course_to_clbum.objects.filter(course=course):
            course.clbum += clbum.clbum.class_name
        course.teacher_name = course.teacher.name
        course.course_label = course.get_course_label_display()
        test = Course_to_test.objects.get(course=course)
        course.starttime = test.test.starttime.strftime('%Y-%m-%d %H:%M:%S')
        course.endtime = test.test.endtime.strftime('%Y-%m-%d %H:%M:%S')
        course.testid = test.test.id
        resultcourse.append(course)
    for course in selectlist:
        course.teacher_name = course.teacher.name
        course.course_label = course.get_course_label_display()
        test = Course_to_test.objects.get(course=course)
        course.starttime = test.test.starttime.strftime('%Y-%m-%d %H:%M:%S')
        course.endtime = test.test.endtime.strftime('%Y-%m-%d %H:%M:%S')
        course.testid = test.test.id
        resultselect.append(course)
    return render(request, 'Myauth/test_info.html',
                  {'clbumlist': resultcourse, 'selectlist': resultselect, 'testlist': testlist})


def update_test_info(request):
    try:
        test = Test.objects.get(pk=request.GET.get('test_id'))
        test.starttime = datetime.datetime.strptime(request.GET.get('starttime'), '%Y-%m-%d %H:%M:%S')
        test.endtime = datetime.datetime.strptime(request.GET.get('endtime'), '%Y-%m-%d %H:%M:%S')
        test.save()
        return HttpResponse('1')
    except Exception as e:
        print(e)
        return HttpResponse('0')


def delete_test_info(request):
    try:
        Course_to_test.objects.filter(course=request.GET.get('course_id')).filter(
            test=request.GET.get('test_id')).delete()
        return HttpResponse('1')
    except:
        return HttpResponse('0')


def select_student_test(request):
    label = request.GET.get('testnum', '')
    student = StudentInformation.objects.get(student=User.objects.get(name=request.session.get('username')))
    courselist = Course_to_student.objects.filter(student=student)
    clbumcourselist = Course_to_clbum.objects.filter(clbum=student.clbum)
    r_list = []
    r_list += [course.course for course in courselist]
    r_list += [course.course for course in clbumcourselist]
    result = []
    for course in r_list:
        try:
            test = Course_to_test.objects.filter(course=course)[0].test
        except:
            continue
        course.starttime = test.starttime
        course.endtime = test.endtime
        course.course_class = student.clbum.class_name
        course.course_type = {1: "选修", 0: "必修"}[course.course_type]
        course.teachername = course.teacher.name
        course.course_label = course.get_course_label_display()
        course.department = course.teacher.department.department_name
        if (label != ""):
            if (label == test.timenode):
                result.append(course)
        else:
            result.append(course)
    return render(request, 'Myauth/student_test.html', {'courselist': result})


def select_teacher_test(request):
    label = request.GET.get('testnum', '')
    teacher = TeacherInformation.objects.get(teacher=User.objects.get(name=request.session.get('username')))
    courselist = CourseInformation.objects.filter(teacher=teacher)
    result = []
    for course in courselist:
        try:
            test = Course_to_test.objects.filter(course=course)[0].test
        except:
            continue
        course.starttime = test.starttime
        course.endtime = test.endtime
        course.course_label = course.get_course_label_display()
        course.department = teacher.department.department_name
        if (course.course_type):
            course.course_class = "选修没有班级"
        else:
            course.course_class = ','.join(
                [c_to_c.clbum.class_name for c_to_c in Course_to_clbum.objects.filter(course=course)])
        course.course_type = {1: "选修", 0: "必修"}[course.course_type]
        course.teachername = course.teacher.name
        if (label != ""):
            if (label == test.timenode):
                result.append(course)
        else:
            result.append(course)
    return render(request, 'Myauth/teacher_test.html', {'courselist': result})


def addclbumindex(request):
    clbumlist = Clbum.objects.all()
    course = CourseInformation.objects.get(course_id=request.GET.get('id'))
    verifylist = [c.clbum.class_name for c in Course_to_clbum.objects.filter(course=course)]
    resultlist = []
    for clbum in clbumlist:
        if clbum.class_name not in verifylist:
            resultlist.append(clbum)
    return render(request, 'Myauth/addclbumindex.html', {'clbumlist': resultlist, 'course_id': request.GET.get('id')})


def addclbum(request):
    try:
        content = request.GET.get('content').split(',')[:-1]
        course = CourseInformation.objects.get(course_id=request.GET.get('course_id'))
        for class_name in content:
            clbum = Clbum.objects.get(class_name=class_name)
            Course_to_clbum(clbum=clbum, course=course).save()
        return HttpResponse("1")
    except:
        return HttpResponse("0")


def insertSoreIndex(request):
    return render(request, 'Myauth/insertsoreindex.html')


def insertSore(request):
    datalist = json.loads(request.POST.get("data"))
    resultlist = []
    for data in datalist:
        course = CourseInformation.objects.get(course_id=data['course'])
        student = StudentInformation.objects.get(student=User.objects.get(name=data['student']))
        if (len([c for c in Score.objects.filter(course=course).filter(student=student)]) != 0):
            data = '课程号:{0}，姓名:{1},已经存在，不能添加'.format(course.course_name, student.name)
            resultlist.append(data)
            continue
        Score(course=course, student=student, score=float(data['score'])).save()
    return JsonResponse({'datalist': ';'.join(resultlist) if len(resultlist) != 0 else '1'})


def selectCourseIndex(request):
    courselist = CourseInformation.objects.filter(
        teacher=TeacherInformation.objects.get(teacher=User.objects.get(name=request.session.get('username'))))
    return render(request, 'Myauth/selectcourseindex.html', {'courselist': courselist})


def selectScoreIndex(request):
    course = CourseInformation.objects.get(course_id=request.GET.get('type'))
    resultlist = []
    c_to_s = Score.objects.filter(course=course)
    for c in c_to_s:
        data = {}
        data['course_name'] = course.course_name
        data['course_type'] = {1: "选修", 0: "必修"}[course.course_type]
        data['course_id'] = course.course_id
        data['student_id'] = c.student.student.name
        data['student_name'] = c.student.name
        data['score'] = c.score
        data['class_name'] = c.student.clbum.class_name
        resultlist.append(data)
    return render(request, 'Myauth/selectsoreindex.html',
                  {'datalist': resultlist, 'course_id': request.GET.get('type')})


def modifyScore(request):
    try:
        score = \
        Score.objects.filter(course=CourseInformation.objects.get(course_id=request.GET.get('course_id'))).filter(
            student=StudentInformation.objects.get(student=User.objects.get(name=request.GET.get('student_id'))))[0]
        score.score = float(request.GET.get('score'))
        score.save()
        return HttpResponse('1')
    except:
        return HttpResponse('0')


def selectStudentScoreIndex(request):
    student = StudentInformation.objects.get(student=User.objects.get(name=request.session.get('username')))
    scorelist = Score.objects.filter(student=student)
    datalist = []
    for score in scorelist:
        score.class_name = student.clbum.class_name
        score.teacher_name = score.course.teacher.name
        score.course_id = score.course.course_id
        score.course_name = score.course.course_name
        score.course_type = {1: "选修", 0: "必修"}[score.course.course_type]
        datalist.append(score)
    return render(request, 'Myauth/selectstudentscore.html', {'datalist': datalist})


def analyseScoreIndex(request):
    courselist = [course for course in CourseInformation.objects.filter(
        teacher=TeacherInformation.objects.get(teacher=User.objects.get(name=request.session.get('username'))))]
    datalist = []
    max_list = []
    min_list = []
    mean_list = []
    name_list = []
    bar = Bar()
    for course in courselist:
        try:
            course.course_type = {1: "选修", 0: "必修"}[course.course_type]
            course.maxscore = np.max(np.array(list(meanFunction(course.course_id, 'max').values())))
            course.minscore = np.min(np.array(list(meanFunction(course.course_id, 'min').values())))
            course.meanscore = round(np.mean(np.array(list(meanFunction(course.course_id, 'mean').values()))), 3)
            max_list.append(course.maxscore)
            min_list.append(course.minscore)
            mean_list.append(course.meanscore)
            name_list.append(course.course_name)
            if (course.meanscore / 100 >= 0.01 and course.meanscore / 100 < 0.29):
                course.scorelabel = "困难"
            elif (course.meanscore / 100 >= 0.30 and course.meanscore / 100 <= 0.69):
                course.scorelabel = "中等"
            else:
                course.scorelabel = "容易"
            datalist.append(course)
        except:
            continue
    bar.add_xaxis(name_list)
    bar.add_yaxis("最高分", max_list)
    bar.add_yaxis("最低分", min_list)
    bar.add_yaxis("平均分", mean_list)
    bar.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    bar.set_global_opts(
        title_opts=opts.TitleOpts(title="最高分、最低分、平均分"),
        datazoom_opts=opts.DataZoomOpts(),  # 显示水平方向的缩放滑块
        yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(formatter="{value}分")),
    )
    bar.render('./templates/Myauth/collectbar.html')
    return render(request, 'Myauth/analysescore.html', {'datalist': datalist})


def collectBar(request):
    return render(request, 'Myauth/collectbar.html')


def getStudentSort(student):
    courselist = [course.course for course in Course_to_student.objects.filter(student=student)] + [course.course for
                                                                                                    course in
                                                                                                    Course_to_clbum.objects.filter(
                                                                                                        clbum=student.clbum)]
    datalist = []
    countscore = []
    for course in courselist:
        try:
            course.score = Score.objects.filter(student=student).filter(course=course)[0].score
        except:
            continue
        if course.score >= 95:
            count = 4.5
        elif (course.score >= 90 and course.score < 95):
            count = 4
        elif (course.score >= 85 and course.score < 90):
            count = 3.5
        elif (course.score >= 80 and course.score < 85):
            count = 3
        elif (course.score >= 75 and course.score < 80):
            count = 2.5
        elif (course.score >= 70 and course.score < 75):
            count = 2
        elif (course.score >= 65 and course.score < 70):
            count = 1.5
        elif (course.score >= 60 and course.score < 65):
            count = 1
        else:
            count = 0
        countscore.append({course.credit: count})
        course.teacher_name = course.teacher.name
        course.clbum = student.clbum.class_name
        course.sortscore = getSortScore(course.score, course.course_id)
        course.nicescore = str(round(getNiceScore(course.course_id, 80) * 100, 3)) + '%'
        course.goodscore = str(round(getNiceScore(course.course_id, 60) * 100, 3)) + '%'
        course.meanscore = round(getMeanScore(course.course_id), 3)
        course.maxscore = getMaxScore(course.course_id)
        course.minscore = getMinScore(course.course_id)
        course.varscore = getVarScore(course.course_id)
        course.stdscore = getStdScore(course.course_id)
        course.changescore = getChangeScore(course.course_id)
        course.course_type = {1: "选修", 0: "必修"}[course.course_type]
        datalist.append(course)
    result = 0
    resultde = 0
    for c in countscore:
        result += float(list(c.keys())[0]) * float(list(c.values())[0])
        resultde += float(list(c.keys())[0])
    return datalist, result, resultde


def analyStudentseScoreIndex(request):
    student = StudentInformation.objects.get(student=User.objects.get(name=request.session.get('username')))
    datalist, result, resultde = getStudentSort(student)
    returnlist = []
    for s in StudentInformation.objects.filter(clbum=student.clbum):
        try:
            data, r, d = getStudentSort(s)
            s.comment = r / d
            returnlist.append(s)
        except:
            continue
    r_list = [r.comment for r in returnlist]
    r_list.sort(reverse=True)
    sortnum = r_list.index(result / resultde) + 1
    return render(request, 'Myauth/analysestudentscore.html',
                  {'datalist': datalist, 'course_score': round(result / resultde, 3), 'sortnum': sortnum,
                   'returnlist': returnlist})


def getSortScore(score, course_id):
    course = CourseInformation.objects.get(course_id=course_id)
    scorelist = [score.score for score in Score.objects.filter(course=course)]
    scorelist.sort(reverse=True)
    return scorelist.index(score) + 1


def getNiceScore(course_id, label):
    course = CourseInformation.objects.get(course_id=course_id)
    scorelist = np.array([score.score for score in Score.objects.filter(course=course)])
    middlelist = scorelist >= label
    result = scorelist[middlelist].shape[0] / scorelist.shape[0]
    return result


def getMeanScore(course_id):
    course = CourseInformation.objects.get(course_id=course_id)
    scorelist = np.array([score.score for score in Score.objects.filter(course=course)])
    return np.mean(scorelist)


def getMaxScore(course_id):
    course = CourseInformation.objects.get(course_id=course_id)
    scorelist = np.array([score.score for score in Score.objects.filter(course=course)])
    return np.max(scorelist)


def getMinScore(course_id):
    course = CourseInformation.objects.get(course_id=course_id)
    scorelist = np.array([score.score for score in Score.objects.filter(course=course)])
    return np.min(scorelist)


def getVarScore(course_id):
    course = CourseInformation.objects.get(course_id=course_id)
    scorelist = np.array([score.score for score in Score.objects.filter(course=course)])
    return round(np.var(scorelist), 3)


def getStdScore(course_id):
    course = CourseInformation.objects.get(course_id=course_id)
    scorelist = np.array([score.score for score in Score.objects.filter(course=course)])
    return round(np.std(scorelist), 3)


def getChangeScore(course_id):
    course = CourseInformation.objects.get(course_id=course_id)
    scorelist = np.array([score.score for score in Score.objects.filter(course=course)])
    return round(np.std(scorelist) / np.mean(scorelist), 3)


def meanScore(request):
    meanscore = meanFunction(request.GET.get('type'), 'mean')
    bar = Bar()
    bar.add_xaxis(list(meanscore.keys()))
    bar.add_yaxis("平均分", list(meanscore.values()))
    bar.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    bar.set_global_opts(
        title_opts=opts.TitleOpts(title="平均分"),
        datazoom_opts=opts.DataZoomOpts(),  # 显示水平方向的缩放滑块
        yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(formatter="{value}分")),
    )
    bar.render('./templates/Myauth/mean.html')
    return render(request, 'Myauth/mean.html')


def minScore(request):
    coursetype = meanFunction(request.GET.get('type'), 'min')
    bar = Bar()
    bar.add_xaxis(list(coursetype.keys()))
    bar.add_yaxis("最小值", list(coursetype.values()))
    bar.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    bar.set_global_opts(
        title_opts=opts.TitleOpts(title="最小值"),
        datazoom_opts=opts.DataZoomOpts(),  # 显示水平方向的缩放滑块
        yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(formatter="{value}分")),
    )
    bar.render('./templates/Myauth/min.html')
    return render(request, 'Myauth/min.html')


def maxScore(request):
    coursetype = meanFunction(request.GET.get('type'), 'max')
    bar = Bar()
    bar.add_xaxis(list(coursetype.keys()))
    bar.add_yaxis("最大值", list(coursetype.values()))
    bar.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    bar.set_global_opts(
        title_opts=opts.TitleOpts(title="最大值"),
        datazoom_opts=opts.DataZoomOpts(),  # 显示水平方向的缩放滑块
        yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(formatter="{value}分")),
    )
    bar.render('./templates/Myauth/max.html')
    return render(request, 'Myauth/max.html')


def varScore(request):
    coursetype = meanFunction(request.GET.get('type'), 'var')
    bar = Bar()
    bar.add_xaxis(list(coursetype.keys()))
    bar.add_yaxis("方差", list(coursetype.values()))
    bar.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    bar.set_global_opts(
        title_opts=opts.TitleOpts(title="方差"),
        datazoom_opts=opts.DataZoomOpts(),  # 显示水平方向的缩放滑块
        yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(formatter="{value}")),
    )
    bar.render('./templates/Myauth/var.html')
    return render(request, 'Myauth/var.html')


def stdScore(request):
    coursetype = meanFunction(request.GET.get('type'), 'std')
    bar = Bar()
    bar.add_xaxis(list(coursetype.keys()))
    bar.add_yaxis("标准差", list(coursetype.values()))
    bar.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    bar.set_global_opts(
        title_opts=opts.TitleOpts(title="标准差"),
        datazoom_opts=opts.DataZoomOpts(),  # 显示水平方向的缩放滑块
        yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(formatter="{value}")),
    )
    bar.render('./templates/Myauth/std.html')
    return render(request, 'Myauth/std.html')


def niceScore(request):
    page = Page()
    nicedict = meanFunction(request.GET.get('type'), 'nice')
    gooddict = meanFunction(request.GET.get('type'), 'good')
    goodperson = meanFunction(request.GET.get('type'), 'goodperson')
    minscoredict = meanFunction(request.GET.get('type'), 'minscore')
    # personcount = len(Score.objects.filter(course=CourseInformation.objects.get(course_id=request.GET.get('type'))))

    # goodperson = [int(score*personcount) for score in list(gooddict.values())]
    line = Line()
    line.add_xaxis(list(nicedict.keys()))
    line.add_yaxis("优生率", [round(r * 100, 3) for r in list(nicedict.values())], is_smooth=True)
    line.add_yaxis("及格率", [round(r * 100, 3) for r in list(gooddict.values())], is_smooth=True)
    line.add_yaxis("低分率", [round(r * 100, 3) for r in list(minscoredict.values())], is_smooth=True)
    bar = Bar(init_opts=opts.InitOpts(width="500px", height="500px"))
    bar.add_xaxis(list(nicedict.keys()))
    bar.add_yaxis("及格人数", list(goodperson.values()))
    bar.set_global_opts(
        title_opts=opts.TitleOpts(title="及格人数"),
        datazoom_opts=opts.DataZoomOpts(),  # 显示水平方向的缩放滑块
        yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(formatter="{value}人")),
    )
    line.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    line.set_global_opts(
        title_opts=opts.TitleOpts(title="成绩情况图"),
        yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(formatter="{value}%")),
    )
    page.add(line)
    page.add(bar)
    # line.overlap(bar)
    page.render('./templates/Myauth/nice.html')
    return HttpResponse("1")


def courseCollect(request):
    return render(request, 'Myauth/nice.html')


def manyCompare(request):
    course_list = [CourseInformation.objects.get(course_id=course_id) for course_id in request.GET.getlist('id_list[]')]
    good_list = [round(getNiceScore(course.course_id, 60), 3) for course in course_list]
    # label_list = [{"容易":1,"中等":2,"困难":3}[label] for label in request.GET.getlist('label_list[]')]
    sum_list = []
    mean_list = []
    for course in course_list:
        sum_list.append(np.sum(np.array([score.score for score in Score.objects.filter(course=course)])))
    for course in course_list:
        mean_list.append(np.mean(np.array([score.score for score in Score.objects.filter(course=course)])))
    label_list = (np.array(mean_list) / 100).tolist()
    result_list = []
    for index in range(len(good_list)):
        result_list.append(round(label_list[index] / good_list[index], 3))
    course_list = [course.course_name for course in course_list]
    klist = copy.copy(result_list)
    llabel = copy.copy(course_list)
    output = ""
    for _ in range(len(llabel)):
        index = klist.index(max(klist))
        output += llabel[index] + ">"
        del llabel[index]
        del klist[index]
    print(result_list)
    page = Page()
    bar = Bar(init_opts=opts.InitOpts(width="500px", height="700px"))
    bar.add_xaxis(course_list)
    bar.add_yaxis("及格率", good_list)
    line = Bar(init_opts=opts.InitOpts(width="500px", height="700px"))
    line.add_xaxis(course_list)
    line.add_yaxis("难度系数", label_list)
    line.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    line.set_global_opts(
        title_opts=opts.TitleOpts(title="难度系数"),
        yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(formatter="{value}")),
    )
    bar.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    bar.set_global_opts(
        title_opts=opts.TitleOpts(title="综合比较\n" + output[:-1]),
        yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(formatter="{value}")),
    )
    # bar.overlap(line)
    page.add(bar)
    page.add(line)
    page.render('./templates/Myauth/manycompareindex.html')
    return HttpResponse("1")


def manyCompareIndex(request):
    return render(request, 'Myauth/manycompareindex.html')


def goodScore(request):
    coursetype = meanFunction(request.GET.get('type'), 'good')
    bar = Bar()
    bar.add_xaxis(list(coursetype.keys()))
    bar.add_yaxis("及格率", [round(r * 100, 3) for r in list(coursetype.values())])
    bar.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    bar.set_global_opts(
        title_opts=opts.TitleOpts(title="及格率"),
        datazoom_opts=opts.DataZoomOpts(),  # 显示水平方向的缩放滑块
        yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(formatter="{value}")),
    )
    bar.render('./templates/Myauth/good.html')
    return render(request, 'Myauth/good.html')


def changeScore(request):
    coursetype = meanFunction(request.GET.get('type'), 'change')
    bar = Bar()
    bar.add_xaxis(list(coursetype.keys()))
    bar.add_yaxis("变异系数", list(coursetype.values()))
    bar.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    bar.set_global_opts(
        title_opts=opts.TitleOpts(title="变异系数"),
        datazoom_opts=opts.DataZoomOpts(),  # 显示水平方向的缩放滑块
        yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(formatter="{value}")),
    )
    bar.render('./templates/Myauth/change.html')
    return render(request, 'Myauth/change.html')


def tScore(request):
    coursetype = meanFunction(request.GET.get('type'), 'tscore')
    keylist = list(coursetype.keys())
    label = list(coursetype.values())
    klist = copy.copy(keylist)
    llabel = copy.copy(label)
    output = ""
    for _ in range(len(llabel)):
        index = llabel.index(max(llabel))
        output += klist[index] + ">"
        del llabel[index]
        del klist[index]
    bar = Bar()
    bar.add_xaxis(list(coursetype.keys()))
    bar.add_yaxis("T分数", list(coursetype.values()))
    bar.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    bar.set_global_opts(
        title_opts=opts.TitleOpts(title="按照T分数计算，各班级表现排名：\n{}".format(output[:-1])),
        datazoom_opts=opts.DataZoomOpts(),  # 显示水平方向的缩放滑块
        yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(formatter="{value}分")),
    )
    bar.render('./templates/Myauth/tscore.html')
    return render(request, 'Myauth/tscore.html')


def meanFunction(course_type, computetype):
    coursetype = course_type
    scoredata = []
    meandata = {}
    course = CourseInformation.objects.get(course_id=coursetype)
    if (course.course_type):
        clbumlist = Clbum.objects.all()
    else:
        clbumlist = Course_to_clbum.objects.filter(course=course)
    for clbum in clbumlist:
        if (course.course_type == 0):
            clbum = clbum.clbum
        meandata[clbum.class_name] = []
        for student in StudentInformation.objects.filter(clbum=clbum):
            if (course.course_type):
                if (student not in [c_to_s.student for c_to_s in Course_to_student.objects.filter(course=course)]):
                    continue
            if (len(Score.objects.filter(course=course).filter(student=student)) == 0):
                continue
            score = Score.objects.filter(course=course).filter(student=student)[0].score
            meandata[clbum.class_name].append(score)
        if (computetype == 'mean'):
            meandata[clbum.class_name] = np.mean(np.array(meandata[clbum.class_name]))
        elif (computetype == 'min'):
            try:
                meandata[clbum.class_name] = np.min(np.array(meandata[clbum.class_name]))
            except:
                continue
        elif (computetype == 'layer'):
            try:
                scoredata += meandata[clbum.class_name]
            except:
                continue
        elif (computetype == 'max'):
            try:
                meandata[clbum.class_name] = np.max(np.array(meandata[clbum.class_name]))
            except:
                continue
        elif (computetype == 'var'):
            try:
                meandata[clbum.class_name] = np.var(np.array(meandata[clbum.class_name]))
            except:
                continue
        elif (computetype == 'std'):
            try:
                meandata[clbum.class_name] = np.std(np.array(meandata[clbum.class_name]))
            except:
                continue
        elif (computetype == 'change'):
            try:
                meandata[clbum.class_name] = np.mean(np.array(meandata[clbum.class_name])) / np.std(
                    np.array(meandata[clbum.class_name]))
            except:
                continue
        elif (computetype == 'tscore'):
            try:
                meandata[clbum.class_name] = np.sum(
                    np.array(meandata[clbum.class_name]) - np.mean(np.array(meandata[clbum.class_name])) / np.std(
                        np.array(meandata[clbum.class_name]))) * 10 + 60
            except:
                continue
        elif (computetype == 'nice'):
            try:
                meandata[clbum.class_name] = np.array(meandata[clbum.class_name])
                middle = meandata[clbum.class_name] >= 80
                meandata[clbum.class_name] = meandata[clbum.class_name][middle].shape[0] / \
                                             meandata[clbum.class_name].shape[0]
            except:
                continue
        elif (computetype == 'good'):
            try:
                meandata[clbum.class_name] = np.array(meandata[clbum.class_name])
                middle = meandata[clbum.class_name] >= 60
                meandata[clbum.class_name] = meandata[clbum.class_name][middle].shape[0] / \
                                             meandata[clbum.class_name].shape[0]
            except:
                continue
        elif (computetype == 'goodperson'):
            try:
                meandata[clbum.class_name] = np.array(meandata[clbum.class_name])
                middle = meandata[clbum.class_name] >= 60
                meandata[clbum.class_name] = meandata[clbum.class_name][middle].shape[0]
            except:
                continue
        elif (computetype == 'minscore'):
            try:
                meandata[clbum.class_name] = np.array(meandata[clbum.class_name])
                middle = meandata[clbum.class_name] < 40
                meandata[clbum.class_name] = meandata[clbum.class_name][middle].shape[0] / \
                                             meandata[clbum.class_name].shape[0]
            except:
                continue
    resultdata = {}
    for k, v in meandata.items():
        try:
            if (math.isnan(v)):
                continue
        except:
            continue
        resultdata[k] = v
    if (computetype == 'layer'):
        result = {}
        data = np.array(scoredata)
        middle = data >= 95
        result['95以上'] = data[middle].shape[0]
        result['90到95'] = data[np.where((data >= 90) & (data < 95))].shape[0]
        result['85到90'] = data[np.where((data >= 85) & (data < 90))].shape[0]
        result['80到85'] = data[np.where((data >= 80) & (data < 85))].shape[0]
        result['75到80'] = data[np.where((data >= 75) & (data < 80))].shape[0]
        result['70到75'] = data[np.where((data >= 70) & (data < 75))].shape[0]
        result['65到70'] = data[np.where((data >= 65) & (data < 70))].shape[0]
        result['60到65'] = data[np.where((data >= 60) & (data < 65))].shape[0]
        result['60以下'] = data[np.where(data < 60)].shape[0]
        return result
    return resultdata


def getScoreLayer(scoredata):
    result = {}
    data = np.array(scoredata)
    middle = data >= 95
    result['95以上'] = data[middle].shape[0]
    result['90到95'] = data[np.where((data >= 90) & (data < 95))].shape[0]
    result['85到90'] = data[np.where((data >= 85) & (data < 90))].shape[0]
    result['80到85'] = data[np.where((data >= 80) & (data < 85))].shape[0]
    result['75到80'] = data[np.where((data >= 75) & (data < 80))].shape[0]
    result['70到75'] = data[np.where((data >= 70) & (data < 75))].shape[0]
    result['65到70'] = data[np.where((data >= 65) & (data < 70))].shape[0]
    result['60到65'] = data[np.where((data >= 60) & (data < 65))].shape[0]
    result['60以下'] = data[np.where(data < 60)].shape[0]
    return result


def scoreLayer(request):
    page = Page()
    course = CourseInformation.objects.get(course_id=request.GET.get('type'))
    coursetype = meanFunction(request.GET.get('type'), 'layer')
    line = (
        Line()  # 生成line类型图表
            .add_xaxis(list(coursetype.keys()))  # 添加x轴，Faker.choose()是使用faker的随机数据生成x轴标签
            .add_yaxis("人数", list(coursetype.values()), is_smooth=True)  # 添加y轴，Faker.values()是使用faker的随机数据生成y轴数值
            .set_global_opts(
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(font_size=10, interval=0)),
            title_opts=opts.TitleOpts(
                title=CourseInformation.objects.get(course_id=request.GET.get('type')).course_name + "成绩分布图"),
            # datazoom_opts=opts.DataZoomOpts(),  # 显示水平方向的缩放滑块
            yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(formatter="{value}人")),
        )
    )
    page.add(line)
    studentlist = [score.student for score in Score.objects.filter(course=course)]
    clbumlist = list(set([student.clbum for student in studentlist]))
    for clbum in clbumlist:
        scorelist = []
        for student in StudentInformation.objects.filter(clbum=clbum):
            try:
                score = Score.objects.filter(course=course).filter(student=student)[0].score
                scorelist.append(score)
            except:
                continue
        result = getScoreLayer(scorelist)
        line = (
            Line()  # 生成line类型图表
                .add_xaxis(list(result.keys()))  # 添加x轴，Faker.choose()是使用faker的随机数据生成x轴标签
                .add_yaxis("人数", list(result.values()),
                           is_smooth=True)  # 添加y轴，Faker.values()是使用faker的随机数据生成y轴数值
                .set_global_opts(
                xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(font_size=10, interval=0)),
                title_opts=opts.TitleOpts(title=CourseInformation.objects.get(
                    course_id=request.GET.get('type')).course_name + "班级是：" + clbum.class_name + "成绩分布图"),
                # datazoom_opts=opts.DataZoomOpts(),  # 显示水平方向的缩放滑块
                yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(formatter="{value}人")),
            )
        )
        page.add(line)
    page.render('./templates/Myauth/scorelayer.html')
    return render(request, 'Myauth/scorelayer.html')


def searchScore(request):
    try:
        student = StudentInformation.objects.get(student=User.objects.get(name=request.GET.get('username')))
        course = CourseInformation.objects.get(course_id=request.GET.get('course_id'))
        c = Score.objects.filter(course=course).filter(student=student)[0]
        data = {}
        data['course_name'] = course.course_name
        data['course_type'] = {1: "选修", 0: "必修"}[course.course_type]
        data['course_id'] = course.course_id
        data['student_id'] = c.student.student.name
        data['student_name'] = c.student.name
        data['score'] = c.score
        data['class_name'] = c.student.clbum.class_name
        return JsonResponse({'data': data})
    except Exception as e:
        print(e)
        return HttpResponse('0')


def compareScore(request):
    course_list = [CourseInformation.objects.get(course_id=course_id).course_name for course_id in
                   request.GET.getlist('id_list[]')]
    score_list = [float(score) for score in request.GET.getlist('score_list[]')]

    changescore_list = [float(score) for score in request.GET.getlist('changescore_list[]')]
    sumchange = np.sum(np.array(changescore_list))
    changescore_list = [score / sumchange for score in changescore_list]
    result = {}
    for index, course in enumerate(course_list):
        result[course] = score_list[index] * changescore_list[index]

    klist = copy.copy(list(result.keys()))
    llabel = copy.copy(list(result.values()))
    output = ""
    for _ in range(len(llabel)):
        index = llabel.index(max(llabel))
        output += klist[index] + ">"
        del llabel[index]
        del klist[index]

    bar = Bar(init_opts=opts.InitOpts(width="500px", height="700px"))
    bar.add_xaxis(list(result.keys()))
    bar.add_yaxis("变异系数加权比较", list(result.values()))
    bar.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    bar.set_global_opts(
        title_opts=opts.TitleOpts(title="成绩比较如下：\n{}".format(output[:-1])),
        datazoom_opts=opts.DataZoomOpts(),  # 显示水平方向的缩放滑块
        yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(formatter="{value}分")),
    )
    bar.render('./templates/Myauth/comparescore.html')
    return HttpResponse("1")


def compareIndex(request):
    return render(request, 'Myauth/comparescore.html')
