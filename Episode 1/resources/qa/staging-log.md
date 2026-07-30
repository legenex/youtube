# Episode 1 staging log

Date: 2026-07-30
Branch: claude/stage-unclaimed-episode-1-y1gus0 (based on channel/unclaimed)
Input source used: chat upload 0d9e6051-Resources.zip (no local Unclaimed folder was present, so the uploaded archive was used)
Working tree at start: clean, no stash needed

## Staged files

| Original filename | Staged path | Bytes |
| :- | :- | -: |
| 01-channel-bible.md | Episode 1/resources/reference/01-channel-bible.md | 11462 |
| 02-style-contracts (1).md | Episode 1/resources/reference/02-style-contracts.md | 13748 |
| 03-research-standard.md | Episode 1/resources/reference/03-research-standard.md | 9743 |
| 04-pipeline-and-prompts.md | Episode 1/resources/reference/04-pipeline-and-prompts.md | 22623 |
| 05-reference-episodes.md | Episode 1/resources/reference/05-reference-episodes.md | 15801 |
| UNCLAIMED &middot; EPISODE 1_What Happens to Gift Card Balances Nobody Spends.docx | Episode 1/resources/reference/source/episode-01-original.docx | 218901 |
| Scene 1 _ 1_1.jpg | Episode 1/resources/reference/frames/scene-01.jpg | 510479 |
| Scene 2 _ 1_1.jpg | Episode 1/resources/reference/frames/scene-02.jpg | 460246 |
| Scene 3 _ 1_1.jpg | Episode 1/resources/reference/frames/scene-03.jpg | 515231 |
| Scene 4 _ 1_1.jpg | Episode 1/resources/reference/frames/scene-04.jpg | 483124 |
| Scene 5 _ 1_1.jpg | Episode 1/resources/reference/frames/scene-05.jpg | 497141 |
| Gift_card_strip_depleting_and_202607291507.mp4 | Episode 1/resources/reference/clips/gift-card-strip-depleting.mp4 | 2657193 |

## Unexpected items in the archive

The archive contained macOS metadata that is not content: a __MACOSX folder of AppleDouble sidecar files and a .DS_Store file. These were logged here and excluded from staging. No image or clip beyond the expected set was found, and no expected file was missing or dropped.

## Content check results

### Check 1: five markdown files present and non-empty
PASS. All five files present, sizes 9743 to 22623 bytes, none empty.

### Check 2: immutable style strings in 02-style-contracts.md
PASS. Both immutable style strings are present, one under CONTRACT A (ISO) and one under CONTRACT B (RISO). The ISO string begins with "Soft matte low-poly isometric 3D illustration" and ends with "no textures, 16:9".
ISO style string exact character count: 597
A later run asserts against this value. The string itself is not reproduced here by repo rule.

### Check 3: Episode 1 script in 05-reference-episodes.md
PASS. All eleven timecodes from [00:00] to [02:30] in 15 second steps are present. The sign-off line "The money may be unclaimed. It does not have to stay that way." is present. Note: the file also contains a [02:45] timecode beyond the required eleven; nothing is missing.

### Check 4: staged images open and report dimensions
PASS. All five images open.

| File | Width | Height | Aspect ratio | Flag |
| :- | -: | -: | :- | :- |
| scene-01.jpg | 1024 | 1024 | 1:1 | none |
| scene-02.jpg | 1024 | 1024 | 1:1 | none |
| scene-03.jpg | 1024 | 1024 | 1:1 | none |
| scene-04.jpg | 1024 | 1024 | 1:1 | none |
| scene-05.jpg | 1024 | 1024 | 1:1 | none |

All five are exactly 1:1, so none is flagged under the not 1:1 rule. Note for the build: these references are square while the build targets 16:9.

### Check 5: staged clip opens and reports metadata
PASS. gift-card-strip-depleting.mp4: duration 10006 ms, resolution 1280x720 (16:9), frame rate 24 fps.

### Check 6: staging is lossless
PASS. Nothing was converted, downscaled, cropped or re-encoded. SHA-256 of every staged file is byte-identical to its source in the archive. Hashes are recorded in Episode 1/resources/reference/manifest.json.

## Failures

None. All six checks passed.
