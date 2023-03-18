import datetime
import time

import finpy_tse as fpy
import numpy
import pandas
from django.db import connection
from django.db.models import Min, Max

from Asymbol.models import Symbol, Slope
from Exchange.celery import app
from utils.engine import create_sqlite_engine
from utils.task_functions import calculate_time_axis_point, \
    calculate_final_price_changes_from_Final_percent_and_Final_amount, \
    convert_date_time_str_list_to_date_time_obj_list

ENGINE = create_sqlite_engine(path='D:\programming\python\django\projects\Exchange\db.sqlite3')


def get_data_from_tsetmc_com():
    '''
    it is a task that gets symbol data from tsetmc.com and returns them

    :return:
    '''

    market_watch_data_frame = fpy.Get_MarketWatch(save_excel=False)[0]
    market_watch_data_frame['stored_date'] = datetime.datetime.now()

    cleaned_market_watch_data_frame = market_watch_data_frame[[
        'Name', 'Time', 'Final', 'Volume', 'Market', 'Sector', 'stored_date', 'Final(%)',
    ]]
    cleaned_market_watch_data_frame.columns = [
        'name', 'time', 'final_price_amount', 'volume', 'market', 'sector', 'stored_date', 'final_price_percent'
    ]
    final_price_change_list = calculate_final_price_changes_from_Final_percent_and_Final_amount(cleaned_market_watch_data_frame)
    cleaned_market_watch_data_frame['final_price_change'] = final_price_change_list
    cleaned_market_watch_data_frame.index.name = 'symbol_name'
    return cleaned_market_watch_data_frame


def calculate_slope(from_date, to_date):
    cursor = connection.cursor()
    sub_query = f'''
        WITH Asymbol_symbol_subquery AS (
            SELECT "id" as pk, symbol_name, to_seconds(CAST(stored_date as text)) as time, CAST(final_price_change as float) as price 
            from "Asymbol_symbol" 
            WHERE stored_date BETWEEN {from_date} AND {to_date}
        ), average_subquery AS (
            SELECT symbol_name, sum(CAST(time as float)) / count(time)  as avgx, sum(CAST(price as float)) / count(price) as avgy
            FROM Asymbol_symbol_subquery group by  symbol_name
        ), division as (
			SELECT Asymbol_symbol_subquery.symbol_name as symbol_name, 
			sum((Asymbol_symbol_subquery.time - avgx) * (Asymbol_symbol_subquery.price - average_subquery.avgy)) as face,
			sum((Asymbol_symbol_subquery.time - average_subquery.avgx) * (Asymbol_symbol_subquery.time - average_subquery.avgx)) as denominator
			FROM Asymbol_symbol_subquery
			join average_subquery on Asymbol_symbol_subquery.symbol_name = average_subquery.symbol_name
			group by Asymbol_symbol_subquery.symbol_name
		)
    '''
    query = '''
        SELECT division.symbol_name as symbol_name,
        cast ((division.face /(CASE  WHEN division.denominator=0   THEN Null else division.denominator END)) as integer)
        as  slope
        FROM division
    '''
    full_query = sub_query + query
    cursor.execute(full_query)
    symbol_slope_list = cursor.fetchall()
    slope_data_frame = pandas.DataFrame(symbol_slope_list, columns=['symbol_name', 'value'])
    slope_data_frame['from_date'] = from_date
    slope_data_frame['to_date'] = to_date
    return slope_data_frame


@app.task()
def manage_tasks():
    symbol_table_name = Symbol.objects.model._meta.db_table
    slope_table_name = Symbol.objects.model._meta.db_table
    time_start = datetime.datetime.now()
    while True:
        data_from_tsetmc_com = get_data_from_tsetmc_com()
        data_from_tsetmc_com.to_sql('{0}'.format(symbol_table_name), con=ENGINE, if_exists='append', index=True)
        time.sleep(3)
        time_delta = datetime.datetime.now() - time_start
        if time_delta.total_seconds() >= 300: # 5 min * 60 sec = 300 sec
            today_date_time = datetime.datetime.today()
            today_date = datetime.datetime(year=today_date_time.year, month=today_date_time.month, day=today_date_time.day)
            slope_qs = Slope.objects.filter(from_date__gte=today_date)
            if slope_qs.exists():
                from_date = slope_qs.aggregate(Max('stored_date'))
                to_date = from_date + datetime.timedelta(seconds=300)
            else:
                from_date = Symbol.objects.filter().aggregate(today_smallest_date=Min('stored_date'))['today_smallest_date']
                to_date = from_date + datetime.timedelta(seconds=300)
            slope_data_frame = calculate_slope(from_date=from_date, to_date=to_date)
            slope_data_frame.to_sql('{0}'.format(slope_table_name), con=ENGINE, if_exists='append', index=True)
            time_start = datetime.datetime.now()
