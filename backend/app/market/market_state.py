from datetime import datetime


class MarketState:

    @staticmethod
    def now():
        return datetime.now()

    @staticmethod
    def current_session():

        hour = datetime.now().hour

        if 0 <= hour < 3:
            return "After Hours"

        if 3 <= hour < 8:
            return "London"

        if 8 <= hour < 9:
            return "London Pre-NY"

        if 9 <= hour < 16:
            return "New York"

        if 16 <= hour < 17:
            return "New York Close"

        return "After Hours"

    @staticmethod
    def market_open():

        return MarketState.current_session() != "After Hours"

    @staticmethod
    def spread_status(spread: float):

        if spread <= 2:
            return "GOOD"

        if spread <= 3:
            return "WARNING"

        return "BAD"

    @staticmethod
    def tradable(spread: float):

        return (
            MarketState.market_open()
            and spread <= 2
        )