# granite_off_m04_workshop_r1_201112

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

Elizabeth: For the client workshop, Darcy and I talked yesterday. She'll send the invites tomorrow.
Akhash: Who's printing the handouts?
Elizabeth: Darcy again. She said she can print them the day before the workshop.
Goutham: The workshop's on the 14th, right?
Elizabeth: Yes, the 14th.
Akhash: I'll book the meeting room today. And we need someone to follow up with the client about dietary needs.

```

## Thinking
```
(none)
```

## Answer
owner | task | deadline
Darcy | send the invites for the client workshop | tomorrow
Darcy | print the handouts the day before the workshop | day before the 14th
Akhash | book the meeting room today | today
Akhash | follow up with the client about dietary needs | before the workshop on the 14th
