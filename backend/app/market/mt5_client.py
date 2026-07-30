import MetaTrader5 as mt5


class MT5Client:

    _initialized = False

    @classmethod
    def initialize(cls):

        if cls._initialized:
            return True

        cls._initialized = mt5.initialize()

        return cls._initialized

    @classmethod
    def shutdown(cls):

        if cls._initialized:
            mt5.shutdown()
            cls._initialized = False