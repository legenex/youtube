# Build log: five style test trailers, Episode 5

Date: 2026-08-03
Branch: `channel/unclaimed`
Scope: style test only, not a production run. Five 25 second trailers for
"The Supreme Court Said Counties Stole Home Equity. Billions Must Go Back."

Everything below is what was actually done, including where the plan in the
brief could not be followed and what was done instead.

---

## 1. Outcome

| Style | Name | Shots | Longest hold | Avg cut | Size |
| --- | --- | --- | --- | --- | --- |
| 1 | Redacted Document | 20 | 2.47s | 1.25s | 3.1 MB |
| 2 | Kinetic Type Over Footage | 17 | 1.90s | 1.47s | 5.2 MB |
| 3 | Annotated Screen | 20 | 1.93s | 1.25s | 3.8 MB |
| 4 | High Speed Cut | 66 | 0.70s | 0.38s | 8.6 MB |
| 5 | Case File | 16 | 2.00s | 1.56s | 5.3 MB |

Shots and holds are measured, not estimated, using the command in the brief:
`ffmpeg -i out/style-N.mp4 -vf "select='gt(scene,0.1)',showinfo" -an -f null -`
via `measure.py`. All five clear the 8 scene change floor and all five sit
inside their per style maximum static hold.

Encode contract verified on every file: 1280x720, 30fps, H.264 High, yuv420p,
CRF 21, AAC 192k at 48 kHz stereo, faststart confirmed by atom order,
integrated loudness exactly -14.0 LUFS, true peak -2.5 dBFS.

---

## 2. Voiceover: one generation, reused five times

| Item | Detail |
| --- | --- |
| Source | ElevenLabs `text_to_speech`, one call only |
| Voice id | `SAz9YHcvj6GT2YYXdXww` |
| Model | `eleven_multilingual_v2` |
| Raw file | `assets/shared/vo-raw.mp3`, 29.91s, 719 KB |
| Working file | `assets/shared/vo.wav`, 24.32s |
| Cost | 1 generation, approximately 440 characters |

**Deviation.** The narration read at 29.91s, but the brief requires a 22 to 26
second runtime. Rather than cut or rewrite a single word, the read was time
compressed with `atempo=1.23`, then high passed at 85 Hz, lightly compressed
and limited. The words are verbatim and complete; only the pace changed. All
five videos run 25.0s except style 4 at 24.87s.

Phrase boundaries were extracted from the finished wav with `silencedetect`
rather than guessed, so cuts land on the facts. Recovered timings:

| Time | Phrase |
| --- | --- |
| 0.00 to 0.80 | In 2015, |
| 1.09 to 5.57 | Geraldine Tyler owed fifteen thousand dollars ... lived in. |
| 6.27 to 7.38 | Hennepin County seized it, |
| 7.71 to 9.81 | sold it for forty thousand, and kept every cent. |
| 10.24 to 10.73 | Not the debt. |
| 11.05 to 11.39 | All of it. |
| 12.14 to 15.11 | In 2023 the Supreme Court ruled that unconstitutional, |
| 15.42 to 16.20 | nine to nothing. |
| 16.67 to 18.90 | Counties across the country are now sitting on surplus |
| 19.15 to 21.07 | that legally belongs to the people they took it from. |
| 21.45 to 22.56 | The money may be unclaimed. |
| 22.90 to 24.03 | It does not have to stay that way. |

---

## 3. Music: one bed, reused five times

| Item | Detail |
| --- | --- |
| File | `assets/shared/music.wav`, 30.9s |
| Source | Synthesised locally with ffmpeg. Cost 0. |
| Recipe | Sine drones at 55, 82.5 and 110 Hz with slow independent tremolo, brown noise air, low passed at 1.6 kHz, slow echo, 3s fades |

**Deviation.** The brief offered one generated bed or one Envato track. Neither
route was available. Higgsfield's audio tool explicitly refuses standalone
music (`sonilo_music` is reserved for its game pipeline and must not be used
for general audio), and the Envato MCP cannot download (see section 5). A
synthesised drone was built instead. It is deliberately plain: low sustained
tone, no melody, no resolution. Mixed at 0.15 gain under the voice.

