import logging

import pandas as pd

from src.errors.InsufficientCashError import InsufficientCashError
from src.Constants import TYPE, POSITION_TYPE_LONG, QUANTITY, SYMBOL, PRICE, BUY, STOP_LOSS, OPEN, CLOSED, ENTRY_DATE, \
    EXIT_DATE, EXIT_PRICE, TX_DATE, TX_PRICE, SELL, POSITION_TYPE_SHORT, POSITION_VALUE

orders = []
position_status = {}
open_positions = {}
available_cash = 1000000


# open_positions = pd.DataFrame(columns=[SYMBOL, QUANTITY, ENTRY_DATE, ENTRY_PRICE, EXIT_DATE, EXIT_PRICE, TYPE])
def validate_cash_balance(transaction_price):
    if transaction_price > available_cash:
        raise InsufficientCashError(transaction_price, available_cash)


def deduct_cash(transaction_price):
    global available_cash
    ac = available_cash

    available_cash = available_cash - transaction_price

    logging.info("Deducting cash {} from available cash {}. New balance: {}".format(
        transaction_price, ac, available_cash))


def add_cash(transaction_price):
    global available_cash
    ac = available_cash

    available_cash = available_cash + transaction_price

    logging.info("Adding cash {} to available cash {}. New balance: {}".format(
        transaction_price, ac, available_cash))


def get_latest_position_for_symbol(symbol):
    return open_positions[symbol][-1]


def square_off_position(position, order):
    symbol = order[SYMBOL]
    position_status[symbol] = CLOSED
    position[EXIT_DATE] = order[TX_DATE]
    position[EXIT_PRICE] = order[TX_PRICE]


def add_to_existing_position(order):
    symbol = order[SYMBOL]
    quantity = order[QUANTITY]

    # Group by SYMBOL and apply the function to get the latest row
    open_position = get_latest_position_for_symbol(symbol)
    open_position[QUANTITY] = open_position[QUANTITY] + quantity
    open_position[POSITION_VALUE] = open_position[POSITION_VALUE] - order[TX_PRICE]

    if open_position[QUANTITY] == 0:
        square_off_position(open_position, order)


def remove_from_existing_position(order):
    symbol = order[SYMBOL]
    quantity = order[QUANTITY]

    # Group by SYMBOL and apply the function to get the latest row
    open_position = get_latest_position_for_symbol(symbol)
    open_position[QUANTITY] = open_position[QUANTITY] - quantity
    open_position[POSITION_VALUE] = open_position[POSITION_VALUE] + order[TX_PRICE]

    if open_position[QUANTITY] == 0:
        square_off_position(open_position, order)


def take_new_long_position(order):
    global open_positions

    symbol = order[SYMBOL]
    position_status[symbol] = OPEN

    new_position = {
        QUANTITY: order[QUANTITY],
        ENTRY_DATE: order[TX_DATE],
        POSITION_VALUE: order[TX_PRICE] * -1,
        EXIT_DATE: None,
        EXIT_PRICE: 0
    }

    logging.info("Taking new long position {} for symbol {}".format(new_position, symbol))

    open_positions[symbol] = []
    open_positions[symbol].append(new_position)

    logging.info("Open positions: {}".format(open_positions))


def take_new_short_position(order):
    global open_positions

    symbol = order[SYMBOL]
    position_status[symbol] = OPEN

    new_position = {
        QUANTITY: order[QUANTITY],
        ENTRY_DATE: order[TX_DATE],
        POSITION_VALUE: order[TX_PRICE],
        EXIT_DATE: None,
        EXIT_PRICE: 0
    }

    logging.info("Taking new short position {} for symbol {}".format(new_position, symbol))

    open_positions[symbol] = []
    open_positions[symbol].append(new_position)

    logging.info("Open positions: {}".format(open_positions))


def buy(symbol, quantity, price, stop_loss, buy_date):
    tx_price = quantity * price

    validate_cash_balance(tx_price)

    order = {
        TYPE: BUY,
        TX_DATE: buy_date,
        SYMBOL: symbol,
        QUANTITY: quantity,
        PRICE: price,
        TX_PRICE: tx_price,
        STOP_LOSS: stop_loss
    }

    if symbol in position_status and position_status[symbol] == OPEN:
        add_to_existing_position(order)
    else:
        take_new_long_position(order)

    deduct_cash(order[TX_PRICE])

    return order


def sell(symbol, quantity, price, stop_loss, sell_date):
    tx_price = quantity * price

    order = {
        TYPE: SELL,
        TX_DATE: sell_date,
        SYMBOL: symbol,
        QUANTITY: quantity,
        PRICE: price,
        TX_PRICE: tx_price,
        STOP_LOSS: stop_loss
    }

    if symbol in position_status and position_status[symbol] == OPEN:
        remove_from_existing_position(order)
    else:
        take_new_short_position(order)

    add_cash(order[TX_PRICE])

    return order


def get_all_positions():
    # List to store the transformed data
    rows = []

    # Iterate over the dictionary
    for symbol, entries in open_positions.items():
        for entry in entries:
            row = {
                SYMBOL: symbol
            }
            row.update(entry)

            rows.append(row)

    return pd.DataFrame(rows)

