from datetime import date
from tabulate import tabulate
from datatypes import Transaction, DEFAULT_CONFIGURATION, WaterfallConfiguration, TransactionType, Commitment
from tier import WaterfallTier, TIERS, TotalTier, Tier
import pandas as pd
import datetime as dt
from utils import strip_float

class Waterfall:
    def __init__(
        self, transactions: list[Transaction], configuration: WaterfallConfiguration
    ):
        self.transactions = transactions
        self.configuration = configuration

    def run(self, id: int, date: date) -> list[WaterfallTier]:
        previous_tier = None
        tiers: list[WaterfallTier] = []
        transactions_filtered = [
            transaction
            for transaction in self.transactions
            if transaction.transaction_date <= date and transaction.commitment.id == id
        ]
        for tier_type in TIERS:
            tier: WaterfallTier = TIERS[tier_type](
                tier_type, transactions_filtered, date, self.configuration
            )
            tier.calculate_tier(previous_tier)
            previous_tier = tier
            tiers.append(tier)
        total_tier: TotalTier = TotalTier(Tier.Total, None, None, None, tiers)
        total_tier.calculate_tier(None)
        tiers.append(total_tier)
        return tiers

class WaterfallDataSet:
    def __init__(self):
        self.commitments = {}
        self.transactions: list[Transaction] = []
        self.configuration = DEFAULT_CONFIGURATION
        self.min_date = dt.date(9999, 1, 1)
        self.ids: list[int] = []
        
    def read_commitements(self, csv_file: str):
        self.commitments = {}
        self.ids = []
        df = pd.read_csv(csv_file)
        for row in df.itertuples(index=True):
            commitement = Commitment(
                row.entity_name, int(row.id), strip_float(row.commitment_amount)
            )
            self.commitments[commitement.id] = commitement
            self.ids.append(commitement.id)
            

    def read_transactions(self, csv_file: str):
        self.transactions = []
        df = pd.read_csv(csv_file)
        for row in df.itertuples(index=True):
            transaction = Transaction(
                dt.datetime.strptime(row.transaction_date, '%m/%d/%Y').date(),
                strip_float(row.transaction_amount),
                TransactionType(row.contribution_or_distribution),
                self.commitments[int(row.commitment_id)],
            )
            self.min_date = min(transaction.transaction_date, self.min_date)
            self.transactions.append(transaction)
    

    def calculate_waterfall(self, id: int, date: date, print_table = True) -> list[WaterfallTier]:
        waterfall: Waterfall = Waterfall(self.transactions, self.configuration)
        tiers = waterfall.run(id, date)
        data = [[]]
        [data.append(tier.get_table()) for tier in tiers]
        if(print_table):
            print(
                tabulate(
                    data,
                    headers=[
                        "Tier Name",
                        "Starting Tier Capital",
                        "LP Allocation",
                        "GP Allocation",
                        "Total Tier Distribution",
                        "Remaining Capital for Next Tier",
                    ],
                )
            )
        return tiers
