#!/usr/bin/env python3
"""Episode 1 builder: emits episode.md and scenes.json from the beat table,
then self-checks every rule in the brief. Beats are authored here so the
checks and the output can never drift apart."""
import json, re, os, sys

ROOT = "/workspaces/youtube/channels/unclaimed/episodes/episode-01"
STYLE = open("/tmp/iso_style.txt").read()
assert len(STYLE) == 597, f"style string is {len(STYLE)} chars, expected 597"

GREEN_BEAT = 17

# (voice, narration, visual, motion_verb, type_layer)
BEATS = [
 ("Flat and certain. Pause after \"right now\".",
  "There is a gift card in your house right now with money still on it. Not the whole balance. Just the awkward part you never went back for. You know the one.",
  "A single kitchen drawer sits open in isolation against empty pale sage, no room or cabinet around it, its front panel in bone cream with a cornflower periwinkle handle. Inside lie three flat gift cards in pale putty, loose and untidy among a set of keys and a pen. No green anywhere.",
  "The drawer slides open once.", "UNCLAIMED"),

 ("Even and unhurried. Slight weight on \"not spent it\".",
  "It sits in a kitchen drawer, or a coat pocket, or the back of a wallet. You have seen it more than once. You have not spent it. That is normal.",
  "A single bone cream coat hangs alone against empty pale sage, one pale putty gift card protruding from its lower pocket. A bone cream wallet lies open on the ground beneath it with a second pale putty card inside. No green anywhere.",
  "The card in the pocket settles downward.", None),

 ("Dry. Land on \"throw away\".",
  "The balance is rarely round. It is four dollars and change, or eleven, or seventeen. Too small to plan a trip around. Too large to throw away. So it waits in the drawer.",
  "A single gift card lies flat and alone at the centre of the frame in warm bone cream, one corner slightly bent upward. A small bone cream price tag rests beside it, blank and unmarked. Empty pale sage all around. No green anywhere.",
  "The bent corner lifts slightly.", None),

 ("Cold on \"It is income\".",
  "Inside the company that sold it, your leftover has a name. It is called breakage. And breakage is not a loss. It is income. That is the accounting term they use.",
  "A single bone cream office building stands alone at the centre of the frame in isometric projection, low and wide with a flat roof. One pale putty gift card lies flat on the ground in front of its entrance, oversized against the building. Empty pale sage all around. No green anywhere.",
  "A long shadow lengthens from the building.", "BREAKAGE"),

 ("Explanatory. Slow on \"revenue\".",
  "When you buy a fifty dollar card, the retailer cannot count that fifty as revenue yet. You have not received anything yet, and neither have they. The transaction is not yet complete.",
  "A single gift card lies flat at the centre of the frame in warm bone cream with a small periwinkle ribbon bow on its upper left corner. The numerals 50 are printed crisply on the card face in bold condensed sans-serif in warm tan. Empty pale sage all around. No green anywhere.",
  "The ribbon bow is placed onto the card.", "50"),

 ("Measured. Beat before \"That is the rule\".",
  "It sits on their books as a promise they owe you in goods. Not money in the bank. A liability, recorded and carried, until you walk in and use it. That is the rule.",
  "A bone cream ledger book lies open flat at the centre of the frame with two ruled columns of pale putty entry bars. A single gift card rests on the left-hand page. Empty pale sage all around. No green anywhere.",
  "The ledger page turns once.", None),

 ("Flat and factual. Emphasis on \"booked\".",
  "They know how this ends. Across millions of cards, a predictable share is never fully spent. That share can be estimated, and once estimated it can be booked. The pattern holds.",
  "A wide grid of forty identical pale putty gift cards lies flat in isometric projection filling the frame, arranged in even rows. Empty pale sage at the edges. No green anywhere.",
  "A single card in the grid is lifted away.", None),

 ("Quiet. Let \"over years\" sit.",
  "The money does not turn into income all at once. It is recognized gradually, in proportion to the cards that do get redeemed. Quietly, over years. That is how the books absorb it.",
  "A bone cream wall calendar stands upright and alone at the centre of the frame, its page a grid of pale putty squares. A short stack of pale putty gift cards rests flat against its base. Empty pale sage all around. No green anywhere.",
  "The calendar page turns once.", None),

 ("Plain. Full stop after each sentence.",
  "By the time the balance is counted as earned, nobody has told you. There is no letter. There is no notice. The card in your drawer looks exactly the same. Nothing changes on it.",
  "A single pale putty gift card lies flat and alone at the exact centre of the frame, plain and unmarked on both visible edges. A wide expanse of empty pale sage surrounds it on every side. No green anywhere.",
  "A soft shadow lengthens beneath the card.", None),

 ("Conversational. Beat before \"You do not\".",
  "You spend thirty seven of it. You mean to go back for the rest. You do not. That is the whole mechanism. There is nothing more complicated underneath it. It is ordinary.",
  "A single gift card lies flat at the centre of the frame in warm bone cream, and beside it a bone cream shop receipt lies unrolled and flat, ruled with fine pale putty lines. Empty pale sage all around. No green anywhere.",
  "The receipt unrolls a little further.", "37"),

 ("Wry. Land on \"later\".",
  "The card goes into the drawer. Not thrown away. Just put somewhere reasonable, next to the batteries and the spare keys. You will deal with it later. You do not deal with it.",
  "A bone cream kitchen drawer sits half open at a three quarter angle against empty pale sage, its cornflower periwinkle handle catching the light. Inside lie two pale putty batteries, a ring of bone cream keys and one pale putty gift card. No green anywhere.",
  "The drawer closes partway.", None),

 ("Slower. Full beat before \"Then years\".",
  "The card moves to the back of the drawer and stays there. Under a receipt, and under everything that arrived after it. Months pass. Then years. You stop seeing it at all.",
  "The same open kitchen drawer from the opening frame at the identical angle. A single gift card in pale putty lies at the very back, partly beneath a folded bone cream receipt, its corner bent. No green anywhere.",
  "The folded receipt is placed over the card.", None),

 ("Clear and procedural. Emphasis on \"five years\".",
  "Federal law does protect the balance for a while. Under the Credit Card Act, the funds cannot expire for at least five years. That runs from the date they were loaded.",
  "A bone cream wall calendar stands upright and alone at the centre of the frame, its page a grid of pale putty squares. The numerals 5 are printed large across the page in bold condensed sans-serif in warm tan. Empty pale sage all around. No green anywhere.",
  "The calendar page turns once.", "5 YEARS"),

 ("Brisk. Flat on \"federal floor\".",
  "Fees are limited too. An inactivity fee cannot be charged unless the card has gone unused for a full twelve months. After that, one fee per calendar month. That is the federal floor.",
  "A single pale putty gift card lies flat at the centre of the frame beside a bone cream wall calendar standing upright, its page a grid of pale putty squares. The numerals 12 are printed across the calendar page in bold condensed sans-serif in warm tan. Empty pale sage all around. No green anywhere.",
  "The calendar page turns once.", "12 MONTHS"),

 ("This is a hinge. Clear and deliberate.",
  "What that law does not do is give the balance back to you. It stops the money vanishing on a schedule. It says nothing about who ends up holding it. That is decided elsewhere.",
  "A single bone cream official document lies flat at the centre of the frame, its printed lines rendered as fine pale putty bars beneath a blank header block. One pale putty gift card rests on its lower corner. Empty pale sage all around. No green anywhere.",
  "The document is placed down flat.", None),

 ("Quiet. Let the last sentence land.",
  "So the balance sits. Protected from expiry, protected from fees, and still completely unspent. The law kept it alive. It did not send it home. That distinction matters more than it sounds.",
  "A single pale putty gift card lies flat and alone at the centre of the frame inside a shallow bone cream tray. Empty pale sage all around. No green anywhere.",
  "A shadow lengthens across the tray.", None),

 ("Let the number sit. Full beat before \"still enormous\".",
  "Americans are holding an estimated twenty seven billion dollars in unused gift cards and store credit. That is a survey estimate, not a government figure. It is still enormous. The scale is the point.",
  "A tall neat stack of banded money bundles stands alone at the centre of the frame in solid emerald green, the only green in the image. A single bone cream gift card lies flat at its base for scale. Above, the numerals 27,000,000,000 in bold condensed sans-serif in warm tan.",
  "The stack of bundles fills upward.", "27,000,000,000"),

 ("Precise. Land on \"single year\".",
  "One company shows the shape of it. Starbucks reported two hundred and twenty two million dollars of breakage in a single year. That is one chain, and it sits in their annual filing.",
  "A tall neat stack of banded money bundles stands alone at the centre of the frame in warm grey. A small bone cream takeaway coffee cup stands beside it at the base for scale. Above, the numerals 222,000,000 in bold condensed sans-serif in warm tan. No green anywhere.",
  "The stack of bundles fills upward.", "222,000,000"),

 ("Flat. No emphasis on \"never drank\".",
  "That figure is not a rounding error hidden in a footnote. It is reported revenue, counted in the same statements as coffee sold and stores opened. Customers paid for coffee they never drank.",
  "A single bone cream takeaway coffee cup stands alone and empty at the centre of the frame, its lid removed and resting beside it. A bone cream ledger book lies open flat behind it. Empty pale sage all around. No green anywhere.",
  "The cup lid is lifted away.", None),

 ("Steady. Land hard on \"expects\".",
  "Multiply that across every retailer that sells a card. The balance you forgot is not an accident in the system. It is a line item the system expects. It is planned for in advance.",
  "A wide grid of forty identical pale putty gift cards lies flat in isometric projection filling the frame, arranged in even rows, one card in each row tilted slightly out of line. Empty pale sage at the edges. No green anywhere.",
  "One tilted card settles back into line.", None),

 ("This is the turn. Clear and deliberate.",
  "Here is the part almost nobody knows. In some states, that leftover balance is not the company's to keep. It has to be handed to the state instead. And held for you.",
  "A bone cream government building with a columned front stands alone at the centre of the frame, a single closed filing drawer visible in its base. Empty pale sage all around. No green anywhere.",
  "The filing drawer opens once.", None),

 ("Naming register. Slow on \"unclaimed property law\".",
  "The mechanism is called unclaimed property law. Every state has one. It covers forgotten bank accounts, uncashed paychecks, and in some states, the money left on a gift card. That is their term.",
  "A single bone cream filing box sits alone at the centre of the frame with its lid removed, holding a row of upright pale putty folders. Empty pale sage all around. No green anywhere.",
  "One folder is lifted from the box.", "UNCLAIMED PROPERTY"),

 ("Naming register. Slow on \"escheat\".",
  "The transfer itself has a name. It is called escheat. The company reports the balance, and the state takes custody of it, and holds it for the owner. The claim stays open.",
  "A single bone cream strongbox stands closed and alone at the centre of the frame, a cornflower periwinkle handle on its lid. One pale putty gift card lies flat beside it. Empty pale sage all around. No green anywhere.",
  "The strongbox lid closes once.", "ESCHEAT"),

 ("Factual. Emphasis on \"five years\".",
  "New York is one of them. There, an unredeemed gift certificate unclaimed for five years is treated as abandoned property. It is then paid to the state comptroller. That is written into the statute.",
  "A bone cream government building with a columned front stands alone at the centre of the frame, one open filing drawer in its base holding a single pale putty gift card upright. Empty pale sage all around. No green anywhere.",
  "The gift card is placed into the drawer.", None),

 ("Flat on \"by design\".",
  "California goes the other way. State law exempts most gift certificates from unclaimed property entirely. The balance is not handed over. It stays with the company that sold it. Legally, and by design.",
  "A single bone cream office building stands alone at the centre of the frame in isometric projection, low and wide. One pale putty gift card lies flat on its roof. Empty pale sage all around. No green anywhere.",
  "A shadow lengthens from the building.", None),

 ("Even. No emphasis anywhere.",
  "States do not agree on this. Some require the balance to be reported and handed over. Others exempt gift cards from unclaimed property entirely. There is no single national rule. It depends entirely.",
  "A flat map of the United States lies in isometric projection filling the frame. Some states are raised slightly above the surface as bone cream blocks, the rest recessed below as pale putty depressions. No labels. No green anywhere.",
  "The raised states rise a little further.", None),

 ("Deliberate. Emphasis on \"not where you live\".",
  "The rule that decides is not where you live. Unclaimed property goes first to the state of the owner's last known address. That address comes from the company's own records. Not yours.",
  "A single bone cream envelope lies flat at the centre of the frame, addressed side up with a blank address block. A small faceless periwinkle figure stands beside it, dwarfed by its scale. Empty pale sage all around. No green anywhere.",
  "The envelope is placed down flat.", None),

 ("Land on \"state of incorporation\".",
  "A shop does not ask your name when you buy a gift card. With no address on record, the balance falls to the second rule. That is the company's state of incorporation.",
  "A single bone cream office building stands alone at the centre of the frame in isometric projection with a small periwinkle door. A bone cream certificate lies flat on the ground in front of it, blank and unmarked. Empty pale sage all around. No green anywhere.",
  "The small periwinkle door closes once.", None),

 ("Warmer. Lift on \"costs nothing\".",
  "Where a state does hold it, that money is searchable by name. It sits in a public database, waiting for someone to ask for it. Searching costs nothing. The state wants it claimed.",
  "A single desktop monitor stands alone on a plain surface, casing in bone cream, screen a flat pale putty panel with one empty rectangular search field and a small periwinkle button beside it. A bone cream keyboard in front with a periwinkle hand resting on it. No green anywhere.",
  "The periwinkle hand presses the button once.", None),

 ("Clear and slow on the site name.",
  "Go to MissingMoney dot com. It is run by the state unclaimed property administrators themselves. It is free, and most states participate in it. That is the place to start looking.",
  "A single desktop monitor stands alone on a plain surface, casing in bone cream, screen a flat pale putty panel showing one empty rectangular search field. A small periwinkle cursor arrow rests at the right of the field. Empty pale sage all around. No green anywhere.",
  "The cursor arrow drifts to the search field.", "MISSINGMONEY.COM"),

 ("Clear and slow on the site name.",
  "Not every state is in that one database. The national association of unclaimed property administrators keeps a directory at unclaimed dot org. It links to every state program directly. Use both.",
  "A single bone cream directory board stands upright and alone at the centre of the frame, its face a grid of blank pale putty panels arranged in even rows. Empty pale sage all around. No green anywhere.",
  "One panel on the board is revealed.", "UNCLAIMED.ORG"),

 ("Instructional. Emphasis on \"every state\".",
  "Then check the treasury or comptroller site for every state you have lived in. Each one runs its own search. A balance held in one state will not appear in another.",
  "Three bone cream government buildings with columned fronts stand in a row across the frame in isometric projection, each with one closed filing drawer in its base. Empty pale sage all around. No green anywhere.",
  "One filing drawer opens once.", None),

 ("Instructional, brisk. Emphasis on \"had\".",
  "Search every version of your name, and every old address. Records follow the address the company had, not the one you have now. Misspellings and maiden names count too. So do middle initials.",
  "A single mailbox stands alone at the centre of the frame in bone cream with a periwinkle flag, one envelope wedged half in and half out of the slot. Empty pale sage all around. No green anywhere.",
  "The mailbox flag is lowered once.", None),

 ("Practical. Land on \"Check again\".",
  "The most common mistake is searching once, with one spelling, and stopping. Property is added to these databases constantly. A search that finds nothing today may find something next year. Check again.",
  "A bone cream wall calendar stands upright at the centre of the frame beside a single desktop monitor in bone cream with a flat pale putty screen. The calendar page is a grid of pale putty squares. Empty pale sage all around. No green anywhere.",
  "The calendar page turns once.", None),

 ("Practical. Flat on \"never ask\".",
  "Then take the card back to the shop. Fourteen states require a retailer to pay out a small remaining balance in cash if you ask for it. Most people never ask.",
  "A bone cream shop counter stands alone at the centre of the frame in isometric projection. One pale putty gift card lies flat on its surface, and a small faceless periwinkle figure stands in front of it. Empty pale sage all around. No green anywhere.",
  "The gift card is placed onto the counter.", "14 STATES"),

 ("Brisk through the figures.",
  "The thresholds are small and they vary. In Washington the limit is five dollars. In California it is now fifteen dollars. Check the figure for your own state. Each state sets its own.",
  "Two bone cream price tags hang side by side at the centre of the frame from a slim pale putty rail. The numerals 5 and 15 are printed on them in bold condensed sans-serif in warm tan. Empty pale sage all around. No green anywhere.",
  "One price tag drifts slightly on the rail.", "5 AND 15"),

 ("Practical and warm.",
  "Before you search, write down what you need. Every surname you have used. Every address from the last twenty years. That list is the whole preparation. It takes about ten minutes.",
  "A single bone cream notepad lies flat and open at the centre of the frame, ruled with fine pale putty lines and blank. A bone cream pen rests across its lower edge. Empty pale sage all around. No green anywhere.",
  "A single ruled line is drawn on the pad.", None),

 ("Reassuring. Flat on \"Nothing unusual\".",
  "If a state is holding something, it will ask you to prove you are you. Usually identification, and a document tying you to the old address. Nothing unusual. The claim form is free.",
  "A single bone cream identification card lies flat at the centre of the frame beside a folded bone cream utility bill ruled with fine pale putty lines. Empty pale sage all around. No green anywhere.",
  "The utility bill unfolds once.", None),

 ("Firm. Emphasis on \"free\".",
  "Nobody needs to be paid to do this for you. The state databases are free, and the administrators say so plainly. A company charging a percentage is charging for a free search.",
  "A single bone cream invoice lies flat and alone at the centre of the frame, ruled with fine pale putty lines and blank. A small pale putty coin rests on its lower corner. Empty pale sage all around. No green anywhere.",
  "The coin is lifted from the invoice.", None),

 ("Practical, then warm. Full pause before the last line. Runs 20 seconds.",
  "So start with the drawer. Take out every card and check the balance on each one. Then search your name in every state you have lived in. It costs nothing to look. The money may be unclaimed. It does not have to stay that way.",
  "The same open kitchen drawer from the opening frame at the identical angle, now empty except for one bone cream gift card lying flat in the centre. No green anywhere.",
  "The drawer slides fully open once.", "UNCLAIMED"),
]

