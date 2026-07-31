# UNCLAIMED · STYLE CONTRACTS

Governs every image and clip. The style strings below are immutable. They are copied character for character into every generation prompt. Never paraphrase, shorten, reorder or improve them.

Default contract is ISO. Use RISO only when explicitly named.

---

# LAYER SPLIT · GENERATED VERSUS COMPOSED

The contracts below define the whole look. They do not all get produced the same way.

| Layer | Produced by | Why |
|---|---|---|
| Objects, materials, light, shadow, grain, halftone | Image model (Higgsfield or Nano Banana Pro) | Cannot be specified exactly. Accept a range, check the result. |
| Motion of the object itself | Video model (Veo via API or Flow, or Higgsfield) | Same reason. One action per clip. |
| Wordmark, episode labels, spoken numerals | **Hyperframes HTML and CSS** | The contract states these as exact values. Tracking 120 to 150 is a CSS property. `#F2EDDF` is a CSS property. An image model approximates both. |
| Accent overlay animation, draw-on reveals, travelling arrows | **Hyperframes GSAP** | Deterministic and repeatable across every episode. |
| Cuts, timing, captions, aspect reframes | **Hyperframes** | Frame-accurate and content-hashable. |

**This split applies in pipeline mode only.** When the Project outputs paste-ready prompts for manual generation in Higgsfield or Flow with no Hyperframes compositing step, text goes into the frame under the typography sections as written, because there is no later layer to put it in. The mode is set in the selection line. Everything below describes pipeline mode.

**The operative rule in pipeline mode: generated frames contain no text.** Every image prompt appends `No text, no numerals, no lettering anywhere in the image.` The type that the beat calls for is recorded separately and composed on top.

This does not change the immutable style strings. They stay exactly as written. It changes only where the typography sections of the contracts are executed.

Two consequences worth holding in mind:

1. **The four-word cap becomes enforceable.** It is a validation rule in the composition rather than a hope about what the model rendered.
2. **The closed palette becomes literal.** Composed elements reference CSS custom properties generated from the config, so no composed element can ever fall outside the table. Only the generated layer needs checking against the palette.

If Hyperframes is unavailable for a run, the fallback is to generate type into the frame under the typography sections as originally written, and to record the fallback. The output will be less exact. Do not make it the default.

---

# CONTRACT A · ISO

## GOAL
Render the supplied scene as a soft matte low-poly isometric illustration that is visually indistinguishable from every other frame produced under this contract.

## STYLE STRING (immutable)
Reproduce verbatim at the head of every generation. Never paraphrase, shorten or reorder.

> Soft matte low-poly isometric 3D illustration, clean thirty degree isometric projection, pale sage green background, objects modelled in warm bone cream and pale putty with soft long diffuse shadows, cornflower periwinkle blue used for hands handles and human elements, one saturated emerald green accent used only to mark money that is recoverable, simple faceless rounded figures at consistent small scale, matte non-reflective surfaces, soft even ambient light with no harsh highlights, generous negative space around the subject, subtle film grain, no photorealism, no gloss, no textures, 16:9

## CLOSED PALETTE

| Role | Hex |
|---|---|
| Background | #D8E0D6 |
| Primary objects | #F2EDDF |
| Secondary objects, recesses | #E0D9C8 |
| Hands, handles, human elements | #8FA8DC |
| Recoverable money | #3AAE5C |
| Money that is gone | #B5B2A8 |
| Type | #F2EDDF or #C9B48A |
| Type, thumbnails only | #1F3A6E |

No colour outside this table appears in any frame.

`#1F3A6E` is the Contract B ink navy, admitted here as a **type only** role and
**only on thumbnails**. It may never be used on an object, a ground or any
element inside an episode frame. Reason: bone cream on pale sage measures
1.15 to 1 and warm tan on pale sage measures 1.50 to 1, so both vanish at feed
size. Navy on pale sage measures 8.24 to 1. Episode body type keeps cream and
tan, because that type is redundant against the spoken narration and is not
being read at thumbnail scale. Amended 2026-07-31.

## ACCENT RULE
Emerald marks money that is recoverable. Warm grey marks money that is gone. Emerald appears on exactly one object per frame. If the frame contains no recoverable money, it contains no emerald.

