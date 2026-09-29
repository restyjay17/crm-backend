from jose import jwt, JWTError

from fastapi import Depends, Request, HTTPException

from app.core.security import (
    SECRET_KEY,
    ALGORITHM
)

# security = HTTPBearer()

def get_access_token(request: Request):
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Missing access token")

    return token


def get_current_user(token: str = Depends(get_access_token)):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid access token")

        return payload
    
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    

def require_role(*allowed_roles):
    def role_checker(current_user=Depends(get_current_user)):
        user_role = current_user.get("role")

        if user_role not in allowed_roles:
            raise HTTPException(status_code=403, detail="You are not authorize to access this endpoint")
        
        return current_user
    
    return role_checker


def verify_csrf(request: Request):
    csrf_cookie = request.cookies.get("csrf_token")
    csrf_header = request.headers.get("X-CSRF-Token")

    if not csrf_cookie or not csrf_header:
        raise HTTPException(status_code=403, detail="Missing CSRF Token")
    
    if csrf_cookie != csrf_header:
        raise HTTPException(status_code=403, detail="Invalid CSRF Token")