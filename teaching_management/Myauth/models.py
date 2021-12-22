from django.db import models


# from django.contrib.auth.models import User


# Create your models here.
class User(models.Model):
    manager = 0
    student = 1
    teacher = 2
    Identity = (
        (manager, '管理员'),
        (student, '学生'),
        (teacher, '老师'),
    )
    user_type = models.PositiveIntegerField(default=0, choices=Identity, verbose_name='用户身份')
    name = models.CharField(max_length=50, primary_key=True, verbose_name='账号')
    password = models.CharField(max_length=50, verbose_name='密码')

    class Meta:
        verbose_name = verbose_name_plural = '用户信息表'

    def __str__(self):
        return self.name


class Department(models.Model):
    department_name = models.CharField(max_length=20,primary_key=True,verbose_name="班级名字")


class Clbum(models.Model):
    class_name = models.CharField(max_length=20,primary_key=True,verbose_name="班级名字")
    department = models.ForeignKey('Department', on_delete=models.CASCADE)


class StudentInformation(models.Model):
    # 外键
    Gender = (
        ('男', '男'),
        ('女', '女'),
    )

    Department = (
        ('计算机学院', '计算机学院'),
        ('理学院', '理学院'),
        ('文学院', '文学院'),
        ('商学院', '商学院'),
    )
    student = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    name = models.CharField(blank=False, max_length=50, verbose_name='学生姓名')
    birthday = models.DateField(blank=False, verbose_name='出生日期')
    sex = models.CharField(default='男', max_length=10, choices=Gender, verbose_name="性别")  # 4/5改

    email = models.EmailField(blank=False, verbose_name='邮箱')
    phone = models.CharField(blank=False, max_length=11, verbose_name='手机号码')
    admission_date = models.DateField(blank=False, verbose_name='入学时间')
    clbum = models.ForeignKey('Clbum', on_delete=models.CASCADE)

    class Meta:
        verbose_name = verbose_name_plural = '学生信息表'

    def __str__(self):
        return self.name


class TeacherInformation(models.Model):
    Gender = (
        ('男', '男'),
        ('女', '女'),
    )

    Rank = (
        ('教授', '教授'),
        ('副教授', '副教授'),
        ('讲师', '讲师'),
    )

    teacher = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    name = models.CharField(blank=False, max_length=50, verbose_name='教师姓名')
    birthday = models.DateField(blank=False, verbose_name='出生日期')
    sex = models.CharField(default='男', max_length=10, choices=Gender, verbose_name="性别")  # 4/5改

    email = models.EmailField(blank=False, verbose_name='邮箱')
    phone = models.CharField(blank=False, max_length=11, verbose_name='手机号码')
    admission_date = models.DateField(blank=False, verbose_name='入职时间')
    department = models.ForeignKey('department', on_delete=models.CASCADE)  # 4/5改
    rank = models.CharField(default='教授', max_length=30, choices=Rank, verbose_name='教师职称')  # 4/5改

    class Meta:
        verbose_name = verbose_name_plural = '教师信息表'

    def __str__(self):
        return self.name


class ManagerInformation(models.Model):
    Gender = (
        ('男', '男'),
        ('女', '女'),
    )

    manager = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    name = models.CharField(blank=False, max_length=50, verbose_name='教师姓名')
    birthday = models.DateField(blank=False, verbose_name='出生日期')
    sex = models.CharField(default='男', max_length=10, choices=Gender, verbose_name="性别")  # 4/5改

    email = models.EmailField(blank=False, verbose_name='邮箱')
    phone = models.CharField(blank=False, max_length=11, verbose_name='手机号码')

    class Meta:
        verbose_name = verbose_name_plural = '管理员信息表'

    def __str__(self):
        return self.name


