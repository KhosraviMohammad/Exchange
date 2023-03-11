import datetime

from celery import shared_task
import requests
import time
import io
import pandas
from Asymbol.models import Symbol

from utils.engine import create_sqlite_engine

ENGINE = create_sqlite_engine(path='D:\programming\python\django\projects\Exchange\db.sqlite3')

@shared_task
def get_data_from_tsetmc_com():
    while True:
        response = requests.get('http://members.tsetmc.com/tsev2/excel/MarketWatchPlus.aspx?d=0')
        xlsx = io.BytesIO(response.content)
        df = pandas.read_excel(xlsx)
        df = df.iloc[2:, [0,3, 11, 19]]
        df.columns = ['name', 'volume', 'final_price', 'price']
        df['stored_date'] = datetime.datetime.now()
        table_name = Symbol.objects.model._meta.db_table
        df.to_sql('{0}'.format(table_name), con=ENGINE, if_exists='append', index=False)
        time.sleep(5)

