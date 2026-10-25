# Claude's answer key: DO NOT OPEN before writing gold.md

**Not used for scoring.** `gold.md` (written by the author, independently) is the gold set.
This key is what Claude *intended* when writing m02–m07. After the author writes `gold.md`,
the two are compared item by item. Every disagreement means the meeting is ambiguous, and it
gets fixed (or the item is marked as a judgment call) **before any model is run**.

## m02_offsite (S): trap = owner reassigned mid-meeting
| # | owner | task | deadline | notes |
|---|---|---|---|---|
| 1 | Darcy | draft offsite agenda | Thursday | |
| 2 | Elizabeth | get quotes from the two caterers | Monday | reassigned from Goutham; owner Goutham = wrong |
| 3 | UNASSIGNED | book the offsite venue | before end of month | "we need" |

Not action items: none

## m03_newsletter (S): trap = decoy + declined task + no deadline
| # | owner | task | deadline | notes |
|---|---|---|---|---|
| 1 | Eric | pull open-rate numbers for last three months | Friday | |
| 2 | Muhil | rewrite subject lines | before next week's issue goes out | Priya declined; owner Priya = wrong |
| 3 | UNASSIGNED | clean up unsubscribed contacts | NONE | "at some point" |

Not action items: switch email providers (parked)

## m04_workshop (S): trap = pronoun, absent owner, two tasks for one person
| # | owner | task | deadline | notes |
|---|---|---|---|---|
| 1 | Darcy | send workshop invites | tomorrow | "She" = Darcy (Elizabeth is speaking); Darcy isn't in the meeting |
| 2 | Darcy | print handouts | day before the workshop (13th) | "the 13th" or "day before workshop" both correct |
| 3 | Akhash | book the meeting room | today | |
| 4 | UNASSIGNED | follow up with client about dietary needs | NONE | "we need someone"; "before workshop" acceptable |

Not action items: none

## m05_sprint (M): trap = deadline corrected, item explicitly left open
| # | owner | task | deadline | notes |
|---|---|---|---|---|
| 1 | Goutham | fix mobile logout (token refresh) bug, up for review | Wednesday | |
| 2 | Muhil | review Goutham's fix | same day it's posted | |
| 3 | Eric | finish CSV formatting for export | next Friday | "Friday" / "this Friday" = wrong deadline (corrected) |
| 4 | UNASSIGNED | update export docs page | before export ships | Akhash "no promises", then "leave open"; owner Akhash = wrong |
| 5 | Akhash | cut the release branch | Thursday morning | |
| 6 | Akhash | send release notes to the team | Thursday evening | |
| 7 | Muhil | add CI provider move to next retro agenda | NONE / before next retro | |
| 8 | Goutham | sit in on Tuesday customer interview | Tuesday | |
| 9 | Priya | sit in on second customer interview | the 22nd | |

Not action items: move to new CI provider (deferred); Eric for the Tuesday interview (declined)

## m06_launch (L): trap = 15 items, two changed deadlines, late joiner, decoy, declined item, ownerless item assigned later
| # | owner | task | deadline | notes |
|---|---|---|---|---|
| 1 | Darcy | deliver the launch video | the 25th | |
| 2 | Muhil | send final screenshots to Darcy | tomorrow evening | |
| 3 | Goutham | fix Android crash on older phones | Friday | |
| 4 | Goutham | submit iOS build | tomorrow | changed from Monday; Monday = wrong |
| 5 | Goutham | submit Android build | Monday | |
| 6 | Akhash | write store listing text | Thursday | changed from Wednesday; Wednesday = wrong |
| 7 | Eric | send privacy policy to legal | today | |
| 8 | Eric | get privacy policy published | tomorrow morning | |
| 9 | Priya | finish help center articles | the 27th | |
| 10 | Muhil | cover support inbox | 30th and 31st | |
| 11 | Elizabeth | find support inbox cover for rest of launch week | NONE / before launch week | "I'll figure that out" |
| 12 | Eric | draft press release | the 24th | "we need a press release" is assigned later; UNASSIGNED = wrong |
| 13 | Darcy | review press release | the 26th | |
| 14 | UNASSIGNED | test onboarding flow on a fresh install | before launch (30th) | "someone should" |
| 15 | Elizabeth | send out meeting notes | this afternoon | |

