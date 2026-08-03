# UNCLAIMED · RESEARCH STANDARD AND TOPIC ENGINE

Governs Job A (ideation and demand) and Job B (research and fact gate).

---

# PART 1 · SOURCE HIERARCHY

Every claim carries a tier. Tier determines whether it can ship.

| Tier | What it is | Ships? |
|---|---|---|
| OFFICIAL | The agency, treasury, court, administrator or regulator that actually holds the money or writes the rule. `.gov`, state treasury, settlement administrator site, court docket, agency publication. | Yes |
| PRIMARY | The company's own filing or disclosure. SEC 10-K, annual report, published policy, terms of service, statute text. | Yes |
| SECONDARY | Reputable reporting or a specialist aggregator that cites an official source you can follow. | Only with the underlying official URL attached |
| CONTESTED | Figures that vary by methodology, estimates from advocacy groups, anything two credible sources disagree on. | Only if the narration says it is an estimate |

**Never used:** content farms, SEO listicles, recovery companies charging finder's fees, AI-generated summary sites, undated blog posts, anything that will not survive a click.

## Standing official source set

Use these first, every time.

- `usa.gov/unclaimed-money` and `unclaimed.org` (NAUPA), plus the individual state treasury or comptroller site
- `missingmoney.com` for the multi-state search
- `fiscal.treasury.gov` and `treasurydirect.gov` Treasury Hunt for federal securities and undeliverable payments
- `pbgc.gov` for unclaimed pensions
- U.S. Courts unclaimed funds locator for bankruptcy
- `irs.gov` for refunds, credits and the three-year window
- `disasterassistance.gov` and FEMA publications for disaster aid
- `dol.gov` and state labor departments for wage claims
- `naic.org` life insurance policy locator
- `cms.gov` and state insurance departments for medical billing and coverage
- `transportation.gov` for airline refund and compensation rules
- `ftc.gov` for refund programmes and redress administration
- `classaction.org` and settlement administrator sites for open settlements, followed to the administrator's own page

---

# PART 2 · THE FACT GATE

Run before a single line of script is written. It is adversarial: assume the research is wrong and try to break it.

**Gate checks, in order:**

1. **Live URL per claim.** Every figure, deadline, state count, statute reference, programme name and eligibility rule has a URL that resolves right now. Not a homepage. The specific page.
2. **Figure matches source exactly.** No rounding up, no "roughly", no carrying a number forward from an older article.
3. **Date currency.** Deadlines, dollar thresholds and programme names change. Anything older than 18 months gets re-verified against the current page. Note the check date.
4. **Jurisdictional scope stated.** Federal, state, or state-varying. If state-varying, the mechanism that determines which rule applies is identified (state of incorporation, state of residence, state where the loss occurred).
5. **Counterexample search.** Actively look for the case where the claim does not hold. If a rule has a major exception, the script names it.
6. **Institution's own language checked.** If the episode names what the institution calls something, that name is confirmed in the institution's own material.
7. **Nothing that reads as advice.** Every claim is a statement about how a system works, not an instruction about what this viewer should do.

**Gate output:**

```
FACT GATE: PASS | FAIL
Unsourced claims: <list or none>
Secondary-only claims: <list or none>
Contested figures: <list, with the disagreement stated>
Stale sources: <list, with age>
Scope gaps: <list or none>
Verdict reason: <one line>
```

A FAIL means the affected claims are cut or downgraded to hedged language, then the gate reruns. Two consecutive FAILs on the same claim means the claim is dropped and the beat is rewritten around what survives.

---

# PART 3 · TOPIC SCORING

Every candidate topic is scored before it enters the queue. Six criteria, 1 to 5 each. Total out of 30.

| Criterion | Scores 5 when |
|---|---|
| **Search demand** | People already search this in plain language, without knowing the technical term |
| **Recoverability** | There is a real, free, official route to the money that a viewer can follow today |
| **Surprise** | The turn is genuinely counterintuitive, not just unfamiliar |
| **Source depth** | Official structured record exists and is machine-readable or reliably published |
| **RPM band** | Sits in insurance, tax, banking, legal compensation or property rather than general consumer interest |
| **Evergreen** | Still true and still searched in two years, not tied to one settlement's deadline |

**Thresholds:** 24 and above goes straight to the queue. 18 to 23 is held for a stronger angle. Below 18 is rejected and the reason recorded so it is not re-proposed.

