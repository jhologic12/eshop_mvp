# backend/app/core/base_uuid.py
import uuid
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.declarative import declared_attr
from app.core.database import Base

class UUIDMixin:
    """Mixin base que define un campo id UUID universal."""
    @declared_attr
    def id(cls):
        return Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
