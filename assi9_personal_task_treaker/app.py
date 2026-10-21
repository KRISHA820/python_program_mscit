from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI(title="Personal Task Tracker")

app.add_middleware(SessionMiddleware,secret_key="replace-with-a-long-random-secret")

BASE_DIR = Path(__file__).resolve().parent
DATABASE_URL = f"sqlite:///{BASE_DIR / 'tasks.db'}"

engine = create_engine(DATABASE_URL,connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    description = Column(String(300), default="")
    priority = Column(String(20), default="Medium")
    is_completed = Column(Boolean, default=False)
    created_by = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.now)


# Create table automatically
Base.metadata.create_all(bind=engine)


# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Login helper
def get_user(request: Request):
    return request.session.get("user")


def require_user(request: Request):
    user = get_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Please log in first")
    return user


# GET /
@app.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    user = get_user(request)

    if not user:
        raise HTTPException(status_code=401, detail="Please log in first")

    tasks = (
        db.query(Task)
        .filter(Task.created_by == user)
        .order_by(Task.created_at.desc())
        .all()
    )

    pending = [task for task in tasks if not task.is_completed]
    completed = [task for task in tasks if task.is_completed]

    def task_data(task):
        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "is_completed": task.is_completed,
            "created_by": task.created_by,
            "created_at": task.created_at.isoformat()
        }

    return {
        "user": user,
        "pending_tasks": [task_data(t) for t in pending],
        "completed_tasks": [task_data(t) for t in completed],
        "theme": request.cookies.get("theme", "light")
    }


# GET /login
@app.get("/login")
def login_page():
    return {
        "message": "Submit your name to POST /login",
        "example": {"name": "Hasmukh"}
    }


# POST /login
@app.post("/login")
def login(request: Request, name: str = Form(...)):
    name = name.strip()

    if not name or len(name) > 100:
        raise HTTPException(
            status_code=400,
            detail="Name must contain 1 to 100 characters"
        )

    request.session.clear()
    request.session["user"] = name

    return {
        "message": "Login successful",
        "user": name
    }


# POST /add
@app.post("/add")
def add_task(
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    priority: str = Form("Medium"),
    db: Session = Depends(get_db)
):
    user = require_user(request)

    title = title.strip()
    description = description.strip()

    if not title or len(title) > 150:
        raise HTTPException(status_code=400, detail="Invalid task title")

    if len(description) > 300:
        raise HTTPException(status_code=400, detail="Description too long")

    if priority not in ["High", "Medium", "Low"]:
        raise HTTPException(status_code=400, detail="Invalid priority")

    task = Task(
        title=title,
        description=description,
        priority=priority,
        is_completed=False,
        created_by=user
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return {
        "message": "Task added successfully",
        "task_id": task.id
    }


# GET /toggle/{id}
@app.get("/toggle/{id}")
def toggle_task(
    id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    user = require_user(request)

    task = db.query(Task).filter(
        Task.id == id,
        Task.created_by == user
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.is_completed = not task.is_completed
    db.commit()

    return {
        "message": "Task status updated",
        "is_completed": task.is_completed
    }


# GET /edit/{id}
@app.get("/edit/{id}")
def edit_task(
    id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    user = require_user(request)

    task = db.query(Task).filter(
        Task.id == id,
        Task.created_by == user
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "is_completed": task.is_completed
    }


# POST /update/{id}
@app.post("/update/{id}")
def update_task(
    id: int,
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    priority: str = Form("Medium"),
    db: Session = Depends(get_db)
):
    user = require_user(request)

    task = db.query(Task).filter(
        Task.id == id,
        Task.created_by == user
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    title = title.strip()
    description = description.strip()

    if not title or len(title) > 150:
        raise HTTPException(status_code=400, detail="Invalid task title")

    if len(description) > 300:
        raise HTTPException(status_code=400, detail="Description too long")

    if priority not in ["High", "Medium", "Low"]:
        raise HTTPException(status_code=400, detail="Invalid priority")

    task.title = title
    task.description = description
    task.priority = priority

    db.commit()

    return {"message": "Task updated successfully"}


# POST /delete/{id}
@app.post("/delete/{id}")
def delete_task(
    id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    user = require_user(request)

    task = db.query(Task).filter(
        Task.id == id,
        Task.created_by == user
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()

    return {"message": "Task deleted successfully"}


# GET /set-theme/{theme}
@app.get("/set-theme/{theme}")
def set_theme(theme: str, request: Request):
    if not get_user(request):
        raise HTTPException(status_code=401, detail="Please log in first")

    if theme not in ["light", "dark"]:
        raise HTTPException(status_code=400, detail="Invalid theme")

    response = {
        "message": "Theme preference saved",
        "theme": theme
    }

    from fastapi.responses import JSONResponse
    result = JSONResponse(response)

    result.set_cookie(
        key="theme",
        value=theme,
        max_age=31536000,
        httponly=True,
        samesite="lax"
    )

    return result


# GET /logout
@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return {"message": "Logged out successfully"}
