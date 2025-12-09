# W7_lab/__init__.py

"""
Week 7 Lab - Authentication Module
Provides secure user authentication with bcrypt
"""

from .auth import (
    register_user,
    login_user,
    verify_password,
    check_password_strength,
    validate_username,
    validate_password
)

__all__ = [
    'register_user',
    'login_user', 
    'verify_password',
    'check_password_strength',
    'validate_username',
    'validate_password'
]