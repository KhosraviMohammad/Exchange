import datetime
from Asymbol.models import Symbol
import pandas
import numpy


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
