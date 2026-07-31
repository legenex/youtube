# Episode 1 Build Log

Run date: 2026-07-30, resumed 2026-07-31
Branch: `channel/unclaimed`
Status: **SUPERSEDED BY THE RESUME RUN.** See section 11 at the end of this
file. The 2026-07-30 run below is kept intact as the record of loops A, B, E
and the decisions taken then. Its two blockers are now both resolved: the style
conflict was reconciled by the repo owner in favour of the ISO contract, and an
image generation backend became reachable, so loops C, D, G and H have now run.

Original 2026-07-30 status: **PARTIAL**. Script, research, scenes, narration,
music, programme audio and metadata are complete. Frames, clips, the video
master and the thumbnails were not produced, because no image generation
backend is reachable in this environment. Detail under "Blocking failure"
below.

This log supersedes the previous halted run recorded in this file. That run
halted at the environment check having made no generation calls; its blockers
on the reference files, on FFmpeg and on the audio engine are all resolved
here. Its finding on the style conflict is confirmed and still open.

---

## 1. Working state verified before anything else

All four required inputs are present:

- `channels/unclaimed/brand/` with all five markdown files
- `channels/unclaimed/reference/frames/scene-01.jpg` to `scene-05.jpg`
- `channels/unclaimed/reference/clips/gift-card-strip-depleting.mp4`
- `channels/unclaimed/channel.config.json`

Nothing was recreated. Working tree was clean on `channel/unclaimed` at start.
No branch was created, no pull request opened, `main` untouched.

---

## 2. Style contract authority

**CONFIG_STYLE_MISMATCH. Requires human reconciliation.**

The two style strings are not merely different in wording, they describe two
different visual systems.

- `brand/02-style-contracts.md`, Contract A, ISO: 597 characters. Soft matte
  low-poly isometric, pale sage ground, bone cream and pale putty objects,
  cornflower periwinkle for human elements, one emerald accent.
- `channel.config.json` → `visual_style.style_string`: 686 characters.
  Hand-drawn black marker linework on white paper, flat illustration, green
  `#1B7F4D` accent.

Per the brief this was not treated as a halt. The `brand/02-style-contracts.md`
value is authoritative for this build, because the produced Episode 1 reference
frames are isometric and confirm it. Asserted at 597 characters and byte
identical to the brand file before every prompt was assembled.

The `sha256` of the authoritative string is recorded in `frame-report.json` and
in `scenes.json` as `style_string_sha256`, so a later run can prove it used the
same bytes.

**No agent may write or paraphrase a channel's style string**, so
`channel.config.json` was left exactly as it was. Reconciling the two is a
human editorial decision and is one of the items still needing a human.

**Other style strings found in the repo, ignored as belonging elsewhere:**

- `brand/02-style-contracts.md`, Contract B, RISO. Same channel, different
  named contract, not selected. ISO is the default and was not overridden.
- No style string belonging to `behavior-by-design` or `law-actually` exists on
  this branch, so nothing cross-channel was encountered.

---

## 3. Environment check

| # | Check | Result |
|---|---|---|
| 1 | Node 22 or higher | PASS. v24.14.0, no install needed |
| 2 | FFmpeg and ffprobe | Absent. Installed `ffmpeg` via apt. Both respond, version 6.1.1 |
| 3 | Pillow | Absent. Not installed. No frames were generated, so no downscale step ran. Had it been needed, FFmpeg was present and would have been used, recorded as a substitution |
| 4 | Hyperframes CLI | PASS. Responds, version 0.7.86. Skill suite already installed |
| 5 | Higgsfield MCP | **FAIL. Unreachable.** See below |
| 6 | Audio engine | RESOLVED at option (b) |
| 7 | Voice id | Selected automatically, see below |

### 5 · Higgsfield MCP, unreachable

No MCP servers are reachable in this session. Tool discovery returns no
Higgsfield tools under any query. The only MCP server configured for this
project in `~/.claude.json` is `elevenlabs`, and its tools are not discoverable
either. `models_explore` could not be called, so **no image model and no
image-to-video model were chosen**. There is no other image generation backend
in this environment, and the brief specifies no fallback generator for Loops C
and D.

The earlier halted run recorded Higgsfield as reachable. That was a different
session. It is not reachable now, and this was verified by direct tool
discovery rather than inferred from the absence of a config entry.

