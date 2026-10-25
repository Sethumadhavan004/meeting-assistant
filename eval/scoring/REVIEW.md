# Scoring review: decisions for the author

Claude drafted 208 labels (`labels.csv`) and 40 format calls (`runs.csv`). 42 rows carry a `REVIEW`
flag. They fall into **6 decisions**. Decide each one once; Claude applies it to every affected row
and re-runs `python eval/scoring/score.py`.

Current draft = the "Claude's default" column. Numbers in `scores.csv` use these defaults.

| # | decision | rows | Claude's default | alternative | effect if you choose the alternative |
|---|---|---|---|---|---|
| 1 | **Contradicting duplicates.** The same task listed again with a wrong owner (e.g. caterer quotes for Goutham *and* Elizabeth). The protocol says duplicates are ignored, but it was written for harmless splits | 9 (Bonsai off 2, Granite off 4, Phi 3) | `duplicate`, ignored (protocol as written) | count as `wrong` | lowers precision for those three; Granite off is hit most. Needs a dated protocol change-log entry |
| 2 | **Deadline judged from the whole item**, not just the "Deadline:" field (e.g. "attend the interview scheduled for the 22nd · Deadline: Not specified") | 5 (mostly Phi m05) | correct | judge only the field | lowers Phi's deadline accuracy |
| 3 | **One line covering two gold items** (e.g. "cut branch Thursday morning and send notes Thursday evening") | 6 (m05, m06) | counts for both | counts for one | lowers recall a little for the off configs |
| 4 | **"ASAP" in m08**, where no deadline exists | 6 (Phi m08) | invented deadline | not a deadline | Phi's invented deadlines 6 → 0 |
| 5 | **Format calls**: Bonsai off puts the owner under "Task:" (m01, m02) or inside a sentence (m04); Granite off m07 lists lines it says are "omitted"; prose lines with the deadline inside the sentence (Granite off m05/m06, Phi m06) | 7 | Bonsai m01/m02/m04 = 0, Granite m07 = 0, prose = 1 | your call per case | changes format_ok counts only |
| 6 | **Single judgment matches** | 9 | see notes | your call | small |

The rows for decision 6, in `labels.csv`:
- Bonsai off m05 ext 4: "before release (Next Friday)" accepted as "before export ships"
- Bonsai off m05 ext 7: "Tuesday, 22nd" counted wrong (conflates the two interviews)
- Bonsai off m06 ext 3: "Wednesday (adjusted to Thursday)" accepted as Thursday
- Bonsai off m06 ext 4: "draft privacy policy" matched to "send to legal" (already drafted)
- Phi m05 ext 8: "Eric, task: Not specified" counted as a wrong item
- Phi m06 ext 9: legal deadline missing (only "tomorrow morning" given) counted wrong
- Granite off m07 ext 11–15: lines the model marks "omitted" but still lists, treated as extracted

How to check any of them: open `outputs/<run_id>.md`, read the **Answer** section only, and compare with
`gold.md`. Tell Claude the decision number and your choice (e.g. "1 wrong, 2 ok, 3 ok, 4 ok, 5 ok, 6 ok").

## Author's decisions (2026-10-25)

All six defaults kept, so the numbers in `scores.csv` did not change. Flags in `labels.csv` and
`runs.csv` now read `decided` instead of `REVIEW`, so the judgment rows stay visible.

| # | decision | author's reasoning |
|---|---|---|
| 1 | `duplicate` (protocol as written; no change-log entry needed) | The task was captured, not omitted. The contradiction is a product problem: the app needs a review step that resolves conflicting owners |
| 2 | deadline judged from the whole item | same reasoning as 1 |
| 3 | one line counts for both gold items | one line can carry two tasks |
| 4 | "ASAP" = invented deadline | the report should show it was invented |
| 5 | Claude's defaults | format matters; expected to be solved by a fixed output format in the app |
| 6 | Claude's defaults, noted as judgment calls | as above |
