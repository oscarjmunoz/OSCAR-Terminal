from app.execution import calculator


def test_calculate_risk_money():
    assert calculator.calculateRiskMoney(10000.0, 0.5) == 50.0
    assert calculator.calculateRiskMoney(0.0, 0.5) == 0.0


def test_calculate_pip_and_reward_distance_for_fx():
    risk_pips = calculator.calculatePipDistance(1.17520, 1.17440, "EURUSD")
    reward_pips = calculator.calculateRewardDistance(1.17520, 1.17760, "EURUSD")

    assert risk_pips == 8.0
    assert reward_pips == 24.0


def test_calculate_jpy_pip_distance():
    risk_pips = calculator.calculatePipDistance(147.150, 147.050, "USDJPY")
    assert risk_pips == 10.0


def test_calculate_rr_lot_margin_and_reward_money():
    rr = calculator.calculateRR(24.0, 8.0)
    lot = calculator.calculateLotSize(risk_money=50.0, risk_pips=8.0, pip_value_per_lot=10.0)
    margin = calculator.calculateMarginEstimate(entry_price=1.17520, lot_size=0.62, leverage=100.0)
    reward_money = calculator.calculateRewardMoney(reward_pips=24.0, pip_value_per_lot=10.0, lot_size=0.62)

    assert rr == 3.0
    assert lot == 0.62
    assert margin == 728.62
    assert reward_money == 148.8
