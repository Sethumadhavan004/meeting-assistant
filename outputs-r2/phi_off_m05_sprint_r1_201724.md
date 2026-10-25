# phi_off_m05_sprint_r1_201724

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

Priya: Okay, let's get through sprint planning, we've got thirty minutes. First, the login bug. Customers are still getting logged out on mobile.
Goutham: That's mine. I think it's the token refresh. I'll have a fix up for review by Wednesday.
Priya: Good. Muhil, can you review it when it's up?
Muhil: Yeah, I'll review it the same day he posts it.
Priya: Next, the export feature. Eric, where are we?
Eric: Backend is done. The CSV formatting still needs work. I'll finish it by Friday.
Priya: Friday this week?
Eric: Sorry, no, next Friday. This week is too tight with the release.
Priya: Okay, next Friday. Then we need the docs page for export updated before it ships.
Akhash: I can take a look at the docs, but no promises.
Priya: Let's leave the docs open for now, then. Next, the release. Akhash, you're release manager this time.
Akhash: Right. I'll cut the release branch Thursday morning and send the release notes to the team by Thursday evening.
Muhil: Can we also talk about moving to the new CI provider?
Priya: Not this sprint. Let's put it on the next retro agenda.
Muhil: Fine, I'll add it to the retro agenda.
Priya: Last thing, the customer interviews. Darcy asked for two engineers to sit in.
Goutham: I'll join the Tuesday one.
Eric: I can't do Tuesday.
Priya: Okay, I'll sit in on the second one myself, it's on the 22nd.
Priya: That's it. Thanks, everyone.

```

## Thinking
```
(none)
```

## Answer
Goutham | fix the login bug | Wednesday
Muhil | review the login bug fix | Wednesday
Eric | finish CSV formatting for export feature | Next Friday
Akhash | update the docs page for export | Before shipping
Akhash | manage the release | Thursday
Akhash | send release notes to the team | Thursday evening
Priya | sit in on the second customer interview | Tuesday 22nd
