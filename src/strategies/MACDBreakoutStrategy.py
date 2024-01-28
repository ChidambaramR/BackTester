import logging

from ta import add_all_ta_features
from ta.utils import dropna
from src.Constants import CLOSE
from src.strategies.StrategyBase import Strategy


class MACDBreakout(Strategy):
    def __init__(self, symbol):
        super().__init__(symbol)

    def pre_condition(self, df):
        if len(df) <= 50:
            return False

        return True

    def execute(self, df):
        super().execute(df)

        df = df.copy()

        df = add_all_ta_features(df, 'open', 'high', 'low', 'close', 'volume')

        df.head()

