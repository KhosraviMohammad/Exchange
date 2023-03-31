import sqlalchemy


def create_sqlite_engine():
    engine = sqlalchemy.create_engine(fr'postgresql+psycopg2://postgres:amir@localhost:5432/test')
    return engine