## COMPOSITION
True thirty degree isometric, no perspective convergence. Locked-off camera. One subject, centred or near-centred. Objects float on plain sage with no floor plane, no room, no horizon unless the scene requires ground. Consistent scale: a figure is always the same height relative to a door, a counter, a cabinet. Text occupies the upper third, subject the lower two thirds, never overlapping.

## SURFACE AND LIGHT
Matte and non-reflective. No specular highlights, no gloss, no rim light. Soft ambient light from above and slightly left. Long soft low-opacity shadow falling down and right, always diffuse. Subtle film grain across the whole frame. Low-poly forms with rounded edges, nothing sharp, nothing detailed.

## TYPOGRAPHY
Brand wordmark UNCLAIMED in high-contrast Didone serif, all capitals, tracking 120 to 150, bone cream. Episode titles and labels in bold condensed sans-serif, all capitals, tight tracking, four words maximum. Numerals only ever appear when the narration states that figure in the same beat.

**Execution:** composed in Hyperframes over the generated frame, using `--object` for the wordmark and `--type-warm` for numerals and labels. The generated frame itself carries no lettering.

## LOOP
For each frame: render, then check every item below. On any failure, regenerate with the failed item restated. Maximum three attempts, then output the closest pass and name the failure.

- Style string present verbatim
- Every colour in the closed palette
- Emerald on exactly one object, or absent
- True isometric with no perspective convergence
- Matte, no gloss, no specular highlight
- Shadow soft, long, down and right
- No lettering present in the generated frame (type is composed separately)
- Figures faceless and at consistent scale

## NEVER
Glossy product render. Corporate clip art isometric. Crypto or fintech illustration. Game asset. Gradients, reflections, neon, or a second accent colour.

## EXIT CONDITION
Frame passes all LOOP checks. Output and stop.

---

# CONTRACT B · RISO

## GOAL
Render the supplied scene as a two colour risograph print that is visually indistinguishable from every other frame produced under this contract.

## STYLE STRING (immutable)

> Risograph print illustration on warm cream uncoated paper stock with visible paper grain and speckle, limited spot colour printing, heavy halftone dot texture throughout, slight ink misregistration with each colour offset a fraction from its outline, deep navy blue as the primary ink for all linework and type, one saturated green accent used only to mark money that is recoverable, bold simplified shapes with thick confident hand-cut linework, flat overprint areas where two inks overlap and darken, mid-century printed pamphlet aesthetic, no gradients, no photorealism, no 3D, 16:9

## CLOSED PALETTE

| Role | Hex |
|---|---|
| Paper stock | #F5F0E3 |
| Primary ink, all linework and type | #1F3A6E |
| Recoverable money | #2E8B57 |
| Secondary fill | #C9A96A |
| Money that is gone | #B5B2A8 |

Overprint where navy crosses green darkens to near black. That is the only fifth value permitted and it must occur naturally at overlaps, never be painted in.

## ACCENT RULE
Green marks money that is recoverable. Warm grey marks money that is gone. Green appears on exactly one object per frame.

## PRINT CHARACTER
This is what makes it read as riso rather than flat vector. All four are mandatory in every frame.

1. Visible paper grain and speckle across the whole surface.
2. Heavy halftone dot texture inside every flat colour area, coarse enough to see.
3. Ink misregistration: each colour sits a fraction off its outline, consistently in the same direction across the frame.
4. Flat overprint darkening wherever two inks overlap.

## COMPOSITION
Head-on and frontal, no perspective. Bold simplified shapes, thick hand-cut linework, high contrast against the paper. One clear subject. Generous paper visible around it. Text in the upper third, never over the subject.

## TYPOGRAPHY
Brand wordmark UNCLAIMED in high-contrast Didone serif, navy, all capitals, wide tracking. Episode titles in bold condensed sans-serif, navy, all capitals, four words maximum. Both print with visible halftone and slight offset like every other element.

**Execution:** composed in Hyperframes over the generated frame using `--ink`, with the halftone and offset reproduced as a CSS filter and a small transform on a duplicated text layer so composed type matches the printed character of the generated layer. The generated frame itself carries no lettering.

## LOOP
Render, then check. Regenerate on failure with the failed item restated. Maximum three attempts.

