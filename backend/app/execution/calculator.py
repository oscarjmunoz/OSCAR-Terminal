from __future__ import annotations


def resolvePipSize(symbol: str) -> float:
    normalized = symbol.upper()

    if normalized.startswith("XAU"):
        return 0.1

    if normalized.startswith("US30") or normalized.startswith("NAS"):
        return 1.0

    if normalized.endswith("JPY"):
        return 0.01

    return 0.0001


def calculateRiskMoney(account_balance: float, risk_percent: float) -> float:
    if account_balance <= 0 or risk_percent <= 0:
        return 0.0

    return round(account_balance * (risk_percent / 100.0), 2)


def calculatePipDistance(entry_price: float, stop_loss: float, symbol: str) -> float:
    pip_size = resolvePipSize(symbol)

    if pip_size <= 0:
        return 0.0

    return round(abs(entry_price - stop_loss) / pip_size, 1)


def calculateRewardDistance(entry_price: float, take_profit: float, symbol: str) -> float:
    pip_size = resolvePipSize(symbol)

    if pip_size <= 0:
        return 0.0

    return round(abs(take_profit - entry_price) / pip_size, 1)


def calculateRR(reward_pips: float, risk_pips: float) -> float:
    if risk_pips <= 0:
        return 0.0

    return round(reward_pips / risk_pips, 2)


def calculateLotSize(
    risk_money: float,
    risk_pips: float,
    pip_value_per_lot: float,
    lot_step: float = 0.01,
) -> float:
    if risk_money <= 0 or risk_pips <= 0 or pip_value_per_lot <= 0:
        return 0.0

    raw_lot = risk_money / (risk_pips * pip_value_per_lot)

    if lot_step <= 0:
        return round(raw_lot, 2)

    normalized = round(raw_lot / lot_step) * lot_step
    return round(max(normalized, 0.0), 2)


def calculateMarginEstimate(
    entry_price: float,
    lot_size: float,
    leverage: float,
    contract_size: float = 100000.0,
) -> float:
    if entry_price <= 0 or lot_size <= 0 or leverage <= 0 or contract_size <= 0:
        return 0.0

    margin = (entry_price * lot_size * contract_size) / leverage
    return round(margin, 2)


def calculateRewardMoney(reward_pips: float, pip_value_per_lot: float, lot_size: float) -> float:
    if reward_pips <= 0 or pip_value_per_lot <= 0 or lot_size <= 0:
        return 0.0

    return round(reward_pips * pip_value_per_lot * lot_size, 2)
