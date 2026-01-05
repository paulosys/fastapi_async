from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from settings import Settings

_engine = create_engine(Settings().DATABASE_URL)


def get_session():
    with Session(_engine) as session:
        yield session
