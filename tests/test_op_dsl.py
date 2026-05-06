"""Tests for the operation DSL parser."""
import sys; sys.path.insert(0, "src")
from sage.compiler.op_dsl import parse_op_dsl


def test_noop():
    assert parse_op_dsl("NOOP", "") == []
    assert parse_op_dsl("  NOOP  ", "") == []
    assert parse_op_dsl("", "") == []


def test_set():
    text = "Latif has 5 coins."
    ops = parse_op_dsl("SET|Latif.coins|5|span=Latif has 5 coins", text)
    assert len(ops) == 1
    assert ops[0]["op"] == "SET"
    assert ops[0]["target"] == "Latif.coins"
    assert ops[0]["value"] == 5
    assert ops[0]["evidence"]["span"] == "Latif has 5 coins"
    assert text[ops[0]["evidence"]["start"]:ops[0]["evidence"]["end"]] == "Latif has 5 coins"


def test_add():
    text = "Latif gains three apples."
    ops = parse_op_dsl("ADD|Latif.apples|3|span=Latif gains three apples", text)
    assert len(ops) == 1
    assert ops[0]["op"] == "ADD"


def test_sub():
    text = "Latif spends 2 coins."
    ops = parse_op_dsl("SUB|Latif.coins|2|span=Latif spends 2 coins", text)
    assert len(ops) == 1
    assert ops[0]["op"] == "SUB"
    assert ops[0]["value"] == 2


def test_transfer():
    text = "Arno gives 3 coins to Latif."
    ops = parse_op_dsl("TRANSFER|Arno.coins|Latif.coins|3|span=Arno gives 3 coins to Latif", text)
    assert len(ops) == 1
    assert ops[0]["op"] == "TRANSFER"
    assert ops[0]["from"] == "Arno.coins"
    assert ops[0]["to"] == "Latif.coins"


def test_query():
    text = "Question: How many coins does Latif have?"
    ops = parse_op_dsl("QUERY|Latif.coins|span=Question: How many coins does Latif have?", text)
    assert len(ops) == 1
    assert ops[0]["op"] == "QUERY"
    assert ops[0]["target"] == "Latif.coins"


def test_multiline():
    text = "Latif has 5 coins. Latif spends 2 coins."
    dsl = "SET|Latif.coins|5|span=Latif has 5 coins\nSUB|Latif.coins|2|span=Latif spends 2 coins"
    ops = parse_op_dsl(dsl, text)
    assert len(ops) == 2
    assert ops[0]["op"] == "SET"
    assert ops[1]["op"] == "SUB"


def test_leading_trailing_whitespace():
    text = "Latif gains three coins."
    ops = parse_op_dsl("  ADD|Latif.coins|3|span=Latif gains three coins  ", text)
    assert len(ops) == 1
    assert ops[0]["op"] == "ADD"


def test_invalid_line():
    text = "some text"
    ops = parse_op_dsl("INVALID|something", text)
    assert len(ops) == 0


def test_missing_span():
    ops = parse_op_dsl("SET|Latif.coins|5", "")
    assert len(ops) == 0


def test_span_not_found():
    ops = parse_op_dsl("SET|Latif.coins|5|span=not in text", "different text")
    assert len(ops) == 0


if __name__ == "__main__":
    test_noop()
    test_set()
    test_add()
    test_sub()
    test_transfer()
    test_query()
    test_multiline()
    test_leading_trailing_whitespace()
    test_invalid_line()
    test_missing_span()
    test_span_not_found()
    print("All DSL tests passed!")
