import json
DUR = 318.767
sil = json.load(open("silences.json"))
mot = json.load(open("motion.json"))

def subtract(a, b, ivs):
    """return [a,b] minus all motion intervals"""
    out = [[a, b]]
    for ms, me in ivs:
        nxt = []
        for s, e in out:
            if me <= s or ms >= e: nxt.append([s, e]); continue
            if ms > s: nxt.append([s, ms])
            if me < e: nxt.append([me, e])
        out = nxt
    return out

# Real-file slides get extra dwell so judges can read: slide 3, 6, 10, 13
PROTECT = [(28.0, 46.0), (74.0, 80.0), (134.0, 139.0),
           (140.0, 146.0), (222.0, 226.0), (162.0, 170.0),
           (225.0, 250.0), (224.0, 229.0)]
def protected(t):
    return any(a <= t <= b for a, b in PROTECT)

KEEP_DEFAULT = 0.55   # residual still-silence kept on each still gap
KEEP_PROTECT = 1.60   # on real-file slides, leave reading time
KEEP_HEAD    = 0.30
KEEP_TAIL    = 0.90

cuts = []
for s, e in sil:
    for a, b in subtract(s, e, mot):
        L = b - a
        if a < 0.5:                       keep = KEEP_HEAD      # leading silence
        elif b > DUR - 1.0:               keep = KEEP_TAIL      # trailing silence
        elif protected((a + b) / 2):      keep = KEEP_PROTECT
        else:                             keep = KEEP_DEFAULT
        if L > keep + 0.12:
            excess = L - keep
            mid = (a + b) / 2
            cuts.append([round(mid - excess/2, 3), round(mid + excess/2, 3)])

cuts.sort()
removed = sum(e - s for s, e in cuts)
new = DUR - removed
print(f"cuts: {len(cuts)}   removed: {removed:.2f}s   new length: {new:.2f}s = {int(new//60)}:{new%60:05.2f}")

# invert -> keep segments
keeps = []
prev = 0.0
for s, e in cuts:
    if s > prev: keeps.append([round(prev,3), round(s,3)])
    prev = e
if prev < DUR: keeps.append([round(prev,3), round(DUR,3)])
keeps = [k for k in keeps if k[1]-k[0] > 0.04]
print(f"keep segments: {len(keeps)}  total {sum(b-a for a,b in keeps):.2f}s")
json.dump({"cuts":cuts, "keeps":keeps, "new_duration":new}, open("cutplan.json","w"), indent=1)
print("\nlongest cuts:")
for s,e in sorted(cuts, key=lambda c: c[0]-c[1])[:12]:
    print(f"  {int(s//60)}:{s%60:05.2f} -> {int(e//60)}:{e%60:05.2f}  removes {e-s:5.2f}s")
