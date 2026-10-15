from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from pathlib import Path

app = Flask(__name__)

app.config["SECRET_KEY"] = "todo-app-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///" + str(Path(app.root_path) / "tasks.db")
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(300), nullable=True)
    priority = db.Column(db.String(20), nullable=False, default="Medium")
    is_completed = db.Column(db.Boolean, default=False, nullable=False)
    due_date = db.Column(db.Date, nullable=True)


@app.route("/")
def index():
    pending_tasks = Task.query.filter_by(
        is_completed=False
    ).order_by(Task.due_date.asc()).all()

    completed_tasks = Task.query.filter_by(
        is_completed=True
    ).order_by(Task.id.desc()).all()

    return render_template(
        "index.html",
        pending_tasks=pending_tasks,
        completed_tasks=completed_tasks
    )


# Add a new task
@app.route("/add", methods=["POST"])
def add():
    try:
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        priority = request.form.get("priority", "Medium")
        date_text = request.form.get("due_date", "")

        if not title or len(title) > 150:
            raise ValueError("Title is required and must be at most 150 characters.")

        if len(description) > 300:
            raise ValueError("Description must be at most 300 characters.")

        if priority not in ["High", "Medium", "Low"]:
            raise ValueError("Please select a valid priority.")

        due_date = (
            datetime.strptime(date_text, "%Y-%m-%d").date()
            if date_text else None
        )

        task = Task(
            title=title,
            description=description,
            priority=priority,
            due_date=due_date
        )

        db.session.add(task)
        db.session.commit()
        flash("Task added successfully!", "success")

    except ValueError as error:
        db.session.rollback()
        flash(str(error), "error")

    return redirect(url_for("index"))


# Toggle task between Pending and Completed
@app.route("/toggle/<int:id>")
def toggle(id):
    task = db.session.get(Task, id)

    if task is None:
        flash("Task not found.", "error")
        return redirect(url_for("index"))

    task.is_completed = not task.is_completed
    db.session.commit()

    flash("Task status updated!", "success")
    return redirect(url_for("index"))


# Update an existing task
@app.route("/update/<int:id>", methods=["POST"])
def update(id):
    task = db.session.get(Task, id)

    if task is None:
        flash("Task not found.", "error")
        return redirect(url_for("index"))

    try:
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        priority = request.form.get("priority", "Medium")
        date_text = request.form.get("due_date", "")

        if not title or len(title) > 150:
            raise ValueError("Title is required and must be at most 150 characters.")

        if len(description) > 300:
            raise ValueError("Description must be at most 300 characters.")

        if priority not in ["High", "Medium", "Low"]:
            raise ValueError("Please select a valid priority.")

        due_date = (
            datetime.strptime(date_text, "%Y-%m-%d").date()
            if date_text else None
        )

        task.title = title
        task.description = description
        task.priority = priority
        task.due_date = due_date

        db.session.commit()
        flash("Task updated successfully!", "success")

    except ValueError as error:
        db.session.rollback()
        flash(str(error), "error")
        return redirect(url_for("edit", id=id))

    return redirect(url_for("index"))


# Edit page
@app.route("/edit/<int:id>")
def edit(id):
    task = db.session.get(Task, id)

    if task is None:
        flash("Task not found.", "error")
        return redirect(url_for("index"))

    return render_template("edit.html", task=task)


# Delete a task
@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    task = db.session.get(Task, id)

    if task is None:
        flash("Task not found.", "error")
        return redirect(url_for("index"))

    db.session.delete(task)
    db.session.commit()

    flash("Task deleted successfully!", "success")
    return redirect(url_for("index"))


# Create database tables
with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
