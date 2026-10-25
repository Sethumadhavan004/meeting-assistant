# Round 2 scoring: decisions for the author

Claude labelled 30 round-2 runs (`r2/labels.csv`, `r2/runs.csv`) and the 6 baseline runs on
held-out m09/m10 (appended to `../labels.csv`, `../runs.csv`). Rows flagged `REVIEW` fall into the
decisions below. Every baseline decision (1–6 in `../REVIEW.md`) was applied unchanged.

| # | decision | rows | Claude's default | alternative | effect of the alternative |
|---|---|---|---|---|---|
| A | **No owner written anywhere** (Bonsai baseline m09, m10 list tasks with no owner field at all). New value `owner_ok = none` | 8 | counts as not correct for owner accuracy; for an UNASSIGNED item scores 1 (omitted), not 0 (invented) | treat as 0 everywhere | Bonsai baseline held-out ambiguity 1.00 → 0.00 |
| B | **Header line** `owner \| task \| deadline` printed above the list (Granite r2: 6 runs) | 6 | format **invalid** (a strict parser reads it as an item owned by "owner") | valid (an app can skip one known line) | Granite r2 format 3/8 → 8/8 on seen, 1/2 → 2/2 held-out |
| C | **"UNASSIGNED" written in the deadline field** with an invented owner (Granite m03, m09; Phi m03) | 3 | format valid (it parses); the wrong owner is already counted | invalid | Granite/Phi format −1 each |
| D | **A deadline from a neighbouring task** ("take over the contract · Friday", where Friday is the vendor-email date) | 4 | deadline wrong (invented for a NONE item) | correct | deadline accuracy up slightly for all three in m10 |
| E | Single judgment matches | 5 | see notes | your call | small |

Rows for E:
- r2 Bonsai m06 ext 9: "UNASSIGNED · cover rest of support week" matched to Elizabeth's "find cover" with owner wrong
- r2 Phi m05 ext 5: "manage the release · Thursday" matched to "cut the branch (Thursday morning)"
- r2 Phi m07 ext 2: "help with the partner request part of the proposal" matched to Darcy's notes to Eric
- baseline Granite m09 ext 5: "no separate item needed" line counted as a wrong item (same as Phi m05 ext 8)
- baseline Phi m10 ext 8: owner "Not specified" counted as flagged UNASSIGNED

Not a decision, recorded as fact: Bonsai r2 m02 and Granite r2 m08 copied the system prompt's
example lines ("book a room for the review", "Sam · send the budget draft") into their answers.
Both are labelled `wrong`.
