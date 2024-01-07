from strategies.Strategy import Strategy


class PriceVolumeBreakout(Strategy):
    def __init__(self, symbol):
        super().__init__(symbol)

    def pre_condition(self, df, current_date, current_closing_price):
        if len(df) <= 20:
            return False

        return True

    def execute(self, df, current_time, current_close_price):
        super().execute(df, current_time, current_close_price)

        # Get the length of candle's body (from open to close)
        df['O-to-C'] = df['close'] - df['open']

        # Get the maximum OC compared to the recent 10 candles
        df['MaxOC_Prev10'] = df['O-to-C'].rolling(10).max()
        
        # Get the rolling mean of the candles' bodies for recent 20 candles
        df['OC-20D-Mean'] = df['O-to-C'].rolling(20).mean()
        
        # Get the % change of the current OC relative from the rolling mean
        df['OC-%-from-20D-Mean'] = 100 * (df['O-to-C'] - df['OC-20D-Mean']) / df['OC-20D-Mean']
        
        # Get the rolling mean of volume for the recent 20 candles
        df['Volume-20D-Mean'] = df['volume'].rolling(20).mean()
        
        # Get the % change of the current volume relative from the rolling mean
        df['Volume-%-from-20D-Mean'] = 100 * (df['volume'] - df['Volume-20D-Mean']) / df['Volume-20D-Mean']
        
        # Drop the null values for the first 19 rows, where no mean can be computed yet
        df = df.dropna()

        condition = (
                        (df['O-to-C'] >= 0.0) &
                        (df['O-to-C'] >= df['MaxOC_Prev10']) &
                        (df['OC-%-from-20D-Mean'] >= 100.0) &
                        (df['Volume-%-from-20D-Mean'] >= 50.0)
                    )