SIGN_OFF = "The money may be unclaimed. It does not have to stay that way."

def timecode(i):
    s = i * 15
    return f"[{s // 60:02d}:{s % 60:02d}]"

def words(t):
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’,\.]*", t))

def wc(t):
    return len([w for w in re.split(r"\s+", t.strip()) if w])

def sentences(t):
    return [s for s in re.split(r"(?<=[.!?])\s+", t.strip()) if s]

# ---------------- self-check ----------------
errors, warnings = [], []
assert len(BEATS) == 40, f"expected 40 beats, got {len(BEATS)}"

FORBIDDEN = ["here's the thing", "but here's where it gets interesting",
             "experts say", "studies show", "—", "--", "–"]

for i, (voice, narr, vis, motion, tl) in enumerate(BEATS):
    n = i + 1
    tc = timecode(i)
    w = wc(narr)
    lo, hi = (42, 46) if n == 40 else (31, 34)
    if not (lo <= w <= hi):
        errors.append(f"beat {n} {tc}: word count {w} outside {lo}-{hi}")
    sl = [wc(s) for s in sentences(narr)]
    avg = sum(sl) / len(sl)
    if avg >= 14:
        errors.append(f"beat {n}: avg sentence length {avg:.1f} >= 14")
    low = narr.lower()
    for f in FORBIDDEN:
        if f in low or f in vis.lower():
            errors.append(f"beat {n}: forbidden construction {f!r}")
    if re.search(r"\b(we|our|us|i|my)\b", low):
        errors.append(f"beat {n}: first person in narration")
    if re.search(r"\d", narr):
        errors.append(f"beat {n}: numeral in narration (must be spelled out)")
    # visual: green discipline
    is_green = (n == GREEN_BEAT)
    if is_green:
        if "No green anywhere." in vis:
            errors.append(f"beat {n}: green beat must not say 'No green anywhere.'")
        if "the only green in the image" not in vis:
            errors.append(f"beat {n}: green beat must name the single emerald object")
    else:
        if not vis.rstrip().endswith("No green anywhere."):
            errors.append(f"beat {n}: visual must end 'No green anywhere.'")
        if "emerald" in vis.lower() or "green" in vis.lower().replace("no green anywhere.", ""):
            errors.append(f"beat {n}: non-green beat mentions green")
    # visual must be a still frame
    for bad in ["then", "camera", "pans", "zooms", "orbits", "whip"]:
        if re.search(rf"\b{bad}\b", vis, re.I):
            errors.append(f"beat {n}: motion/camera word {bad!r} in VISUAL")
    # motion vocabulary
    if wc(motion) > 9:
        warnings.append(f"beat {n}: motion verb long ({wc(motion)} words)")

