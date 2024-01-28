import logging
import unittest
from datetime import date

import pandas as pd
from pandas._testing import assert_frame_equal

from src.Constants import IS_PROFIT, IS_LOSS, PROFIT, LOSS, QUANTITY
from src.orders import OrderManager
from strategies.MACDBreakoutStrategy import MACDBreakout


class PriceVolumeBreakOutTest(unittest.TestCase):
    df = pd.DataFrame()
    strategy = MACDBreakout("TCS")

    strategy.set_target_profit_pct(5, 2)

    def drive(self):
        for index, row in self.df.iterrows():
            # Get rows up to the current index
            _df = self.df.loc[:index]

            if self.strategy.pre_condition(_df):
                self.strategy.execute(_df)
                self.strategy.post_execute(_df)

        self.strategy.square_off_all_open_long_positions(self.df)

    def setUp(self):
        file_path = "/Users/chidr/PycharmProjects/BackTester/tests/test_data/PriceVolumeBreakOut/TCS_one_year_23_24.xlsx"
        self.df = pd.read_excel(file_path, index_col=0)
        self.df = self.df[['open', 'high', 'low', 'close', 'adjclose', 'volume']]
        self.df.index = self.df.index.date

        OrderManager.open_positions = {}
        OrderManager.position_status = {}
        OrderManager.available_cash = 200000

        self.assertTrue(len(self.strategy.open_long_positions) == 0)
        self.assertFalse(OrderManager.open_positions)
        self.assertFalse(OrderManager.position_status)

        logger = logging.getLogger()
        logger.level = logging.INFO

    def tearDown(self):
        OrderManager.open_positions = {}
        OrderManager.position_status = {}
        OrderManager.available_cash = 0

    def test_breakout_happened(self):
        self.drive()
        self.assertEqual({"TCS": "CLOSED"}, OrderManager.position_status)

        stats = self.strategy.get_stats()
        self.assertEqual(3, (stats[IS_PROFIT] == 1).sum())
        self.assertEqual(3, (stats[IS_LOSS] == 1).sum())
        self.assertEqual(5687.5, (stats[PROFIT] * stats[QUANTITY]).sum())
        self.assertEqual(-1304.99755859375, (stats[LOSS] * stats[QUANTITY]).sum())
        self.assertEqual((200000 + 5687.5 - 1304.99755859375), OrderManager.available_cash)

        actual_open_positions = OrderManager.get_all_positions()
        expected_open_positions = pd.DataFrame([
            {
                "SYMBOL": "TCS",
                "QUANTITY": 0,
                "ENTRY_DATE": date(year=2023, month=3, day=1),
                "POSITION_VALUE": 4382.50244,
                "EXIT_DATE": date(year=2023, month=11, day=30),
                "EXIT_PRICE": 34876.00098
            }
        ])
        assert_frame_equal(actual_open_positions, expected_open_positions, check_dtype=False)



