# -*- coding: utf-8 -*-

from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_user, logout_user, login_required, current_user
from . import auth
from ..models import User
from .forms import LoginForm, RegistrationForm, ChangePassForm, \
	ResetPasswordRequestForm, ResetPasswordForm, ChangeEmailForm
from ..email import send_email
from .. import db

@auth.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user is not None and user.verify_password(form.password.data):
			login_user(user, form.remember_me.data)
			return redirect(request.args.get('next') or url_for('main.index'))
		flash(u'账号不存在或密码错误')
	return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
	logout_user()
	flash(u'注销成功')
	return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(email=form.email.data, username=form.username.data, password=form.password.data)
		db.session.add(user)
		db.session.commit()
		token = user.generate_confirmation_token()
		send_email(user.email, 'Confirm Your Account', 'auth/email/confirm', user=user, token=token)
		flash(u'确认账号的邮件已经发往你的邮箱。')
		return redirect(url_for('auth.login'))
	return render_template('auth/register.html', form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
	if current_user.confirmed:
		return redirect(url_for('main.index'))
	if current_user.confirm(token):
		flash(u'验证成功！')
	else:
		flash(u'验证链接非法或者已超时')
	return redirect(url_for('main.index'))

@auth.before_app_request
def before_request():
	if current_user.is_authenticated():
		current_user.ping()
		if not current_user.confirmed \
		and request.endpoint[:5] != 'auth.' \
		and request.endpoint != 'static':
			return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
	if current_user.is_anonymous() or current_user.confirmed:
		return redirect(url_for('main.index'))
	return render_template('auth/unconfirmed.html')

@auth.route('/confirm')
@login_required
def resend_confirmation():
	token = current_user.generate_confirmation_token()
	send_email(current_user.email, 'Confirm Your Account', 
		'auth/email/confirm', user=current_user, token=token)
	flash(u'确认账号的邮件已经发往你的邮箱。')
	return redirect(url_for('main.index'))

@auth.route('/changepass', methods=['GET', 'POST'])
@login_required
def change_password():
	form = ChangePassForm()
	if form.validate_on_submit():
		if current_user.verify_password(form.old_pass.data):
			current_user.password = form.new_pass.data
			db.session.add(current_user)
			flash(u'密码修改成功。')
			return redirect(url_for('main.index'))
		flash(u'密码错误')
	return render_template('auth/changepassword.html', form=form)

@auth.route('/reset', methods=['GET', 'POST'])
def reset_password_request():
	if not current_user.is_anonymous():
		return redirect(url_for('main_index'))
	form = ResetPasswordRequestForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.request_email.data).first()
		if user:
			token = user.generate_reset_token()
			send_email(user.email, 'Reset Your Password',
				'auth/email/reset_password', user=user, token=token)
			flash(u'重设密码的邮件已经发往你的邮箱')
			return redirect(url_for('auth.login'))
		flash(u'邮箱不存在')
	return render_template('auth/reset_password.html', form=form)

@auth.route('/reset/<token>', methods=['GET', 'POST'])
def reset_password(token):
	if not current_user.is_anonymous():
		return redirect(url_for('main.index'))
	form = ResetPasswordForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user is None:
			return redirect(url_for('main.index'))
		if user.reset_password(token, form.password.data):
			flash(u'密码重设成功')
			return redirect(url_for('auth.login'))
		else:
			return redirect(url_for('main.index'))
	return render_template('auth/reset_password.html', form=form)

@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
	form = ChangeEmailForm()
	if form.validate_on_submit():
		if (current_user.verify_password(form.password.data)):
			new_email = form.email.data
			token = current_user.generate_change_email_token(new_email)
			send_email(new_email, 'Confirm your email address',
				'auth/email/change_email', user=current_user, token=token)
			flash(u'验证新邮箱身份的邮件已经发往你的邮箱')
			return redirect(url_for('main.index'))
		else :
			flash(u'密码错误')
	return render_template('auth/change_email.html', form=form)

@auth.route('/change-email/<token>')
@login_required
def change_email(token):
	if current_user.change_email(token):
		flash(u'邮箱修改成功')
	else:
		flash(u'非法访问')
	return redirect(url_for('main.index'))

@auth.route('/user/<username>')
def user(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		abort(404)
	render_template('user.html', user=user)