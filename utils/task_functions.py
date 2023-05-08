import datetime

from django.db import connection
from django.core.cache import cache
from django.db.models import Max, Q

import pandas

from Asymbol.models import Symbol


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
        final_price_change_list.append((row[0], final_price_change))

    final_price_change_data_frame = pandas.DataFrame(final_price_change_list, columns=[data_frame.index.name, 'final_price_change'])
    final_price_change_data_frame.set_index(data_frame.index.name, inplace=True)
    return final_price_change_data_frame


def calculate_slope(from_date, to_date):
    with connection.cursor() as cursor:
        sub_query = f'''
            WITH Asymbol_symbol_subquery AS (
                SELECT "id" as pk, symbol_name, to_seconds(CAST(time as text)) as time, CAST(final_price_change as float) as price 
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
    slope_data_frame['from_date'] = from_date
    slope_data_frame['to_date'] = to_date
    return slope_data_frame


def get_limit_date_time():
    limit_date_time = None
    calculated_until_date_time = cache.get('calculated_until_date_time')
    today_date = datetime.datetime.today().date()
    today_biggest_date = Symbol.objects.filter(
        (Q(stored_date__gt=calculated_until_date_time or today_date) & Q(stored_date__gte=today_date))).aggregate(
        today_biggest_date=Max('stored_date'))['today_biggest_date']
    if today_biggest_date is None:
        limit_date_time = None
    elif today_biggest_date is not None and calculated_until_date_time is None:
        limit_date_time = (today_biggest_date, today_date)
        cache.set('calculated_until_date_time', today_biggest_date)
    elif today_biggest_date is not None and calculated_until_date_time is not None:
        limit_date_time = (today_biggest_date, calculated_until_date_time)
        cache.set('calculated_until_date_time', today_biggest_date)
    return limit_date_time
