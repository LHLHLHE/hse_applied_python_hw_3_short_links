from fastapi import security
from passlib.context import CryptContext

reusable_oauth2 = security.HTTPBearer(auto_error=False)

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)
