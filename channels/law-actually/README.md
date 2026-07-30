# Law, Actually (channel branch)

**What happens legally now?** — the network's authority and evergreen
library. Launches last (month 3): it needs the strongest review process
in place first.

- [channel.config.json](channel.config.json) — locked, machine-read by the
  pipeline agents. The style string is verbatim-injected into every image
  prompt; never paraphrase it.
- [format-bible.md](format-bible.md) — legal discipline, the review gate,
  and separation from Unclaimed.
- [episodes/backlog.md](episodes/backlog.md) — launch order and topic
  queues.
- `episodes/<NNN>-<slug>/` — one directory per episode in production.
- `analytics/` — weekly pulls; test suggested-feed performance alongside
  search.

## Producing an episode on this branch

1. A human marks a backlog entry `picked`; jurisdictional framing is
   decided before research begins.
2. Run the agents in order: `researcher` → `fact-checker` (**human
   sign-off required**) → `script-writer` → `scene-breakdown` →
   `video-producer` → `reviewer` → **human legal review, without
   exception** → `publisher` (**human approves the publish**).
3. Human gates on this channel: fact-check sign-off, **legal review**,
   10-frame spot check, thumbnail pick, publish approval. Cadence is
   capped by legal review capacity, not production capacity.

## Before launch (from the 90-day plan)

- [ ] Appoint the legal reviewer; lock disclaimer language
- [ ] Finalise the legal sourcing standard; source archive structure
- [ ] Lock ElevenLabs voice ID (precise, slightly cold) in config
- [ ] Build Canva thumbnail template; put template ID in config
- [ ] Build scenario and court-process visual templates
- [ ] Separate Google account; channel art, about page, banner
- [ ] Ten scripts researched, written and cleared; first three videos
      produced before launch
