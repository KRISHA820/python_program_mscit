import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = (
    'sqlite:///' + os.path.join(basedir, 'tasks.db')
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Task(db.Model):

    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)

    taskname = db.Column(
        db.String(100),
        nullable=False
    )

    finishdate = db.Column(
        db.String(20),
        nullable=False
    )

    status = db.Column(
        db.String(50),
        nullable=False
    )

    def __repr__(self):
        return f"<Task #{self.id}: {self.taskname}>"


@app.route('/')
def index():
    tasks = Task.query.order_by(Task.id.desc()).all()

    return render_template(
        'index.html',
        tasks=tasks
    )

@app.route('/add', methods=['POST'])
def add_task():

    taskname = request.form.get(
        'taskname', ''
    ).strip()

    finishdate = request.form.get(
        'finishdate', ''
    ).strip()

    status = request.form.get(
        'status', ''
    ).strip()

    # Check all fields are filled
    if taskname and finishdate and status:

        new_task = Task(
            taskname=taskname,
            finishdate=finishdate,
            status=status
        )

        # Add task to session
        db.session.add(new_task)

        # Save task into SQLite
        db.session.commit()

    return redirect(url_for('index'))

@app.route('/update/<int:id>')
def update_task(id):

    # Find task by ID
    task = db.session.get(Task, id)

    if task:

        # Change status
        if task.status == "Pending":
            task.status = "In Progress"

        elif task.status == "In Progress":
            task.status = "Completed"

        else:
            task.status = "Pending"

        # Save change
        db.session.commit()

    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete_task(id):

    # Find task by ID
    task = db.session.get(Task, id)

    if task:

        # Delete task
        db.session.delete(task)

        # Save change
        db.session.commit()

    return redirect(url_for('index'))

if __name__ == '__main__':

    # Create database table
    with app.app_context():

        db.create_all()

    app.run(
        debug=True,
        port=5003
    )