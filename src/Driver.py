from Constants import CLOSE
from data.DataFetcher import get_stock_data


def drive(symbol, strategy, start_date, end_date):
    data = get_stock_data(symbol, start_date, end_date)
    current_date = data.index[-1]
    current_close_price = data[CLOSE][-1]

    for index, row in data.iterrows():
        # Get rows up to the current index
        df = data.loc[:index]

        if strategy.pre_condition(df, current_date, current_close_price):
            strategy.execute(df, current_date, current_close_price)
