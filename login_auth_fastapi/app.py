from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm
)
from pydantic import BaseModel

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String
)

from sqlalchemy.orm import (
    declarative_base,
    sessionmaker,
    Session
)

from datetime import datetime, timedelta, timezone

import jwt
import hashlib


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="FastAPI JWT Authentication with ORM"
)


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DATABASE_URL = "sqlite:///./users.db"


engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    }
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


Base = declarative_base()


# ============================================================
# USER DATABASE TABLE
# ============================================================

class UserDB(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    username = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    password = Column(
        String(255),
        nullable=False
    )

    full_name = Column(
        String(100),
        nullable=False
    )


# ============================================================
# CREATE TABLE
# ============================================================

Base.metadata.create_all(
    bind=engine
)


# ============================================================
# DATABASE DEPENDENCY
# ============================================================

def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()


# ============================================================
# JWT CONFIGURATION
# ============================================================

SECRET_KEY = "gggggj6yt6o"

ALGORITHM = "HS256"

# JWT token valid for 3 hours
TOKEN_EXPIRE_HOURS = 3


# ============================================================
# OAUTH2
# ============================================================

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login"
)


# ============================================================
# PYDANTIC MODELS
# ============================================================

class UserSignup(BaseModel):

    username: str

    password: str

    full_name: str


# ============================================================
# PASSWORD HASHING
# ============================================================

def hash_password(password: str):

    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


# ============================================================
# 1. SIGNUP
# ============================================================

@app.post("/signup")
def signup(
    user: UserSignup,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # Check username already exists
    # --------------------------------------------------------

    existing_user = db.query(UserDB).filter(
        UserDB.username == user.username
    ).first()

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    # --------------------------------------------------------
    # Create new user
    # --------------------------------------------------------

    new_user = UserDB(

        username=user.username,

        password=hash_password(
            user.password
        ),

        full_name=user.full_name
    )

    # --------------------------------------------------------
    # Save to database
    # --------------------------------------------------------

    db.add(new_user)

    db.commit()

    db.refresh(new_user)

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {

        "message": "User created successfully",

        "user": {

            "id": new_user.id,

            "username": new_user.username,

            "full_name": new_user.full_name
        }
    }


# ============================================================
# 2. LOGIN
# ============================================================
# IMPORTANT:
# OAuth2PasswordRequestForm is used because Swagger
# Authorize sends username/password as FORM DATA.
# ============================================================

@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # Find user by username
    # --------------------------------------------------------

    db_user = db.query(UserDB).filter(
        UserDB.username == form_data.username
    ).first()

    # --------------------------------------------------------
    # Username check
    # --------------------------------------------------------

    if not db_user:

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    # --------------------------------------------------------
    # Password check
    # --------------------------------------------------------

    hashed_password = hash_password(
        form_data.password
    )

    if hashed_password != db_user.password:

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    # --------------------------------------------------------
    # Token expiration
    # --------------------------------------------------------
    # Current time + 3 hours
    # --------------------------------------------------------

    expire = (
        datetime.now(timezone.utc)
        + timedelta(
            hours=TOKEN_EXPIRE_HOURS
        )
    )

    # --------------------------------------------------------
    # JWT PAYLOAD
    # --------------------------------------------------------

    payload = {

        "sub": db_user.username,

        "name": db_user.full_name,

        "exp": expire
    }

    # --------------------------------------------------------
    # CREATE JWT TOKEN
    # --------------------------------------------------------

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {

        "message": "Login successful",

        "access_token": token,

        "token_type": "bearer",

        "expires_in": "3 hours"
    }


# ============================================================
# 3. GET CURRENT USER FROM JWT
# ============================================================

def get_current_user(

    token: str = Depends(
        oauth2_scheme
    ),

    db: Session = Depends(
        get_db
    )
):

    try:

        # ----------------------------------------------------
        # Decode JWT token
        # ----------------------------------------------------

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        # ----------------------------------------------------
        # Get username from token
        # ----------------------------------------------------

        username = payload.get("sub")

        if username is None:

            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        # ----------------------------------------------------
        # Find user in database
        # ----------------------------------------------------

        user = db.query(UserDB).filter(
            UserDB.username == username
        ).first()

        if user is None:

            raise HTTPException(
                status_code=401,
                detail="User not found"
            )

        return user

    # --------------------------------------------------------
    # JWT expired
    # --------------------------------------------------------

    except jwt.ExpiredSignatureError:

        raise HTTPException(
            status_code=401,
            detail="Token has expired. Please login again."
        )

    # --------------------------------------------------------
    # Invalid JWT
    # --------------------------------------------------------

    except jwt.InvalidTokenError:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )


# ============================================================
# 4. PROTECTED PROFILE API
# ============================================================

@app.get("/profile")
def get_profile(

    current_user: UserDB = Depends(
        get_current_user
    )
):

    return {

        "message": "Authentication successful!",

        "id": current_user.id,

        "username": current_user.username,

        "full_name": current_user.full_name
    }


# ============================================================
# 5. GET ALL USERS
# ============================================================
# JWT TOKEN REQUIRED
# ============================================================

@app.get("/users")
def get_users(

    # --------------------------------------------------------
    # JWT authentication
    # --------------------------------------------------------

    current_user: UserDB = Depends(
        get_current_user
    ),

    # --------------------------------------------------------
    # Database
    # --------------------------------------------------------

    db: Session = Depends(
        get_db
    )
):

    # --------------------------------------------------------
    # Get all users from database
    # --------------------------------------------------------

    users = db.query(UserDB).all()

    # --------------------------------------------------------
    # Return all users
    # --------------------------------------------------------

    return {

        "message": "Users fetched successfully",

        "login_user": current_user.username,

        "total_users": len(users),

        "users": [

            {

                "id": user.id,

                "username": user.username,

                "full_name": user.full_name

            }

            for user in users
        ]
    }