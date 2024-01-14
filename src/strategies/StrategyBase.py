import logging
import sys

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

import src.orders.OrderManager as orders
from src.Constants import QUANTITY, STOP_LOSS, PRICE, CLOSE, TX_DATE, EXIT_PRICE, IS_PROFIT, IS_LOSS, \
    PROFIT_PCT, LOSS_PCT, PROFIT, LOSS, ENTRY_PRICE, EXIT_DATE


def get_change_pct(current, previous):
    try:
        return ((current - previous) / previous) * 100.0
    except ZeroDivisionError:
        return 0


def get_change(current, previous):
    return current - previous


class Strategy:
    def __init__(self, symbol):
        self.symbol = symbol

        self.open_long_positions = []
        self.open_short_positions = []

        self.target_profit_pct = 0
        self.target_stop_loss_pct = 0

        self.stats = []

    def pre_condition(self, df):
        return False

    def execute(self, df):
        pass

    def post_execute(self, df):
        current_time = df.index[-1]
        current_close_price = df[CLOSE].iloc[-1]

        self.exit_long_position_if_target_attained(current_time, current_close_price)

        self.exit_long_position_if_stop_loss_breached(current_time, current_close_price)

    def set_target_profit_pct(self, profit_pct, risk_reward_ratio):
        self.target_profit_pct = profit_pct
        self.target_stop_loss_pct = profit_pct / risk_reward_ratio

    def square_off_all_open_long_positions_at_a_profit(self, df):
        current_time = df.index[-1]
        current_close_price = df[CLOSE].iloc[-1]

        logging.info("Squaring off all open long positions for symbol {} at {}".format(self.symbol, current_time))

        old_target_pct = self.target_profit_pct
        self.target_profit_pct = 0
        self.exit_long_position_if_target_attained(current_time, current_close_price)

        # Restore things
        self.target_profit_pct = old_target_pct

    def square_off_all_open_long_positions_at_a_loss(self, df):
        current_time = df.index[-1]
        current_close_price = df[CLOSE].iloc[-1]

        logging.info("Squaring off all open long positions for symbol {} at {}".format(self.symbol, current_time))

        open_positions_bkup = self.open_long_positions
        self.open_long_positions = \
            [{k: sys.maxsize if k == STOP_LOSS else v for k, v in entry.items()} for entry in open_positions_bkup]

        self.exit_long_position_if_stop_loss_breached(current_time, current_close_price)

    def exit_long_position_if_target_attained(self, current_time, current_close_price):
        open_positions_new = []

        if self.open_long_positions:
            for open_long_position in self.open_long_positions:
                entry_price = open_long_position[PRICE]
                change_pct = get_change_pct(current_close_price, entry_price)
                change = get_change(current_close_price, entry_price)

                if change_pct >= self.target_profit_pct:
                    logging.info("Target profit percent for long position attained at {}".format(str(current_time)))
                    self.do_exit_long_position(open_long_position, current_time, current_close_price)

                    self.stats.append({
                        TX_DATE: open_long_position[TX_DATE],
                        EXIT_DATE: current_time,
                        ENTRY_PRICE: entry_price,
                        EXIT_PRICE: current_close_price,
                        QUANTITY: open_long_position[QUANTITY],
                        IS_PROFIT: 1,
                        PROFIT_PCT: change_pct,
                        PROFIT: change,
                        IS_LOSS: 0,
                        LOSS_PCT: 0,
                        LOSS: 0
                    })

                    continue

                open_positions_new.append(open_long_position)

        self.open_long_positions = open_positions_new

    def exit_long_position_if_stop_loss_breached(self, current_time, current_close_price):
        open_positions_new = []

        if self.open_long_positions:
            for open_long_position in self.open_long_positions:
                stop_loss_price = open_long_position[STOP_LOSS]
                entry_price = open_long_position[PRICE]
                change_pct = get_change_pct(entry_price, current_close_price)
                change = get_change(entry_price, current_close_price)

                if current_close_price < stop_loss_price:
                    logging.info("Stop loss breached for long position at {}".format(str(current_time)))
                    self.do_exit_long_position(open_long_position, current_time, current_close_price)

                    self.stats.append({
                        TX_DATE: open_long_position[TX_DATE],
                        EXIT_DATE: current_time,
                        ENTRY_PRICE: entry_price,
                        EXIT_PRICE: current_close_price,
                        QUANTITY: open_long_position[QUANTITY],
                        IS_PROFIT: 0,
                        PROFIT_PCT: 0,
                        PROFIT: 0,
                        IS_LOSS: 1,
                        LOSS_PCT: change_pct * -1,
                        LOSS: change * -1
                    })

                    continue

                open_positions_new.append(open_long_position)

        self.open_long_positions = open_positions_new

    def do_exit_long_position(self, long_position, current_time, current_close_price):
        if not long_position:
            raise ValueError("No open long position to exit")

        logging.info("Exiting long position for symbol {} on {} at price {}. Entry price {}".format(
            self.symbol, current_time, current_close_price, long_position[PRICE]))

        orders.sell(self.symbol, long_position[QUANTITY], current_close_price, 0, current_time)

    def enter_long_position(self, quantity, current_time, current_close_price, stop_loss=0):
        logging.info("Entering long position for symbol {} at {}".format(self.symbol, current_time))
        self.open_long_positions.append(orders.buy(self.symbol, quantity, current_close_price, stop_loss, current_time))

    def get_stats(self):
        return pd.DataFrame(self.stats)

    def print_stats(self):
        stats = self.get_stats()
        stats['trades'] = stats['profit_pct']
        stats.loc[stats['profit_pct'] == 0, 'trades'] = stats['loss_pct']

        win_rate = round((stats['is_profit'].sum() / len(stats['is_profit'])) * 100, 2)
        loss_rate = round((stats['is_loss'].sum() / len(stats['is_loss'])) * 100, 2)
        avg_profit_pct = round(stats.loc[stats['is_profit'] == 1, 'profit_pct'].mean(), 2)
        avg_loss_pct = round(stats.loc[stats['is_loss'] == 1, 'loss_pct'].mean(), 2)

        sns.histplot(pd.Series(stats['trades']), bins=20)
        plt.title(f"Distribution of Breakout Profits for {self.symbol.upper()}")
        plt.text(0.95, 0.95,
                 f"Total Breakouts: {len(stats)} \n Avg profit: {avg_profit_pct}% \n Avg loss: {avg_loss_pct}% \n Win "
                 f"Rate: {win_rate}% \n Loss Rate: {loss_rate}%",
                 ha='right', va='top', transform=plt.gca().transAxes)
        plt.ylabel('Number of Breakouts')
        plt.xlabel('Profit (%)')
        plt.show()