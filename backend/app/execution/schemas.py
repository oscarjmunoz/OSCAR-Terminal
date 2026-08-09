from enum import Enum

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator


class TradeSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class ExecutionStatus(str, Enum):
    READY = "READY"
    REVIEW = "REVIEW"
    BLOCKED = "BLOCKED"


class ExecutionRequest(BaseModel):
    symbol: str
    side: TradeSide
    entry_price: float = Field(gt=0)
    stop_loss: float = Field(gt=0)
    take_profit: float = Field(gt=0)
    risk_percent: float = Field(gt=0)
    account_balance: float | None = Field(default=None, gt=0)

    spread: float | None = Field(default=None, ge=0)
    pip_value: float | None = Field(default=None, gt=0)
    tick_value: float | None = Field(default=None, gt=0)
    leverage: float | None = Field(default=None, gt=0)
    contract_size: float | None = Field(default=None, gt=0)

    min_rr: float = Field(default=2.0, gt=0)
    max_risk_percent: float = Field(default=2.0, gt=0)
    max_spread: float = Field(default=2.5, ge=0)
    min_lot: float = Field(default=0.01, gt=0)
    max_lot: float = Field(default=100.0, gt=0)
    margin_buffer: float = Field(default=0.7, gt=0, lt=1)

    @field_validator("symbol")
    @classmethod
    def _normalize_symbol(cls, value: str) -> str:
        symbol = value.strip().upper()
        if not symbol:
            raise ValueError("symbol is required")
        return symbol


class ValidationResultSchema(BaseModel):
    status: str
    message: str
    severity: str


class ExecutionResult(BaseModel):
    symbol: str
    side: TradeSide
    entry: float
    stop_loss: float
    take_profit: float
    lot_size: float
    risk_percent: float
    risk_money: float
    reward_money: float
    risk_pips: float
    reward_pips: float
    rr: float
    pip_value: float
    tick_value: float
    margin_required: float
    spread: float
    validation_results: list[ValidationResultSchema]
    institutional_score: float
    execution_status: ExecutionStatus
