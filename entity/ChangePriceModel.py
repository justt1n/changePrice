from dataclasses import dataclass, field
from typing import Optional

@dataclass
class ChangePriceModel:
    wholesale_mode: int = field(metadata={"required": True, "min": 0, "max": 2})
    seller_price: Optional[float] = field(default=None, metadata={"min": 0})
    tier_one_seller_price: Optional[float] = field(default=None, metadata={"min": 0})
    tier_two_seller_price: Optional[float] = field(default=None, metadata={"min": 0})
    status: int = field(default=1, metadata={"min": 0, "max": 1})
    keys: Optional[int] = field(default=None, metadata={"min": 0, "max": 10000})
    is_preorder: Optional[bool] = field(default=None)

    def __post_init__(self):
        if not (0 <= self.wholesale_mode <= 2):
            raise ValueError("wholesale_mode must be between 0 and 2")
        if self.seller_price is not None and self.seller_price < 0:
            raise ValueError("seller_price must be >= 0")
        if self.tier_one_seller_price is not None and self.tier_one_seller_price < 0:
            raise ValueError("tier_one_seller_price must be >= 0")
        if self.tier_two_seller_price is not None and self.tier_two_seller_price < 0:
            raise ValueError("tier_two_seller_price must be >= 0")
        if not (0 <= self.status <= 1):
            raise ValueError("status must be 0 or 1")
        if self.keys is not None and not (0 <= self.keys <= 10000):
            raise ValueError("keys must be between 0 and 10000")