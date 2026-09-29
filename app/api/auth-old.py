from fastapi import APIRouter, Request, Response, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timezone

from app.db.session import get_db
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.schemas.user import (
    UserLogin,
    Token
)

from app.core.security import (
    SECRET_KEY,
    ALGORITHM,
    verify_password,
    create_access_token,
    create_refresh_token,
    hash_token,
    generate_csrf_token
)
from app.core.dependencies import verify_csrf

ACTIVE_STATUS = "active"
REFRESH_TYPE = "refresh"

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

def set_auth_cookies(
    response: Response,
    access_token: str,
    refresh_token: str
):
    response.set_cookie(
        key="access_token",
        value=access_token,
        path="/",
        httponly=True,
        secure=False,
        samesite="lax"
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        path="/",
        httponly=True,
        secure=False,
        samesite="lax"
    )

    csrf_token = generate_csrf_token()

    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        httponly=False,
        secure=False,
        samesite="lax",
        path="/"
    )

@router.post("/login")
def login(payload: UserLogin, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if user.status != ACTIVE_STATUS:
        raise HTTPException(status_code=403, detail="Account not active")

    access_token = create_access_token(
        {
            "sub": str(user.id),
            "name": user.full_name,
            "email": user.email,
            "role": user.role,
            "org": str(user.organization_id)
        }
    )

    refresh_token, expires_at = create_refresh_token({
        "sub": str(user.id)
    })

    try:
        db_token = RefreshToken(
            token_hash=hash_token(refresh_token),
            user_id=user.id,
            expires_at=expires_at
        )
        db.add(db_token)
        db.commit()
    except Exception:
        db.rollback()
        raise

    set_auth_cookies(
        response,
        access_token,
        refresh_token
    )
    return {
        "message": "Login successful"
    }


@router.post("/refresh")
def refresh_token(
    request: Request, 
    response: Response, 
    db: Session = Depends(get_db),
    csrf: None = Depends(verify_csrf)
):
    token = request.cookies.get("refresh_token")

    if not token:
        raise HTTPException(status_code=401, detail="Missing refresh token")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if payload["type"] != REFRESH_TYPE:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        user_id = payload["sub"]
        token_hash = hash_token(token)

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        if user.status != ACTIVE_STATUS:
            raise HTTPException(status_code=403, detail="Account not active")
        
        # check db token
        stored_token = db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash,
            # RefreshToken.revoked.is_(False)
        ).first()

        if not stored_token:
            raise HTTPException(status_code=401, detail="Refresh token not found")

        if stored_token.revoked:
            raise HTTPException(status_code=401, detail="Refresh token already revoked")

        if stored_token.expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=401, detail="Refresh token expired")
        
        if stored_token.user_id != user.id:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        new_refresh_token, expires_at = create_refresh_token({
            "sub": str(user.id)
        })
        
        try:
            # revoked old token
            if stored_token.revoked:
                raise HTTPException(
                    status_code=401,
                    detail="Refresh token already used"
                )

            stored_token.revoked = True

            new_token_hash = hash_token(new_refresh_token)

            # store new token
            db.add(
                RefreshToken(
                    token_hash=new_token_hash,
                    user_id=user.id,
                    expires_at=expires_at
                )
            )
            db.commit()
        except Exception:
            db.rollback()
            raise

        new_access_token = create_access_token({
            "sub": str(user.id),
            "name": user.full_name,
            "email": user.email,
            "role": user.role,
            "org": str(user.organization_id)
        })

        set_auth_cookies(
            response,
            new_access_token,
            new_refresh_token
        )

        return {
            "message": "Token refreshed"
        }
    
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    
@router.post("/logout")
def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    csrf: None = Depends(verify_csrf)
):
    token = request.cookies.get("refresh_token")

    if token:
        try:
            token_hash = hash_token(token)

            stored = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()
            if stored:
                stored.revoked = True
                db.commit()

            # add deleting old tokens periodically

        except Exception:
            db.rollback()

    response.delete_cookie(
        key="access_token",
        path="/",
        secure=False,
        httponly=True,
        samesite="lax"
    )

    response.delete_cookie(
        key="refresh_token",
        path="/",
        secure=False,
        httponly=True,
        samesite="lax"
    )

    response.delete_cookie(
        key="csrf_token",
        path="/",
        secure=False,
        httponly=False,
        samesite="lax"
    )

    return {
        "message": "Logged out"
    }