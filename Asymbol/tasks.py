import datetime
import time
from django.db.models import Min, Max

from Asymbol.models import Symbol, Slope
from Exchange.celery import app
from utils.engine import create_sqlite_engine
from utils.task_functions import calculate_slope, get_data_from_tsetmc_com

ENGINE = create_sqlite_engine(path='D:\programming\python\django\projects\Exchange\db.sqlite3')


@app.task()
def manage_tasks():
    symbol_table_name = Symbol.objects.model._meta.db_table
    slope_table_name = Slope.objects.model._meta.db_table
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
                from_date = slope_qs.aggregate(last_date_slop=Max('to_date'))['last_date_slop']
                to_date = from_date + datetime.timedelta(seconds=300)
            else:
                from_date = Symbol.objects.filter(stored_date__gte=today_date.date()).aggregate(today_smallest_date=Min('stored_date'))['today_smallest_date']
                to_date = from_date + datetime.timedelta(seconds=300)
            slope_data_frame = calculate_slope(from_date=from_date, to_date=to_date)
            slope_data_frame['value'] = slope_data_frame['value'].round(decimals=2)
            if len(slope_data_frame) == 0:
                slope_data_frame = slope_data_frame.append({'symbol_name': None, 'value': None}, ignore_index=True)
            slope_data_frame.to_sql('{0}'.format(slope_table_name), con=ENGINE, if_exists='append', index=False)
            time_start = datetime.datetime.now()
