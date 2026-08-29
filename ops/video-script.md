# Video — 5 minutes

You are not reading an essay. You are showing something working and saying what you see.

**Words that are banned in this video.** You never have to say any of these:
idempotency, assertion, harness, ablation, baseline (say "the normal way" or "the plain agent"),
invariant. If a word feels wrong in your mouth, it is not in the script.

**The thing everyone gets wrong is called "the double charge".** That is all you ever call it.

---

## Set up before you record

I will have these two things open for you. You do not need to find anything.

- **Tab 1** — the report page in your browser
- **Tab 2** — the GitHub repo

And one terminal window, already sitting in the project folder, with one command typed but
**not** pressed. You will press Enter on camera.

---

## 1. The problem — 40 seconds

**You, talking. No screen needed, or show the ticket.**

- "I build software on my own. There's nobody else. No other developer, no QA."
- "AI writes most of my code now. And the only thing that tells me it's finished is the AI saying 'done, tests pass'."
- "Here's a real ticket. Customers are getting charged twice when their connection drops. Fix it so the same payment can't go through twice."
- "That's the whole ticket. One sentence. That's normal — nobody writes down the obvious stuff."

---

## 2. Run the normal way, live — 50 seconds

**Press Enter on the command that's already typed. It takes about 30 seconds.**

While it runs:

- "This is a normal coding agent. One go, no review. Same as what most people are doing right now."

When it finishes:

- "Passed every test that came with the ticket."
- "And it still charges the customer twice. Two different ways."
- "If two requests land at the same moment, both go through. If the connection drops halfway, nothing gets saved, so the retry charges them again."
- "So the tests were never the problem. The problem is nobody wrote down what this thing actually has to do — and there's no second person to catch it."

*(If the live run makes you nervous, I'll record it separately and you talk over it. Say the word.)*

---

## 3. What I built — 75 seconds

**Switch to Tab 1, the report page. Scroll slowly.**

- "So I added a second AI. Its only job is to attack the code."
- "It's told to find how this will break in production. And it's not allowed to touch anything — it can only write down what it finds."
- "What it finds goes to a third step that fixes it. Then the reviewer looks again at the fixed version, because a fix can break something that was working."
- "This is what comes out."

**Point at the first finding.**

- "It found the double charge. And look — it doesn't just say 'this looks wrong'. It says exactly which rule is broken, and what happens to a real customer."
- "It worked that out on its own. It never saw the tests it was being marked against."

**Scroll to the bottom section — "Still flagged after the repair pass".**

- "This is the bit I actually care about. After the fix, it *still* says there's a way to double charge."
- "It doesn't tell me it's done. It says five things are still open. And right at the top —" *(scroll up to the banner)* "— it says this is a recommendation, not an approval."
- "I'm still the one deciding. I'm just deciding with a reviewer's notes instead of nothing."

---

## 4. The numbers — 45 seconds

**Switch to Tab 2, the README on GitHub. Scroll to the results table.**

- "Same three tickets both ways. Same AI. Same marking, and the marker doesn't know which version wrote the code."
- "Do nothing, you get 1 out of 18. The normal agent gets 11. Mine gets 14."
- "I ran the normal one four times and mine three times. Same score every single time."

**Scroll down to the table underneath.**

- "But here's the thing I nearly missed, and it's the most useful thing I learned."
- "The score is steady. What it actually does isn't."
- "Only two of those fixes happen every time. Four of them flip run to run and just happen to add up to the same number."
- "If I'd trusted the total, I'd be telling you it reliably fixes four things. It reliably fixes two."

---

## 5. What made the difference — 40 seconds

**Scroll to the changelog on GitHub.**

- "Every experiment is logged here as I ran it."
- "The thing that made the difference was the reviewer that isn't allowed to edit. Splitting 'find the problem' from 'fix the problem' is the whole gain. 61% to 78%."
- "It costs about seven times more and takes about thirteen times longer. For a payment bug, I'll take that trade."

---

## 6. The one I threw away — 60 seconds

**Stay on the changelog, on the row marked REMOVED.**

- "One thing I tried and binned."
- "The reviewer sometimes argues really confidently for a rule that isn't real, and the fixer believes it. It actually broke something the plain agent got right."
- "So I built a check: a finding can only change the code if it proves itself first."
- "Made everything worse. 78% down to 65%. It blocked two things that were correct, to half-stop one that was wrong."
- "And I think I know why. My check was grading how well the reviewer *argued*. That's the one thing AI is brilliant at faking."
- "The finding that actually hurt me was dangerous for a completely different reason — using it deleted something that already worked. I wasn't looking for that at all."
- "So: don't grade the argument. Just check whether the change breaks something that's currently fine."
- "And the other one — a score that repeats isn't the same as behaviour that repeats. Look underneath the number."

---

## If you run long

Cut in this order:

1. The cost line in section 5
2. "So the tests were never the problem…" at the end of section 2
3. One of the two findings you point at in section 3

**Never cut:** the flipping-scores bit in section 4, or section 6. Those two are what nobody else will have.

## Three things not to say

- Don't say it "works" or is "production ready". It fixes 14 out of 18 and breaks one. Say that.
- Don't say "on average". It was the same every run. That's a stronger thing to say and it's true.
- Don't pretend three tickets is plenty. Say you spent the time running them over and over instead of adding more, and it's the first thing you'd change.
