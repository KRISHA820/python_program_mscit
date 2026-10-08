import os

from fastapi import FastAPI, Form
from fastapi.responses import RedirectResponse

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker


app = FastAPI()


# ---------------- DATABASE ----------------

basedir = os.path.abspath(os.path.dirname(__file__))

DATABASE_URL = "sqlite:///" + os.path.join(
    basedir,
    "tasks.db"
)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# ---------------- MODEL ----------------

class Task(Base):

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)

    taskname = Column(
        String(100),
        nullable=False
    )

    finishdate = Column(
        String(20),
        nullable=False
    )

    status = Column(
        String(50),
        nullable=False
    )


# Create table
Base.metadata.create_all(bind=engine)


# ---------------- DISPLAY ----------------

@app.get("/")
def index():

    db = SessionLocal()

    tasks = db.query(Task).order_by(
        Task.id.desc()
    ).all()

    db.close()

    return tasks


# ---------------- ADD ----------------

@app.post("/add")
def add_task(
    taskname: str = Form(...),
    finishdate: str = Form(...),
    status: str = Form(...)
):

    db = SessionLocal()

    new_task = Task(
        taskname=taskname,
        finishdate=finishdate,
        status=status
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    db.close()

    return {
        "message": "Task added successfully",
        "task": {
            "id": new_task.id,
            "taskname": new_task.taskname,
            "finishdate": new_task.finishdate,
            "status": new_task.status
        }
    }


# ---------------- UPDATE ----------------

@app.get("/update/{id}")
def update_task(id: int):

    db = SessionLocal()

    task = db.get(Task, id)

    if task is None:

        db.close()

        return {
            "message": "Task not found"
        }

    if task.status == "Pending":

        task.status = "In Progress"

    elif task.status == "In Progress":

        task.status = "Completed"

    else:

        task.status = "Pending"

    db.commit()

    new_status = task.status

    db.close()

    return {
        "message": "Task updated successfully",
        "id": id,
        "status": new_status
    }


# ---------------- DELETE ----------------

@app.delete("/delete/{id}")
def delete_task(id: int):

    db = SessionLocal()

    task = db.get(Task, id)

    if task is None:

        db.close()

        return {
            "message": "Task not found"
        }

    db.delete(task)
    db.commit()

    db.close()

    return {
        "message": "Task deleted successfully",
        "id": id
    }