# green count
greens = sum(1 for i, b in enumerate(BEATS) if "the only green in the image" in b[2])
if greens != 1:
    errors.append(f"expected exactly 1 green beat, found {greens}")

# sign-off verbatim as final two sentences of beat 40
if not BEATS[39][1].rstrip().endswith(SIGN_OFF):
    errors.append("beat 40 does not end with the verbatim sign-off")

# anchor object returns
anchor_phrase = "the same open kitchen drawer from the opening frame at the identical angle"
returns = [i + 1 for i, b in enumerate(BEATS) if anchor_phrase in b[2].lower()]
if returns != [12, 40]:
    errors.append(f"anchor returns are {returns}, expected [12, 40]")

total_words = sum(wc(b[1]) for b in BEATS)
if not (1300 <= total_words <= 1340):
    errors.append(f"total word count {total_words} outside 1300-1340")

if errors:
    print("SELF-CHECK FAILED")
    for e in errors:
        print("  ERROR:", e)
    sys.exit(1)
print(f"SELF-CHECK PASSED - 40 beats, {total_words} words, green at {timecode(GREEN_BEAT-1)}")
for w_ in warnings:
    print("  warn:", w_)

# ---------------- strip numerals for scenes.json ----------------
def strip_numerals(vis):
    """Remove the numeral/label sentence so generated frames carry no text."""
    out = re.split(r"(?<=[.])\s+", vis)
    kept = [s for s in out if not re.search(r"\bnumerals?\b", s, re.I)]
    return " ".join(kept).strip()

