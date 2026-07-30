# backend/app/smart_money/README.md

"""
===========================================================
OSCAR TERMINAL
SMART MONEY ENGINE
Version: 0.3.0-alpha
===========================================================

Estado actual
-------------

✔ Swing Engine
✔ Geometry Engine
✔ Market Structure
✔ API REST

Endpoints disponibles
----------------------

GET

/api/v1/smart-money/swings/{symbol}

/api/v1/smart-money/structure/{symbol}


Ejemplos

/api/v1/smart-money/swings/USDCHF.pro

/api/v1/smart-money/structure/USDCHF.pro


Respuesta Swings
----------------

[
    {
        "index": 21,
        "time": "...",
        "price": 0.80491,
        "kind": "HIGH",
        "structure": "HH"
    },
    {
        "index": 34,
        "time": "...",
        "price": 0.80422,
        "kind": "LOW",
        "structure": "HL"
    }
]


Respuesta Structure
-------------------

{
    "trend":"BULLISH",
    "last_high":0.80522,
    "last_low":0.80411,
    "bos":true,
    "choch":false,
    "mss":false
}


Roadmap
-------

HD-005.2
---------

✔ BOS Detector

✔ CHoCH Detector

✔ MSS Detector

HD-005.3
---------

✔ Liquidity Engine

✔ Equal Highs

✔ Equal Lows

✔ Liquidity Sweep

HD-005.4
---------

✔ Order Block Engine

✔ Mitigation

✔ Breaker Blocks

HD-005.5
---------

✔ Fair Value Gaps

✔ Inversion FVG

✔ Balanced Price Range

HD-006
-------

✔ Probability Engine

✔ Institutional Score

✔ Trade Engine

===========================================================
"""