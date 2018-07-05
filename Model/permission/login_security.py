#coding = utf-8
from MES import session
from Model.permission.permission_modules import User


def security(security_status):
    if security_status == '':
        return {'status':False, 'msg': '请输入图形验证码'}
    elif security_status == False:
        return {'status': False, 'msg': '验证码不匹配'}
    return {'status': True, 'msg': '验证码匹配成功'}

def login_handler(job_number, password):
    job_number = User.by_login_id(job_number)
    if job_number == job_number:
        return {'status': False, 'msg': '用户已存在'}
    if job_number =='' or password =='' :
        return {'status': False, 'msg': '账号和密码不能为空'}
    user = User.by_login_id(job_number)
    if  user and user.auth_password(password):
        return {'status': True, 'msg': '登录成功'}
    return {'status': False, 'msg': '账号或密码输入错误'}


def register_handler(user_name, job_number, password1, password2, email, tel):
    if password1 != password2:
        return {'status': False, 'msg': '两次输入的密码不匹配'}

    user = User.by_name(user_name)
    if user is not None:
        return {'status': False, 'msg': "用户已存在!"}

    user = User()
    user.name = user_name
    user.password = password2
    user.job_number = job_number
    user.mobile = tel
    user.email = email
    session.add(user)
    session.commit()
    return {'status': True}













