# The video is narrated in Raj's own voice, not TTS

Decided 2026-08-30 by Raj, after checking `RULES.md` in full.

**The rules permit TTS.** Deliverable 3 specifies only the six content beats and a 5:00 cap —
nothing about voice, face or narrator. Ground rule 3 (licence terms) is the only constraint, and
both Gemini and OpenAI TTS voices are commercially usable.

**Why we still didn't:**
- **End to End Quality is 20 points** and names the failure mode: *"does it read as clearly AI
  generated?"* A synthetic narrator on a video about AI agents is the loudest possible signal.
- The video is a deck scroll with no face, so **the voice is the only human thing in it.**
- The script is first person — "I build software on my own." Problem & User Value (15 pts) asks
  *who experiences the bottleneck*, and the answer is Raj. A voice that isn't his breaks that.
- Practically, a live take syncs scroll to speech for free. TTS means matching the scroll to
  generated audio afterwards — more work, not less.

**How to apply:**
- A take with a stumble beats a polished synthetic one for this rubric. The script carries 31
  seconds of slack for exactly that.
- Never patch one bad section with TTS. A narrator that changes halfway is worse than either
  option alone.
- This flips only if Raj loses his voice, or the real choice becomes "AI voice or no video" —
  a synthetic narrator scores far above a missing deliverable.
- For reference, his house voice is Gemini `gemini-2.5-flash-preview-tts` / **Sulafat** (female
  warm narrator), driven by a natural-language `steer` string, in `keepaisharp-youtube`. Not
  ElevenLabs — there is no ElevenLabs code anywhere in his projects.

Related: [[reference-rubric-weights]] · [[constraint-packaging-is-the-gap]]
