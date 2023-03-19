import datetime
import finpy_tse as fpy
import pandas
from django.db import connection

def convert_date_time_str_list_to_date_time_obj_list(time_list, format):
    date_time_obj_list = []
    for time_in_str in time_list:
        date_time_obj = datetime.datetime.strptime(time_in_str, format)
        date_time_obj_list.append(date_time_obj)
    return date_time_obj_list


def calculate_time_axis_point(date_time_obj_list):
    time_axis_point_list = [0]
    for index, date_time_obj in enumerate(date_time_obj_list):
        if len(date_time_obj_list) > index + 1:
            next_date_time_obj = date_time_obj_list[index + 1]
            time_delta_obj = next_date_time_obj - date_time_obj
            total_second = time_delta_obj.total_seconds()
            time_point = time_axis_point_list[index] + total_second
            time_axis_point_list.append(time_point)
        else:
            break
    return time_axis_point_list


def calculate_final_price_changes_from_Final_percent_and_Final_amount(data_frame):
    '''
    calculates finale price changes for data frame that has final_price_percent and final_price_amount

    :param data_frame:
    :return: final_price_change_list
    '''
    final_price_change_list = []
    for row in data_frame.iterrows():
        final_price_percent = (float(row[1]['final_price_percent']) / 100)
        final_price_amount = float(row[1]['final_price_amount'])
        denominator = (1 + final_price_percent)
        if denominator == 0:
            final_price_change = None
        else:
            final_price_change = (final_price_amount * final_price_percent) / denominator
        final_price_change_list.append(final_price_change)
    return final_price_change_list


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
            WHERE stored_date BETWEEN '{from_date}' AND '{to_date}'
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
        cast ((division.face /(CASE  WHEN division.denominator=0   THEN Null else division.denominator END)) as float)
        as  slope
        FROM division
    '''
    full_query = sub_query + query
    cursor.execute(full_query)
    symbol_slope_list = cursor.fetchall()
    slope_data_frame = pandas.DataFrame(symbol_slope_list, columns=['symbol_name', 'value'])
    slope_data_frame['value'] = slope_data_frame['value'].round(decimals=2)
    if len(symbol_slope_list) == 0:
        slope_data_frame = slope_data_frame.append({'symbol_name': None, 'value': None}, ignore_index=True)
    slope_data_frame['from_date'] = from_date
    slope_data_frame['to_date'] = to_date
    return slope_data_frame