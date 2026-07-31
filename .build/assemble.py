#!/usr/bin/env python3
"""Assemble episode.md (4 sections) and metadata.json."""
import json, re, hashlib

ROOT = "/workspaces/youtube/channels/unclaimed/episodes/episode-01"
body = open(f"{ROOT}/resources/script/episode.body.md").read()
sc = json.load(open(f"{ROOT}/resources/script/scenes.json"))

CHECKED = "2026-07-30"
SBUX = "https://www.sec.gov/Archives/edgar/data/829224/000082922425000114/sbux-20250928.htm"
CFPB = "https://www.consumerfinance.gov/rules-policy/regulations/1005/20/"
USC = "https://www.law.cornell.edu/uscode/text/15/1693l-1"
BANK = "https://www.bankrate.com/credit-cards/news/gift-cards-survey/"
NAUPA = "https://unclaimed.org/"
MM = "https://www.missingmoney.com/"
NY = "https://www.nysenate.gov/legislation/laws/ABP/1315"
CACCP = "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CCP&sectionNum=1520.5"
CACIV = "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CIV&sectionNum=1749.5"
WA = "https://app.leg.wa.gov/rcw/default.aspx?cite=19.240.020"
CT = "https://www.cga.ct.gov/2023/rpt/pdf/2023-R-0195.pdf"
TXNJ = "https://www.law.cornell.edu/supremecourt/text/379/674"
USAGOV = "https://www.usa.gov/unclaimed-money"

SOURCES = [
 ("[00:45]", "Breakage is the issuer's term for an unspent balance and is recognized as revenue", "n/a", SBUX, "PRIMARY", "US, issuer accounting"),
 ("[01:00]", "Card loads are deferred revenue, not revenue at point of sale", "n/a", SBUX, "PRIMARY", "US, issuer accounting"),
 ("[01:15]", "The balance is carried as a liability until redeemed", "n/a", SBUX, "PRIMARY", "US, issuer accounting"),
 ("[01:30]", "A predictable unredeemed share is estimated from historical redemption rates", "n/a", SBUX, "PRIMARY", "US, issuer accounting"),
 ("[01:45]", "Breakage is recognized in proportion to redemptions, over time", "n/a", SBUX, "PRIMARY", "US, issuer accounting"),
 ("[03:00]", "Gift card funds cannot expire for at least five years from last load", "5 years", CFPB, "OFFICIAL", "Federal"),
 ("[03:00]", "Statutory basis for the five year floor", "15 USC 1693l-1", USC, "OFFICIAL", "Federal"),
 ("[03:15]", "Inactivity fees require twelve months of no activity, one fee per calendar month", "12 months", CFPB, "OFFICIAL", "Federal"),
 ("[04:00]", "Estimated value of unused gift cards, vouchers and store credit held by US adults", "$27bn", BANK, "CONTESTED", "US, survey estimate"),
 ("[04:15]", "Starbucks breakage revenue recognized in fiscal year ended 28 September 2025", "$222.4m", SBUX, "PRIMARY", "One issuer, one fiscal year"),
 ("[04:30]", "Breakage is reported inside company-operated and licensed store revenue", "n/a", SBUX, "PRIMARY", "One issuer"),
 ("[05:15]", "Every state runs an unclaimed property program", "50 states", NAUPA, "OFFICIAL", "State, all"),
 ("[05:30]", "The transfer to a state is called escheat and the state holds it for the owner", "n/a", NAUPA, "OFFICIAL", "State, all"),
 ("[05:45]", "New York deems an unredeemed gift certificate abandoned after five years and pays it to the comptroller", "5 years", NY, "OFFICIAL", "New York"),
 ("[06:00]", "California exempts most gift certificates from unclaimed property", "n/a", CACCP, "OFFICIAL", "California"),
 ("[06:15]", "States differ; there is no single national rule on gift card escheat", "n/a", CT, "OFFICIAL", "State-varying"),
 ("[06:30]", "First priority rule: the owner's last known address on the holder's records", "n/a", TXNJ, "OFFICIAL", "Federal, Texas v. New Jersey 379 U.S. 674"),
 ("[06:45]", "Second priority rule: the holder's state of incorporation", "n/a", TXNJ, "OFFICIAL", "Federal, Texas v. New Jersey 379 U.S. 674"),
 ("[07:15]", "MissingMoney.com is run by state administrators, is free, and most states participate", "free", NAUPA, "OFFICIAL", "US, multi-state"),
 ("[07:30]", "NAUPA maintains a directory of every state program", "n/a", NAUPA, "OFFICIAL", "US, all states"),
 ("[08:45]", "Fourteen states require cash payout of a small remaining balance on request", "14 states", CT, "OFFICIAL", "State-varying"),
 ("[09:00]", "Washington cash redemption threshold", "$5", WA, "OFFICIAL", "Washington"),
 ("[09:00]", "California cash redemption threshold, operative 1 April 2026", "$15", CACIV, "OFFICIAL", "California"),
 ("[09:30]", "State unclaimed property searches are free", "free", NAUPA, "OFFICIAL", "US, all states"),
]

