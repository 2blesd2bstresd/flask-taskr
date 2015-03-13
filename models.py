from views import db
import datetime

class Task(db.Model):

	__tablename__ = "tasks"

	task_id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String, nullable=False)
	due_date = db.Column(db.Date, default=datetime.datetime.utcnow(), nullable=False)
	priority = db.Column(db.Integer, nullable=False)
	status = db.Column(db.Integer)
	user_id = db.Column(db.String, db.ForeignKey('users.id'))

	def __init__(self, name, due_date, priority, status, user_id):

		self.name = name
		self.due_date = due_date
		self.priority = priority
		self.status = status
		self.user_id = user_id

	def __repr__(self):
		return '<name %r>' % (self.name)

class User(db.Model):

	__tablename__ = 'users'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String, nullable=False, unique=True)
	email = db.Column(db.String, nullable=False, unique=True)
	password = db.Column(db.String, nullable=False)
	tasks = db.relationship('Task', backref='poster')

	def __init__(self, name, email, password):
		self.name = name
		self.email = email
		self.password = password

	def __repr__(self):
		return '<User %r>' % (self.name)