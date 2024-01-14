import pandas as pd
import openpyxl
from yahoo_fin.stock_info import get_data
from datetime import datetime as dt


def get_stock_data(symbol, start_date, end_date):
    df = get_data(symbol, start_date=start_date, end_date=end_date)
    df.drop(columns=['ticker'], inplace=True)
    df.index = df.index.date
    return df


def save_data_for_local_use(symbol, start_date, end_date):
    _df = get_stock_data(symbol, start_date, end_date)

    file_path = "/Users/chidr/PycharmProjects/BackTester/tests/test_data/raw/TCS_one_year_23_24.xlsx"
    _df.to_excel(file_path)

    # Read back and make sure we have saved correctly
    _df = pd.read_excel(file_path, index_col=0)
    _df.index = _df.index.date
    return _df


# df = save_data_for_local_use("tcs.ns", dt.strptime('01/01/2023', '%m/%d/%Y'), dt.strptime('12/01/2023', '%m/%d/%Y'))