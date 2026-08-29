# The story

The whole project, in plain words. Nothing gets drawn or filmed until these words are right.

---

I build apps on my own. There is nobody else. No other developer, no tester, nobody to look
over my shoulder.

When I need something built now, I ask an AI to write the code. It writes it. Then it tells me
it is done and the tests all passed.

It tells me that every time. It told me that the time it got my checkout wrong.

## What went wrong

A customer buys something from me for $89. She taps pay. Her phone loses signal halfway through.
She taps pay again. Stripe charges her $89 twice. She is out $178, and I find out three days
later when she emails me.

The AI did not lie to me. I asked it to stop people being charged twice, and it wrote code that
stops people being charged twice — as long as nothing goes wrong. I never told it what to do
when the phone loses signal. I never thought of it.

At a big company, someone else reads your work and says "what happens if the phone drops?" On my
own, nobody says it. The customer says it.

## What I tried

I hired a second AI.

Its only job is to look at the first AI's work and tell me what is going to break. It has one
rule: **it is not allowed to change anything.** It can only tell me.

Then a third AI fixes what the second one found. Then the second one looks again, because fixing
one thing breaks another thing.

So: one AI builds it. One AI attacks it. One AI fixes it. Then the attacker looks again.

## How I know if it actually helped

Feeling like it helped is not the same as it helping. So I measured it.

I made a list of 18 things the finished code has to get right. Real things:

- A "forgot my password" link has to stop working after 10 minutes.
- The same payment must never go through twice.
- If someone changes your password, you have to be told.

**I did not make these up.** I copied them out of security rules published by a group called
OWASP, and out of Stripe's own written instructions. If I invented the rules myself, I could
quietly pick easy ones and look clever.

**I hid the list from both AIs.** If the AI can read the test, it writes code that passes the
test instead of code that works. Same reason you do not give a kid the exam paper the night
before.

## What happened

The AI on its own got **11 of the 18 right.**

The AI with the checker got **14 of the 18 right.**

I ran the whole thing seven times. Four times with just the builder. Three times with the
checker added. Same score every single time.

The checker costs about seven times more money and takes about thirteen times longer. For
someone's card being charged twice, I will pay that.

## The part I nearly missed

It gets 14 every time. But it does not fix the *same* 14 every time.

Only **two** of the fixes happen on every run. **Four** of them are a coin flip — sometimes it
catches them, sometimes it does not.

If I had only looked at the score, I would be telling you this thing reliably fixes four
problems. It reliably fixes two. The steady number was hiding a wobbly machine underneath.

## The thing I tried that made it worse

The checker sometimes argues very confidently for a rule that is not real. And the fixer
believes it. Once, it broke something that was already working fine.

So I built a guard: the fixer can only change the code if the checker proves its case first.

**It made everything worse.** The score went from 14 down to about 12. The guard blocked two
things that were correct, to half-stop one thing that was wrong.

Here is why, and it is the useful bit. My guard was marking **how well the checker argued.**
Arguing well is the one thing AI is brilliant at. The finding that actually hurt me was not badly
argued — it was dangerous because using it *deleted something that already worked*, and I was
not looking for that at all.

## What I would tell anyone building this

Do not mark the argument. Mark the damage. Before you let an AI change your code, check whether
the change breaks something that was working a minute ago. That is cheap, it needs no judgement,
and it would have caught the one that hurt me.

And look underneath your score. A number that stays the same is not the same as a machine that
behaves the same.
