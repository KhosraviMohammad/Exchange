import datetime
import io
import time

import pandas
import requests
from django.db.models import Min, Max

from Asymbol.models import Symbol, Slope
from Exchange.celery import app
from utils.engine import create_postgres_engine
from utils.task_functions import calculate_slope, calculate_final_price_changes_from_Final_percent_and_Final_amount, \
    get_limit_date_time

import finpy_tse as fpy

ENGINE = create_postgres_engine()


@app.task()
def get_data_from_tsetmc_com():
    '''
    it is a task that gets symbol data from tsetmc.com and store them

    :return:
    '''
    response = requests.get('http://members.tsetmc.com/tsev2/excel/MarketWatchPlus.aspx?d=0')
    xlsx = io.BytesIO(response.content)
    df = pandas.read_excel(xlsx)
    df = df.iloc[2:, [0, 3, 11, 19]]
    df.columns = ['symbol_name', 'volume', 'final_price_change', 'price']
    df['stored_date'] = datetime.datetime.now()
    table_name = Symbol.objects.model._meta.db_table
    df.to_sql('{0}'.format(table_name), con=ENGINE, if_exists='append', index=False)
    print('fetching data')


@app.task()
def manage_slope():
    slope_table_name = Slope.objects.model._meta.db_table
    range_date_time = get_limit_date_time()
    if range_date_time is not None:
        to_date, from_date = range_date_time
        slope_data_frame = calculate_slope(from_date=from_date, to_date=to_date)
        indexes_to_round = slope_data_frame.loc[slope_data_frame['value'].notnull()].index
        slope_data_frame.loc[indexes_to_round, 'value'] = slope_data_frame.loc[slope_data_frame['value'].notnull()].round(decimals=2)['value']

        slope_data_frame.to_sql('{0}'.format(slope_table_name), con=ENGINE, if_exists='append', index=False)
