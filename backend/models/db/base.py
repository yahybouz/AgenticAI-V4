"""
Base SQLAlchemy pour tous les modèles
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass
