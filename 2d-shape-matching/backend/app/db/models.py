from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Image(Base):
    """
    SQLAlchemy model for storing shape metadata.
    """

    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    img_name = Column(String, nullable=False, index=True)
    img_src = Column(String, nullable=False)
    extracted_features = Column(JSONB, nullable=True)



