# application/services/user_auth_service.py
# Purpose: Handles user registration, authentication, and JWT token creation

from core.db_infrastructure.db_components.schemas import UserRead
import bcrypt
from datetime import datetime, timedelta
from jose import jwt
import os
from dotenv import load_dotenv


# ========================
# AUTH CONFIGURATION
# ========================
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# ========================
# EXCEPTIONS
# ========================
class UserAlreadyExistsError(Exception):
    """Raised when attempting to register an existing user."""
    pass


class InvalidCredentialsError(Exception):
    """Raised when login credentials are invalid."""
    pass


# ========================
# AUTH SERVICE
# ========================
class AuthService:
    """
    Handles user registration and authentication.

    Responsibilities:
    - Register users (with hashed passwords)
    - Verify login credentials
    - Issue JWT access tokens

    Does NOT:
    - Handle HTTP logic
    - Manage DB sessions directly
    """

    def __init__(self, db_interface):
        self.db = db_interface

    # ------------------------
    # REGISTER
    # ------------------------

    def register_user(self, email, password):
        """
        Create a new user.

        Behavior:
        - First registered user is assigned role = "primary"
        - All subsequent users are assigned role = "user"

        Steps:
        1. Normalize email (case-insensitive handling)
        2. Check if user already exists
        3. Determine role based on existing users
        4. Hash password
        5. Persist user via DB layer
        """

        # Normalize email to ensure consistent lookup
        email = email.lower()

        # Prevent duplicate registrations
        existing_user = self.db.get_user_by_email(email)
        if existing_user:
            raise UserAlreadyExistsError("User already exists")

        # Determine role:
        # - If no users exist → this becomes the primary user
        # - Otherwise → standard user
        existing_users = self.db.get_all_users()
        role = "primary" if not existing_users else "user"

        # Hash password before storing
        hashed_password = self._hash_password(password)

        # Create user in database with assigned role
        user = self.db.create_user(email, hashed_password, role)

        # Return validated schema (safe for API response)
        return UserRead.model_validate(user)

    # ------------------------
    # LOGIN
    # ------------------------
    def login_user(self, email, password):
        """
        Authenticate a user and return a JWT token.

        Steps:
        - Normalize email
        - Retrieve user
        - Verify password
        - Issue access token
        """
        email = email.lower()

        user = self.db.get_user_by_email(email)
        if not user:
            raise InvalidCredentialsError("Invalid email or password")

        if not self._verify_password(password, user.hashed_password):
            raise InvalidCredentialsError("Invalid email or password")

        token = self._create_access_token({"sub": user.email})

        return {
            "access_token": token,
            "token_type": "bearer"
        }

    # ------------------------
    # TOKEN
    # ------------------------
    def _create_access_token(self, data: dict):
        """
        Create a signed JWT token.

        Adds:
        - expiration (exp)
        """
        to_encode = data.copy()

        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})

        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    # ------------------------
    # PASSWORD
    # ------------------------
    def _hash_password(self, password):
        """Hash a plaintext password using bcrypt."""
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def _verify_password(self, password, hashed_password):
        """Verify a plaintext password against a stored hash."""
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))