---

## 4. Higgsfield: exactly on budget

Budget allowed: 12 images and 4 clips total across all five videos.
Used: **12 images and 4 clips.** Nothing regenerated.

**Total spend: 54 credits** (balance 8633.25 before, 8579.25 after).

Images, `nano_banana_pro`, 16:9, 1376x768, in `assets/shared/gen/`:

| File | Subject |
| --- | --- |
| `img-01-condo-empty.png` | Empty condo living room, blind light stripes |
| `img-02-keys-counter.png` | House keys on a bare kitchen counter |
| `img-03-envelope-mat.png` | Official window envelope on a doormat |
| `img-04-condo-exterior.png` | 1970s brick condominium block, winter |
| `img-05-courthouse.png` | County courthouse, stone columns |
| `img-06-county-office.png` | Empty county service office after hours |
| `img-07-desk-folders.png` | Manila folders and paperwork under a lamp |
| `img-08-yard-sign.png` | Blank sign staked in a front lawn |
| `img-09-aerial-suburb.png` | Top down aerial of suburban rooftops |
| `img-10-bedroom-empty.png` | Stripped bare bedroom |
| `img-11-vault-boxes.png` | Wall of safe deposit boxes |
| `img-12-stamp-macro.png` | Rubber stamp and ink pad on documents |

Clips, `kling3_0_turbo`, 720p, 5.04s each:

| File | Subject |
| --- | --- |
| `clip-1-courthouse-push.mp4` | Slow push in on a courthouse facade |
| `clip-2-condo-drift.mp4` | Lateral drift across an empty condo |
| `clip-3-aerial-suburb.mp4` | Aerial drift over rooftops |
| `clip-4-desk-papers.mp4` | Dolly across scattered documents |

Reuse across styles, which is the point of the test: the same courthouse push
appears in styles 2 and 4 cut differently; the same empty condo appears in
styles 2, 4 and pinned to the board in style 5. Distinct Higgsfield assets
referenced per style: style 1 zero, style 2 fourteen, style 3 zero, style 4
sixteen, style 5 three.

One clip submission was rejected with a preset recommendation ("IN THE DARK")
and was resubmitted once with brighter wording. That resubmission is counted in
the 4.

---

## 5. Envato: searched, not used

**Deviation, and the largest one.** The brief expected Envato stock to be the
primary footage source. The Envato MCP available in this session exposes
`search_*` tools only. There is no download tool, and the only reachable media
are watermarked previews at
`video-previews.elements.envatousercontent.com/.../watermarked_preview.mp4`,
confirmed by fetching an item page directly. Cover images are reachable but are
single JPEG stills.

Using watermarked previews would put a diagonal Envato watermark across every
frame of a look test, which defeats the purpose. So:

- **Envato clips used: 0.**
- **Envato AI generations used: 0 of the 20 permitted.**
- Searches were run to confirm the limitation (`courthouse exterior`, stock
  video, horizontal, 1080p) and the result was catalogue metadata plus preview
  links only.

The gap was covered the way the brief's own priority order suggests: documents
and type cost nothing, so reach for them first, and use the sanctioned
Higgsfield budget for the physical material that cannot be built. Styles 1 and
3 therefore use no footage at all and cost nothing, which turned out to be a
useful finding in its own right.

If a licensed Envato download path is wired up later, styles 2 and 4 accept
stock substitution directly: their footage only has to read as a dark graded
texture, and `build.py` takes any file path.

---

## 6. Documents: the highest value assets, and free

Built as hand written HTML, screenshotted with headless Chrome at 2x. Cost 0.
Sources in `assets/shared/html/`, output in `assets/shared/docs/`.

