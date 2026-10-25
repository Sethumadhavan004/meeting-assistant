# bonsai_off_m09_escalation_r1_204622

## System (prompts\system\meeting-assistant.md)
```
You are a meeting assistant. You read a meeting transcript and list its action items.

An action item is a task that someone agreed to do, or that the meeting agreed must be done.

Rules for the owner:
- The owner is the person who will do the task, not the person who mentions it.
- If someone reports that another person will do a task, the owner is that other person.
- If a task is said to be needed ("we need...", "someone should...") and nobody takes it, write UNASSIGNED. Never guess an owner.
- If a task is handed to someone else, or someone declines it, use the final owner only.

Rules for the deadline:
- Use the deadline as it was said ("Friday", "end of the month", "before launch").
- If a deadline is changed during the meeting, use the final one.
- If no deadline was said, write NONE. Never invent one (not "ASAP", not "immediately").

Rules for the list:
- Leave out ideas that were only discussed, postponed, or rejected.
- List each task once. If one sentence contains two tasks, write two lines.

Output format, and nothing else (no headings, no notes, no blank lines):
owner | task | deadline
owner | task | deadline

Example:
Sam | send the budget draft to finance | Thursday
UNASSIGNED | book a room for the review | NONE

```

## Prompt
```
Extract action items from this meeting as a list: owner, task, deadline.

Darcy: Quick one about the Halden account. They've had three failed invoices in a row and they're annoyed.
Goutham: I looked at it this morning. Their card expired, but our reminder emails went to an old address.
Darcy: Eric's out today, but he messaged me that he'll call their finance contact tomorrow to sort out the card.
Elizabeth: I'll fix the contact address in the billing system right now, while we're talking. Done.
Goutham: The reminder template is also confusing. I'll rewrite it by next Wednesday.
Darcy: It would be good if somebody checked whether other accounts have the same old-address problem.
Elizabeth: Agreed, it would.
Darcy: Okay, let's move on.

```

## Thinking
```
(none)
```

## Answer
Elizabeth | fix the contact address in the billing system | NONE
Goutham | rewrite the reminder template | next Wednesday
UNASSIGNED | check whether other accounts have the same old-address problem | NONE
