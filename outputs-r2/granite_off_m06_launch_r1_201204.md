# granite_off_m06_launch_r1_201204

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

Elizabeth: Okay, I think everyone's here. Eric's joining late, he's stuck in traffic. Let's start anyway, we've got a lot to cover for the app launch on the 30th.
Akhash: Before we start, did anyone see the match last night?
Goutham: Don't. I'm still recovering.
Elizabeth: Ha, okay, after the meeting. So, three areas: marketing, the app store submission, and support. Marketing first. Darcy?
Darcy: So the launch video is about eighty percent done. I need final screenshots from the app to finish it. Once I have them, I can deliver the video by the 25th.
Elizabeth: Who can get Darcy the screenshots?
Muhil: That's me, I've got the latest build on my phone. I'll send them over by tomorrow evening.
Darcy: Perfect. Also, um, we need a press release. I've done one before, but I really don't have the bandwidth right now.
Elizabeth: Okay. Let's... let's come back to that.
Priya: On marketing, I was thinking we could do a launch event, like an actual in-person thing.
Akhash: With what budget?
Priya: Fair. Forget it, it was just an idea.
Elizabeth: Let's keep it online this time. Okay, app store submission. Goutham?
Goutham: So the iOS build is ready. Android has one crash on older phones that I'm still chasing. I'll fix the crash by Friday, and then I'll submit both builds on Monday.
Elizabeth: Monday's cutting it close. Apple review can take a few days.
Goutham: True. Okay, I'll submit iOS tomorrow, since it's ready, and Android on Monday after the fix.
Elizabeth: Better. Who's writing the store listing text? The description, keywords, all that.
Akhash: I can do it. By Wednesday?
Elizabeth: Wednesday works.
Eric: Hey, sorry, sorry, I'm here. Traffic was insane.
Elizabeth: No worries. We're on the store listing, Akhash has it. Eric, you were going to handle the privacy policy page, right?
Eric: Yeah, it's drafted. Legal needs to sign off, though. I'll send it to legal today.
Elizabeth: And it has to be live before the iOS submission, Apple checks the link.
Eric: Right, so I'll chase legal and get it published by tomorrow morning.
Elizabeth: Great. Support next. Priya?
Priya: So I've written about half of the help center articles. I'll finish the rest by the 27th. The bigger problem is that we need someone on the support inbox during launch week. I can't do it, I'm traveling from the 29th.
Muhil: I could do the first two days.
Elizabeth: Okay, Muhil covers the support inbox on the 30th and 31st. We still need someone for the rest of the week; I'll figure that out.
Akhash: Wait, going back to the store listing. I just checked my calendar and Wednesday doesn't work, I'm at the conference. Can I do Thursday instead?
Elizabeth: Hmm. iOS goes in tomorrow, so it needs a listing too.
Goutham: The iOS listing can be minimal for submission. We can update the text later without a new review.
Elizabeth: Okay, then Thursday is fine.
Darcy: And the press release?
Elizabeth: Right. Eric, you've written press releases before, haven't you?
Eric: A couple of times. I can draft it, but I'd want Darcy to review it.
Darcy: Happy to review.
Elizabeth: Then Eric drafts it by the 24th, and Darcy reviews it by the 26th.
Priya: One more thing. Someone should test the onboarding flow on a fresh install before launch. Last time we missed a broken sign-up screen.
Elizabeth: Yes, good point. Okay, I think that's everything. I'll send out the notes this afternoon. Thanks, everyone.

```

## Thinking
```
(none)
```

## Answer
owner | task | deadline
Muhil | send screenshots to Darcy | tomorrow evening
Darcy | deliver the launch video by the 25th | the 25th
Akhash | write the store listing text (description, keywords, etc.) | Wednesday
Akhash | update the store listing text after iOS submission | Thursday
Eric | send the privacy policy page to legal and get it published by tomorrow morning | tomorrow morning
Muhil | cover the support inbox on the 30th and 31st | the 30th and 31st
Eric | draft the press release and have Darcy review it | the 24th (draft) and the 26th (review)
Darcy | review the press release draft | the 26th
Priya | finish the help center articles by the 27th | the 27th
Priya | test the onboarding flow on a fresh install before launch | before the launch on the 30th
