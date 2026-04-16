"""
Users Router - CRUD endpoints for user management.
"""

import logging
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status

from grilo_admin.auth import (
    create_access_token,
    get_current_user,
    get_password_hash,
    require_role,
    user_store,
    verify_password,
)
from grilo_admin.models import (
    Token,
    User,
    UserCreate,
    UserLogin,
    UserRole,
    UserUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])


class UserManager:
    """Manages user operations."""

    async def create_user(self, user_data: UserCreate) -> Optional[User]:
        """Create a new user."""
        user_id = str(uuid.uuid4())
        password_hash = get_password_hash(user_data.password)

        success = user_store.add_user(
            user_id=user_id,
            email=user_data.email,
            password_hash=password_hash,
            role=user_data.role,
        )

        if not success:
            return None

        user_dict = user_store.get_by_id(user_id)
        return self._dict_to_user(user_dict)

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        user_dict = user_store.get_by_id(user_id)
        if user_dict:
            return self._dict_to_user(user_dict)
        return None

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        user_dict = user_store.get_by_email(email)
        if user_dict:
            return self._dict_to_user(user_dict)
        return None

    async def update_user(self, user_id: str, updates: UserUpdate) -> Optional[User]:
        """Update user fields."""
        updates_dict = {}
        if updates.email is not None:
            updates_dict["email"] = updates.email
        if updates.role is not None:
            updates_dict["role"] = updates.role.value
        if updates.is_active is not None:
            updates_dict["is_active"] = updates.is_active
        if updates.password is not None:
            updates_dict["password_hash"] = get_password_hash(updates.password)

        if updates_dict:
            success = user_store.update(user_id, updates_dict)
            if success:
                user_dict = user_store.get_by_id(user_id)
                return self._dict_to_user(user_dict)
        return None

    async def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        return user_store.delete(user_id)

    async def list_users(self) -> list[User]:
        """List all users."""
        users = []
        for user_dict in user_store.list_all():
            users.append(self._dict_to_user(user_dict))
        return users

    def _dict_to_user(self, d: dict) -> User:
        """Convert stored dict to User model."""
        return User(
            id=d["id"],
            email=d["email"],
            role=UserRole(d["role"]),
            is_active=d["is_active"],
            created_at=d["created_at"],
            updated_at=d["updated_at"],
            last_login=d.get("last_login"),
        )


user_manager = UserManager()


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """
    Authenticate user and return JWT token.
    """
    user_dict = user_store.get_by_email(credentials.email)

    if not user_dict:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(credentials.password, user_dict["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user_dict["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )

    user_store.update(user_dict["id"], {"last_login": datetime.now()})

    token, expires_in = create_access_token(
        user_id=user_dict["id"],
        email=user_dict["email"],
        role=UserRole(user_dict["role"]),
    )

    user = user_manager._dict_to_user(user_dict)

    return Token(
        access_token=token,
        token_type="bearer",
        expires_in=expires_in,
        user=user,
    )


@router.get("/me", response_model=User)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user.
    """
    return current_user


@router.get("", response_model=list[User])
async def list_users(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    List all users. Admin only.
    """
    return await user_manager.list_users()


@router.post("", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Create a new user. Admin only.
    """
    user = await user_manager.create_user(user_data)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    logger.info(f"User created: {user.email} by {current_user.email}")
    return user


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: str,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Get user by ID. Admin only.
    """
    user = await user_manager.get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: str,
    updates: UserUpdate,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Update user. Admin only.
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update your own account via this endpoint",
        )

    user = await user_manager.update_user(user_id, updates)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    logger.info(f"User updated: {user_id} by {current_user.email}")
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Delete user. Admin only.
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )

    deleted = await user_manager.delete_user(user_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    logger.info(f"User deleted: {user_id} by {current_user.email}")
