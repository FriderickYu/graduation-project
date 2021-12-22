from django.contrib import admin
from .models import User, StudentInformation, TeacherInformation, ManagerInformation, CourseInformation


# Register your models here.


# class MoreTwoInfo(admin.StackedInline):
#     model = StudentInformation
#     list_display = ('name', 'birthday', 'sex', 'email', 'phone', 'admission_date', 'clbum', 'grade', 'department')
#     fields = ('name', 'birthday', 'sex', 'email', 'phone', 'admission_date', 'clbum', 'grade', 'department')
#     search_fields = ['name']  # 搜索栏
#     list_filter = ['name']  # 右侧的过滤器


class MoreThreeInfo(admin.StackedInline):
    model = TeacherInformation
    list_display = ('name', 'birthday', 'sex', 'email', 'phone', 'admission_date', 'department', 'rank')
    fields = ('name', 'birthday', 'sex', 'email', 'phone', 'admission_date', 'department', 'rank')
    search_fields = ['name']  # 搜索栏
    list_filter = ['name']  # 右侧的过滤器


class MoreInfo(admin.StackedInline):
    model = ManagerInformation
    list_display = ('name', 'birthday', 'sex', 'email', 'phone')
    fields = ('name', 'birthday', 'sex', 'email', 'phone')
    search_fields = ['name']  # 搜索栏
    list_filter = ['name']  # 右侧的过滤器


@admin.register(User)
class Userinfo(admin.ModelAdmin):
    list_display = ('user_type', 'name', 'password')
    fields = ('user_type', 'name', 'password')
    search_fields = ['user_type', 'name']  # 搜索栏
    inlines = [MoreInfo, MoreThreeInfo]


# @admin.register(CourseInformation)
# class CourseInformationAdmin(admin.ModelAdmin):
#     list_display = ('course_id', 'course_name', 'course_label',
#                     'course_room', 'credit', 'course_class')
#     fields = ('course_id', 'course_name', 'course_time_begin', 'course_time_end',
#               'course_room', 'credit', 'course_class')
#     search_fields = ['course_id', 'course_name']
#     list_filter = ['course_name']
