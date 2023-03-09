from celery import shared_task
import requests
import time
import io
import pandas


@shared_task
def get_data_from_tsetmc_com():
    i = 0
    while True:
        i += 1
        response = requests.get('http://members.tsetmc.com/tsev2/excel/MarketWatchPlus.aspx?d=0')
        xlsx = io.BytesIO(response.content)
        df = pandas.read_excel(xlsx)
        df = df.iloc[2:, [0, 9]]
        df.to_excel(f"output{i}.xlsx")
        time.sleep(10)
