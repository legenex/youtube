# Unclaimed (channel branch)

**What am I owed?** — the network's commercial engine.

- [channel.config.json](channel.config.json) — locked, machine-read by the
  pipeline agents. The style string in here is verbatim-injected into
  every image prompt; never paraphrase it.
- [format-bible.md](format-bible.md) — editorial boundaries and
  channel-specific production rules.
- [episodes/backlog.md](episodes/backlog.md) — launch order and topic
  queue.
- `episodes/<NNN>-<slug>/` — one directory per episode in production.
- `analytics/` — weekly pulls from the publisher agent.

## Producing an episode on this branch

1. A human marks a backlog entry `picked`.
2. Run the agents in order: `researcher` → `fact-checker` (**human
   sign-off required**) → `script-writer` → `scene-breakdown` →
   `video-producer` (manual insert: portal screen recordings) →
   `reviewer` → `publisher` (**human approves the publish**).
3. Human gates on this channel: fact-check sign-off, 10-frame spot check,
   portal recordings, thumbnail pick, publish approval.

## Before launch (from the 90-day plan)

- [ ] Lock ElevenLabs voice ID (warm, measured) in config
- [ ] Build Canva thumbnail template; put template ID in config
- [ ] Create reusable eligibility-tree graphics
- [ ] Separate Google account; channel art, about page, banner
- [ ] Newsletter landing page (The Unclaimed Report)
- [ ] Funnel-separation rules documented before any commercial pathway
- [ ] Ten scripts written and verified; first three videos produced
