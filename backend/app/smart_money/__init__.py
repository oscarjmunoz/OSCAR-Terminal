# backend/app/smart_money/__init__.py
# REEMPLAZAR COMPLETAMENTE EL ARCHIVO

"""
OSCAR Terminal
Smart Money Concepts Package

Este paquete contiene todos los motores institucionales
que utilizará OSCAR para interpretar la estructura del mercado.

Motores actuales
----------------
✔ Swing Engine
✔ Market Structure Engine

Motores siguientes
------------------
- BOS Engine
- CHoCH Engine
- MSS Engine
- Liquidity Engine
- Order Block Engine
- Fair Value Gap Engine
- Premium / Discount Engine
"""

from .models import (
    Swing,
    MarketStructure,
)

from .swing_engine import SwingEngine
from .geometry import GeometryEngine
from .market_structure import MarketStructureEngine
from .service import SmartMoneyService

__all__ = [
    "Swing",
    "MarketStructure",
    "SwingEngine",
    "GeometryEngine",
    "MarketStructureEngine",
    "SmartMoneyService",
]