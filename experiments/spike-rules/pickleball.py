"""Official doubles pickleball scoring, done properly, as the answer key.

Rules from the USA Pickleball rulebook: side-out scoring in traditional doubles.
Only the serving side can score. The score is called server-score, receiver-score,
server-number. The very first service turn of the game starts at server number 2.
When the serving side loses a rally, service passes to the partner; when the second
server loses, the serve goes to the other team, starting at server number 1.
"""
from __future__ import annotations


def play(rallies: list) -> list:
    """rallies is a list of 'S' (serving side won) or 'R' (receiving side won).

    Returns the called score after every rally, as strings like "4-2-1".
    """
    score = {"A": 0, "B": 0}
    serving = "A"
    server_no = 2          # first service turn of the game starts on server 2
    out = []

    for r in rallies:
        if r == "S":
            score[serving] += 1
        else:
            if server_no == 1:
                server_no = 2
            else:
                serving = "B" if serving == "A" else "A"
                server_no = 1
        receiving = "B" if serving == "A" else "A"
        out.append("%d-%d-%d" % (score[serving], score[receiving], server_no))
    return out


CASES = [
    ["S", "S", "R", "R", "S"],
    ["R", "R", "S", "S", "S", "R"],
    ["S", "R", "S", "R", "S", "R", "S"],
    ["R", "S", "S", "R", "R", "S", "S", "S"],
    ["S", "S", "S", "R", "S", "R", "R", "S", "S"],
]

if __name__ == "__main__":
    for i, c in enumerate(CASES, 1):
        print(i, " ".join(c), "->", " ".join(play(c)))
