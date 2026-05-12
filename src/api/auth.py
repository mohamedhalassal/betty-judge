from fastapi import APIRouter, HTTPException, Depends

from sqlmodel import Session, select
from src.database import engine,get_session
from src.models.user import User

from src.schemas.auth import GoogleLoginRequest

from src.core.google_auth import verify_google_token
from src.core.security import create_access_token

router = APIRouter()

