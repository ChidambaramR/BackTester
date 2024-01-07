import pandas as pd
from yahoo_fin.stock_info import get_data
from datetime import datetime as dt


def get_stock_data(symbol, start_date, end_date):
    df = get_data(symbol, start_date=start_date, end_date=end_date)
    df.index = df.index.normalize()


get_stock_data("tcs.ns", dt.strptime('01/01/2023', '%m/%d/%Y'), dt.strptime('12/01/2023', '%m/%d/%Y'))
