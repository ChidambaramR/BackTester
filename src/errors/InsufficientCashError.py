class InsufficientCashError(Exception):
    def __init__(self, tx_cash, available_cash):
        self.message = "Insufficient cash balance to make a tx of {} while available cash is {}".format(tx_cash, available_cash)
        super().__init__(self.message)