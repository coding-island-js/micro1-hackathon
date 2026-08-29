// Wait for the next Telegram message from Raj, print it, and only then mark it read.
//   node tools/tg-wait.js [maxSeconds]
// Prints "NOTHING" if nothing arrives inside the window.
//
// The first version of this file seeded an offset before listening, which silently
// discarded any message that had already arrived. Nothing is acknowledged now until
// after it has been printed.
const t = require('../../AutomationTools/telegram');

const maxSeconds = parseInt(process.argv[2] || '240', 10);
const started = Date.now();

function textsFrom(items) {
  const out = [];
  for (const u of items) {
    const m = u.message || u.edited_message;
    if (m && m.text) out.push({ id: u.update_id, when: m.date, text: m.text });
  }
  return out;
}

async function main() {
  let lastSeen;

  while ((Date.now() - started) / 1000 < maxSeconds) {
    let res;
    try {
      res = await t._getUpdates(lastSeen, 30);
    } catch (e) {
      // Transient network blips are normal on a long poll. Wait and try again.
      await new Promise((r) => setTimeout(r, 3000));
      continue;
    }

    const items = (res && res.result) || [];
    const msgs = textsFrom(items);

    if (msgs.length) {
      console.log('MESSAGES:');
      msgs.forEach((m, i) => {
        console.log(`[${i + 1}] ${new Date(m.when * 1000).toLocaleTimeString()}  ${m.text}`);
      });
      // Acknowledge only what we just printed.
      const highest = items[items.length - 1].update_id;
      try {
        await t._getUpdates(highest + 1, 0);
      } catch (e) {
        /* the next run will re-read them, which is the safe failure */
      }
      return;
    }
  }
  console.log('NOTHING');
}

main().catch((e) => {
  console.log('ERROR: ' + e.message);
  process.exit(1);
});
