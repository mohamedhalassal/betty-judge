import random
import re
from sqlmodel import select
from src.models.user import User

def generate_unique_username(email: str, session):
    base_username = email.split("@")[0].lower()

    base_username = re.sub(r"[^a-zA-Z0-9_]", "", base_username)

    if not base_username:
        base_username = "user"

    base_username = base_username[:10]

    while session.exec(
        select(User).where(User.username == username)
    ).first():

        username = f"{base_username}_{random.randint(1000,9999)}"

    return username