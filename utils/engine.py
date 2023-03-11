import sqlalchemy


def create_sqlite_engine(*, path):
    engine = sqlalchemy.create_engine(fr'sqlite:///{path}')
    return engine