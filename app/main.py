from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from .database import SessionLocal, engine
from . import models, schemas, auth, hash
import string
import random
from datetime import datetime, timezone, timedelta
from fastapi.responses import RedirectResponse
from .config import SECRET, ALG
from jose import JWTError, jwt
import pytz


tz = pytz.timezone('Europe/Moscow')

SECRET_KEY = SECRET
ALGORITHM = ALG

ACCESS_TOKEN_EXPIRE_MINUTES = 30
INACTIVITY_DAYS = 30

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user = db.query(models.User).filter(models.User.username == username).first()
        if user is None:
            raise HTTPException(status_code=401, detail="Not authorized")
        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="Not authorized")


def generate_link_short_code():
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(6))


@app.get("/")
async def root_message():
    return {"message": "Добро пожаловать на API-сервис сокращения ссылок!"}


@app.post("/register")
async def register(user: schemas.User, db: Session = Depends(get_db)):
    user_in_db = db.query(models.User).filter(models.User.username == user.username).first()
    if user_in_db:
        raise HTTPException(status_code=400, detail="User with this username already exist")

    hashed_password = hash.hash_password(user.password)
    created_user = models.User(username=user.username, email=user.email, password=hashed_password)

    db.add(created_user)
    db.commit()
    db.refresh(created_user)

    return {"message": "User created successfully"}


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Not authorized")

    password_is_correct = hash.verify_password(form_data.password, user.password)
    if not password_is_correct:
        raise HTTPException(status_code=401, detail="Not authorized")

    access_token = auth.create_access_token(user.username)
    return {"access_token": access_token}


@app.post("/links/shorten")
async def shorten_link(link_create: schemas.LinkCreate, db: Session = Depends(get_db)):
    if link_create.custom_alias:
        short_code = link_create.custom_alias
        link = db.query(models.Link).filter(models.Link.short_code == short_code).first()
        if link is not None:
            raise HTTPException(status_code=400, detail="Short code already exist")
    else:
        short_code = generate_link_short_code()
        link = db.query(models.Link).filter(models.Link.short_code == short_code).first()
        while link is not None:
            short_code = generate_link_short_code()
            link = db.query(models.Link).filter(models.Link.short_code == short_code).first()

    expires_at = link_create.expires_at
    original_url = link_create.original_url

    link_with_short_code = models.Link(
        original_url=original_url,
        short_code=short_code,
        created_at=datetime.strptime(datetime.now(tz).strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M"),
        expires_at=expires_at
    )

    db.add(link_with_short_code)
    db.commit()
    db.refresh(link_with_short_code)

    return {"message" : "Link successfully created", "original_url" : original_url, "short_code": short_code}


@app.get("/links/{short_code}")
async def redirect_link(short_code: str, db: Session = Depends(get_db)):
    link = db.query(models.Link).filter(models.Link.short_code == short_code).first()

    if link is None:
        raise HTTPException(status_code=404, detail="Link not found")

    link.access_count += 1
    link.last_accessed_at = datetime.strptime(datetime.now(tz).strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M")
    db.commit()

    if ((link.expires_at is not None) and (link.expires_at < datetime.strptime(datetime.now(tz).strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M"))):
        raise HTTPException(status_code=400, detail="Link expired")

    original_url = link.original_url

    if ((original_url[:8] != 'https://') and (original_url[:7] != 'http://')):
        original_url = 'http://' + original_url

    return RedirectResponse(url=original_url)


@app.delete("/links/{short_code}")
async def delete_link(short_code: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    link = db.query(models.Link).filter(models.Link.short_code == short_code).first()
    if link is None:
        raise HTTPException(status_code=404, detail="Link not found")

    db.delete(link)
    db.commit()

    return {"message": "Link successfully deleted"}


@app.put("/links/{short_code}")
async def update_link(link_update_data: schemas.LinkUpdate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    short_code_old = link_update_data.short_code_old
    short_code_new = link_update_data.short_code_new

    link = db.query(models.Link).filter(models.Link.short_code == short_code_old).first()
    if link is None:
        raise HTTPException(status_code=404, detail="Link not found")

    link.short_code = short_code_new
    db.commit()

    return {"message" : "short_code updated successfully", "original_url" : link.original_url, "short_code" : link.short_code}


@app.get("/links/{short_code}/stats")
async def get_link_stats(short_code: str, db: Session = Depends(get_db)):
    link = db.query(models.Link).filter(models.Link.short_code == short_code).first()
    if link is None:
        raise HTTPException(status_code=404, detail="Link not found")

    return {
        "original_url" : link.original_url,
        "short_code" : link.short_code,
        "created_at" : link.created_at.strftime("%Y-%m-%d %H:%M"),
        "last_accessed_at" : link.last_accessed_at.strftime("%Y-%m-%d %H:%M") if link.last_accessed_at is not None else link.last_accessed_at,
        "expires_at": link.expires_at.strftime("%Y-%m-%d %H:%M") if link.expires_at is not None else link.expires_at,
        "access_count" : link.access_count,
    }


@app.get("/links/search/link")
async def search_link(original_url: str, db: Session = Depends(get_db)):
    link = db.query(models.Link).filter(models.Link.original_url == original_url).first()
    if link is None:
        raise HTTPException(status_code=404, detail="Link not found")

    return {"short_code": link.short_code}


@app.delete("/links/remove_unused/links")
async def remove_unused_links(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    unused_links = db.query(models.Link).filter(
        or_(
            models.Link.last_accessed_at.is_(None),
            models.Link.last_accessed_at < datetime.strptime((datetime.now(tz) - timedelta(days=INACTIVITY_DAYS)).strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M")
        )
    ).all()
    unused_links_ids = [link.id for link in unused_links]

    if unused_links_ids:
        db.query(models.Link).filter(models.Link.id.in_(unused_links_ids)).delete(synchronize_session=False)
        db.commit()
        return {"message": f"Deleted {len(unused_links_ids)} unused links"}
    else:
        return {"message": "There are no unused links"}


@app.get("/links/expired/links", response_model=list)
async def get_expired_links(db: Session = Depends(get_db)):
    expired_links = db.query(models.Link).filter(
        and_(
            models.Link.expires_at.isnot(None),
            models.Link.expires_at < datetime.strptime(datetime.now(tz).strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M"),
        )
    ).all()

    expired_links_list = []
    for expired_link in expired_links:
        expired_links_list.append(
            {
                "original_url": expired_link.original_url,
                "short_code": expired_link.short_code,
                "created_at": expired_link.created_at.strftime("%Y-%m-%d %H:%M"),
                "expires_at": expired_link.expires_at.strftime("%Y-%m-%d %H:%M")
            }
        )

    return expired_links_list
