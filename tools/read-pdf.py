#!/usr/bin/env python
"""Pull the text out of the hackathon brief PDF, so RULES.md can be checked against it."""
import re
import sys
import zlib

path = sys.argv[1]
data = open(path, "rb").read()

chunks = []
for m in re.finditer(rb"stream\r?\n(.*?)endstream", data, re.S):
    try:
        chunks.append(zlib.decompress(m.group(1)).decode("latin-1"))
    except Exception:
        pass

body = "\n".join(chunks)
pieces = re.findall(r"\((?:\\.|[^()\\])*\)", body)
text = "".join(p[1:-1] for p in pieces)
text = text.replace(r"\(", "(").replace(r"\)", ")").replace("\\\\", "")
print(text)
