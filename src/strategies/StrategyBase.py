import logging

import src.orders.OrderManager as orders
from src.Constants import QUANTITY, STOP_LOSS, STATUS, CLOSED, PRICE


def get_change_pct(current, previous):
    try:
        return ((current - previous) / previous) * 100.0
    except ZeroDivisionError:
        return 0


class Strategy:
    def __init__(self, symbol):
        self.symbol = symbol

        self.open_long_positions = []
        self.open_short_positions = []

        self.target_profit_pct = 0

    def pre_condition(self, df, current_time, current_close_price):
        return False

    def execute(self, df, current_time, current_close_price):
        pass

    def post_execute(self, df, current_time, current_close_price):
        self.exit_long_position_if_target_attained(current_time, current_close_price)

        self.exit_long_position_if_stop_loss_breached(current_time, current_close_price)

    def exit_long_position_if_target_attained(self, current_time, current_close_price):
        open_positions_new = []

        if self.open_long_positions:
            for open_long_position in self.open_long_positions:
                entry_price = open_long_position[PRICE]
                change_pct = get_change_pct(current_close_price, entry_price)

                if change_pct >= self.target_profit_pct:
                    logging.info("Target profit percent for long position attained at {}".format(str(current_time)))
                    self.exit_long_position(open_long_position, current_time, current_close_price)
                    open_long_position[STATUS] = CLOSED
                    continue

                open_positions_new.append(open_long_position)

        self.open_long_positions = open_positions_new

    def exit_long_position_if_stop_loss_breached(self, current_time, current_close_price):
        open_positions_new = []

        if self.open_long_positions:
            for open_long_position in self.open_long_positions:
                stop_loss_price = open_long_position[STOP_LOSS]

                if current_close_price < stop_loss_price:
                    logging.info("Stop loss breached for long position at {}".format(str(current_time)))
                    self.exit_long_position(open_long_position, current_time, current_close_price)
                    open_long_position[STATUS] = CLOSED
                    continue

                open_positions_new.append(open_long_position)

        self.open_long_positions = open_positions_new

    def exit_long_position(self, long_position, current_time, current_close_price):
        if not long_position:
            raise ValueError("No open long position to exit")

        logging.info("Exiting long position for symbol {} at {}".format(self.symbol, current_time))
        orders.sell(self.symbol, long_position[QUANTITY], current_close_price, 0, current_time)
