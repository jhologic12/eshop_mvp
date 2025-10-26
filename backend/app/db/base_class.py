import uuid
from sqlalchemy import Column, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class BaseUUID:
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
