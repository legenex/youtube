# Automation Pipeline

Channel-agnostic production pipeline. Everything channel-specific is read
from `channels/<channel>/channel.config.json` — see
[`channel.config.schema.json`](channel.config.schema.json).

## Layers

| # | Layer | Automation level |
|---|---|---|
| 1 | Demand and idea generation | Automated; human picks from the queue |
| 2 | Research (source URL required per claim) | Automated; URL requirement enforced at schema level |
| 3 | Fact gate | Automated for Behavior by Design; **human sign-off mandatory for Unclaimed and Law, Actually** |
| 4 | Script | Automated |
| 5 | Scene breakdown + prompt generation | Fully automated; **style string injected from config, never model-written** |
| 6 | Image generation | Automated; human spot-checks 10 frames per episode |
| 7 | Voice (locked voice ID per channel) | Fully automated |
| 8 | Assembly | Automated (manual insert: portal screen recordings on Unclaimed) |
| 9 | Music and sound | Automated |
| 10 | Thumbnails | Automated; human picks between three variants |
| 11 | Metadata and SEO | Automated |
| 12 | Publish + Shorts extraction | Automated; **human approves the publish** |
| 13 | Analytics loop | Automated reporting; human decides changes |

## Non-negotiables

1. **The style string is injected programmatically.** The one production
   failure that has already happened was prompt drift off a paraphrased
   style string. No agent writes or paraphrases it — the scene-breakdown
   step reads `visual_style.style_string` verbatim from config.
2. **No claim ships without a live official URL** in the script file
   (Unclaimed), and **nothing publishes without legal review**
   (Law, Actually).
3. **Three distinct voices, three separate Google accounts.** A shared
   voice is the fastest way to get algorithmically linked as one operator.
4. Fact-checking, legal review, title/thumbnail iteration, and format
   variation stay human.

## Episode working directory

Each episode lives at `channels/<channel>/episodes/<NNN>-<slug>/`:

```
research.md        # claims, each with source URL; fact-gate verdict at top
script.md          # locked format; disclaimer block appended
scenes.json        # 100-150 timestamped scenes with injected image prompts
assets/            # generated frames, voice track, thumbnail variants
metadata.md        # title variants, description, tags, playlist, Shorts cut points
review.md          # reviewer agent output + human sign-offs
```
