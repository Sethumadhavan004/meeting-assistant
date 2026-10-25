# Gold set

The correct answers used to score every model's output. Written by the author from the
transcripts alone, before any model saw m02–m08. Cross-checked against Claude's independent key
(`eval/design/claude-key.md`); every disagreement was resolved by the author.

## How to read this file

| term | meaning for scoring |
|---|---|
| owner `UNASSIGNED` | nobody took the task. Flagged as unassigned = 2 (best), omitted = 1 (ok), invented an owner = 0 (wrong) |
| deadline `NONE` | no deadline was stated. A model writing any deadline here = wrong deadline |
| **notes** | acceptable alternatives and known wrong answers for that item |
| **Not action items** | discussed but not agreed, or declined. Extracting one = a wrong item (counts against precision) |
| **Optional** | borderline. Extracting it or not is both fine; it doesn't count for recall or precision |

Task wording doesn't have to match. An extracted item matches if it's the same task
(e.g. "write copy" = "complete the copy"). The author makes the final call on every match.

---

## m01_pricing

| # | owner | task | deadline | notes |
|---|---|---|---|---|
| 1 | Meena | send logo files | today by 5pm | |
| 2 | Arjun | write pricing page copy | Wednesday | |
| 3 | Arjun | email client to confirm demo time | tomorrow morning | |
| 4 | UNASSIGNED | get pricing page live | before Friday demo | team goal; an invented owner (e.g. Priya) = wrong |

**Not action items:** none
**Optional:** none

## m02_offsite

| # | owner | task | deadline | notes |
|---|---|---|---|---|
| 1 | Darcy | draft the offsite agenda | Thursday | |
| 2 | Elizabeth | get quotes from the two caterers | Monday | reassigned because Goutham is out next week; owner Goutham = wrong |
| 3 | UNASSIGNED | book the offsite venue | before end of month | team goal |

**Not action items:** none
**Optional:** none

## m03_newsletter

| # | owner | task | deadline | notes |
|---|---|---|---|---|
| 1 | Eric | pull open-rate numbers for the last three months | Friday | |
| 2 | Muhil | rewrite the subject lines | before next week's issue goes out | Priya declined (audit); owner Priya = wrong |
| 3 | UNASSIGNED | clean up unsubscribed contacts | NONE | raised as a comment at the end ("at some point") |

**Not action items:**
- switch email providers (parked, not decided)

**Optional:** none

## m04_workshop

| # | owner | task | deadline | notes |
|---|---|---|---|---|
| 1 | Darcy | send the workshop invites | tomorrow | "She" = Darcy. Darcy isn't in the meeting; Elizabeth reports it. Owner Elizabeth = wrong; "Darcy (via Elizabeth)" = correct |
| 2 | Darcy | print the handouts | day before the workshop | "the 13th" also correct (workshop is on the 14th) |
| 3 | Akhash | book the meeting room | today | |
| 4 | UNASSIGNED | follow up with the client about dietary needs | NONE | "before the workshop" also acceptable |

**Not action items:** none
**Optional:** none

## m05_sprint

| # | owner | task | deadline | notes |
|---|---|---|---|---|
| 1 | Goutham | fix the mobile login bug and put it up for review | Wednesday | |
| 2 | Muhil | review Goutham's login fix | Wednesday | "same day it's posted" also correct |
| 3 | Eric | finish the export feature (CSV formatting) | next Friday | backend is done; "finish CSV formatting" also correct; "Friday" / "this Friday" = wrong deadline (corrected in the meeting) |
| 4 | UNASSIGNED | update the export docs page | before export ships | Akhash said "no promises", then it was left open; owner Akhash = wrong |
| 5 | Akhash | cut the release branch | Thursday morning | |
| 6 | Akhash | send the release notes to the team | Thursday evening | |
| 7 | Muhil | add the CI provider move to the next retro agenda | NONE | "before the next retro" also acceptable |
| 8 | Goutham | sit in on Tuesday's customer interview | Tuesday | |
| 9 | Priya | sit in on the second customer interview | the 22nd | |

**Not action items:**
- move to the new CI provider (deferred: "not this sprint")
- Eric sits in on the Tuesday interview (declined)

**Optional:** none

## m06_launch

