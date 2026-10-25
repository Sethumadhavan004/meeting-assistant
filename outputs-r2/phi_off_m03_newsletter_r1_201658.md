# phi_off_m03_newsletter_r1_201658

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

Muhil: Can we talk about the newsletter? Open rates dropped again.
Eric: Maybe we should switch email providers.
Priya: Honestly, that's a big move. Let's not decide that today.
Muhil: Agreed, park it. Eric, can you pull the open-rate numbers for the last three months?
Eric: I can do that by Friday.
Muhil: Priya, could you rewrite the subject lines before next week's issue goes out?
Priya: I can't this week, I'm on the audit.
Muhil: Okay, I'll do the subject lines myself then.
Eric: Someone should also clean up the unsubscribed contacts at some point.

```

## Thinking
```
(none)
```

## Answer
Eric | pull open-rate numbers for the last three months | Friday
Priya | rewrite the subject lines for the next week's newsletter | NONE
Muhil | clean up the unsubscribed contacts | UNASSIGNED
