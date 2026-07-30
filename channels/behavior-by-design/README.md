# Behavior by Design (channel branch)

**Why did I do that?** — the network's audience growth engine, and the
first channel to launch (month 1: it proves the pipeline fastest).

- [channel.config.json](channel.config.json) — locked, machine-read by the
  pipeline agents. The style string and character construction in here are
  verbatim-injected into every image prompt; never paraphrase them.
- [format-bible.md](format-bible.md) — the editorial split, tone rules,
  and the red rule.
- [episodes/backlog.md](episodes/backlog.md) — launch order, both family
  queues, and the future episode bank.
- `episodes/<NNN>-<slug>/` — one directory per episode in production.
- `analytics/` — weekly pulls; track internal vs designed-system
  performance separately.

## Producing an episode on this branch

1. A human marks a backlog entry `picked` (keep the A/B alternation).
2. Run the agents in order: `researcher` → `fact-checker` (automated on
   this channel) → `script-writer` → `scene-breakdown` →
   `video-producer` → `reviewer` → `publisher` (**human approves the
   publish**).
3. Human gates on this channel: 10-frame spot check, thumbnail pick,
   publish approval.

## Before launch (from the 90-day plan)

- [ ] Lock ElevenLabs voice ID (dry, mechanical) in config
- [ ] Lock character/diagram style as the verbatim string (done in config
      — review once, then freeze)
- [ ] Build Canva thumbnail template; put template ID in config
- [ ] Build prompt-generation pipeline; reusable behaviour-loop graphics
- [ ] Separate Google account; channel art, about page, banner
- [ ] Ten scripts written and fact-checked; first three videos produced
      before launch
