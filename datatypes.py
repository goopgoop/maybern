from enum import Enum
from datetime import date

class WaterfallConfiguration:
    def __init__(self, pref: float, catch_up: float, carried_interest: float):
        self.pref = pref
        self.catch_up = catch_up
        self.carried_interest = carried_interest


class TransactionType(Enum):
    CONTRIBUTION = "contribution"
    DISTRIBUTION = "distribution"


class Commitment:
    def __init__(self, entity_name: str, id: int, amount: float):
        self.entity_name = entity_name
        self.id = id
        self.amount = amount


class Transaction:
    def __init__(
        self,
        transaction_date: date,
        amount: float,
        transaction_type: TransactionType,
        commitment: Commitment,
    ):
        self.id = id
        self.transaction_date = transaction_date
        self.transaction_type = transaction_type
        self.amount = amount
        self.commitment = commitment
        
DEFAULT_CONFIGURATION = WaterfallConfiguration(0.08, 1, 0.2)