| File | What it is |
| --- | --- |
| `doc-opinion.png` | 2560x3800. **Facsimile** of a Supreme Court slip opinion. |
| `doc-surplus.png` | 2560x3000. **Facsimile** of a county surplus funds listing. |
| `doc-notice.png` | 2560x3240. **Facsimile** of a notice of forfeiture and sale. |
| `br-surplus.png` | 2560x1440. **Facsimile** county website, unclaimed surplus listing, in browser chrome. |
| `br-search-0/1/2.png` | 2560x1440. **Facsimile** county surplus search page, empty, one character typed, filled. |
| `tex-paper.png`, `tex-manila.png` | Procedural paper and manila textures, CSS plus SVG turbulence. |

Every one of these is a **facsimile**. They imitate the structure and typography
of a real record. None reproduces a real document. This is stated on each page
in a footnote and again in the page footer of `index.html`.

To place highlights exactly rather than by eye, key lines were tagged with
`data-hl` and the browser was asked to report `getBoundingClientRect` for each,
read back through `--dump-dom` (`tag-docs.py`). Style 1's lit lines and style
3's annotations are positioned from those measured rectangles.

Overlays in `assets/shared/overlay/`: seven transparent PNGs, hand drawn feel
emerald circle, wide circle, underline, arrow, up arrow, box, and an oversized
cursor. Built once, reused everywhere. Cost 0.

Evidence board in `assets/shared/board/`: nine states of accumulation at
3072x1728, composed in `board.html` from the three document facsimiles and three
generated stills. Cost 0.

---

## 7. Fact discipline

No figure, date or claim appears beyond the narration. The permitted set is
15,000 / 40,000 / 25,000 / 9 to 0 / 2015 / 2023, and all four required figures
appear on screen in all five videos.

Specific decisions:

