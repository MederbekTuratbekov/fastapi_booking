from fastapi import Depends, HTTPException, APIRouter
from booking.db.database import SessionLocal
from typing import Optional
from sqlalchemy.orm import Session
from jose import jwt
from booking.db.models import UserProfile, RefreshToken
from booking.db.schema import UserProfileSchema, UserProfileLoginSchema, TokenSchema
from passlib.context import CryptContext
from booking.db.config import ALGORITHM, SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
from datetime import timedelta, timezone, datetime

auth_router = APIRouter(prefix='/auth', tags=['Auth'])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    if not hashed_password:
        return False
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({'exp': expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict):
    return create_access_token(data, expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))


@auth_router.post('/register', response_model=dict)
async def auth_register(user: UserProfileSchema, db: Session = Depends(get_db)):
    if db.query(UserProfile).filter(UserProfile.username == user.username).first():
        raise HTTPException(status_code=400, detail='Username already exists')
    if db.query(UserProfile).filter(UserProfile.email == user.email).first():
        raise HTTPException(status_code=400, detail='Email already exists')
    user_db = UserProfile(
        first_name=user.first_name,
        lastname=user.lastname,
        username=user.username,
        email=user.email,
        age=user.age,
        phone_number=user.phone_number,
        role=user.role,
        password=get_password_hash(user.password),
    )
    db.add(user_db)
    db.commit()
    db.refresh(user_db)
    return {'message': 'created'}


@auth_router.post('/login')
async def login(form_data: UserProfileLoginSchema, db: Session = Depends(get_db)):
    user = db.query(UserProfile).filter(UserProfile.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Неверные данные")
    access_token = create_access_token({"sub": user.username})
    refresh_token = create_refresh_token({"sub": user.username})
    db.add(RefreshToken(user_id=user.id, token=refresh_token))
    db.commit()
    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}


@auth_router.post('/logout')
async def logout(payload: TokenSchema, db: Session = Depends(get_db)):
    stored_token = db.query(RefreshToken).filter(RefreshToken.token == payload.refresh_token).first()
    if not stored_token:
        raise HTTPException(status_code=401, detail="Токен не найден")
    db.delete(stored_token)
    db.commit()
    return {'message': 'Вышли'}


@auth_router.post('/refresh')
async def refresh(payload: TokenSchema, db: Session = Depends(get_db)):
    stored_token = db.query(RefreshToken).filter(RefreshToken.token == payload.refresh_token).first()
    if not stored_token:
        raise HTTPException(status_code=401, detail="Токен не найден")
    access_token = create_access_token({"sub": stored_token.user.username})
    return {'access_token': access_token, 'token_type': 'bearer'}
