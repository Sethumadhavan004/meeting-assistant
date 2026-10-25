# phi_off_m02_offsite_r1_201648

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

Akhash: Quick one. We need the venue booked for the offsite before the end of the month.
Darcy: I can draft the agenda by Thursday.
Akhash: Great. Goutham, can you get quotes from the two caterers?
Goutham: Sure, I'll have them by Monday.
Elizabeth: Goutham's out next week though, isn't he?
Goutham: Oh, right. Elizabeth, could you take the caterer quotes instead?
Elizabeth: Fine, same deadline.

```

## Thinking
```
(none)
```

## Answer
Elizabeth | get quotes from the two caterers | Monday
Darcy | draft the agenda | Thursday
Akhash | book the venue for the offsite | end of the month
