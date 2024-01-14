import unittest
from datetime import datetime as dt, timedelta

import pandas as pd
from pandas._testing import assert_frame_equal

from src.orders import OrderManager
from src.strategies.StrategyBase import Strategy


class StrategyTest(unittest.TestCase):
    entry_date = None

    def setUp(self):
        self.entry_date = dt.now()

    def tearDown(self):
        OrderManager.open_positions = {}
        OrderManager.position_status = {}

    def test_exit_long_position_when_target_profit_reached(self):
        order = OrderManager.buy("TCS", 10, 2000, 1995, self.entry_date)
        self.assertIs("open", OrderManager.position_status["TCS"])

        s = Strategy(symbol="TCS")
        s.target_profit_pct = 10
        s.open_long_positions = [order]

        self.assertTrue(len(s.open_long_positions) == 1)

        s.exit_long_position_if_target_attained(self.entry_date + timedelta(hours=1), 2300)
        actual_open_positions = OrderManager.get_all_positions()

        self.assertTrue(len(s.open_long_positions) == 0)
        self.assertIs("CLOSED", OrderManager.position_status["TCS"])

        expected_open_positions = pd.DataFrame([
            {
                "SYMBOL": "TCS",
                "QUANTITY": 0,
                "ENTRY_DATE": self.entry_date,
                "POSITION_VALUE": 3000,
                "EXIT_DATE":  self.entry_date + timedelta(hours=1),
                "EXIT_PRICE": 23000
            }
        ])
        assert_frame_equal(actual_open_positions, expected_open_positions, check_dtype=False)

    def test_exit_all_long_positions_when_target_profit_reached(self):
        order1 = OrderManager.buy("TCS", 10, 2000, 1995, self.entry_date)
        order2 = OrderManager.buy("TCS", 10, 2100, 1995, self.entry_date)
        self.assertIs("open", OrderManager.position_status["TCS"])

        s = Strategy(symbol="TCS")
        s.target_profit_pct = 10
        s.open_long_positions = [order1, order2]

        self.assertTrue(len(s.open_long_positions) == 2)

        s.exit_long_position_if_target_attained(self.entry_date + timedelta(hours=1), 2500)
        actual_open_positions = OrderManager.get_all_positions()

        self.assertTrue(len(s.open_long_positions) == 0)
        self.assertIs("CLOSED", OrderManager.position_status["TCS"])

        expected_open_positions = pd.DataFrame([
            {
                "SYMBOL": "TCS",
                "QUANTITY": 0,
                "ENTRY_DATE": self.entry_date,
                "POSITION_VALUE": 9000,
                "EXIT_DATE":  self.entry_date + timedelta(hours=1),
                "EXIT_PRICE": 25000
            }
        ])
        assert_frame_equal(actual_open_positions, expected_open_positions, check_dtype=False)

    def test_exit_one_long_position_when_target_profit_reached(self):
        order1 = OrderManager.buy("TCS", 10, 2000, 1995, self.entry_date)
        order2 = OrderManager.buy("TCS", 10, 2400, 1995, self.entry_date)
        self.assertIs("open", OrderManager.position_status["TCS"])

        s = Strategy(symbol="TCS")
        s.target_profit_pct = 10
        s.open_long_positions = [order1, order2]

        self.assertTrue(len(s.open_long_positions) == 2)

        s.exit_long_position_if_target_attained(self.entry_date + timedelta(hours=1), 2500)
        actual_open_positions = OrderManager.get_all_positions()

        self.assertTrue(len(s.open_long_positions) == 1)
        self.assertIs("open", OrderManager.position_status["TCS"])

        expected_open_positions = pd.DataFrame([
            {
                "SYMBOL": "TCS",
                "QUANTITY": 10,
                "ENTRY_DATE": self.entry_date,
                "POSITION_VALUE": -19000,
                "EXIT_DATE":  None,
                "EXIT_PRICE": 0
            }
        ])
        assert_frame_equal(actual_open_positions, expected_open_positions, check_dtype=False)

    def test_exit_no_long_position_when_target_profit_not_reached(self):
        order1 = OrderManager.buy("TCS", 10, 2000, 1995, self.entry_date)
        order2 = OrderManager.buy("TCS", 10, 2400, 1995, self.entry_date)
        self.assertIs("open", OrderManager.position_status["TCS"])

        s = Strategy(symbol="TCS")
        s.target_profit_pct = 50
        s.open_long_positions = [order1, order2]

        self.assertTrue(len(s.open_long_positions) == 2)

        s.exit_long_position_if_target_attained(self.entry_date + timedelta(hours=1), 2500)
        actual_open_positions = OrderManager.get_all_positions()

        self.assertTrue(len(s.open_long_positions) == 2)
        self.assertIs("open", OrderManager.position_status["TCS"])

        expected_open_positions = pd.DataFrame([
            {
                "SYMBOL": "TCS",
                "QUANTITY": 20,
                "ENTRY_DATE": self.entry_date,
                "POSITION_VALUE": -44000,
                "EXIT_DATE":  None,
                "EXIT_PRICE": 0
            }
        ])
        assert_frame_equal(actual_open_positions, expected_open_positions, check_dtype=False)

    def test_exit_long_position_when_stop_loss_breached(self):
        order = OrderManager.buy("TCS", 10, 2000, 1995, self.entry_date)
        self.assertIs("open", OrderManager.position_status["TCS"])

        s = Strategy(symbol="TCS")
        s.target_profit_pct = 1
        s.open_long_positions = [order]

        self.assertTrue(len(s.open_long_positions) == 1)

        s.exit_long_position_if_stop_loss_breached(self.entry_date + timedelta(hours=1), 1994)
        actual_open_positions = OrderManager.get_all_positions()

        self.assertTrue(len(s.open_long_positions) == 0)
        self.assertIs("CLOSED", OrderManager.position_status["TCS"])

        expected_open_positions = pd.DataFrame([
            {
                "SYMBOL": "TCS",
                "QUANTITY": 0,
                "ENTRY_DATE": self.entry_date,
                "POSITION_VALUE": -60,
                "EXIT_DATE":  self.entry_date + timedelta(hours=1),
                "EXIT_PRICE": 19940
            }
        ])
        assert_frame_equal(actual_open_positions, expected_open_positions, check_dtype=False)

    def test_exit_all_long_positions_when_stop_loss_breached(self):
        order1 = OrderManager.buy("TCS", 10, 2000, 1995, self.entry_date)
        order2 = OrderManager.buy("TCS", 10, 2100, 1995, self.entry_date)
        self.assertIs("open", OrderManager.position_status["TCS"])

        s = Strategy(symbol="TCS")
        s.target_profit_pct = 10
        s.open_long_positions = [order1, order2]

        self.assertTrue(len(s.open_long_positions) == 2)

        s.exit_long_position_if_stop_loss_breached(self.entry_date + timedelta(hours=1), 1994)
        actual_open_positions = OrderManager.get_all_positions()

        self.assertTrue(len(s.open_long_positions) == 0)
        self.assertIs("CLOSED", OrderManager.position_status["TCS"])

        expected_open_positions = pd.DataFrame([
            {
                "SYMBOL": "TCS",
                "QUANTITY": 0,
                "ENTRY_DATE": self.entry_date,
                "POSITION_VALUE": -1120,
                "EXIT_DATE":  self.entry_date + timedelta(hours=1),
                "EXIT_PRICE": 19940
            }
        ])
        assert_frame_equal(actual_open_positions, expected_open_positions, check_dtype=False)

    def test_exit_no_long_position_when_stop_loss_not_reached(self):
        order1 = OrderManager.buy("TCS", 10, 2000, 1995, self.entry_date)
        order2 = OrderManager.buy("TCS", 10, 2400, 1995, self.entry_date)
        self.assertIs("open", OrderManager.position_status["TCS"])

        s = Strategy(symbol="TCS")
        s.target_profit_pct = 50
        s.open_long_positions = [order1, order2]

        self.assertTrue(len(s.open_long_positions) == 2)

        s.exit_long_position_if_stop_loss_breached(self.entry_date + timedelta(hours=1), 1996)
        actual_open_positions = OrderManager.get_all_positions()

        self.assertTrue(len(s.open_long_positions) == 2)
        self.assertIs("open", OrderManager.position_status["TCS"])

        expected_open_positions = pd.DataFrame([
            {
                "SYMBOL": "TCS",
                "QUANTITY": 20,
                "ENTRY_DATE": self.entry_date,
                "POSITION_VALUE": -44000,
                "EXIT_DATE":  None,
                "EXIT_PRICE": 0
            }
        ])
        assert_frame_equal(actual_open_positions, expected_open_positions, check_dtype=False)

    def test_exit_one_long_position_when_stop_loss_breached(self):
        order1 = OrderManager.buy("TCS", 10, 2000, 1995, self.entry_date)
        order2 = OrderManager.buy("TCS", 10, 2400, 2000, self.entry_date)
        self.assertIs("open", OrderManager.position_status["TCS"])

        s = Strategy(symbol="TCS")
        s.target_profit_pct = 10
        s.open_long_positions = [order1, order2]

        self.assertTrue(len(s.open_long_positions) == 2)

        s.exit_long_position_if_stop_loss_breached(self.entry_date + timedelta(hours=1), 1999)
        actual_open_positions = OrderManager.get_all_positions()

        self.assertTrue(len(s.open_long_positions) == 1)
        self.assertIs("open", OrderManager.position_status["TCS"])

        expected_open_positions = pd.DataFrame([
            {
                "SYMBOL": "TCS",
                "QUANTITY": 10,
                "ENTRY_DATE": self.entry_date,
                "POSITION_VALUE": -24010,
                "EXIT_DATE":  None,
                "EXIT_PRICE": 0
            }
        ])
        assert_frame_equal(actual_open_positions, expected_open_positions, check_dtype=False)