### 6 · AUDIO_ENGINE = `elevenlabs_rest`

Resolved in the prescribed order:

- (a) ElevenLabs MCP: tools not discoverable, same root cause as Higgsfield.
- (b) `ELEVENLABS_API_KEY` present in the environment. REST API called
  directly. `GET /v1/voices` returns 200 with 27 voices, `POST
  /v1/text-to-speech/{id}` returns 200 with valid audio. **This resolved.**
- (c) Higgsfield audio: not reached, and would not have been available.

The key lacks the `user_read` permission, so `/v1/user/subscription` returns
401. That endpoint is not needed for synthesis and nothing downstream depends
on it.

### 7 · Voice id, selected automatically

`channel.config.json` carried the placeholder
`TODO-locked-voice-id-unclaimed`, so a voice was selected rather than halting.

**Chosen: `SAz9YHcvj6GT2YYXdXww`, "River, Relaxed, Neutral, Informative".**

Reason: of the 27 available voices it is the closest match to the brief's
requirement of calm, mid pace, unhurried, US accent, no broadcast hype, suited
to plain declarative sentences about money. Its own labels are American accent,
middle aged, descriptive "calm", use case "conversational". Two alternates were
generated for comparison from the beat 1 line before committing: Eric (Smooth,
Trustworthy) reads warmer and slightly more salesy, Brian (Deep, Resonant) sits
lower and more broadcast. River is the plainest of the three.

A 15 second test line from beat 1 was generated before committing to it, as
required.

Written into `channel.config.json` with
`"voice_id_status": "provisional, set automatically on Episode 1, confirm
before Episode 2"`. The style string in that file was not touched.

---

## 4. Blocking failure and what it stopped

**Loops C, D, G and H did not run.** All four depend on generated imagery.

- Loop C, frames: 0 of 40. No image backend.
- Loop D, clips: 0 of 40. Depends on Loop C.
- Loop G, composition and render: not run. A 40 scene timeline over blank
  ground would have produced a file of the correct duration carrying none of
  the episode's visual content. That is a worse outcome than not producing it,
  so it was not produced.
- Loop H, thumbnails: 0 of 3. Needs generated object frames.

Everything upstream and downstream of the image path was completed in full.
The work is staged so that a run with a working image backend needs no
re-authoring: `scenes.json` carries the numeral-stripped VISUAL line, the
motion verb and the type layer for all 40 beats, and the asserted 597 character
ISO string is recorded by hash.

---

## 5. Pre-authorised decisions taken

**Format.** Long form as specified. 40 beats, beats 1 to 39 at 15 seconds,
beat 40 at 20 seconds. Runtime 10:05. Word count **1,309**, inside the 1,300 to
1,340 band. Every beat inside its 31 to 34 word budget, beat 40 at 45 words
inside its 42 to 46 budget. Verified programmatically, not by eye.

**Expansion.** The eleven original beats survive in wording wherever the
40 beat structure allows. Three had to move or change:

- The national dollar figure moved out of original beat 2 into the number
  block at beats 17 to 20, because the beat function map fixes the number
  there. Its figure also changed, see swaps.
- The "at least nineteen states" / "thirty seven states" pair was cut. It could
  not be sourced and the two counts sum to fifty six, which exceeds the number
  of states. Rewritten around two named states with their own statutes.
- The Starbucks figure changed with the current filing.

Everything else, including the opening beat and the sign-off, is carried
intact.

**Green beat: `[04:00]`, beat 17.** The beat function map puts green on the
first beat in 17 to 20 that states the dollar figure out loud. Beat 17 is that
beat. Exactly one beat carries emerald; validated in `scenes.json` and by
string check across all 40 VISUAL lines.

**Anchor object: the kitchen drawer.** Beat 1 open and cluttered, beat 12 the
mid-episode return, changed, beat 40 resolved and nearly empty. Both returns
use the exact phrase "the same open kitchen drawer from the opening frame at
the identical angle". Beat 11 shows a drawer at a deliberately different three
quarter angle so the two identical-angle returns stay distinct.

**Voice direction** written for all 40 beats, one or two short sentences each
naming register plus one emphasis or pause.

**Motion verb** chosen for all 40 clips, each a single action from the
permitted vocabulary, present tense, single clause. No draw-on reveals, no
travelling arrows, no accent landing; those are composition work.

