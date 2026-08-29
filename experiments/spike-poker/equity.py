"""Exact Texas Hold'em equity by enumeration. No estimates, no simulation.

Heads-up, both hands known, board known. We deal out every possible remaining board and
count. That makes the right answer a fact, not an opinion -- which is the whole reason
poker is worth testing an agent on.
"""
from __future__ import annotations

import itertools
from collections import Counter

RANKS = "23456789TJQKA"
SUITS = "cdhs"
RVAL = {r: i for i, r in enumerate(RANKS, start=2)}

DECK = [r + s for r in RANKS for s in SUITS]


def parse(cards: str) -> list:
    return cards.split()


def _rank7(cards: list) -> tuple:
    """Best 5-card rank from 7. Higher tuple wins."""
    best = None
    for combo in itertools.combinations(cards, 5):
        r = _rank5(combo)
        if best is None or r > best:
            best = r
    return best


def _rank5(cards) -> tuple:
    vals = sorted((RVAL[c[0]] for c in cards), reverse=True)
    suits = [c[1] for c in cards]
    counts = Counter(vals)
    # order by count first, then by value
    ordered = sorted(counts.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
    shape = [c for _, c in ordered]
    kick = [v for v, _ in ordered]

    flush = len(set(suits)) == 1
    uniq = sorted(set(vals), reverse=True)
    straight_hi = None
    if len(uniq) >= 5:
        for i in range(len(uniq) - 4):
            if uniq[i] - uniq[i + 4] == 4:
                straight_hi = uniq[i]
                break
        if straight_hi is None and set([14, 5, 4, 3, 2]).issubset(set(uniq)):
            straight_hi = 5

    if flush and straight_hi:
        return (8, straight_hi)
    if shape[0] == 4:
        return (7, kick[0], kick[1])
    if shape[0] == 3 and shape[1] == 2:
        return (6, kick[0], kick[1])
    if flush:
        return (5, *vals)
    if straight_hi:
        return (4, straight_hi)
    if shape[0] == 3:
        return (3, *kick)
    if shape[0] == 2 and shape[1] == 2:
        return (2, *kick)
    if shape[0] == 2:
        return (1, *kick)
    return (0, *vals)


def equity(hero: str, villain: str, board: str) -> float:
    """Hero's exact equity (win + half of ties) as a fraction."""
    h, v, b = parse(hero), parse(villain), parse(board) if board.strip() else []
    known = set(h + v + b)
    rest = [c for c in DECK if c not in known]
    need = 5 - len(b)

    win = tie = total = 0
    for extra in itertools.combinations(rest, need):
        full = b + list(extra)
        hr = _rank7(h + full)
        vr = _rank7(v + full)
        total += 1
        if hr > vr:
            win += 1
        elif hr == vr:
            tie += 1
    return (win + tie / 2.0) / total


def correct_action(hero: str, villain: str, board: str, pot: float, to_call: float) -> dict:
    """Call is correct when equity beats the price you are being laid."""
    eq = equity(hero, villain, board)
    breakeven = to_call / (pot + to_call)
    return {
        "equity": round(eq * 100, 2),
        "breakeven_pct": round(breakeven * 100, 2),
        "action": "call" if eq > breakeven else "fold",
        "margin_pts": round((eq - breakeven) * 100, 2),
    }
