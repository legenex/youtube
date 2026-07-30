# UNCLAIMED · CHANNEL BIBLE

Governs Job C (script and scene build). Everything editorial lives here.

---

## 1. Positioning

UNCLAIMED reveals money, benefits, compensation, refunds, settlements and financial rights that ordinary people do not know exist.

Every episode opens on the same possibility: there may be money connected to your name, your situation, or something that happened to you.

**Central question:** is money being held, withheld, overlooked or left unclaimed?

**Not** a personal injury channel. Not a get-rich channel. Coverage spans unclaimed property, insurance benefits, class action settlements, employment compensation, consumer refunds, government programmes, tax credits, banking errors, travel compensation, property deposits, estates and inheritance, data breach settlements, product recalls and medical billing refunds.

**Separation from every other money channel.** Finance channels cover earning, investing, saving and side hustles. UNCLAIMED covers money that may already be attached to the viewer. That is a different curiosity gap and it lands on existing search behaviour rather than creating it.

---

## 2. Editorial boundaries

**Does:** explain what the money is, why it exists, who may qualify, where it is held, what the process looks like, what proof is usually needed, what mistakes prevent recovery, and where official information can be checked.

**Does not:** guarantee eligibility, guarantee payment, promise a settlement value, imply every viewer has money waiting, use manufactured urgency, present general information as personalised advice, or turn an episode into a lead form.

**The funnel rule.** The educational answer is complete on its own. A viewer who never clicks anything still got the whole thing. Commercial pathways live in the description block, visibly separate. This rule protects the channel's entire value and is not negotiable for a single episode.

---

## 3. Audience

US adults 25 to 65. Homeowners, employees, parents, consumers, travellers, accident victims, former tenants, people managing estates, people dealing with insurance or medical bills.

Secondary: consumer-rights viewers, older viewers, family members helping relatives, people who distrust complex institutions, people under sudden financial pressure.

Write for someone with no background in law, tax or insurance who is capable and busy. Never condescend, never over-explain, never assume ignorance of ordinary life.

---

## 4. Locked format

This is the format actually in production. It supersedes any longer-form spec in earlier planning documents.

| Parameter | Value |
|---|---|
| Runtime | 2:50 |
| Beats | 11 |
| Beat length | 15 seconds each, final beat 20 seconds |
| Pace | 130 wpm |
| Words per beat | 30 to 34, final beat 42 to 46 |
| Person | Second person |
| Aspect | 16:9 primary, 1:1 companion set for Shorts and social |
| Green beat | Exactly one beat carries the emerald accent |
| Sign-off | Verbatim, always the last two sentences |

**Timecodes are fixed:** 00:00, 00:15, 00:30, 00:45, 01:00, 01:15, 01:30, 01:45, 02:00, 02:15, 02:30.

**Header line, always present above the AI production script:**
`2:50 · 11 beats at 15s · 130 wpm · green at [TT:TT]`

---

## 5. Beat architecture

The 11 beats map onto seven editorial functions. The mapping flexes by one beat either way depending on the topic, but the sequence never reorders.

| Beats | Function | What it does |
|---|---|---|
| 1 | The overlooked money | State the possibility plainly, in the viewer's own house or life. Concrete object, not abstraction. |
| 2 to 3 | Why the money exists | The programme, obligation, settlement, policy or legal mechanism. Name it. |
| 4 to 5 | How it becomes unclaimed | The ordinary human sequence that loses it. No blame. |
| 6 | The number | One figure that makes the scale real. Usually the green beat. |
| 7 to 8 | The turn | The rule, right or exception almost nobody knows. This is why the episode exists. |
| 9 to 10 | How to verify it | Official database, publication, phone line, document. Named on screen, never in the description alone. |
| 11 | What to prepare, then sign-off | One practical instruction, full pause, then the verbatim sign-off. Runs 20 seconds. |

**The green beat.** Emerald marks money that is recoverable. It appears in exactly one beat per episode. Place it where recoverable money first becomes a concrete quantity: usually beat 6 (the number) or beat 1 (when the cold open is the money itself, as in Episode 2). Every other beat's visual line ends with `No green anywhere.`

**Object continuity.** One recurring object anchors the episode. It appears in beat 1, returns mid-episode changed, and returns in beat 11 resolved. Episode 1 uses the kitchen drawer: open and cluttered, then buried and crushed, then empty but for one card. Write the return frames as "the same [object] from the opening frame at the identical angle" so the generator holds continuity.

---

## 6. Script file structure

Every episode is one file with four sections in this order.

### Section 1 · `Script`
Timestamped narration only. No direction, no visuals. This is what gets read, checked and quoted. Format:

```
[00:00] Narration sentence. Narration sentence. Narration sentence.
[00:15] ...
```

### Section 2 · `AI PRODUCTION SCRIPT`
Title line, then the header line, then one block per beat. Format:

```
[TT:TT] · GREEN   (the "· GREEN" marker appears on exactly one beat)
VOICE <direction>. <Emphasis or pause instruction>.
NARRATION <the narration, identical to Section 1>
VISUAL [ISO] <scene description ending in "No green anywhere." unless this is the green beat>
```

