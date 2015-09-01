# -*- coding: utf-8 -*-

from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email

class LoginForm(Form):
	email = StringField('email', validators=[Required(), Length(1, 64), Email()])
	password = PasswordField('password')
	remember_me = BooleanField('Remember me')
	submit = SubmitField('Login')