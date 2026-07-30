# Three-Channel YouTube Network

Automated production system for three YouTube channels, built from the
[Three-Channel Network Playbook](docs/PLAYBOOK.md).

| Channel | Question | Role | Branch |
|---|---|---|---|
| **Unclaimed** | What am I owed? | Commercial engine | `channel/unclaimed` |
| **Behavior by Design** | Why did I do that? | Audience growth engine | `channel/behavior-by-design` |
| **Law, Actually** | What happens legally now? | Authority / evergreen library | `channel/law-actually` |

## How this repo is organised

**One codebase. Three config files.** The pipeline and the agents are
channel-agnostic. Everything channel-specific lives in that channel's
`channels/<channel>/channel.config.json` and format bible.

- This base branch holds the shared infrastructure: the playbook, the
  pipeline documentation (`pipeline/`), and the agent definitions
  (`.claude/agents/`).
- Each `channel/*` branch layers a `channels/<channel>/` directory on top:
  channel config, format bible, episode backlog, and produced episodes.

## The pipeline (per episode)

1. **Idea** — demand-scored topic queue (`idea-scout` agent)
2. **Research** — every claim carries a source URL (`researcher` agent)
3. **Fact gate** — adversarial claim review (`fact-checker` agent; human
   sign-off mandatory for Unclaimed and Law, Actually)
4. **Script** — written against the channel's format bible (`script-writer`)
5. **Scene breakdown** — 100–150 timestamped scenes; the style string is
   injected programmatically from config, never written by a model
   (`scene-breakdown` agent)
6. **Images / voice / assembly** — generation against injected prompts,
   locked voice ID per channel, timeline assembled from scene JSON
   (`video-producer` agent)
7. **Review** — quality, style-drift, and compliance gate (`reviewer` agent;
   legal review is a hard gate on Law, Actually)
8. **Metadata + publish** — titles, description, disclaimer block, playlist,
   Shorts extraction (`publisher` agent; human approves the publish)

## Where automation stops

Four things stay human, deliberately: fact-checking sign-off, legal review,
title/thumbnail iteration, and genuine format variation between episodes.
A channel that automates all four is the exact pattern platforms enforce
against.

## Working on a channel

```bash
git checkout channel/unclaimed          # or channel/behavior-by-design, channel/law-actually
```

Each channel branch's `channels/<channel>/README.md` is the entry point.
