# UNCLAIMED Episode 1: staging log

Run type: staging only. No generation, no research, no rendering.
Date: 2026-07-30
Branch: channel/unclaimed

## Source used

Priority 1 source. Branch `claude/stage-unclaimed-episode-1-y1gus0` at commit
`23cefec` existed on the remote and carried all twelve staged files under
`Episode 1/resources/reference/`. Files were extracted from that tree with
`git archive` and relocated. The branch was not merged. The original
`Episode 1/` path does not exist on `channel/unclaimed`.

Upstream provenance recorded in that branch: chat upload
`0d9e6051-Resources.zip`. Original filenames are preserved in
`../reference/manifest.json`.

## Exclusions

No `__MACOSX` sidecars, `.DS_Store` files or AppleDouble `._*` files were
present in the source tree. Nothing was excluded on those grounds. They had
already been dropped upstream.

## Content checks

### Check 1: five markdown files present and non-empty

PASS.

| File | Bytes | Lines |
|-|-|-|
| 01-channel-bible.md | 11462 | 180 |
| 02-style-contracts.md | 13748 | 217 |
| 03-research-standard.md | 9743 | 186 |
| 04-pipeline-and-prompts.md | 22623 | 391 |
| 05-reference-episodes.md | 15801 | 128 |

The file landed as `02-style-contracts.md` with no ` (1)` suffix, which is the
name the build run reads. The original upload name was `02-style-contracts (1).md`
and is preserved in the manifest.

### Check 2: both immutable style strings in 02-style-contracts.md

PASS. The file carries two style contracts, each under a
`## STYLE STRING (immutable)` heading:

- `# CONTRACT A · ISO`
- `# CONTRACT B · RISO`

ISO string verification, string itself not reproduced here:

- Begins `Soft matte low-poly isometric 3D illustration`: confirmed.
- Ends `no textures, 16:9`: confirmed.
- Single line, no internal newlines: confirmed.
- Exact character count: **597**. This matches the expected value of 597, so the
  build run assertion should hold.

### Check 3: Episode 1 script timecodes and sign-off

PASS.

`05-reference-episodes.md` holds two reference episodes. Scoped to the
`# EPISODE 1 · What Happens to Gift Card Balances Nobody Spends` section, the
script carries exactly eleven timecodes:

`[00:00] [00:15] [00:30] [00:45] [01:00] [01:15] [01:30] [01:45] [02:00] [02:15] [02:30]`

The exact sign-off line
`The money may be unclaimed. It does not have to stay that way.`
is present in the Episode 1 script.

Note for whoever reads this next: a twelfth timecode `[02:45]` does appear in
the file, but it belongs to the `# EPISODE 2` section, which runs to twelve
timecodes. It is not part of the Episode 1 script and is not a failure.

### Check 4: staged images open and report dimensions

PASS. All five parsed cleanly from their JPEG SOF markers.

| File | Width | Height | Aspect |
|-|-|-|-|
| frames/scene-01.jpg | 1024 | 1024 | 1:1 |
| frames/scene-02.jpg | 1024 | 1024 | 1:1 |
| frames/scene-03.jpg | 1024 | 1024 | 1:1 |
| frames/scene-04.jpg | 1024 | 1024 | 1:1 |
| frames/scene-05.jpg | 1024 | 1024 | 1:1 |

All five are **square**, at the expected 1024 x 1024. The build targets
**1280 x 720**. These five images are **style reference only**. They never
enter a timeline and are not to be treated as renderable frames. Do not
upscale, crop or letterbox them into the build. They exist so a generation call
can be checked against the intended look.

### Check 5: staged clip opens and reports duration, resolution, frame rate

PASS.

| Property | Value |
|-|-|
| File | clips/gift-card-strip-depleting.mp4 |
| Duration | 10006 ms |
| Resolution | 1280 x 720 |
| Frame rate | 24.000 fps |
| Video codec | avc1 |
| Frame count | 240 |

Read from the MP4 `mvhd`, `tkhd` and `stsd` boxes and the `stts` sample table.

### Check 6: sha256 of every staged file matches its source

PASS. Twelve of twelve match. Zero mismatches. No conversion, no downscale, no
re-encode. Staging is lossless. Hashes also agree with the manifest carried on
the source branch, so the content is unchanged since the original upload.

## Summary

Six of six checks pass. Nothing failed. Nothing was skipped.

Tooling note: `ffprobe` and Pillow were not available in this Codespace, so
image and container metadata were parsed directly from the file headers in
Python rather than through a media library. The values above are read from the
bytes on disk.
