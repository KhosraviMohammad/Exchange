import datetime
from builtins import enumerate

from celery import shared_task
import requests
import time
import io
import pandas
import numpy
from django.db.models import Count, F

from Asymbol.models import Symbol

from utils.engine import create_sqlite_engine
from utils.task_functions import calculate_time_axis
import finpy_tse as fpy


ENGINE = create_sqlite_engine(path='D:\programming\python\django\projects\Exchange\db.sqlite3')


@shared_task
def get_data_from_tsetmc_com():
    response = requests.get('http://members.tsetmc.com/tsev2/excel/MarketWatchPlus.aspx?d=0')
    xlsx = io.BytesIO(response.content)
    df = pandas.read_excel(xlsx)
    df = df.iloc[2:, [0,3, 11, 19]]
    df.columns = ['name', 'volume', 'final_price', 'price']
    df['stored_date'] = datetime.datetime.now()
    table_name = Symbol.objects.model._meta.db_table
    df.to_sql('{0}'.format(table_name), con=ENGINE, if_exists='append', index=False)

@shared_task
def calculate_slope():
    # calculate x axis
    time_axis_point_list = calculate_time_axis()

    # calculate y axis
    symbol_qs = Symbol.objects.all()
    data_frame = pandas.DataFrame(list(symbol_qs.values('name', 'final_price')))
    data_frame = data_frame.astype({'final_price': 'float'})
    data_frame = data_frame.groupby('name')['final_price'].apply(list).reset_index(name='final_prices')
    final_prices_data_frame = data_frame.iloc[:, [1]]
    prices_list = []
    for prices in final_prices_data_frame['final_prices']:
        prices_list.append(prices)
    final_price_axis_point_list = numpy.array(prices_list).T
    slope = numpy.polyfit(time_axis_point_list, final_price_axis_point_list, 1)[0]
    slope = slope.reshape(len(slope), 1)
    data_frame['slope'] = slope

    return 1