- **Redacted rather than invented.** Every field a real record would carry but
  the narration does not state (parcel numbers, owner name, address, docket
  number, argument date, form numbers, other parcels' figures) is drawn as a
  solid black redaction bar. This satisfies fact discipline and doubles as
  style 1's signature device, which is why the surplus listing has nine
  redacted rows and one real one.
- **No count up through invented numbers.** The brief asks for numbers that
  count up then lock in style 2. A literal counter would display figures such
  as `$6,480` that are not in the script. Implemented instead as a digit
  reveal: `$__,___` resolves left to right through redaction blocks to
  `$15,000`, then locks. No intermediate figure is ever shown. Used in styles 1
  and 2.
- **Figure captions.** An early cut labelled all three figures "unclaimed
  surplus", which is wrong: 15,000 is the debt and 40,000 is the sale price.
  Corrected so each figure carries its own caption, "tax debt owed", "sold
  for", "surplus kept".
- **No further research.** Nothing was looked up about the case.

---

## 8. Content safety: no identifiable person, and Geraldine Tyler is never portrayed

- Geraldine Tyler is never depicted, impersonated or represented. The visual
  vocabulary is empty rooms, keys, envelopes, notices and records.
- Every Higgsfield prompt specified no people.
- **`img-11-vault-boxes.png` came back with a gloved hand holding cash.** It is
  cropped to `(0, 0, 900, 500)` in `build.py`, written to `work/img-vault.png`,
  so the hand is removed entirely before the still is ever used.
- **`img-05-courthouse.png` came back with "FRANKLIN COUNTY COURTHOUSE AD 1891"
  carved on the frieze.** That invents both a county that is not Hennepin and a
  date not in the narration, and could imply a specific county did this. It is
  cropped to the colonnade, `(0, 250, 1376, 518)`, written to
  `work/img-court.png`, so the building is anonymous. The evidence board was
  repointed at the cropped file and all nine states were re-rendered.
- The generated clips were checked and carry no signage or text.

---

## 9. Assembly

One script, `build.py`, builds all five from the shared pool. It renders each
shot to an intermediate, concatenates, then muxes audio. No browser compositor
is used for video; that path is closed. FFmpeg 8.1.1.

**Deviation.** This ffmpeg is built without `libfreetype`, so there is no
`drawtext` filter. Every piece of type is instead rendered as a transparent PNG
by headless Chrome from `type.html` and composited with `overlay`. This costs
nothing, is cached by a hash of its parameters, and gives better control of
condensed faces and letter spacing than `drawtext` would have. 60 type cards
were generated.

Two ffmpeg limits shaped the implementation:

- `crop` cannot animate its width, so style 3's draw on reveal is a per pixel
  alpha mask (`geq`) rather than a moving crop.
- Composites are built at 1728x972 and only then driven through `zoompan` to
  1280x720, so that style 1's lit line and style 3's annotations stay
  registered to the page while it drifts, and so zoom stays sharp.

Loudness needed two passes. A single `loudnorm` pass landed at -15.7 LUFS on
all five, so `normalise_audio()` measures, then applies with the measured
values and `-c:v copy`, landing exactly -14.0.

---

## 10. Rhythm work: what failed and was re-cut

The brief requires measuring rather than estimating, and re-cutting anything
that fails. Three videos failed a first measurement and were re-cut.

**Style 1 failed twice.** First measurement: 8 changes, longest static hold
7.83s. The cause was real, not a detector artefact: consecutive shots were all
dim documents on near black, so neither the detector nor a viewer could see the
cuts. Two re-cuts:

1. Forced strict document alternation, so no two adjacent shots share a
   document, and added wide/mid framing contrast. Result: 14 changes, 4.43s.
2. Implemented the brief's own "close on the lit line" framing so emerald fills
   the frame on every third shot, varied the dim level per shot between 0.34
   and 0.80 so adjacent pages differ in tonal mass, and split the sign off into
   three beats with a document ghost behind two of them. Result: **19 changes,
   2.47s longest hold.** Passes.

**Style 3 failed once.** Longest hold 3.00s, caused by two consecutive opinion
document shots. A break shot back to the county listing was inserted at 14.45s.
Result: **19 changes, 1.93s.** Passes.

**Style 4 failed once.** Longest hold 1.23s against a 1.0s maximum, caused by
the final shot, and a second 1.07s hold caused by two adjacent shots from the
same document. The closing line was split across two shots and the second
document shot was changed to a different document. Result: **65 changes, 0.70s
longest hold.** Passes.

Styles 2 and 5 passed first time at 1.90s and 2.00s.

---

## 11. Style notes and no em dashes

`&mdash;` entities in three facsimile pages rendered em dashes on screen. They
were replaced with middots and the affected screenshots, board states and four
videos were rebuilt. No em dash or double hyphen appears in any committed prose
or on screen. The double hyphens remaining in `index.html` are CSS custom
property syntax, which is code, not text.

---

## 12. File inventory

```
style-tests/
  build.py          one build script for all five
  measure.py        rhythm measurement
  gen-index.py      comparison page generator
  tag-docs.py       document rect tagging
  index.html        self contained comparison page
  build-log.md      this file
  out/              style-1.mp4 to style-5.mp4
  guides/           style-1.md to style-5.md
  assets/shared/
    vo-raw.mp3 vo.wav music.wav
    html/           document, browser, board, type, texture, annotation sources
    docs/           screenshotted facsimiles
    gen/            12 Higgsfield images, 4 Higgsfield clips
    overlay/        7 annotation PNGs
    board/          9 evidence board states
  work/             intermediates, type card cache, normalised clips
```

`assets/s1` to `assets/s5` were created as the brief specified but are empty:
no style needed a private asset. Everything is shared, which is the result the
test was meant to surface.

---

## 13. What this test actually shows

Styles 1 and 3 cost nothing per shot and are the fastest to produce, because a
document facsimile is free and reusable across a whole series. Style 4 looks the
most expensive and is, but only in editing hours: at 159 shots per minute a 10
minute episode needs roughly 1,600 beats, which means every asset must be cut 8
to 12 ways. Style 5 is the most reusable after its first build. Style 2 is the
most tolerant of substituted footage, since the footage is only a texture.

The rhythm failures are the useful finding. A dark, low contrast style can hold
a viewer's eye for four seconds without a single perceptible change even when
the edit list says there were four cuts. Alternating the document is not
enough; the tonal mass has to change too.
