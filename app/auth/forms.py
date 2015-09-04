# -*- coding: utf-8 -*-

from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(Form):
	email = StringField(u'邮箱', validators=[Required(), Length(1, 64), Email()])
	password = PasswordField(u'密码')
	remember_me = BooleanField(u'记住我')
	submit = SubmitField(u'登陆')

class RegistrationForm(Form):
	email = StringField(u'邮箱', validators=[Required(), Length(1, 64), Email()])
	username = StringField(u'用户名', validators=[
		Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 
											u'用户名必须字包含字母、数组、下划线和点号')])
	password = PasswordField(u'密码', validators=[
		Required(), EqualTo('password2', message=u'两次输入的密码必须相同')])
	password2 = PasswordField(u'确认密码', validators=[Required()])
	submit = SubmitField(u'注册')

	def validate_email(self, field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError(u'邮箱已经被注册了')
	def validate_username(self, field):
		if User.query.filter_by(username=field.data).first():
			raise ValidationError(u'用户名已被使用')

class ChangePassForm(Form):
	old_pass = PasswordField(u'旧密码', validators=[Required()])
	new_pass = PasswordField(u'新密码', validators=[Required(), EqualTo('new_pass2', message=u'两次输入的密码必须相同') ])
	new_pass2 = PasswordField(u'确认密码', validators=[Required()])
	submit = SubmitField(u'修改密码')

class ResetPasswordRequestForm(Form):
	request_email = StringField(u'邮箱', validators=[Required(), Email(), Length(1, 64)])
	submit = SubmitField(u'重设密码')

class ResetPasswordForm(Form):
	email = StringField(u'邮箱', validators=[Required(), Email(), Length(1, 64)])
	password = PasswordField(u'新密码', validators=[Required(), EqualTo('password2', message=u'两次输入的密码必须相同')])
	password2 = PasswordField(u'确认密码', validators=[Required()])
	submit = SubmitField(u'重设密码')

	def validate_email(self, field):
		if User.query.filter_by(email=field.data).first() is None:
			raise ValidationError(u'未知邮箱')

class ChangeEmailForm(Form):
	email = StringField(u'新邮箱', validators=[Required(), Length(1, 64), Email()])
	password = PasswordField(u'密码', validators=[Required()])
	submit = SubmitField(u'提交')

	def validate_email(self, field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError(u'邮箱已经被注册了')