VOICE direction is one or two short sentences. It names delivery register and one specific emphasis or pause. Examples in use: `Flat and certain. Pause after "right now".` / `Land hard on "revenue".` / `Let the number sit. Full beat before "counted as profit".` / `This is the turn. Clear and deliberate.`

VISUAL is written per file 02's scene-writing rules. It is a static scene description only. It never describes motion, camera moves or sequences of events.

### Section 3 · `SOURCES`
One row per factual claim:

```
[TT:TT] | <claim as stated in narration> | <exact figure> | <source URL> | <tier> | <date checked> | <scope>
```

Tier is OFFICIAL, PRIMARY, SECONDARY or CONTESTED. Any SECONDARY or CONTESTED row must be justified in a line beneath it or the claim is cut.

### Section 4 · `METADATA`
Title (three variants, pick first), description block, disclaimer block, tags, playlist, thumbnail text options, Shorts cut points.

---

## 7. Writing rules

**Sentence construction.** Short declaratives. Average sentence length under 14 words. One idea per sentence. Fragments are permitted where they land ("Not a loan. A grant."). Never two subordinate clauses in one sentence.

**Numbers.** Spelled out in narration ("twenty one billion dollars", "sixty days") because the voice model reads them better. Written as numerals in the VISUAL line only, and only when the narration states that figure in the same beat.

**Naming things.** When an institution has a name for something, use it and say it is their name. "Inside the company that sold it, your leftover has a name. It is called breakage." That move is the channel's signature and should appear in most episodes.

**The turn.** Every episode has one sentence that reframes the whole thing. Set it up with "Here is the part almost nobody knows" or an equivalent, then state it flatly. Do not oversell it.

**Verification beats.** Name the resource out loud and slowly. Site names are said as words ("MissingMoney dot com"), not spelled. Always pair the resource with the one thing people get wrong when using it (old addresses, maiden names, misspellings, denial codes).

**Forbidden constructions.** Rhetorical questions. "Here's the thing." "But here's where it gets interesting." Rule of three lists used for rhythm rather than content. "Experts say." "Studies show." Any adjective doing emotional work that the fact does not earn.

**Contractions.** Sparingly. The narrator says "It is" and "do not" more often than "it's" and "don't". This is deliberate and carries the register.

---

## 8. Metadata standard

**Titles.** Question or plain-statement form. No clickbait punctuation, no all-caps, no brackets. Under 60 characters where possible. The pattern in use: `What Happens to Gift Card Balances Nobody Spends`, `Disaster Relief Money That Goes Unclaimed Every Year`.

**Description block.** Fixed structure, in this order:
1. Two-sentence plain summary.
2. `Official resources mentioned in this video:` then each named resource with its live URL, one per line.
3. `Sources:` then every URL from the SOURCES section.
4. Disclaimer block, verbatim.
5. Chapter timestamps.
6. Any commercial pathway, clearly under its own heading, last.

**Disclaimer block, verbatim:**
```
This video is general information about US programmes, rules and databases. It is not legal, tax, insurance or financial advice, and it does not create any professional relationship. Rules and deadlines vary by state and change over time. Always verify your own situation directly with the official source or administrator named above, or with a qualified professional. We do not charge for information about how to claim money, and neither do the official databases mentioned here.
```

**Thumbnail text.** Four words maximum. Options in rotation: `They Still Owe You` / `Check Your Name` / `You May Qualify` / `Refund Never Sent` / `Where It Went` / `Before It Expires` / `Nobody Claimed It`.

**Playlists.** Forgotten Money · Refunds · Settlements · Insurance · Work and Government · Property and Estates.

**Shorts.** Three per episode, cut from: the number beat, the turn, and the verification beat. Vertical reframe uses the 1:1 companion frames.

---

## 9. Compliance and monetisation discipline

**Sensitive-topic handling.** Episodes touching death, disaster, medical debt or job loss stay restrained. No dramatisation of loss. No imagery of injury or damage beyond the neutral object level (a storm-damaged roof is fine, a person in distress is not). The figures in these episodes get the strictest sourcing.

**State-level variation.** Where a rule differs by state, the narration says so and gives the mechanism that determines which rule applies (in the gift card episode: state of incorporation, not state of residence). Never state a rule as national when it is not.

**Monetisation layers, in priority order:**
1. AdSense. Planning band $10 to $22 RPM, higher on insurance, tax, banking and legal compensation topics.
2. Affiliate. Identity and credit monitoring, tax preparation, estate and will services, consumer document services, flight compensation, subscription cancellation, insurance comparison, data removal.
3. Lead generation. The Legenex connection: personal injury, workers compensation, mass tort screening, insurance enquiries, consumer legal enquiries, firm matching. Description block only.
4. Digital products. Unclaimed money search checklist, settlement verification checklist, estate document organiser, insurance document checklist, consumer refund tracker.
5. Newsletter, The Unclaimed Report. Weekly: new settlements, claim deadlines, refund programmes, recalls, government benefits, useful official databases.

**The rule that governs all five.** None of them appears inside the narration, ever.
