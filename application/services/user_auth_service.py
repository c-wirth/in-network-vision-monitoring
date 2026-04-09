from core.db_infrastructure.db_components.schemas import UserRead
import bcrypt


class UserAlreadyExistsError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class AuthService:
    """
    Handles user authentication logic.
    """

    def __init__(self, db_interface):
        self.db = db_interface

    # ------------------------
    # REGISTER
    # ------------------------
    def register_user(self, email, password):
        email = email.lower()
        existing_user = self.db.get_user_by_email(email)
        if existing_user:
            raise UserAlreadyExistsError("User already exists")

        hashed_password = self._hash_password(password)

        user = self.db.create_user(email, hashed_password)

        return UserRead.model_validate(user)

    # ------------------------
    # LOGIN
    # ------------------------
    def login_user(self, email, password):
        email = email.lower()
        user = self.db.get_user_by_email(email)

        if not user:
            raise InvalidCredentialsError("Invalid email or password")

        if not self._verify_password(password, user.hashed_password):
            raise InvalidCredentialsError("Invalid email or password")

        return UserRead.model_validate(user)

    # ------------------------
    # INTERNAL
    # ------------------------
    def _hash_password(self, password):
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def _verify_password(self, password, hashed_password):
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))