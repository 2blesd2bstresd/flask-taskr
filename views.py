#views.py
import datetime
from flask import Flask, flash, redirect, render_template, request, \
				  session, url_for, g, Blueprint

from functools import wraps
from forms import AddTaskForm, RegisterForm, LoginForm
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

from models import User

def login_required(test):
	@wraps(test)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return test(*args, **kwargs)
		else:
			flash('Login first.')
			return redirect(url_for('login'))
	return wrap

@app.route('/logout/')
def logout():
	session.pop('logged_in', None)
	session.pop('user_id', None)
	flash('You are logged out.')
	return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST']) 	
def login():
	error = None
	form = LoginForm(request.form) 
	if request.method == 'POST':
		if form.validate_on_submit(): 
			u = User.query.filter_by(
					name=request.form['name'],
					password=request.form['password']).first()
			if u is None:
				error = 'Invalid username or password.' 
				return render_template(
					"login.html", form=form, error=error) 
			else:
				session['logged_in'] = True 
				session['user_id'] = u.id 
				flash('You are logged in. Go Crazy.')
				return redirect(url_for('tasks'))
		else:
			return render_template(
				"login.html", form=form, error=error)
	if request.method == 'GET':
		return render_template('login.html', form=form)

@app.route('/tasks/')
@login_required
def tasks():
	from models import Task
	open_tasks = db.session.query(Task) \
		.filter_by(status='1').filter_by(user_id=session['user_id']).order_by(Task.due_date.asc())
	closed_tasks = db.session.query(Task) \
		.filter_by(status='0').filter_by(user_id=session['user_id']).order_by(Task.due_date.asc())
	return render_template('tasks.html', form=AddTaskForm(request.form),
							open_tasks=open_tasks, closed_tasks=closed_tasks)

@app.route('/add/', methods=['GET', 'POST'])
@login_required
def add_task():
	from models import Task
	form = AddTaskForm(request.form)
	if request.method == 'POST':
		if form.validate_on_submit():
			t = Task(form.name.data,
					 datetime.datetime.now(),
					 form.priority.data,
					 '1',
					 session['user_id']
					 )
			db.session.add(t)
			db.session.commit()
			flash('SpotKey Added')
		else:
			flash('Invalid format.')
	return redirect(url_for('tasks'))

@app.route('/complete/<int:task_id>/')
@login_required
def complete(task_id):
	from models import Task
	db.session.query(Task).filter_by(task_id=task_id).update({'status':'0'})
	db.session.commit()
	flash ("SpotKey activated.")
	return redirect(url_for('tasks'))

@app.route('/delete/<int:task_id>')
@login_required
def delete(task_id):
	from models import Task
	db.session.query(Task).filter_by(task_id=task_id).delete()
	db.session.commit()
	flash ("SpotKey deleted.")
	return redirect(url_for('tasks'))

@app.route('/uncomplete/<int:task_id>') 
@login_required
def uncomplete(task_id):
	from models import Task
	db.session.query(Task).filter_by(task_id=task_id).update({'status':'1'})
	db.session.commit()
	flash('SpotKey deactivated.')
	return redirect(url_for('tasks'))

# User Registration:
@app.route('/register/', methods=['GET', 'POST']) 
def register():
	error = None
	form = RegisterForm(request.form) 
	if request.method == 'POST':
		if form.validate_on_submit(): 
			new_user = User(form.name.data, form.email.data, form.password.data)
			db.session.add(new_user)
			db.session.commit()
			flash('Thanks for registering. Please login.') 
			return redirect(url_for('login'))
		else:
			return render_template('register.html', form=form, error=error)
	if request.method == 'GET':
		return render_template('register.html', form=form)

