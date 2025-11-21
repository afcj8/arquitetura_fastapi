from datetime import datetime, timedelta
from dateutil import tz
from typing import Optional
from functools import partial
from jose import jwt
from task_manager_api.config import SECRET_KEY, ALGORITHM

def criar_access_token(
    data: dict, 
    expires_delta: Optional[timedelta] = None, 
    scope: str = "access_token"
) -> str:
    """Cria um token de acesso"""
    
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(tz=tz.tzutc()) + expires_delta
    else:
        expire = datetime.now(tz=tz.tzutc()) + timedelta(minutes=30)
    to_encode.update({"exp": expire, "scope": scope})
    encoded_jwt = jwt.encode(
        to_encode, 
        SECRET_KEY,  # pyright: ignore
        algorithm=ALGORITHM,  # pyright: ignore
    )
    return encoded_jwt

criar_refresh_token = partial(criar_access_token, scope="refresh_token")