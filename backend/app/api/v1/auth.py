"""认证与用户接口。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.models.user import User
from app.schemas.user import LoginRequest, TokenOut, UserOut
from app.schemas.common import ok
from app.api.v1.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    token = create_access_token({"sub": str(user.id), "username": user.username})
    return ok(TokenOut(
        access_token=token,
        user=UserOut(id=user.id, username=user.username,
                     real_name=user.real_name, role=user.role),
    ).model_dump())


@router.get("/me")
def me(current=Depends(get_current_user)):
    if not current:
        return ok(None)
    return ok({"id": current.id, "username": current.username,
               "real_name": current.real_name, "role": current.role})
