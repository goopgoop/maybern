import datetime
import unittest
from dataset import WaterfallDataSet
from datatypes import Commitment, Transaction, TransactionType
from tier import WaterfallTier

# Run with py -m unittest tests.py (on windows)
# Run with python -m unittest tests.py (on mac)
class WaterfallTestCases(unittest.TestCase):
    def setup_waterfall(self):
        self.waterfall = WaterfallDataSet()

    def get_transaction(
        self,
        transaction_date: str,
        amount: float,
        transaction_type: TransactionType,
        commitment: int,
    ):
        return Transaction(
            datetime.datetime.strptime(transaction_date, "%m/%d/%Y"),
            amount,
            transaction_type,
            Commitment("", commitment, 0),
        )

    def expect_tiers_to_equal(self, tiers: list[WaterfallTier], tier_data: list[list]):
        for i in range(0, len(tiers)):
            tier = tiers[i]
            data = tier_data[i]
            self.assertAlmostEqual(data[0], tier.starting_captial, places=2)
            self.assertAlmostEqual(data[1], tier.LP_allocation, places=2)
            self.assertAlmostEqual(data[2], tier.GP_allocation, places=2)
            self.assertAlmostEqual(data[3], tier.total_tier_distribution, places=2)
            self.assertAlmostEqual(data[4], tier.remaining_capital, places=2)

    def test_basic(self):
        self.setup_waterfall()
        self.waterfall.transactions = [
            self.get_transaction("01/01/2019", 1000, TransactionType.CONTRIBUTION, 1),
            self.get_transaction("01/01/2020", 2000, TransactionType.DISTRIBUTION, 1),
        ]
        tiers = self.waterfall.calculate_waterfall(
            1, datetime.datetime.strptime("01/01/2020", "%m/%d/%Y"), False
        )
        self.expect_tiers_to_equal(
            tiers,
            [
                [2000, 1000, None, 1000, 1000],
                [1000, 80, None, 80, 920],
                [920, 0, 20, 20, 900],
                [900, 720, 180, 900, 0],
                [None, 1800, 200, 2000, None],
            ],
        )
                
    def test_multiple_contributions(self):
        self.setup_waterfall()
        self.waterfall.transactions = [
            self.get_transaction("01/01/2019", 1000, TransactionType.CONTRIBUTION, 1),
            self.get_transaction("05/18/2019", 1000, TransactionType.CONTRIBUTION, 1),
            self.get_transaction("01/01/2020", 5000, TransactionType.DISTRIBUTION, 1),
        ]
        tiers = self.waterfall.calculate_waterfall(
            1, datetime.datetime.strptime("01/01/2020", "%m/%d/%Y"), False
        )
        
        self.expect_tiers_to_equal(
            tiers,
            [
                [5000, 2000, None, 2000, 3000],
                [3000, 129.25, None, 129.25, 2870.75],
                [2870.75, 0, 32.31, 32.31, 2838.44],
                [2838.44, 2270.75, 567.69, 2838.44, 0],
                [None, 4400, 600, 5000, None],
            ],
        )
        
    def test_multiple_distributions(self):
        self.setup_waterfall()
        self.waterfall.transactions = [
            self.get_transaction("01/01/2019", 1000, TransactionType.CONTRIBUTION, 1),
            self.get_transaction("05/18/2019", 500, TransactionType.CONTRIBUTION, 1),
            self.get_transaction("01/01/2020", 5000, TransactionType.DISTRIBUTION, 1),
            self.get_transaction("01/01/2021", 500, TransactionType.DISTRIBUTION, 1),
        ]
        tiers = self.waterfall.calculate_waterfall(
            1, datetime.datetime.strptime("01/01/2021", "%m/%d/%Y"), False
        )
        self.expect_tiers_to_equal(
            tiers,
            [
                [5500, 1500, None, 1500, 4000],
                [4000, 233.36, None, 233.36, 3766.64],
                [3766.64, 0, 58.34, 58.34, 3708.30],
                [3708.30, 2966.64, 741.66, 3708.30, 0],
                [None, 4700, 800, 5500, None],
            ],
        )
        
    def test_loss(self):
        self.setup_waterfall()
        self.waterfall.transactions = [
            self.get_transaction("01/01/2019", 5000, TransactionType.CONTRIBUTION, 1),
            self.get_transaction("05/18/2019", 6000, TransactionType.CONTRIBUTION, 1),
            self.get_transaction("01/01/2020", 5000, TransactionType.DISTRIBUTION, 1),
            self.get_transaction("01/01/2021", 500, TransactionType.DISTRIBUTION, 1),
        ]
        tiers = self.waterfall.calculate_waterfall(
            1, datetime.datetime.strptime("01/01/2021", "%m/%d/%Y"), False
        )
        self.expect_tiers_to_equal(
            tiers,
            [
                [5500, 5500, None, 5500, 0],
                [0, 0, None, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [None, 5500, 0, 5500, None],
            ],
        )
       
        
    
        