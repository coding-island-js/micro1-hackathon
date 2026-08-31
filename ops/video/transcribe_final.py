import json, sys
from faster_whisper import WhisperModel

model = WhisperModel("small.en", device="cpu", compute_type="int8")
segments, info = model.transcribe(
    "final16k.wav",
    beam_size=5,
    word_timestamps=True,
    vad_filter=False,
)

def ts(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}"

out = []
srt = []
txt = []
for i, seg in enumerate(segments, 1):
    words = [{"w": w.word, "s": round(w.start, 3), "e": round(w.end, 3)} for w in (seg.words or [])]
    out.append({"id": i, "start": round(seg.start, 3), "end": round(seg.end, 3),
                "text": seg.text.strip(), "words": words})
    srt.append(f"{i}\n{ts(seg.start).replace('.', ',')} --> {ts(seg.end).replace('.', ',')}\n{seg.text.strip()}\n")
    txt.append(f"[{int(seg.start//60):d}:{seg.start%60:06.3f} -> {int(seg.end//60):d}:{seg.end%60:06.3f}] {seg.text.strip()}")
    print(txt[-1], flush=True)

json.dump(out, open("transcript-final.json", "w", encoding="utf-8"), indent=1)
open("transcript-final.srt", "w", encoding="utf-8").write("\n".join(srt))
open("transcript-final.txt", "w", encoding="utf-8").write("\n".join(txt))
print("DONE segments=", len(out))
