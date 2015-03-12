#views.py

from flask import Flask, flash, redirect, render_template, request, \
				  session, url_for, g

from functools import wraps

import sqlite3
from forms import AddTaskForm

app = Flask(__name__)
app.config.from_object('config')

def connect_db():
	return sqlite3.connect(app.config['DATABASE'])

def login_required(test):
	@wraps(test)
	def wrap(*args, **kwargs):
		if 'logged in' in session:
			return test(*args, **kwargs)
		else:
			flash('Login first.')
			return redirect(url_for('login'))
	return wrap

@app.route('/logout/')
def logout():
	session.pop('logged_in', None)
	flash('You are logged out.')
	return redirect(url_for('login'))

@app.route('/', methods=['GET','POST'])
def login():
	if request.method =='POST':
		if request.form['username'] != app.config['USERNAME'] or \
		request.form['password'] != app.config['PASSWORD']:
			errors.append('Incorrect credentials')
			return render_template('login.html', errors)
		else:
			session['logged in'] = True
			return redirect(url_for('tasks'))
	if request.method == 'GET':
		return render_template('login.html')

@app.route('/tasks/')
@login_required
def tasks():
	g.db = connect_db()
	cur = g.db.execute('select name, due_date, priority, task_id from tasks where status=1')
	open_tasks = [dict(name=row[0],due_date=row[1],priority=row[2],task_id=row[3]) for row in cur.fetchall()]
	cur = g.db.execute('select name, due_date, priority, task_id from tasks where status=0')
	closed_tasks = [dict(name=row[0],due_date=row[1],priority=row[2],task_id=row[3]) for row in cur.fetchall()]
	g.db.close()
	return render_template('tasks.html', form=AddTaskForm(request.form),
							open_tasks=open_tasks, closed_tasks=closed_tasks)

@app.route('/add/', methods=['POST'])
@login_required
def add_task():
	name = request.form['name']
	due_date = request.form['due_date']
	priority = request.form['priority']
	if not name or not due_date or not priority:
		flash('All fields required.')
		return redirect(url_for('tasks'))
	else:
		g.db = connect_db()
		g.db.execute('INSERT INTO tasks VALUES(NULL, ?, ?, ?, 1)',[name, due_date, priority])
		g.db.commit()
		g.db.close()
		flash('Entry successful')
		return redirect(url_for('tasks'))

@app.route('/complete/<int:task_id>/')
@login_required
def complete(task_id):
	g.db = connect_db()
	g.db.execute('update tasks set status = 0 where task_id =' + str(task_id))
	g.db.commit()
	g.db.close()
	flash ("Task Completed.")
	return redirect(url_for('tasks'))

@app.route('/delete/<int:task_id>')
@login_required
def delete(task_id):
	g.db = connect_db()
	g.db.execute('delete from tasks where task_id =' + str(task_id))
	g.db.commit()
	g.db.close()
	flash ("Task Deleted.")
	return redirect(url_for('tasks'))

@app.route('/uncomplete/<int:task_id>') 
@login_required
def uncomplete(task_id):
	g.db = connect_db()
	g.db.execute('update tasks set status = 1 where task_id =' + str(task_id))
	g.db.commit()
	g.db.close()
	flash('Task Completed.')
	return redirect(url_for('tasks'))

