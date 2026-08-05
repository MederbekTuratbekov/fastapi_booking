from fastapi import APIRouter, Depends, HTTPException
from starlette.requests import Request
from authlib.integrations.starlette_client import OAuth
from sqlalchemy.orm import Session
from booking.db.config import settings
from booking.db.database import SessionLocal
from booking.db.models import UserProfile, RefreshToken
from booking.api.auth import create_access_token, create_refresh_token

social_router = APIRouter(prefix='/oauth', tags=['Social Auth'])

oauth = OAuth()

oauth.register(
    name='github',
    client_id=settings.GITHUB_CLIENT_ID,
    client_secret=settings.GITHUB_KEY,
    authorize_url='https://github.com/login/oauth/authorize',
    access_token_url='https://github.com/login/oauth/access_token',
    client_kwargs={'scope': 'user:email'},
)

oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_KEY,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    access_token_url='https://oauth2.googleapis.com/token',
    client_kwargs={'scope': 'openid profile email'},
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_or_create_social_user(db: Session, email: str, first_name: str, lastname: str, username: str) -> UserProfile:
    user = db.query(UserProfile).filter(UserProfile.email == email).first()
    if user:
        return user

    base_username = username or email.split('@')[0]
    final_username = base_username
    suffix = 1
    while db.query(UserProfile).filter(UserProfile.username == final_username).first():
        suffix += 1
        final_username = f'{base_username}{suffix}'

    user = UserProfile(
        first_name=first_name or 'Unknown',
        lastname=lastname or 'Unknown',
        username=final_username,
        email=email,
        password=None,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def issue_tokens_for_user(db: Session, user: UserProfile) -> dict:
    access_token = create_access_token({'sub': user.username})
    refresh_token = create_refresh_token({'sub': user.username})
    db.add(RefreshToken(user_id=user.id, token=refresh_token))
    db.commit()
    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}


@social_router.get('/github/login')
async def login_github(request: Request):
    return await oauth.github.authorize_redirect(request, settings.GITHUB_URL)


@social_router.get('/github/callback')
async def callback_github(request: Request, db: Session = Depends(get_db)):
    token = await oauth.github.authorize_access_token(request)

    resp = await oauth.github.get('user', token=token)
    profile = resp.json()

    email = profile.get('email')
    if not email:
        emails_resp = await oauth.github.get('user/emails', token=token)
        emails = emails_resp.json()
        primary = next((e for e in emails if e.get('primary')), None)
        email = primary['email'] if primary else (emails[0]['email'] if emails else None)

    if not email:
        raise HTTPException(status_code=400, detail='GitHub не вернул email')

    full_name = (profile.get('name') or '').split(' ', 1)
    first_name = full_name[0] if full_name else 'Unknown'
    lastname = full_name[1] if len(full_name) > 1 else 'Unknown'

    user = get_or_create_social_user(
        db,
        email=email,
        first_name=first_name,
        lastname=lastname,
        username=profile.get('login'),
    )
    return issue_tokens_for_user(db, user)


@social_router.get('/google/login')
async def login_google(request: Request):
    return await oauth.google.authorize_redirect(request, settings.GOOGLE_URL)


@social_router.get('/google/callback')
async def callback_google(request: Request, db: Session = Depends(get_db)):
    token = await oauth.google.authorize_access_token(request)

    resp = await oauth.google.get('https://openidconnect.googleapis.com/v1/userinfo', token=token)
    profile = resp.json()

    email = profile.get('email')
    if not email:
        raise HTTPException(status_code=400, detail='Google не вернул email')

    user = get_or_create_social_user(
        db,
        email=email,
        first_name=profile.get('given_name', 'Unknown'),
        lastname=profile.get('family_name', 'Unknown'),
        username=email.split('@')[0],
    )
    return issue_tokens_for_user(db, user)