**Automatic rejections regardless of score:**
- Any topic where the only route to the money runs through a paid recovery service
- Any topic whose figure cannot be sourced to an official or primary tier
- Any topic that requires implying the viewer specifically has money waiting
- Any active tragedy still in the news cycle
- Any topic where the honest answer is "you are probably not eligible"

---

# PART 4 · DEMAND MONITORING

Scheduled agents feed the queue. Four watchers, each producing scored candidate rows rather than finished ideas.

| Watcher | Source | Fires on |
|---|---|---|
| Settlement watch | Settlement administrator feeds, `classaction.org`, court dockets | New settlement opens for claims, or a claim deadline is inside 60 days |
| Programme watch | Agency refund and benefit announcements, FTC redress, state treasury press | New refund programme, threshold change, or a state law change |
| Deadline watch | Existing covered topics | A deadline in a published episode is approaching or has moved |
| Question watch | Own comment sections, search suggest, related-query data | A repeated high-intent question with no episode covering it |

**The comment section is the primary topic pipeline.** High-intent questions from viewers who already trust the channel outrank anything a watcher surfaces. Mine it every week.

---

# PART 5 · TOPIC ARCHITECTURE

Six clusters. Long-run balance roughly even, weighted toward the top three because they carry the RPM.

### A · Unclaimed property and forgotten assets
State-held property, dormant bank accounts, uncashed paychecks, utility deposits, lost life insurance policies, unclaimed shares and dividends, safe deposit boxes, savings bonds, inheritances nobody knew existed, bankruptcy funds.

### B · Insurance, employment and government money
Death benefits nobody claimed, pensions from old employers, unpaid wages and overtime, tax credits people assume they earn too much for, benefits that do not arrive automatically, disaster assistance and appeals, claims when the policyholder dies.

### C · Settlements and collective compensation
Finding settlements you qualify for, why notices look like junk mail, what happens to unclaimed settlement money, how data breach payments are calculated, why payouts vary so widely, the deadline that removes you, how administrators verify a claim, proof requirements for old purchases.

### D · Consumer refunds and compensation
Airline cash versus vouchers, hotel and booking refunds, extended warranty rights, charges after cancellation, duplicate bank payments, recalls that pay cash, gift card balances and breakage, subscription refund rules.

### E · Property, tenancy and estates
Security deposit withholding rules, foreclosure and tax sale surplus, escrow and closing refunds, estates without a will, executor obligations, mortgage insurance refunds.

### F · Medical and billing
Billing errors that become refunds, overpayment recovery, out-of-network reprocessing, hospital financial assistance nobody applies for, insurer refund obligations.

---

# PART 6 · PRODUCED AND QUEUED

**Produced:**
1. What Happens to Gift Card Balances Nobody Spends (cluster D)
2. Disaster Relief Money That Goes Unclaimed Every Year (cluster B)

**Next ten, ordered.** Each still needs its own fact gate before scripting.

3. How to Check Whether a US State Is Holding Money in Your Name (A)
4. How to Find Class Action Settlements You May Qualify For (C)
5. How People Lose Track of Life Insurance Policies (B)
6. The Insurance Benefit People Forget to Claim After a Death (B)
7. What Happens to a Pension From an Employer You Left Years Ago (B)
8. When an Airline Owes You Money Instead of a Voucher (D)
9. When a Security Deposit Can Legally Be Withheld (E)
10. How Medical Billing Errors Turn Into Refunds (F)
11. Why Settlement Notices Look Like Junk Mail (C)
12. The Tax Credits People Miss Because They Assume They Earn Too Much (B)

---

# PART 7 · RESEARCH PACK FORMAT

Job B output. One pack per episode, delivered as a single block.

```
TOPIC: <title>
CLUSTER: <letter and name>
SCORE: <n>/30
EDITORIAL QUESTION: <the one question this episode answers>
THE TURN: <the counterintuitive fact the episode exists for, in one sentence>
GREEN BEAT CANDIDATE: <where recoverable money first becomes concrete>

CLAIMS
| # | Claim | Figure | Source URL | Tier | Checked | Scope |

MECHANISM
<how the money comes to exist and how it comes to be unclaimed, in plain prose, no more than 200 words>

WHERE PEOPLE LOSE IT
<the ordinary sequence, three or four steps>

VERIFICATION ROUTE
<the exact official resource, what the viewer does, and the one thing people get wrong>

INSTITUTION'S OWN TERM
<what they call it internally, sourced, or "none">

STATE VARIATION
<varies or does not, and the mechanism that decides>

FACT GATE
<the gate output block>
```
