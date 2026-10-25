# bonsai_off_m07_postmortem_r1_204340

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

Muhil: Okay, let's do the postmortem for Saturday's outage. I'll keep it blameless. Goutham, can you walk us through the timeline?
Goutham: Sure. At around 2:10 on Saturday, the payment service started timing out. The alert fired at 2:25, so fifteen minutes late. I got paged at 2:30 and we rolled back the config change at 3:05.
Priya: Why did the alert take fifteen minutes?
Goutham: The threshold was five percent errors over ten minutes. It should probably be shorter.
Muhil: Okay. Goutham, can you change the alert window to two minutes?
Goutham: Yes, I'll do that today.
Eric: The bigger issue is that the config change went out without review.
Darcy: That was me. I pushed it Friday evening because the partner asked for it. I didn't realise it touched the payment timeouts.
Muhil: Thanks, Darcy, and again, this isn't about blame. The process let that happen. We need a rule that config changes to payments get a second reviewer.
Eric: I can write that up as a proposal. Give me till next Wednesday.
Muhil: Great. Darcy, would you be okay helping with the partner request part of the proposal, since you know how that came in?
Darcy: Sure, I'll send Eric my notes by Monday.
Elizabeth: From the customer side, we had about three hundred failed payments. Support got forty tickets.
Muhil: Do we know which customers?
Elizabeth: I have the list. I'll email every affected customer an apology by tomorrow.
Akhash: Should we give them a discount code or something?
Elizabeth: Let's not promise anything until finance agrees.
Akhash: Fair. I'll ask finance about a goodwill credit and get back to you by Thursday.
Priya: The other thing is the failed payments themselves. Some of those customers may never retry.
Goutham: We can replay the failed payment requests from the logs. That's maybe a day of work.
Muhil: Do it, but carefully. Who's taking it?
Goutham: I'll do it, but not before the alert fix. Say Wednesday.
Priya: Actually, Goutham, you've got the alert and you're on call this week. I'll take the replay. Same deadline, Wednesday.
Goutham: Thanks, that helps.
Muhil: Okay. Anything else?
Eric: Can we talk about moving the whole payment service to the new cluster? It'd fix a lot of this.
Muhil: That's a quarter-sized project, not a postmortem item. Bring it to planning.
Eric: Okay, I'll put together a one-pager for planning, no rush.
Elizabeth: One more. The status page wasn't updated during the outage at all. Customers found out from Twitter.
Muhil: Yeah. Someone needs to own the status page during incidents. Let's figure that out at the next ops sync.
Akhash: We should also do a fire drill at some point, simulate an outage.
Muhil: Good idea, let's think about it. Okay, I'll write up the postmortem doc and share it by Friday. Thanks, all.

```

## Thinking
```
(none)
```

## Answer
Goutham | change the alert window to two minutes | today
Eric | write a proposal for a second reviewer rule | next Wednesday
Darcy | send Eric notes about the partner request | Monday
Elizabeth | email every affected customer an apology | tomorrow
Akhash | ask finance about a goodwill credit | Thursday
Goutham | replay failed payment requests from logs | Wednesday
Eric | put together a one-pager for planning | no rush
Muhil | write up the postmortem doc | Friday
UNASSIGNED | own the status page during incidents | next ops sync
UNASSIGNED | do a fire drill to simulate an outage | none
