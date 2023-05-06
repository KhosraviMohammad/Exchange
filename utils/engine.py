from django.conf import settings
import sqlalchemy


def create_postgres_engine():
    data_base = settings.DATABASES['default']
    NAME = data_base.get('NAME')
    USER = data_base.get('USER')
    PASSWORD = data_base.get('PASSWORD')
    HOST = data_base.get('HOST')
    engine = sqlalchemy.create_engine(fr'postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:5432/{NAME}')
    return engine
