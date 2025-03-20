from datetime import datetime, timezone, timedelta
from jose import jwt
from .config import SECRET, ALG


SECRET_KEY = SECRET
ALGORITHM = ALG
ACCESS_TOKEN_EXPIRE_IN_MINUTES = 30

def create_access_token(username: str):
    data = {"sub" : username}
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_IN_MINUTES)
    data["exp"] = expire
    encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

