from datetime import date
from enum import Enum
from datatypes import WaterfallConfiguration, Transaction, TransactionType
from utils import dollar_str
import abc


class Tier(Enum):
    ROC = "Return of Capital"
    PR = "Preferred Return"
    CU = "Catch-up"
    FS = "Final Split"
    Total = "Total"


class WaterfallTier(abc.ABC):
    def __init__(
        self,
        tier: Tier,
        transactions: list[Transaction],
        waterfall_date: date,
        configuration: WaterfallConfiguration,
    ):
        self.transactions = transactions
        self.tier = tier
        self.waterfall_date = waterfall_date
        self.configuration = configuration
        self.starting_captial = 0
        self.LP_allocation = 0
        self.GP_allocation = 0
        self.total_tier_distribution = 0
        self.remaining_capital = 0

    def get_table(self) -> list[str]:
        return [
            self.tier.value,
            dollar_str(self.starting_captial),
            dollar_str(self.LP_allocation),
            dollar_str(self.GP_allocation),
            dollar_str(self.total_tier_distribution),
            dollar_str(self.remaining_capital),
        ]

    @abc.abstractmethod
    def calculate_tier(self, previous_tier: "WaterfallTier"):
        pass


class ROC_Tier(WaterfallTier):
    def calculate_tier(self, previous_tier: WaterfallTier):
        self.GP_allocation = None
        for transaction in self.transactions:
            if transaction.transaction_type == TransactionType.DISTRIBUTION:
                self.starting_captial += transaction.amount
            else:
                self.LP_allocation += transaction.amount
        
        # Dont ever go into negative
        self.LP_allocation = min(self.LP_allocation, self.starting_captial)
        self.total_tier_distribution = self.LP_allocation
        self.remaining_capital = self.starting_captial - self.LP_allocation


class PR_Tier(WaterfallTier):
    def calculate_tier(self, previous_tier: WaterfallTier):
        self.GP_allocation = None
        if previous_tier.remaining_capital <= 0:
            return
        self.starting_captial = previous_tier.remaining_capital
        for transaction in self.transactions:
            if transaction.transaction_type == TransactionType.CONTRIBUTION:
                # Calculate interest based on waterfall time - transaction time 
                days = (self.waterfall_date - transaction.transaction_date).days
                PR = transaction.amount * (1 + self.configuration.pref) ** (days / 365) - transaction.amount
                self.LP_allocation += PR
        self.total_tier_distribution = self.LP_allocation
        self.remaining_capital = self.starting_captial - self.LP_allocation


class CU_Tier(WaterfallTier):
    def calculate_tier(self, previous_tier: WaterfallTier):
        if previous_tier.remaining_capital <= 0:
            return
        self.starting_captial = previous_tier.remaining_capital
        PR = previous_tier.total_tier_distribution
        self.GP_allocation = self.configuration.carried_interest * (
            PR / (self.configuration.catch_up - self.configuration.carried_interest)
        )
        self.total_tier_distribution = self.GP_allocation
        self.remaining_capital = self.starting_captial - self.total_tier_distribution


class Final_Split_Tier(WaterfallTier):
    def calculate_tier(self, previous_tier: WaterfallTier):
        if previous_tier.remaining_capital <= 0:
            return
        self.starting_captial = previous_tier.remaining_capital
        self.LP_allocation = (
            1 - self.configuration.carried_interest
        ) * self.starting_captial
        self.GP_allocation = self.starting_captial - self.LP_allocation
        self.total_tier_distribution = self.starting_captial


class TotalTier(WaterfallTier):
    def __init__(
        self,
        tier: Tier,
        transactions: list[Transaction],
        waterfall_date: date,
        configuration: WaterfallConfiguration,
        previous_tiers: list[WaterfallTier],
    ):
        super().__init__(tier, transactions, waterfall_date, configuration)
        self.previous_tiers = previous_tiers

    def calculate_tier(self, previous_tier: WaterfallTier):
        self.starting_captial = self.remaining_capital = None
        for tier in self.previous_tiers:
            self.LP_allocation += tier.LP_allocation
            self.GP_allocation += tier.GP_allocation if tier.GP_allocation is not None else 0
            self.total_tier_distribution += tier.total_tier_distribution


TIERS = {
    Tier.ROC: ROC_Tier,
    Tier.PR: PR_Tier,
    Tier.CU: CU_Tier,
    Tier.FS: Final_Split_Tier,
}