CHAPTERS = [
 ("00:00", "The card in the drawer"),
 ("00:45", "Breakage, and why it is income"),
 ("02:15", "How a balance becomes unclaimed"),
 ("03:00", "What federal law actually protects"),
 ("04:00", "The scale of it"),
 ("05:00", "Unclaimed property law and escheat"),
 ("06:30", "Which state's rule applies"),
 ("07:00", "How to check your own name"),
 ("08:30", "Cash back on small balances"),
 ("09:00", "What to prepare"),
]

RESOURCES = [
 ("MissingMoney.com, the multi-state unclaimed property search", MM),
 ("NAUPA, directory of every state unclaimed property program", NAUPA),
 ("USA.gov, federal unclaimed money resources", USAGOV),
 ("CFPB, federal gift card rules under Regulation E", CFPB),
 ("New York Abandoned Property Law section 1315", NY),
 ("California Civil Code section 1749.5, cash redemption", CACIV),
 ("California Code of Civil Procedure section 1520.5, gift certificate exemption", CACCP),
 ("Washington RCW 19.240.020, cash redemption", WA),
 ("Connecticut OLR 2023-R-0195, gift card cash back laws by state", CT),
 ("Starbucks Form 10-K, fiscal 2025", SBUX),
]

DISCLAIMER = ("This video is general information about US programmes, rules and databases. "
 "It is not legal, tax, insurance or financial advice, and it does not create any "
 "professional relationship. Rules and deadlines vary by state and change over time. "
 "Always verify your own situation directly with the official source or administrator "
 "named above, or with a qualified professional. We do not charge for information about "
 "how to claim money, and neither do the official databases mentioned here.")

TITLE = "What Happens to Gift Card Balances Nobody Spends"
ALTS = ["The Money Left on Gift Cards and Who Ends Up With It",
        "Unspent Gift Card Balances and What the Law Does With Them"]

HOOK = ("There is a gift card in your house with money still on it. Not the whole balance, "
 "just the awkward part you never went back for. That leftover has a name inside the "
 "company that sold it, and in some states it does not belong to them at all.")

SUMMARY = ("This episode explains what breakage is, why an unspent balance is booked as income "
 "rather than treated as a loss, and how federal law protects the funds from expiring "
 "without ever sending them back to you. You will see why two states can reach opposite "
 "answers on the same balance, and which rule decides. You will also see how to search "
 "the official state databases for money held in your name, for free, and what people get "
 "wrong when they search. Every figure is sourced to an official filing, statute or agency page.")

COMMENTS = "If you have found money in a state database, say which state in the comments, it helps other people know where to look."

HASHTAGS = ("#unclaimedmoney #giftcards #unclaimedproperty #breakage #missingmoney #statetreasury "
 "#personalfinance #consumerrights #escheat #moneytips #findyourmoney #giftcardbalance "
 "#unclaimedfunds #cardact #consumerprotection #financialliteracy #moneyback #forgottenmoney "
 "#statelaw #refunds")

TAGS = ("unclaimed money, gift card balance, unclaimed property, breakage, missing money, "
 "state treasury, escheat, gift card laws, gift card expiration, CARD Act, unclaimed funds, "
 "how to find unclaimed money, missingmoney.com, NAUPA, state unclaimed property, "
 "gift card cash back, gift card cash redemption, unused gift cards, forgotten money, "
 "consumer rights, consumer protection, personal finance, money you forgot, "
 "deferred revenue, stored value cards, Starbucks breakage, unclaimed property law, "
 "state of incorporation, last known address rule, free money search, "
 "how to claim unclaimed money, gift card refund, small balance refund, "
 "New York abandoned property, California gift card law")

COMMERCIAL = ("Newsletter: The Unclaimed Report, a weekly roundup of new settlements, claim "
 "deadlines, refund programmes and official databases. Searching any official database "
 "named in this video is free and always will be.")

