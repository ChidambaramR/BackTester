import unittest

import pandas as pd
from pandas.testing import assert_frame_equal

from src.orders import OrderManager
from datetime import datetime as dt, timedelta


class OrderManagerTest(unittest.TestCase):
    entry_date = None

    def setUp(self):
        self.entry_date = dt.now()

    def tearDown(self):
        OrderManager.open_positions = {}
        OrderManager.position_status = {}

    def test_take_new_position(self):
        OrderManager.buy("TCS", 10, 2000, 1995, self.entry_date)

        actual_open_positions = OrderManager.get_all_positions()
        expected_open_positions = pd.DataFrame([
            {
                "SYMBOL": "TCS",
                "QUANTITY": 10,
                "ENTRY_DATE": self.entry_date,
                "POSITION_VALUE": -20000,
                "EXIT_DATE": None,
                "EXIT_PRICE": 0
            }
        ])
        assert_frame_equal(actual_open_positions, expected_open_positions, check_dtype=False)

    def test_take_position_when_position_already_exists(self):
        OrderManager.buy("TCS", 10, 2000, 1995, self.entry_date)
        OrderManager.buy("TCS", 5, 1900, 1800, self.entry_date + timedelta(hours=1))

        actual_open_positions = OrderManager.get_all_positions()
        expected_open_positions = pd.DataFrame([
            {
                "SYMBOL": "TCS",
                "QUANTITY": 15,
                "ENTRY_DATE": self.entry_date,
                "POSITION_VALUE": -29500,
                "EXIT_DATE": None,
                "EXIT_PRICE": 0
            }
        ])
        assert_frame_equal(actual_open_positions, expected_open_positions, check_dtype=False)

    def test_square_off(self):
        OrderManager.buy("TCS", 10, 2000, 1995, self.entry_date)
        OrderManager.sell("TCS", 10, 1900, 1895, self.entry_date + timedelta(hours=1))

        actual_open_positions = OrderManager.get_all_positions()
        expected_open_positions = pd.DataFrame([
            {
                "SYMBOL": "TCS",
                "QUANTITY": 0,
                "ENTRY_DATE": self.entry_date,
                "POSITION_VALUE": -1000,
                "EXIT_DATE":  self.entry_date + timedelta(hours=1),
                "EXIT_PRICE": 19000
            }
        ])
        assert_frame_equal(actual_open_positions, expected_open_positions, check_dtype=False)

    def test_square_off_and_take_new_position(self):
        OrderManager.buy("TCS", 10, 2000, 1995, self.entry_date)
        OrderManager.sell("TCS", 10, 1900, 1895, self.entry_date + timedelta(hours=1))
        OrderManager.buy("TCS", 5, 2100, 2095, self.entry_date + timedelta(hours=2))

        actual_open_positions = OrderManager.get_all_positions()
        expected_open_positions = pd.DataFrame([
            {
                "SYMBOL": "TCS",
                "QUANTITY": 5,
                "ENTRY_DATE": self.entry_date + timedelta(hours=2),
                "POSITION_VALUE": -10500,
                "EXIT_DATE":  None,
                "EXIT_PRICE": 0
            }
        ])
        assert_frame_equal(actual_open_positions, expected_open_positions, check_dtype=False)

    def test_square_off_and_take_new_position_and_square_off(self):
        OrderManager.buy("TCS", 10, 2000, 1995, self.entry_date)
        OrderManager.sell("TCS", 10, 1900, 1895, self.entry_date + timedelta(hours=1))
        OrderManager.buy("TCS", 5, 2100, 2095, self.entry_date + timedelta(hours=2))
        OrderManager.sell("TCS", 5, 2200, 2195, self.entry_date + timedelta(hours=3))

        actual_open_positions = OrderManager.get_all_positions()
        expected_open_positions = pd.DataFrame([
            {
                "SYMBOL": "TCS",
                "QUANTITY": 0,
                "ENTRY_DATE": self.entry_date + timedelta(hours=2),
                "POSITION_VALUE": 500,
                "EXIT_DATE":  self.entry_date + timedelta(hours=3),
                "EXIT_PRICE": 11000
            }
        ])
        assert_frame_equal(actual_open_positions, expected_open_positions, check_dtype=False)

    def test_multiple_symbols(self):
        OrderManager.buy("TCS", 10, 2000, 1995, self.entry_date)
        OrderManager.buy("SBIN", 10, 2000, 1995, self.entry_date)
        OrderManager.sell("TCS", 10, 1900, 1895, self.entry_date + timedelta(hours=1))

        actual_open_positions = OrderManager.get_all_positions()
        expected_open_positions = pd.DataFrame([
            {
                "SYMBOL": "TCS",
                "QUANTITY": 0,
                "ENTRY_DATE": self.entry_date,
                "POSITION_VALUE": -1000,
                "EXIT_DATE": self.entry_date + timedelta(hours=1),
                "EXIT_PRICE": 19000
            },
            {
                "SYMBOL": "SBIN",
                "QUANTITY": 10,
                "ENTRY_DATE": self.entry_date,
                "POSITION_VALUE": -20000,
                "EXIT_DATE":  None,
                "EXIT_PRICE": 0
            }
        ])
        assert_frame_equal(actual_open_positions, expected_open_positions, check_dtype=False)
