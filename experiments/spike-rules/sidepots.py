"""Side pot arithmetic, done properly, as the answer key.

When players are all in for different amounts, the pot splits into a main pot and one
side pot per distinct all-in level. Each pot is contested only by the players who put
in at least that much. This is pure arithmetic with one right answer.
"""
from __future__ import annotations


def pots(contributions: dict) -> list:
    """contributions: player -> chips put in. Returns [(amount, [eligible players])]."""
    levels = sorted(set(contributions.values()))
    out, previous = [], 0
    for level in levels:
        contributors = [p for p, c in contributions.items() if c >= level]
        amount = (level - previous) * len(contributors)
        if amount > 0:
            out.append((amount, sorted(contributors)))
        previous = level
    return out


def award(contributions: dict, ranking: list) -> dict:
    """ranking: players best hand first. Returns player -> chips won."""
    won = {p: 0 for p in contributions}
    for amount, eligible in pots(contributions):
        for player in ranking:
            if player in eligible:
                won[player] += amount
                break
    return won


CASES = [
    # (contributions, ranking best-first, plain description)
    ({"Ann": 100, "Ben": 60, "Cal": 250}, ["Ben", "Ann", "Cal"],
     "Ann is all in for $100, Ben is all in for $60, Cal covers everyone with $250. "
     "Ben has the best hand, Ann second, Cal worst."),
    ({"Ann": 200, "Ben": 200, "Cal": 75}, ["Cal", "Ann", "Ben"],
     "Ann and Ben each put in $200. Cal is all in for $75. Cal has the best hand, "
     "then Ann, then Ben."),
    ({"Ann": 50, "Ben": 120, "Cal": 120, "Dee": 300}, ["Ann", "Dee", "Ben", "Cal"],
     "Ann is all in for $50, Ben and Cal are all in for $120 each, Dee puts in $300. "
     "Ann has the best hand, then Dee, then Ben, then Cal."),
    ({"Ann": 400, "Ben": 90, "Cal": 400}, ["Cal", "Ben", "Ann"],
     "Ann and Cal each put in $400. Ben is all in for $90. Cal has the best hand, "
     "then Ben, then Ann."),
    ({"Ann": 30, "Ben": 30, "Cal": 180, "Dee": 180}, ["Ann", "Cal", "Dee", "Ben"],
     "Ann and Ben are all in for $30 each. Cal and Dee each put in $180. Ann has the "
     "best hand, then Cal, then Dee, then Ben."),
]

if __name__ == "__main__":
    for contributions, ranking, text in CASES:
        print(text)
        print("  pots:", pots(contributions))
        print("  won :", award(contributions, ranking))
        print()
