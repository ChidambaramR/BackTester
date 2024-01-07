import pandas as pd

from src.Constants import TYPE, POSITION_TYPE_LONG, QUANTITY, SYMBOL, PRICE, BUY, STOP_LOSS, OPEN, CLOSED, ENTRY_DATE, \
    EXIT_DATE, EXIT_PRICE, TX_DATE, TX_PRICE, SELL, POSITION_TYPE_SHORT, POSITION_VALUE

orders = []
position_status = {}
open_positions = {}
# open_positions = pd.DataFrame(columns=[SYMBOL, QUANTITY, ENTRY_DATE, ENTRY_PRICE, EXIT_DATE, EXIT_PRICE, TYPE])


def get_latest_position_for_symbol(symbol):
    return open_positions[symbol][-1]


def square_off(order, current_position_type):
    symbol = order[SYMBOL]
    quantity = order[QUANTITY]
    if symbol in position_status and position_status[symbol] == OPEN:
        # Group by SYMBOL and apply the function to get the latest row
        open_position = get_latest_position_for_symbol(symbol)
        open_position[QUANTITY] = open_position[QUANTITY] + quantity
        open_position[POSITION_VALUE] = open_position[POSITION_VALUE] + order[TX_PRICE]

        if open_position[QUANTITY] == 0:
            position_status[symbol] = CLOSED
            open_position[EXIT_DATE] = order[TX_DATE]
            open_position[EXIT_PRICE] = order[TX_PRICE]
    else:
        take_new_position(order, current_position_type)


def take_new_position(order, position_type):
    global open_positions

    symbol = order[SYMBOL]
    position_status[symbol] = OPEN

    new_position = {
        QUANTITY: order[QUANTITY],
        ENTRY_DATE: order[TX_DATE],
        POSITION_VALUE: order[TX_PRICE],
        EXIT_DATE: None,
        EXIT_PRICE: 0,
        TYPE: position_type,
    }

    open_positions[symbol] = []
    open_positions[symbol].append(new_position)


def buy(symbol, quantity, price, stop_loss, buy_date):
    order = {
        TYPE: BUY,
        TX_DATE: buy_date,
        SYMBOL: symbol,
        QUANTITY: quantity,
        PRICE: price,
        TX_PRICE: quantity * price * -1,
        STOP_LOSS: stop_loss
    }

    square_off(order, POSITION_TYPE_LONG)

    return order


def sell(symbol, quantity, price, stop_loss, sell_date):
    order = {
        TYPE: SELL,
        TX_DATE: sell_date,
        SYMBOL: symbol,
        QUANTITY: quantity * -1,
        PRICE: price,
        TX_PRICE: quantity * price,
        STOP_LOSS: stop_loss
    }

    square_off(order, POSITION_TYPE_SHORT)

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


def get_open_position_for_symbol(symbol):
    return open_positions[symbol]