| # | owner | task | deadline | notes |
|---|---|---|---|---|
| 1 | Darcy | deliver the launch video | the 25th | 80% done; depends on Muhil's screenshots |
| 2 | Muhil | send the final app screenshots to Darcy | tomorrow evening | |
| 3 | Goutham | submit the iOS build to the app store | tomorrow | changed from Monday; "Monday" = wrong deadline |
| 4 | Goutham | fix the Android crash on older phones | Friday | |
| 5 | Goutham | submit the Android build to the app store | Monday | after the crash fix |
| 6 | Akhash | write the store listing text (description, keywords) | Thursday | changed from Wednesday (conference clash); "Wednesday" = wrong deadline |
| 7 | Eric | send the privacy policy to legal for sign-off | today | |
| 8 | Eric | get the privacy policy published | tomorrow morning | must be live before the iOS submission |
| 9 | Priya | finish the help center articles | the 27th | half done |
| 10 | Muhil | cover the support inbox | 30th and 31st | first two days of launch week |
| 11 | Elizabeth | find cover for the support inbox for the rest of launch week | NONE | "before launch week" also acceptable |
| 12 | Eric | draft the press release | the 24th | "we need a press release" was raised earlier and assigned here; listing it as UNASSIGNED = wrong owner |
| 13 | Darcy | review the press release draft | the 26th | |
| 14 | UNASSIGNED | test the onboarding flow on a fresh install | before launch (30th) | "someone should" |
| 15 | Elizabeth | send out the meeting notes | this afternoon | |

**Not action items:**
- in-person launch event (Priya's idea, dropped for lack of budget)
- Priya covers the support inbox (declined, traveling from the 29th)

**Optional:**
- app launch on the 30th (context, not a task)

## m07_postmortem

| # | owner | task | deadline | notes |
|---|---|---|---|---|
| 1 | Goutham | change the alert window to two minutes | today | |
| 2 | Eric | write a proposal: payment config changes need a second reviewer | next Wednesday | uses Darcy's notes on the partner request |
| 3 | Darcy | send Eric notes on the partner request process | Monday | |
| 4 | Elizabeth | email an apology to every affected customer | tomorrow | |
| 5 | Akhash | ask finance about a goodwill credit and report back | Thursday | |
| 6 | Priya | replay the failed payment requests from the logs | Wednesday | reassigned from Goutham; owner Goutham = wrong |
| 7 | Eric | write a one-pager on moving the payment service to the new cluster, for planning | NONE | "no rush" |
| 8 | UNASSIGNED | decide who owns the status page during incidents | next ops sync | "someone needs to own" |
| 9 | Muhil | write up and share the postmortem doc | Friday | |

**Not action items:**
- discount code for customers (replaced by item 5, pending finance)
- move the payment service to the new cluster now (deferred to planning)

**Optional:**
- fire drill to simulate an outage ("let's think about it")

## m08_hiring

| # | owner | task | deadline | notes |
|---|---|---|---|---|
| 1 | Akhash | handle the first screening calls with the top candidates | NONE | |
| 2 | Elizabeth | write a shorter take-home exercise | NONE | |
| 3 | Priya | put together the scoring rubric for the panel | NONE | adapting the engineering one; "update the rubric" also correct |
| 4 | Eric | update the careers page with the new salary range and remote option | NONE | listing salary and remote option as two items also correct (second one = duplicate) |
| 5 | Darcy | set up a shared folder for the interview notes | NONE | |
| 6 | UNASSIGNED | let the candidates we didn't shortlist know | NONE | "someone should" |

Every deadline in this meeting is `NONE`. "Last Monday" and "in March" are past references, not deadlines.

**Not action items:**
- bring in an external recruiter ("not yet")

**Optional:**
- sit on the final panel (Darcy, Goutham, Priya)

## m09_escalation

| # | owner | task | deadline | notes |
|---|---|---|---|---|
| 1 | Eric | call the finance contact to sort out the card issue | tomorrow | Eric is absent; Darcy only reports it. Owner Darcy = wrong |
| 2 | Goutham | rewrite the reminder template | next Wednesday | |
| 3 | UNASSIGNED | check whether other accounts have the same old-address problem | NONE | "it would be good if somebody"; Elizabeth agrees but doesn't take it. Owner Darcy or Elizabeth = wrong |

**Not action items:** none
**Optional:**
- Elizabeth updates the contact address in the billing system (done during the meeting)

## m10_budget

| # | owner | task | deadline | notes |
|---|---|---|---|---|
| 1 | Muhil | take over the design-software contract renegotiation | NONE | handed over from Darcy; owner Darcy = wrong. "while Darcy is on leave" acceptable |
| 2 | Darcy | hand over the contract: forward the vendor emails to Muhil | Friday | |
| 3 | Elizabeth | have the forecast for next quarter ready | 2nd | changed 5th → 3rd → 2nd; 5th or 3rd = wrong |
| 4 | Muhil | cancel the unused seats and email the vendor a confirmation | Thursday | Akhash declined; owner Akhash = wrong. Split into two lines = duplicate, not penalised |
| 5 | UNASSIGNED | update the spreadsheet with the actuals | before the finance review | "somebody needs to" |

**Not action items:**
- move everyone to the cheaper laptop model (parked until the hardware refresh in spring)

**Optional:** none