**Music.** Resolved at option (b), ElevenLabs music. Not a placeholder. A
300 second sparse ambient bed was generated with a brief of no percussion, no
melodic hook, no build and no drop, then looped to 630 seconds, low-passed at
2.2 kHz, faded in over 4 seconds and out over 6. Sat under the voice at 0.16
gain with sidechain ducking against the narration. `MUSIC_PLACEHOLDER` does not
apply and `MUSIC_ABSENT` does not apply.

**Thumbnail strings**, chosen but not rendered: "They Still Owe You",
"Check Your Name", "Nobody Claimed It". Objects would have been the kitchen
drawer, the gift card and the drawer again, emerald only on the variant
promising recoverable money.

**Thumbnail palette exception**, recorded as an exception and not as drift:
thumbnail type is warm tan `#C9B48A` rather than bone cream, because cream on
sage sits at roughly two to one contrast and disappears at feed size. The
episode body keeps cream. Not applied this run, since no thumbnail was
rendered.

**Title, description, hashtags and tags** all chosen and written to
`metadata.json`. Title 48 characters, 20 hashtags, 35 SEO tags.

---

## 6. Claims swapped

Five changes, all recorded in full with sources in
`resources/script/claim-log.md`.

1. Total unspent gift card value **$21bn → $27bn**. Current Bankrate survey.
   Stays CONTESTED; the narration says it is an estimate and states outright
   that it is not a government figure.
2. Starbucks breakage **$212m → $222m**. FY2025 Form 10-K, fiscal year ended
   28 September 2025: $200.4m company-operated plus $22.0m licensed. The
   narration rounds down and never overstates the filing.
3. **"At least nineteen states" and "thirty seven states" cut entirely.**
   Unsourceable to official or primary tier after four query reformulations,
   and internally impossible. Rewritten around New York, which deems an
   unredeemed gift certificate abandoned after five years, and California,
   which exempts most gift certificates from escheat.
4. **"Several states" → "fourteen states"** for cash back on small balances,
   from the Connecticut Office of Legislative Research listing, which carries
   the statutory citation for each state.
5. California cash back threshold **$9.99 → under $15**, operative 1 April
   2026 under SB 22, verified against the statute text rather than a secondary
   summary.

One accuracy correction that is not a swap: the original stated the escheat
rule as "state of incorporation, not where you live". That is the second
priority rule. The expanded script states both rules in order, so the mechanism
is correct.

**Claim count by tier:** OFFICIAL 16, PRIMARY 7, CONTESTED 1, SECONDARY 0.
Total 24 sourced claims.

---

## 7. Loop results

Result of the 2026-07-30 run. Superseded by the table in section 11.

| Loop | Result |
|---|---|
| A · script and research | COMPLETE. 40 beats, 1,309 words, all self-checks pass |
| B · scenes | COMPLETE. `scenes.json`, 40 objects, exactly one `is_green` |
| C · frames | **NOT RUN.** No image backend |
| D · clips | **NOT RUN.** Depends on C |
| E · voice | COMPLETE. 40 takes, measured, `voice_ms` written back |
| F · music | COMPLETE. ElevenLabs music, 630s bed |
| G · composition and render | **NOT RUN.** Depends on C and D |
| H · thumbnails | **NOT RUN.** No image backend |
| I · metadata | COMPLETE. All URLs checked |

### Loop E detail

All 40 takes generated, none failed. Delivery pace was corrected rather than
the script: at the initial speed setting 11 beats ran more than 1.5 seconds
past their window, which would have truncated narration mid-sentence in the
padded master. Since the script already satisfies the 31 to 34 word budget, the
variable adjusted was delivery speed, not wording. **No narration was trimmed.**
28 beats were regenerated at a computed speed between 0.749 and 0.992; every
beat now fits inside its window with the 400 ms lead-in applied. Per-beat
speeds are recorded in `voice-refit.json` and `voice_ms` in `scenes.json` is
the measured duration of the take that shipped.

`master.wav` measures 605.00 seconds, exactly 10:05.

### Programme audio, complete and to spec

`resources/voice/episode-audio-master.wav`, 605.00 seconds, voice over ducked
music, integrated loudness **-14.6 LUFS**, true peak **-1.5 dBTP**. Both inside
the specified targets of -14 LUFS and a true peak below -1 dBTP. This is the
finished audio bed for the master and needs no rework once frames exist.

