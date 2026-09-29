import os
import uuid
import bcrypt
import hashlib
import secrets
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from jose import jwt

load_dotenv()

SECRET_KEY = os.environ["ENCRYPTION_SECRET_KEY"]
ALGORITHM = os.environ["ENCRYPTION_ALGORITHM"]
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7


# ---------------------------
# PASSWORD HASHING
# ---------------------------

def hash_password(password: str) -> str:
    if not password:
        raise ValueError("Password cannot be empty")

    password_bytes = password.encode("utf-8")[:72]

    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode("utf-8")[:72]
    return bcrypt.checkpw(password_bytes, hashed_password.encode("utf-8"))


# ---------------------------
# JWT TOKEN
# ---------------------------

def create_access_token(data: dict):
    to_encode = data.copy()

    to_encode.update({"type": "access"})

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def create_refresh_token(data: dict):
    to_encode = data.copy()

    token_hash = str(uuid.uuid4())
    to_encode.update({"token_hash": token_hash})
    to_encode.update({"type": "refresh"})

    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})

    token = jwt.encode(
        to_encode, 
        SECRET_KEY, 
        algorithm=ALGORITHM
    )

    return token,expire


def hash_token(token: str) -> str:
    return hashlib.sha256(
        token.encode()
    ).hexdigest()


def generate_csrf_token():
    return secrets.token_urlsafe(32)