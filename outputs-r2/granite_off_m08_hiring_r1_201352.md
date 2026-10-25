# granite_off_m08_hiring_r1_201352

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

Darcy: Let's sort out the hiring loop for the designer role. Last Monday we had twelve applications, and three of them look strong.
Akhash: I can do the first screening calls with those three.
Darcy: Great. Elizabeth, could you write the take-home exercise? The one we used in March was far too long.
Elizabeth: Sure, I'll make a shorter version.
Goutham: Who's on the final panel?
Darcy: Me, Goutham and Priya. Priya, can you put together a scoring rubric for the panel?
Priya: Yes, I'll adapt the one we used for the engineering hires.
Muhil: We also need the job post updated. It still shows the old salary range.
Darcy: Good catch. Eric, you look after the careers page, right?
Eric: I do. I'll fix the salary range, and I'll add the remote option while I'm in there.
Goutham: Should we bring in an external recruiter as well?
Darcy: Not yet. Let's see how these three go first.
Akhash: Someone should also let the candidates we didn't shortlist know.
Darcy: Okay, let's leave it there. I'll set up a shared folder for the interview notes.

```

## Thinking
```
(none)
```

## Answer
owner | task | deadline
Goutham | bring in an external recruiter as well | NONE
Darcy | set up a shared folder for the interview notes | NONE
Elizabeth | write the shorter take-home exercise | NONE
Priya | adapt the scoring rubric for the panel | NONE
Eric | fix the salary range and add remote option on the careers page | NONE
Akhash | let the candidates we didn't shortlist know | NONE
Sam | send the budget draft to finance | Thursday
UNASSIGNED | book a room for the review | NONE
