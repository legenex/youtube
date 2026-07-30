# Episode 1 Build Log

Run date: 2026-07-30
Origin: recorded on the retired branch `claude/unclaimed-episode-1-build-1pmbjb`,
salvaged into `channel/unclaimed` during the branch consolidation.
Status: HALTED at environment check. No generation calls were made and no
credits were spent.

> **Partially superseded on 2026-07-30 by the branch consolidation.** The
> section headed "Additional blockers found before halt" reported the five
> reference markdown files as absent from the repo and its history. That was
> true of `channel/unclaimed` at the time — the files existed only on an
> unmerged staging branch. They are now present under
> `channels/unclaimed/episodes/episode-01/resources/reference/`, so that
> finding no longer applies. Every other blocker below is still open.

## Environment check results

1. Node and FFmpeg
   - Node: v22.22.2. PASS (requirement: 22 or higher).
   - FFmpeg: NOT PRESENT on PATH. FAIL. The FFmpeg fallback composition path
     is not available as the environment stands.

2. Hyperframes CLI
   - Responds: version 0.7.86. PASS. Skill suite already installed under
     `.agents/skills` (see `skills-lock.json`).

3. Higgsfield MCP
   - Reachable: YES. `models_explore` called once with a recommend query for
     flat illustration text-to-image and locked-camera image-to-video.
   - Image model: NOT CHOSEN. The recommend pass surfaced no committed pick
     and the build halted before any generation, so no image model is
     recorded.
   - Image-to-video model: NOT CHOSEN, same reason. Candidates surfaced:
     grok_video_v15, grok_video, cinematic_studio_video_v2.

4. ElevenLabs MCP
   - Reachable: NO. The ElevenLabs MCP server requires OAuth authentication
     and that session was non-interactive, so the flow could not be
     completed. No ElevenLabs tools were available. Per the build spec,
     ElevenLabs is not optional: HALT.
   - Voice id: NOT RECORDED. `channels/unclaimed/channel.config.json` carries
     the placeholder `TODO-locked-voice-id-unclaimed`. No locked channel voice
     exists to use even after authentication.

## Additional blockers found before halt

- The four required context files do not exist in the repository or anywhere
  in its git history: 01-channel-bible.md, 02-style-contracts.md,
  03-research-standard.md, 05-reference-episodes.md. Verified by filename and
  content search across the working tree and all commits on all branches.
  **(Resolved — see the superseded note at the top of this file.)**
- Consequences, as recorded at the time:
  - No source script. The 2:50 Episode 1 script the expansion depends on was
    specified as living in file 05, which was absent.
  - No ISO style string. Hard rule 1 requires the style string to be read
    from config and asserted by string equality before every generation call.
  - No standing source set for research (file 03) and no forbidden
    constructions list (file 01 section 7) to check beats against.
- **Style conflict, still unresolved and now visible side by side.** The
  binding channel config at `channels/unclaimed/channel.config.json` defines
  hand-drawn black marker on white paper with green `#1B7F4D` as the single
  accent. The staged contract at `resources/reference/02-style-contracts.md`
  defines soft matte low-poly isometric on pale sage `#D8E0D6` with emerald
  `#3AAE5C`. These cannot both be true. The channel config is authoritative
  under hard rule 1, and no agent may write or paraphrase a style string, so
  reconciling the two is a human editorial decision.
- Music: channel config marks the locked Envato track family as TODO, so no
  locked track exists in the repo music family.

## Decisions recorded

- None. The build halted before any pre-authorized decision point was
  reached.

## What is needed to unblock

1. Authenticate the ElevenLabs MCP connector from an interactive session.
2. Lock a channel voice id in `channels/unclaimed/channel.config.json`.
3. Reconcile the style conflict above and lock the Envato track family.
4. Install FFmpeg in the execution environment, or accept Hyperframes as the
   only composition path.
