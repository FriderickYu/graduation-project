import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart


class EmailManage(object):
    def __init__(self, sender_mail='15545567555@163.com', receivers=[], username="", sender_pass='QUMLDTVSAHWGKTPF'):
        self.sender_mail = sender_mail
        self.sender_pass = sender_pass
        self.receivers = receivers  # 接收邮件，可设置为QQ邮箱,网易邮箱,outlook等
        self.username = username

    def sendEmail(self):
        # 创建用于发送带有附件文件的邮件对象
        # related: 邮件内容的格式，采用内嵌的形式进行展示。
        # MIMEMultipart：多形式组合，可包含文本和附件
        # MIMEText：内容为纯文本或HTML页面
        message = MIMEMultipart('related') # 构造一个MIMEMultipart对象代表邮件本身。related 表示使用内嵌资源的形式 将邮件发送给对方
        msg = MIMEText('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Title</title>
        </head>
        <body>
        <div><a href="http://127.0.0.1:8000/reset/?username={}">http://127.0.0.1:8000/resetpwd/</a></div>
        </body>
        </html>
        '''.format(self.username), 'html', 'utf-8')

        message.attach(msg)
        # 从哪来，到哪去，内容是啥
        message['From'] = self.sender_mail
        message['to'] = self.receivers[0]
        message['Subject'] = Header("重置密码", 'utf-8').encode()

        # 绑定网易服务器，默认25号端口
        sftp_obj = smtplib.SMTP('smtp.163.com', 25)
        # 网易登录
        sftp_obj.login(self.sender_mail, self.sender_pass)
        # 三个参数分别是：发件人邮箱账号，收件人邮箱账号，发送的邮件体
        sftp_obj.sendmail(self.sender_mail, self.receivers, message.as_string())
        sftp_obj.quit()
