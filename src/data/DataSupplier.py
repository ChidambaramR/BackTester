from DataFetcher import get_stock_data


def get_time_series_data(symbol, start_date, end_date):
    df = get_stock_data(symbol, start_date, end_date)

    for index, row in df.iterrows():
        cumulative_rows = df.loc[:index]  # Get rows up to the current index
        