### Loop I detail

Every URL in the description was requested. Seven return 200 to a plain
request. Four return 403 to scripted requests because of bot protection and
were confirmed live by other means, documented in `claim-log.md`:
`sec.gov` (200 with a declared User-Agent, per SEC policy),
`consumerfinance.gov` and `nysenate.gov` (both served full text through the
fetch path), and `missingmoney.com` (blocks all automated access; liveness and
operator confirmed by NAUPA's own site). **No official link is dead**, so this
loop did not halt.

---

## 8. Reference asset handling

Nothing from `channels/unclaimed/reference/` entered any timeline. The five
frames are 1:1 and were treated as style reference only. The clip is on
contract and was ignored for timeline purposes, as instructed.

No file in the reference folder is flat vector, carries a gradient background,
uses an outline stroke or shows a large expressive hand, so nothing was
excluded on those grounds.

**The scene-03 defect was handled, not reproduced.** Beat 26's VISUAL specifies
raised bone cream blocks for the states that hold the balance for the owner and
recessed pale putty for the states that let the issuer keep it. That matches
the narration of the beat and is the reverse of the reference frame.

---

## 9. Git handling

Git LFS is installed in the image but **not configured in this repository**:
there is no `.gitattributes` and no tracked LFS patterns. So the LFS route did
not apply.

No master mp4 exists, so the size decision did not arise. Nothing was
force-added. `.gitignore` already excludes `resources/frames/`,
`resources/clips/`, `resources/voice/`, `resources/music/` and
`episodes/*/*.mp4`, and those exclusions were left alone. The generated voice
and music stay untracked and are reproducible from `scenes.json` and the
recorded voice settings.

Committed: `episode.md`, `scenes.json`, `claim-log.md`, `metadata.json`,
`build-log.md`, `frame-report.json`, `render-report.json`, `voice-report.json`,
`voice-refit.json`, and the `channel.config.json` voice id. No thumbnails
exist to commit.

---

## 10. Still needing a human

1. **Fact-check sign-off.** Not an agent action.
2. **Legal read.** Not required for this channel by config, but the gates list
   it as a human action.
3. **Thumbnail choice.** No thumbnails were produced, so there is nothing to
   choose between yet.
4. **Publish approval.** Not an agent action.

Plus two blockers this run could not decide:

5. **CONFIG_STYLE_MISMATCH.** The channel config and the brand contract
   describe two different visual systems. An agent may not write a style
   string, so a human must decide which is the channel's real look and correct
   the other.
6. **Image generation backend.** Frames, clips, the video master and the
   thumbnails cannot be produced until a Higgsfield MCP connection, or an
   agreed substitute, is available in the execution environment.

---

## 11. Resume run, 2026-07-31

Loops A, B and E were **not** re-run. Research, `episode.md`, `claim-log.md`,
`scenes.json` and all 40 narration takes are carried forward unchanged from
commit `1c2e082`. Loops C, D, F, G, H and I were run.

### 11.1 Pre-flight

All 40 wav files in `resources/voice/` were verified present before anything
else, as instructed. None is missing and none is truncated; measured duration
matches `voice_ms` in `scenes.json` to within 60 ms on every beat, so nothing
was regenerated and no timing changed.

The composition timing grid was then derived from the audio rather than
assumed. Cross-correlating each beat's take against `master.wav` puts every
one of the 40 takes at exactly **400.0 ms** into its window, with zero
deviation. The grid is therefore: beat *i* occupies `[(i-1)*15s, +15s)`, beat
40 occupies `[585s, +20s)`, narration starts 400 ms in.

### 11.2 Style contract, now reconciled

The `CONFIG_STYLE_MISMATCH` this log raised on 2026-07-30 has been resolved by
the repo owner in favour of the ISO contract. `channel.config.json` now carries
`"style_contract": "ISO"` and the 597-character Contract A string, copied
programmatically. The displaced hand-drawn marker string was moved to
`channels/unclaimed/ARCHIVE-wrong-style-string.txt`.

The correction is independently confirmed: the sha256 of the string now in
config is `16bab4b1…0fa675`, byte-identical to the value this log recorded on
2026-07-30 and to `style_string_sha256` in `scenes.json`. The previous run's
judgement that the brand file was authoritative was correct.

**Sibling fields still describe the old look.** `visual_style.ground`,
`linework`, `accent`, `frame_vocabulary` and `motion` in `channel.config.json`
still describe white paper, black marker and a green/gold accent. They were out
of scope for the correction and were left alone. Any prompt builder that reads
them will reintroduce the wrong style. This needs a human decision.

### 11.3 How the style string reached the generator

The pipeline requires the style string to be inserted programmatically and
asserted equal before every generation call. It was built into
`frame_prompts.json` and `clip_prompts.json` from config before any call fired,
and asserted equal to the brand file at 597 characters.

One honest caveat: there is no `HIGGSFIELD_API_KEY` in this environment, so
Higgsfield is reachable only over MCP, and every prompt necessarily passed
through a tool-call argument rather than an HTTP body written by a script. That
is weaker than the pipeline intends. It was mitigated by verification rather
than trust: every generation echoes back the prompt the API actually received,
and **all 80 prompts (40 frames, 40 clips) were diffed byte-for-byte against
the programmatically built files. Zero mismatches.** Every one carries the
597-character ISO string verbatim as its prefix.

### 11.4 Loop C, frames

40 of 40 generated, text-free, via `nano_banana_pro` at 16:9, normalised to
1920x1080.

- **Accent rule holds exactly.** Beat 17 carries 8.86% emerald. The other 39
  frames peak at 0.20%, which is the noise floor. Exactly one beat is green.
- **No lettering.** Checked by OCR (tesseract, psm 11, confidence >= 70).
  Three frames failed on the first pass, all texture-heavy: beat 8 (calendar
  grid), beat 26 (state map), beat 38 (ruled utility bill). Each was
  regenerated with the failed check restated verbatim, per the contract loop.
  Beat 8 needed three attempts, beats 26 and 38 two. **0 of 40 frames carry a
  confident glyph run now.**

### 11.5 Loop D, clips

40 of 40 generated, `kling3_0`, image-to-video from the approved frame, one
action, locked-off, 5 s, silent.

- `mode=std` returned 1280x720, which would have shown a visible quality drop
  against the 1920x1080 still holds. `mode=pro` returns native 1920x1080 and
  was used for all 40.
- Two beats (2 and 7) came back as a preset recommendation ("IN THE DARK")
  instead of a generation. That preset would have overridden the style
  contract, so it was declined and both were generated literally.
- **One real defect, caught and fixed.** Beat 21's clip introduced emerald at
  t=4.9 s on a non-green beat, although its source frame carries none. That
  breaks the accent rule. It was regenerated with the failed check restated and
  now reads 0.000 emerald throughout.
- First frame of each clip matches its approved still, so the cut into the clip
  is seamless. Each beat then holds the clip's **last** frame for the remainder
  of its window, so there is no jump back to the pre-motion state.

### 11.6 Loop F, music

Not regenerated. `bed.wav` (630 s) and `episode-audio-master.wav` (605.00 s)
already exist and are in spec, and the composition is fitted to that exact
audio. Re-measured this run: **-14.6 LUFS integrated, -1.5 dBTP true peak**,
both inside target. Regenerating would have cost credits and shifted the mix
the voice timing is fitted to, so it was verified rather than rebuilt.

### 11.7 Loop H, thumbnails

Three variants, each at 16:9 and 1:1. Object frames generated with no
lettering; type composed in HyperFrames over the top, which is what makes the
four-word cap and the palette enforceable.

| Variant | Text | Words | Emerald |
|---|---|---|---|
| a | They Still Owe You | 4 | yes, promises recoverable money |
| b | Check Your Name | 3 | no |
| c | Nobody Claimed It | 3 | no |

OCR reads back each headline exactly. The warm-tan headline exception recorded
on 2026-07-30 was applied. Thumbnail choice remains a human action.

### 11.8 Loop I, metadata

`metadata.json` was verified, not rewritten. All 10 URLs checked: 8 return 200
directly; `nysenate.gov` and `missingmoney.com` return 403 to scripted requests
but are both confirmed live (the NY statute text was retrieved through the
content path and returns the five-year gift certificate rule the script relies
on; MissingMoney is confirmed operating through NAUPA's own site, which returns
200). **No official link is dead**, so this loop did not halt.
