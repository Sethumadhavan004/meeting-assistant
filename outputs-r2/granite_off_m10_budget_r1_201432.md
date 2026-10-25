# granite_off_m10_budget_r1_201432

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

Priya: Let's do the quarterly budget check. We're over on travel and under on tools.
Akhash: Travel is mostly the offsite. That was a one-off.
Priya: Fine. Darcy, you were renegotiating the design-software contract. Where is it?
Darcy: Halfway. But I'm on leave from Monday for two weeks.
Priya: Muhil, can you take the contract over from Darcy while she's away?
Muhil: Sure. Darcy, send me the vendor emails before you go and I'll pick it up.
Darcy: I'll forward them to you on Friday.
Priya: Then the forecast for next quarter. Elizabeth, can you have it ready by the 5th?
Elizabeth: The 5th is the board pack deadline, so I'd need it earlier. Let's say the 3rd.
Priya: Even better if it's the 2nd, the CFO wants a day to read it.
Elizabeth: Okay, the 2nd.
Akhash: Should we look at moving everyone to the cheaper laptop model?
Priya: Not now. Let's park that until the hardware refresh in spring.
Priya: Akhash, could you also cancel the unused seat licences?
Akhash: I'm swamped this week, sorry. Can someone else take it?
Muhil: I'll do it. I'll cancel the seats and email the vendor a confirmation by Thursday.
Priya: Great. Last thing: the spreadsheet with the actuals hasn't been updated since August. Somebody needs to update it before the finance review.
Akhash: Yeah, it's a mess.
Priya: Okay. Thanks, all.

```

## Thinking
```
(none)
```

## Answer
Muhil | take over the design-software contract from Darcy while she's on leave | Friday
Darcy | send the vendor emails before going on leave | Friday
Elizabeth | have the forecast for next quarter ready by the 2nd | 2nd
Muhil | cancel the unused seat licences and email the vendor a confirmation by Thursday | Thursday
Akhash | update the spreadsheet with the actuals before the finance review | NONE
