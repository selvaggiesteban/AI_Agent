#!/usr/bin/env python3
"""
Sistema de escala tipográfica modular para Ad Studio.
Cuarta perfecta (ratio 1.333) — tamaños calculados proporcionalmente al canvas.
"""

MODULAR_RATIO = 1.333
BASE_PERCENT = 0.05
LINE_HEIGHT_MULT = 1.3

_RATIOS = {
    "title": MODULAR_RATIO ** 2,     # 1.777
    "subtitle": MODULAR_RATIO,        # 1.333
    "body": 1.0,
    "caption": 1 / MODULAR_RATIO,     # 0.750
    "detail": 1 / (MODULAR_RATIO ** 2),  # 0.562
}


def round_even(n):
    return int(round(n / 2) * 2)


def get_type_scale(W, H):
    base = min(W, H) * BASE_PERCENT
    return {level: round_even(base * ratio) for level, ratio in _RATIOS.items()}


def get_line_height(font_size):
    return int(font_size * LINE_HEIGHT_MULT)
