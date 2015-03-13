# db_create.py

from views import db
from models import Task
from datetime import date

db.create_all()

# db.session.add(Task('Finish tutorial', date(2015,1,1), 10, 1))
# db.session.add(Task('Train for success', date(2015,2,2), 10, 1))

db.session.commit()