os.makedirs(f"{ROOT}/resources/script", exist_ok=True)
os.makedirs(f"{ROOT}/resources/qa", exist_ok=True)

scenes = []
for i, (voice, narr, vis, motion, tl) in enumerate(BEATS):
    n = i + 1
    scenes.append({
        "beat_index": n,
        "timecode": timecode(i),
        "duration_ms": 20000 if n == 40 else 15000,
        "is_green": n == GREEN_BEAT,
        "narration": narr,
        "visual": strip_numerals(vis),
        "visual_authored": vis,
        "voice_direction": voice,
        "motion_verb": motion,
        "type_layer": tl,
        "voice_ms": None,
    })

green_count = sum(1 for s in scenes if s["is_green"])
assert green_count == 1, f"scenes.json green count {green_count}"

with open(f"{ROOT}/resources/script/scenes.json", "w") as f:
    json.dump({"episode": "episode-01",
               "channel": "unclaimed",
               "contract": "ISO",
               "style_string_sha256": __import__("hashlib").sha256(STYLE.encode()).hexdigest(),
               "runtime_ms": 605000,
               "fps": 30,
               "resolution": "1280x720",
               "word_count": total_words,
               "green_beat": GREEN_BEAT,
               "scenes": scenes}, f, indent=2)

# ---------------- episode.md ----------------
L = []
L.append("# EPISODE 1 · What Happens to Gift Card Balances Nobody Spends")
L.append("")
L.append("## Script")
L.append("")
for i, (voice, narr, vis, motion, tl) in enumerate(BEATS):
    L.append(f"{timecode(i)} {narr}")
    L.append("")
L.append("")
L.append("## AI PRODUCTION SCRIPT")
L.append("")
L.append("**What Happens to Gift Card Balances Nobody Spends**")
L.append("")
L.append(f"**10:05 · 40 beats at 15s · 130 wpm · green at {timecode(GREEN_BEAT-1)}**")
L.append("")
for i, (voice, narr, vis, motion, tl) in enumerate(BEATS):
    n = i + 1
    head = f"{timecode(i)}" + (" · GREEN" if n == GREEN_BEAT else "")
    L.append(f"{head} VOICE {voice} NARRATION {narr} VISUAL [ISO] {vis}")
    L.append("")
open(f"{ROOT}/resources/script/episode.body.md", "w").write("\n".join(L))
print("wrote episode.body.md and scenes.json")
