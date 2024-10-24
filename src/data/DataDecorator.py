from ta import add_all_ta_features

from data.DataFetcher import get_stock_data
from data.candles.CandleStickPatterns import recognize_candlestick


def get_stock_data_with_decorations(symbol, start_date, end_date):
    data = get_stock_data(symbol, start_date, end_date)
    data = add_all_ta_features(data, 'open', 'high', 'low', 'close', 'volume')
    data = recognize_candlestick(data)
    print(data.head())
