from enum import Enum


class UserRole(str, Enum):
    """Represents the different roles a user can have within the system.

    This Enum defines distinct roles such as student, teacher, and administrator,
    each associated with a string value for clear identification and usage across
    the application.
    """
    STUDENT = "STUDENT"
    TEACHER = "TEACHER"
    ADMIN = "ADMIN"
