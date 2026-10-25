"""Unit tests: one small, hand-written case per rule in meeting_assistant/core.py."""
import pytest

from meeting_assistant import config
from meeting_assistant.core import Item, missed_needs, parse, reconcile


def owners(items):
    return [(it.owner, it.task) for it in items]


# ---------------- parse ----------------
def test_parse_reads_three_field_lines_and_strips_bullets():
    items, rejected = parse("- Arjun | write the copy | Wednesday\n2. Meena | send logos | today")
    assert owners(items) == [("Arjun", "write the copy"), ("Meena", "send logos")]
    assert rejected == []


def test_parse_skips_header_line():  # Granite printed it in 6/10 round-2 runs
    items, _ = parse("owner | task | deadline\nArjun | write the copy | Wednesday")
    assert owners(items) == [("Arjun", "write the copy")]


def test_parse_drops_lines_copied_from_the_prompt_example():  # seen in 2/30 round-2 runs
    items, _ = parse("UNASSIGNED | book a room for the review | NONE\nArjun | write the copy | Wednesday")
    assert owners(items) == [("Arjun", "write the copy")]


def test_parse_rejects_lines_without_three_fields():
    items, rejected = parse("Muhil | write up the postmortem doc by Friday\nHere are the items:")
    assert items == []
    assert len(rejected) == 2


# ---------------- reconcile: owner rule ----------------
def test_we_need_given_to_the_speaker_becomes_unassigned():
    t = "Akhash: We need the venue booked for the offsite.\nDarcy: I'll draft the agenda."
    out = reconcile([Item("Akhash", "book the venue for the offsite", "end of month")], t)
    assert out[0].owner == "UNASSIGNED"
    assert "Akhash raised this" in out[0].flags[0]


def test_owner_kept_when_the_speaker_commits_later():
    t = "Muhil: We need the retro agenda updated.\nPriya: Not this sprint.\nMuhil: Fine, I'll add it to the retro agenda."
    out = reconcile([Item("Muhil", "add it to the retro agenda", "NONE")], t)
    assert out[0].owner == "Muhil"


def test_owner_kept_when_someone_else_said_it():
    t = "Priya: We need the release notes sent.\nAkhash: I'll send the release notes Thursday."
    out = reconcile([Item("Akhash", "send the release notes", "Thursday")], t)
    assert out[0].owner == "Akhash"


# ---------------- reconcile: duplicates ----------------
def test_exact_repeat_with_same_owner_is_dropped():
    out = reconcile([Item("Muhil", "write up the postmortem doc", "Friday"),
                     Item("Muhil", "write up the postmortem doc", "Friday")], "")
    assert len(out) == 1


def test_named_owner_replaces_unassigned_copy():
    out = reconcile([Item("UNASSIGNED", "email client to confirm demo time", "NONE"),
                     Item("Arjun", "email client to confirm demo time", "tomorrow morning")], "")
    assert owners(out) == [("Arjun", "email client to confirm demo time")]
    assert out[0].deadline == "tomorrow morning"


def test_dependent_tasks_are_flagged_never_merged():  # the first draft deleted Darcy's review
    out = reconcile([Item("Eric", "draft press release", "24th"),
                     Item("Darcy", "review press release", "26th")], "")
    assert owners(out) == [("Eric", "draft press release"), ("Darcy", "review press release")]
    assert all("similar task" in it.flags[0] for it in out)


def test_reassigned_task_listed_twice_is_flagged_on_both():
    out = reconcile([Item("Goutham", "get quotes from the two caterers", "Monday"),
                     Item("Elizabeth", "take the caterer quotes", "Monday")], "")
    assert len(out) == 2
    assert out[0].flags == ["similar task for Elizabeth: check"]


# ---------------- missed "we need" ----------------
def test_missed_need_is_suggested():  # the author's mic test: the model skipped this line
    t = "Akhash: I will send that budget to Priya by Friday.\nPriya: We need someone to book the room."
    got = missed_needs([Item("Akhash", "send that budget to Priya", "Friday")], t)
    assert got == [("Priya", "We need someone to book the room.")]


def test_covered_need_is_not_suggested():
    t = "Priya: We need someone to book the room."
    assert missed_needs([Item("UNASSIGNED", "book the room", "NONE")], t) == []


@pytest.mark.parametrize("line", ["Eric: Maybe we should switch email providers.",
                                  "Akhash: Should we bring in an external recruiter?",
                                  "Elizabeth: And it has to be live before the iOS submission.",
                                  "Akhash: I'll book the room, we need it today."])
def test_hedges_questions_conditions_and_commitments_are_not_suggested(line):
    assert missed_needs([], line) == []


# ---------------- config ----------------
def test_unreachable_server_gives_a_fix_it_message():
    cfg = config.load()
    cfg["backends"]["bonsai"]["url"] = "http://127.0.0.1:9"  # nothing listens on port 9
    with pytest.raises(config.BackendError, match="start_bonsai"):
        config.check("bonsai", cfg)
