from passlib.context import CryptContext
from jose import jwt

SECRET_KEY = "CHANGE_THIS_LATER"
ALGORITHM = "HS256"
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def hash_password(password):
    return pwd_context.hash(password)

def verify_password(password, password_hash):
    return pwd_context.verify(
      
        password,
        password_hash
    )

def create_access_token(user_id):
    payload = {
        "user_id": user_id
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token