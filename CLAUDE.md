# Repo rules

Automated YouTube production network. Read `README.md` and
`docs/PLAYBOOK.md` before doing anything substantive.

## Branch model

- Base branch: shared pipeline, agents, docs. Channel-agnostic only.
- `channel/unclaimed`, `channel/behavior-by-design`, `channel/law-actually`:
  one branch per channel. Channel-specific work (config, format bible,
  episodes, assets) happens only on its channel branch, under
  `channels/<channel>/`.
- Shared/pipeline changes are made on the base branch and merged into the
  three channel branches — never edited divergently per channel.

## Hard rules for all agents and sessions

1. **Never write or paraphrase a channel's style string.** It lives in
   `channels/<channel>/channel.config.json` → `visual_style.style_string`
   and is injected into prompts programmatically, verbatim.
2. **Human gates are real.** Fact-check sign-off (Unclaimed, Law Actually),
   legal review (Law Actually), thumbnail pick, and publish approval are
   human actions. No agent marks them done.
3. **No claim without a live source URL.** Research and scripts carry the
   URL inline.
4. **Editorial boundaries** in each channel's format bible are binding: no
   guaranteed outcomes, no personalised legal/tax/financial advice, no
   manufactured urgency, no "free money" language.
5. Channels never share a voice ID, thumbnail template, or visual accent.
   Cross-channel reuse of channel-specific assets is a bug.
