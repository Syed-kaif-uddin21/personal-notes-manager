from datetime import datetime, timedelta, timezone
from typing import Optional
import os
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import Session, declarative_base
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import jwt
from fastapi import HTTPException, Header


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "notes.db")
engine = create_engine(f"sqlite:///{DB_PATH}")
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


Base.metadata.create_all(engine)

ACCESS_TOKEN_EXPIRY = 15
REFRESH_TOKEN_EXPIRY = 7 * 24 * 60 
SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = "HS256"
ph = PasswordHasher()


def create_token(user_id: int, email: str, username: str, token_type: str = "access"):
    expiry_minutes = ACCESS_TOKEN_EXPIRY if token_type == "access" else REFRESH_TOKEN_EXPIRY
    payload = {
        "user_id": user_id,
        "email": email,
        "username": username,
        "token_type": token_type,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=expiry_minutes),
    }
    return jwt.encode(payload=payload, key=SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str, token_type: str = "access"):
    if not token:
        return None
    token_str = token.strip()
    if token_str.startswith("Bearer "):
        token_str = token_str[7:].strip()
    try:
        payload = jwt.decode(jwt=token_str, key=SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        return None

    if payload.get("token_type") == token_type:
        return {
            "user_id": payload.get("user_id"),
            "email": payload.get("email"),
            "username": payload.get("username"),
        }
    return None


def get_current_user(
    token: Optional[str] = Header(None),
):
    raw_token = token
    if not raw_token or not raw_token.strip():
        raise HTTPException(status_code=401, detail="Accessing notes without authentication")

    user_info = verify_token(raw_token, token_type="access")
    if not user_info:
        raise HTTPException(status_code=401, detail="Using an invalid or expired access token")
    return user_info


def verify_login(email: str, password: str):
    session = Session(engine)
    user = session.query(User).filter(User.email == email).first()
    if not user:
        session.close()
        return None

    try:
        ph.verify(user.hashed_password, password)
    except VerifyMismatchError:
        session.close()
        return None

    user_id = user.id
    email_val = user.email
    username_val = user.username
    session.close()

    access_token = create_token(user_id=user_id, email=email_val, username=username_val, token_type="access")
    refresh_token = create_token(user_id=user_id, email=email_val, username=username_val, token_type="refresh")

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }
#A1

def register(username, email, password):

    session = Session(engine)
    user_exist = session.query(User).filter(User.email == email).first()
    if user_exist is not None:
        session.close()
        raise HTTPException(status_code=409, detail="Email already exists")

    new_user = User(
        username=username,
        email=email,
        hashed_password=ph.hash(password),
    )
    session.add(new_user)
    session.commit()
    session.close()
    return {"message": "User registered successfully"}


#A2

def login(email, password):
    tokens = verify_login(email=email, password=password)
    if not tokens:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return tokens



# A3
def refresh(refresh_token):
    user = verify_token(token=refresh_token, token_type="refresh")
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    access_token = create_token(
        user_id=user["user_id"],
        email=user["email"],
        username=user["username"],
        token_type="access",
    )
    return {"access_token": access_token, "token_type": "bearer"}

# E1
def get_notes(user_id):
    session = Session(engine)
    notes = session.query(Note).filter(Note.user_id == user_id).all()
    response = [
        {
            "id": note.id,
            "user_id": note.user_id,
            "title": note.title,
            "content": note.content,
            "created_at": note.created_at
        }
        for note in notes
    ]
    session.close()
    return response

# E2
def create_note(user_id, title, content):
    if not title or not content:
        raise HTTPException(status_code=422, detail="Title and content are required")

    session = Session(engine)
    new_note = Note(
        user_id=user_id,
        title=title,
        content=content,
        created_at=datetime.now(),
    )
    session.add(new_note)
    session.commit()
    response = {
        "id": new_note.id,
        "user_id": new_note.user_id,
        "title": new_note.title,
        "content": new_note.content,
        "created_at": new_note.created_at,
    }
    session.close()
    return response