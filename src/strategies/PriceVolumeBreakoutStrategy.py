import logging

from src.Constants import CLOSE
from src.strategies.StrategyBase import Strategy


class PriceVolumeBreakout(Strategy):
    """
    credits: https://python.plainenglish.io/coding-stock-breakouts-in-python-a-step-by-step-guide-592211e36774
    """
    def __init__(self, symbol):
        super().__init__(symbol)

    def pre_condition(self, df):
        if len(df) <= 20:
            return False

        return True

    def execute(self, df):
        super().execute(df)

        df = df.copy()

        # Get the length of candle's body (from open to close)
        df['O-to-C'] = df['close'] - df['open']

        # Get the maximum OC compared to the recent 10 candles
        df['MaxOC_Prev10'] = df['O-to-C'].rolling(10).max()

        # Get the rolling mean of the candles' bodies for recent 20 candles
        df['OC-20D-Mean'] = df['O-to-C'].rolling(20).mean()

        # Get the % change of the current OC relative from the rolling mean
        df['OC-%-from-20D-Mean'] = abs(100 * (df['O-to-C'] - df['OC-20D-Mean']) / df['OC-20D-Mean'])

        # Get the rolling mean of volume for the recent 20 candles
        df['Volume-20D-Mean'] = df['volume'].rolling(20).mean()

        # Get the % change of the current volume relative from the rolling mean
        df['Volume-%-from-20D-Mean'] = abs(100 * (df['volume'] - df['Volume-20D-Mean']) / df['Volume-20D-Mean'])

        condition = (
                (df['O-to-C'] >= 0.0) &
                (df['O-to-C'] >= df['MaxOC_Prev10']) &
                (df['OC-%-from-20D-Mean'] >= 100.0) &
                (df['Volume-%-from-20D-Mean'] >= 50.0)
        )

        breakouts = df[condition]

        current_time = df.index[-1]

        if breakouts.empty:
            logging.debug("No breakout found for {}".format(current_time))
            return

        breakout_time = breakouts.index[-1]

        if current_time == breakout_time:
            logging.info("Breakout identified for symbol {} at {}".format(self.symbol, df.index[-1]))
            self.enter_long_position(10, current_time, df[CLOSE].iloc[-1],
                                     df[CLOSE].iloc[-1] * (1 - self.target_stop_loss_pct))