# ---------------- episode.md ----------------
out = [body.rstrip(), "", "", "## SOURCES", ""]
out.append("`[Timestamp] | claim | figure | source URL | tier | date checked | scope`")
out.append("")
for tc, claim, fig, url, tier, scope in SOURCES:
    out.append(f"{tc} | {claim} | {fig} | {url} | {tier} | {CHECKED} | {scope}")
    out.append("")
out += ["",
 "**CONTESTED row justification.** The twenty seven billion dollar figure at [04:00] is a "
 "survey estimate from Bankrate, fielded 19 to 21 August 2024 with a sample of 2,373 US "
 "adults. No government body publishes a national total for unspent gift card value. The "
 "narration states that it is an estimate and says explicitly that it is not a government "
 "figure, which is the condition under which a CONTESTED row may ship.", "",
 "Full sourcing detail, every swapped claim and the link verification record are in "
 "`claim-log.md` alongside this file.", "", "", "## METADATA", ""]
out.append(f"**Title:** {TITLE}")
out.append("")
for i, a in enumerate(ALTS, 1):
    out.append(f"**Alternate {i}:** {a}")
out += ["", "**Playlist:** Forgotten Money", "", "### Description", "", HOOK, "", SUMMARY, "",
        COMMENTS, "", "**Chapters**", ""]
for t, n in CHAPTERS:
    out.append(f"{t} {n}")
out += ["", "**Official resources mentioned in this video:**", ""]
for n, u in RESOURCES:
    out.append(f"{n}: {u}")
out += ["", "**Disclaimer**", "", DISCLAIMER, "", HASHTAGS, "",
        "**The Unclaimed Report**", "", COMMERCIAL, "",
        "### Thumbnail text options", "",
        "They Still Owe You / Check Your Name / Nobody Claimed It / Where It Went", "",
        "### Shorts cut points", "",
        "[04:00] the number beat, [05:00] the turn, [07:00] the verification beat", ""]

md = "\n".join(out)
for bad in ["—", "--", "–"]:
    assert bad not in md, f"forbidden dash {bad!r} in episode.md"
open(f"{ROOT}/resources/script/episode.md", "w").write(md)

# ---------------- metadata.json ----------------
desc = []
desc.append(HOOK)
desc.append("")
desc.append(SUMMARY)
desc.append("")
desc.append(COMMENTS)
desc.append("")
desc.append("Chapters")
for t, n in CHAPTERS:
    desc.append(f"{t} {n}")
desc.append("")
desc.append("Official resources mentioned in this video:")
for n, u in RESOURCES:
    desc.append(f"{n}: {u}")
desc.append("")
desc.append(DISCLAIMER)
desc.append("")
desc.append(HASHTAGS)
desc.append("")
desc.append("The Unclaimed Report")
desc.append(COMMERCIAL)
description = "\n".join(desc)

meta = {
  "episode": "episode-01",
  "channel": "unclaimed",
  "title": TITLE,
  "title_alternates": ALTS,
  "playlist": "Forgotten Money",
  "runtime": "10:05",
  "description": description,
  "description_blocks": {
     "hook": HOOK, "summary": SUMMARY, "comment_invite": COMMENTS,
     "chapters": [{"timestamp": t, "name": n} for t, n in CHAPTERS],
     "official_resources": [{"name": n, "url": u} for n, u in RESOURCES],
     "disclaimer": DISCLAIMER,
     "hashtags": HASHTAGS,
     "commercial_pathway": {"heading": "The Unclaimed Report", "body": COMMERCIAL},
  },
  "tags": TAGS,
  "thumbnail_text_options": ["They Still Owe You", "Check Your Name",
                             "Nobody Claimed It", "Where It Went"],
  "shorts_cut_points": ["[04:00]", "[05:00]", "[07:00]"],
}
for k, v in [("title", TITLE)] + [(f"alt{i}", a) for i, a in enumerate(ALTS)]:
    assert len(v) < 70, f"{k} is {len(v)} chars"
    assert not re.search(r"[!?]", v), f"{k} has clickbait punctuation"
assert 15 <= len(HASHTAGS.split()) <= 25, f"hashtags {len(HASHTAGS.split())}"
assert 25 <= len(TAGS.split(",")) <= 40, f"tags {len(TAGS.split(','))}"
assert "#" not in TAGS
blob = json.dumps(meta)
for bad in ["—", "--", "–"]:
    assert bad not in blob, f"forbidden dash in metadata"
json.dump(meta, open(f"{ROOT}/metadata.json", "w"), indent=2)
print(f"episode.md + metadata.json written")
print(f"  title {len(TITLE)} chars, hashtags {len(HASHTAGS.split())}, tags {len(TAGS.split(','))}")