class CourseInformation(models.Model):
    course_id = models.CharField(blank=False, max_length=10, primary_key=True, verbose_name='课程号')
    teacher = models.ForeignKey('TeacherInformation', on_delete=models.CASCADE)
    course_name = models.CharField(blank=False, max_length=100, verbose_name='课程名称')
    course_room = models.CharField(blank=False, max_length=50, verbose_name='上课教室')
    credit = models.PositiveIntegerField(blank=False, verbose_name='学分')
    course_type = models.BooleanField(verbose_name='课程类型')
    Identity = (
        (101, '周一08:00至08:45'),
        (102, '周一08:55至09:40'),
        (103, '周一10:10至10:55'),
        (104, '周一11:05至11:50'),
        (105, '周一14:00至14:45'),
        (106, '周一14:55至15:40'),
        (107, '周一16:10至16:55'),
        (108, '周一17:05至17:50'),
        (109, '周一18:30至19:15'),
        (110, '周一19:25至20:10'),
        (111, '周一20:20至21:05'),
        (201, '周二08:00至08:45'),
        (202, '周二08:55至09:40'),
        (203, '周二10:10至10:55'),
        (204, '周二11:05至11:50'),
        (205, '周二14:00至14:45'),
        (206, '周二14:55至15:40'),
        (207, '周二16:10至16:55'),
        (208, '周二17:05至17:50'),
        (209, '周二18:30至19:15'),
        (210, '周二19:25至20:10'),
        (211, '周二20:20至21:05'),
        (301, '周三08:00至08:45'),
        (302, '周三08:55至09:40'),
        (303, '周三10:10至10:55'),
        (304, '周三11:05至11:50'),
        (305, '周三14:00至14:45'),
        (306, '周三14:55至15:40'),
        (307, '周三16:10至16:55'),
        (308, '周三17:05至17:50'),
        (309, '周三18:30至19:15'),
        (310, '周三19:25至20:10'),
        (311, '周三20:20至21:05'),
        (401, '周四08:00至08:45'),
        (402, '周四08:55至09:40'),
        (403, '周四10:10至10:55'),
        (404, '周四11:05至11:50'),
        (405, '周四14:00至14:45'),
        (406, '周四14:55至15:40'),
        (407, '周四16:10至16:55'),
        (408, '周四17:05至17:50'),
        (409, '周四18:30至19:15'),
        (410, '周四19:25至20:10'),
        (411, '周四20:20至21:05'),
        (501, '周五08:00至08:45'),
        (502, '周五08:55至09:40'),
        (503, '周五10:10至10:55'),
        (504, '周五11:05至11:50'),
        (505, '周五14:00至14:45'),
        (506, '周五14:55至15:40'),
        (507, '周五16:10至16:55'),
        (508, '周五17:05至17:50'),
        (509, '周五18:30至19:15'),
        (510, '周五19:25至20:10'),
        (511, '周五20:20至21:05'),
        (601, '周六08:00至08:45'),
        (602, '周六08:55至09:40'),
        (603, '周六10:10至10:55'),
        (604, '周六11:05至11:50'),
        (605, '周六14:00至14:45'),
        (606, '周六14:55至15:40'),
        (607, '周六16:10至16:55'),
        (608, '周六17:05至17:50'),
        (609, '周六18:30至19:15'),
        (610, '周六19:25至20:10'),
        (611, '周六20:20至21:05'),
        (701, '周日08:00至08:45'),
        (702, '周日08:55至09:40'),
        (703, '周日10:10至10:55'),
        (704, '周日11:05至11:50'),
        (705, '周日14:00至14:45'),
        (706, '周日14:55至15:40'),
        (707, '周日16:10至16:55'),
        (708, '周日17:05至17:50'),
        (709, '周日18:30至19:15'),
        (710, '周日19:25至20:10'),
        (711, '周日20:20至21:05'),
    )
    course_label = models.PositiveIntegerField(default=0, choices=Identity, verbose_name='时间标识')

    class Meta:
        verbose_name = verbose_name_plural = '课程信息表'

    def __str__(self):
        return self.course_id


class Course_to_clbum(models.Model):
    course = models.ForeignKey('CourseInformation', on_delete=models.CASCADE)
    clbum = models.ForeignKey('Clbum', on_delete=models.CASCADE)


class Course_to_student(models.Model):
    course = models.ForeignKey('CourseInformation', on_delete=models.CASCADE)
    student = models.ForeignKey('StudentInformation', on_delete=models.CASCADE)


class Score(models.Model):
    course = models.ForeignKey('CourseInformation', on_delete=models.CASCADE)
    student = models.ForeignKey('StudentInformation', on_delete=models.CASCADE)
    score = models.FloatField()


class Test(models.Model):
    starttime = models.DateTimeField(verbose_name='考试开始时间')
    endtime = models.DateTimeField(verbose_name='考试结束时间')


class Course_to_test(models.Model):
    course = models.ForeignKey('CourseInformation', on_delete=models.CASCADE)
    test = models.ForeignKey('Test', on_delete=models.CASCADE)