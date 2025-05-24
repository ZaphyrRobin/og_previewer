from database.enums import URLStatus
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func


Base = declarative_base()

class URLRecord(Base):
    """
    url_records table schema
    # To improve later: add more indexing based on use cases to speed up the query.
    """
    __tablename__ = "url_records"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, nullable=False) # user input url
    image_url = Column(String, nullable=True) # og tag scrapped image_url
    status = Column(String, default=URLStatus.PENDING.value, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
