import datetime
import time
from django.db.models import Min, Max

from Asymbol.models import Symbol, Slope
from Exchange.celery import app
from utils.engine import create_sqlite_engine
from utils.task_functions import calculate_slope, calculate_final_price_changes_from_Final_percent_and_Final_amount, \
    get_limit_date_time

import finpy_tse as fpy

ENGINE = create_sqlite_engine()


@app.task()
def get_data_from_tsetmc_com():
    '''
    it is a task that gets symbol data from tsetmc.com and store them

    :return:
    '''

    symbol_table_name = Symbol.objects.model._meta.db_table
    market_watch_data_frame = fpy.Get_MarketWatch(save_excel=False)[0]
    market_watch_data_frame['stored_date'] = datetime.datetime.now()

    cleaned_market_watch_data_frame = market_watch_data_frame[[
        'Name', 'Time', 'Final', 'Volume', 'Market', 'Sector', 'stored_date', 'Final(%)',
    ]]
    cleaned_market_watch_data_frame.columns = [
        'name', 'time', 'final_price_amount', 'volume', 'market', 'sector', 'stored_date', 'final_price_percent'
    ]
    final_price_change_list = calculate_final_price_changes_from_Final_percent_and_Final_amount(
        cleaned_market_watch_data_frame)
    cleaned_market_watch_data_frame['final_price_change'] = final_price_change_list
    cleaned_market_watch_data_frame.index.name = 'symbol_name'
    cleaned_market_watch_data_frame.to_sql('{0}'.format(symbol_table_name), con=ENGINE, if_exists='append', index=True)


@app.task()
def manage_slope():
    slope_table_name = Slope.objects.model._meta.db_table
    range_date_time = get_limit_date_time()
    if range_date_time is not None:
        to_date, from_date = range_date_time
        slope_data_frame = calculate_slope(from_date=from_date, to_date=to_date)
        slope_data_frame['value'] = slope_data_frame['value'].round(decimals=2)
        slope_data_frame.to_sql('{0}'.format(slope_table_name), con=ENGINE, if_exists='append', index=False)
