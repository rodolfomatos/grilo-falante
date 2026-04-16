"""
Admin Authentication Module.

Provides JWT-based authentication for the admin back-office.
Supports:
- Local authentication (username/password)
- JWT token generation and validation
- Password hashing with bcrypt
"""

import hashlib
import logging
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from grilo_admin.models import TokenData, User, UserRole

logger = logging.getLogger(__name__)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

security = HTTPBearer()


def get_jwt_secret() -> str:
    """Get JWT secret from environment or generate default."""
    secret = os.getenv("GRILO_ADMIN_JWT_SECRET", "dev-secret-change-in-production")
    if secret == "dev-secret-change-in-production":
        logger.warning("Using default JWT secret. Set GRILO_ADMIN_JWT_SECRET in production.")
    return secret


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash using SHA256 with salt."""
    if ":" not in hashed_password:
        return False
    salt, stored_hash = hashed_password.split(":", 1)
    computed = hashlib.sha256((salt + plain_password).encode()).hexdigest()
    return secrets.compare_digest(computed, stored_hash)


def get_password_hash(password: str) -> str:
    """Hash a password using SHA256 with random salt."""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}:{password_hash}"


def create_access_token(user_id: str, email: str, role: UserRole) -> tuple[str, int]:
    """
    Create a JWT access token.

    Returns:
        Tuple of (token, expires_in_seconds)
    """
    secret = get_jwt_secret()
    expires_delta = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    expire = datetime.now(timezone.utc) + expires_delta

    to_encode = {
        "sub": user_id,
        "email": email,
        "role": role.value,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }

    encoded_jwt = jwt.encode(to_encode, secret, algorithm=ALGORITHM)
    return encoded_jwt, int(expires_delta.total_seconds())


def decode_token(token: str) -> Optional[TokenData]:
    """
    Decode and validate a JWT token.

    Returns:
        TokenData if valid, None if invalid
    """
    secret = get_jwt_secret()

    try:
        payload = jwt.decode(token, secret, algorithms=[ALGORITHM])

        user_id = payload.get("sub")
        email = payload.get("email")
        role_str = payload.get("role")
        exp = payload.get("exp")

        if not all([user_id, email, role_str, exp]):
            return None

        return TokenData(
            user_id=user_id,
            email=email,
            role=UserRole(role_str),
            exp=datetime.fromtimestamp(exp, tz=timezone.utc),
        )

    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """
    FastAPI dependency to get the current authenticated user.

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    token_data = decode_token(token)

    if token_data is None:
        raise credentials_exception

    from grilo_admin.routers.users import UserManager

    user_manager = UserManager()
    user = await user_manager.get_user_by_id(token_data.user_id)

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )

    return user


def require_role(required_role: UserRole):
    """
    FastAPI dependency factory that requires a specific role.

    Usage:
        @app.get("/admin-only")
        async def admin_only(user: User = Depends(require_role(UserRole.ADMIN))):
            ...
    """
    async def role_checker(user: User = Depends(get_current_user)) -> User:
        role_hierarchy = {
            UserRole.ADMIN: 3,
            UserRole.OPERATOR: 2,
            UserRole.VIEWER: 1,
        }

        if role_hierarchy.get(user.role, 0) < role_hierarchy.get(required_role, 0):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role.value}' or higher required",
            )
        return user

    return role_checker


class InMemoryUserStore:
    """
    Simple in-memory user store for development.

    In production, this should be replaced with PostgreSQL.
    """

    def __init__(self):
        self._users: dict[str, dict] = {}
        self._by_email: dict[str, str] = {}
        self._initialized = False

    def initialize_defaults(self):
        """Create default admin user if no users exist."""
        if not self._users:
            admin_id = "default-admin"
            admin_hash = get_password_hash("admin123")
            self._users[admin_id] = {
                "id": admin_id,
                "email": "admin@example.com",
                "password_hash": admin_hash,
                "role": UserRole.ADMIN.value,
                "is_active": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "last_login": None,
            }
            self._by_email["admin@example.com"] = admin_id
            logger.info("Created default admin user: admin@example.com / admin123")

    def add_user(
        self,
        user_id: str,
        email: str,
        password_hash: str,
        role: UserRole,
    ) -> bool:
        """Add a new user."""
        if email in self._by_email:
            return False

        self._users[user_id] = {
            "id": user_id,
            "email": email,
            "password_hash": password_hash,
            "role": role.value,
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "last_login": None,
        }
        self._by_email[email] = user_id
        return True

    def get_by_id(self, user_id: str) -> Optional[dict]:
        """Get user by ID."""
        return self._users.get(user_id)

    def get_by_email(self, email: str) -> Optional[dict]:
        """Get user by email."""
        user_id = self._by_email.get(email)
        if user_id:
            return self._users.get(user_id)
        return None

    def update(self, user_id: str, updates: dict) -> bool:
        """Update user fields."""
        if user_id not in self._users:
            return False

        user = self._users[user_id]

        if "email" in updates and updates["email"] != user["email"]:
            if updates["email"] in self._by_email:
                return False
            del self._by_email[user["email"]]
            self._by_email[updates["email"]] = user_id

        user.update(updates)
        user["updated_at"] = datetime.now()
        return True

    def delete(self, user_id: str) -> bool:
        """Delete a user."""
        if user_id not in self._users:
            return False

        user = self._users[user_id]
        del self._by_email[user["email"]]
        del self._users[user_id]
        return True

    def list_all(self) -> list[dict]:
        """List all users."""
        return list(self._users.values())


user_store = InMemoryUserStore()
user_store.initialize_defaults()