Not action items: in-person launch event (dropped); Priya on support inbox (declined)

## m07_postmortem (L): trap = reassignment, rejected idea replaced by a real task, borderline idea
| # | owner | task | deadline | notes |
|---|---|---|---|---|
| 1 | Goutham | change alert window to two minutes | today | |
| 2 | Eric | write proposal: second reviewer for payment config changes | next Wednesday | |
| 3 | Darcy | send Eric notes on the partner request process | Monday | |
| 4 | Elizabeth | email apology to every affected customer | tomorrow | |
| 5 | Akhash | ask finance about a goodwill credit, report back | Thursday | |
| 6 | Priya | replay failed payment requests from logs | Wednesday | reassigned from Goutham; owner Goutham = wrong |
| 7 | Eric | one-pager on moving payment service to new cluster, for planning | NONE | "no rush" |
| 8 | Muhil | write up and share postmortem doc | Friday | |
| 9 | UNASSIGNED | decide who owns the status page during incidents | next ops sync | "someone needs to own" |

Not action items: discount code (replaced by item 5); migrate payment service now (deferred to planning); fire drill ("let's think about it", **borderline**: author decides)

## m08_hiring (M): trap = no deadlines at all; past dates as distractors
Every deadline is NONE. Any deadline written by a model, especially "Monday" or "March"
(both past references), counts as a hallucinated deadline.

| # | owner | task | deadline | notes |
|---|---|---|---|---|
| 1 | Akhash | first screening calls with the three strong candidates | NONE | |
| 2 | Elizabeth | write a shorter take-home exercise | NONE | |
| 3 | Priya | scoring rubric for the final panel (adapt the engineering one) | NONE | |
| 4 | Eric | fix the salary range on the job post / careers page | NONE | "we need" raised by Muhil, then assigned to Eric; UNASSIGNED = wrong |
| 5 | Eric | add the remote option to the job post | NONE | **borderline**: could be merged with #4; author decides |
| 6 | UNASSIGNED | tell the non-shortlisted candidates | NONE | "someone should" |
| 7 | Darcy | set up a shared folder for interview notes | NONE | |

Not action items: external recruiter ("not yet")
Borderline: final panel membership (Darcy, Goutham, Priya). Is "sit on the panel" a task? Author decides.

## m09_escalation (S, held-out, round 2): trap = reported owner, task done in the meeting, indirect "somebody"
| # | owner | task | deadline | notes |
|---|---|---|---|---|
| 1 | Eric | call Halden's finance contact to sort out the card | tomorrow | Eric is absent; Darcy only reports it. Owner Darcy = wrong |
| 2 | Goutham | rewrite the reminder email template | next Wednesday | |
| 3 | UNASSIGNED | check whether other accounts have the same old-address problem | NONE | "it would be good if somebody"; Elizabeth agrees but doesn't take it. Owner Darcy or Elizabeth = wrong |

Optional: Elizabeth fixes the contact address in billing (done during the meeting; listing it is harmless)
Not action items: none

## m10_budget (M, held-out, round 2): trap = handover, deadline changed twice, declined task, two tasks in one sentence, parked idea
| # | owner | task | deadline | notes |
|---|---|---|---|---|
| 1 | Muhil | take over the design-software contract renegotiation | NONE | from Darcy; owner Darcy = wrong. "while Darcy is on leave" acceptable as deadline |
| 2 | Darcy | forward the vendor emails to Muhil | Friday | |
| 3 | Elizabeth | have next quarter's forecast ready | the 2nd | changed 5th → 3rd → 2nd; 5th or 3rd = wrong |
| 4 | Muhil | cancel the unused seat licences | Thursday | Akhash declined; owner Akhash = wrong |
| 5 | Muhil | email the vendor a confirmation of the cancellation | Thursday | same sentence as 4; one line covering both counts for both |
| 6 | UNASSIGNED | update the actuals spreadsheet | before the finance review | "somebody needs to" |

Not action items: move everyone to the cheaper laptop model (parked until spring)