- Style string present verbatim
- Paper grain and speckle visible
- Halftone dots visible inside every flat area
- Misregistration present and consistent in direction
- Overprint darkening at every ink overlap
- Green on exactly one object, or absent
- No gradients anywhere
- No lettering present in the generated frame (type is composed separately)

## NEVER
Clean flat vector with a paper texture layer over it. Watercolour. Screen printed t-shirt look. Gradients. More than one accent colour. Crisp registration.

## EXIT CONDITION
Frame passes all LOOP checks. Output and stop.

---

# SCENE WRITING RULES

These govern how the VISUAL line in a script is written. They apply to both contracts.

**1. One subject.** Name it first, place it, then describe it. "A single kitchen drawer sits open in isolation against empty pale sage."

**2. Materials by palette role, not colour name.** Write "in warm bone cream", "in pale putty", "a cornflower periwinkle handle". Do not write "beige" or "light blue". The palette words are load-bearing.

**3. State the accent explicitly.** Either the frame ends with `No green anywhere.` or it names the single emerald object and says it is the only green: "in solid emerald green, the only green in the image".

**4. Depict what the narration literally says in that exact beat.** If the narration says cart, the frame contains a cart. If it says sixty days, the frame contains a calendar with the numerals 60. Generic abstract stand-ins (unlabelled containers, apertures, rings, streams of figures) are rejected. This was the single most repeated correction on earlier work.

**5. Numerals only when spoken in that beat.** Rendered "in bold condensed sans-serif in warm tan". Never invent a figure to fill the frame.

**6. Continuity frames are described as returns.** "The same open kitchen drawer from the opening frame at the identical angle, now empty except for one bone cream gift card lying flat in the centre."

**7. Figures are faceless, periwinkle, small and used sparingly.** Usually one, usually to show scale or helplessness against an object. Never a crowd, never expressive.

**8. No motion in the VISUAL line.** No "then", no "as", no camera direction. It is a still frame. Motion is specified separately in the clip prompt.

**9. Emptiness is a feature.** Most frames end with "Empty pale sage all around." The negative space is the channel's visual signature and generators will fill it if you let them.

---

# CLIP PROMPTS

Frames are animated to five second clips. One clip per beat, eleven per episode, plus the thumbnail still.

**The rule that governs every clip prompt: one action, one shot, roughly five seconds.** Multi-beat storyboards with four or five sequential events in a single prompt produce mush and are rejected. If a beat needs two things to happen, it needs two clips or it needs a simpler idea.

**Permitted motion vocabulary:**
- An object depletes, empties, fills or drains
- A single element draws on or is revealed
- One item is lifted, placed, opened or closed
- A shadow lengthens
- A slow drift or a very slow push, no more than a few percent of frame
- A shutter, drawer, lid or door moves once

**Forbidden:** camera orbits, whip pans, cuts inside a clip, morphs, particle effects, text animating in, more than one thing moving, anything that breaks the locked-off isometric.

**Do not ask a video model for composed motion.** Draw-on reveals, the accent landing last, arrows travelling along a money trail and any type animation are Hyperframes GSAP work, not clip prompts. Asking a generative model for them produces drift and is unrepeatable across episodes. The clip carries the object's own single action and nothing else.

**Clip prompt format:**
```
<style string verbatim>
<scene description from the VISUAL line>
MOTION: <one action, present tense, single clause>. Locked-off camera. 5 seconds.
```

---

# THUMBNAIL SPEC

Produced under the same contract as the episode frames, at 16:9, plus a 1:1 companion.

- One object plus one number or one eligibility trigger. Never two.
- Four words maximum, bold condensed sans-serif, all capitals, upper third.
- The object is the episode's anchor object, isolated on the ground colour.
- Emerald appears if and only if the thumbnail promises recoverable money.
- Brand wordmark UNCLAIMED present, small, Didone, bone cream or navy.
- Three variants per episode. A human picks one.
- Produced in two parts: the object frame is generated with no lettering, the text and wordmark are composed in Hyperframes from `compositions/thumbnail.html`. This is what makes the four-word cap and the exact palette enforceable.

**Object bank in use:** unopened envelope, blank-name cheque, suitcase and cancelled flight, hospital bill with one circled charge, house and deposit receipt, settlement notice, old bank account passbook, wall calendar with a highlighted deadline, kitchen drawer, filing box, official letter, storm-damaged house.
