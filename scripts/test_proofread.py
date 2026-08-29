#!/usr/bin/env python3
"""Tests for proofread.py. Run: python3 -m unittest scripts/test_proofread.py -v"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import proofread  # noqa: E402


def issues(text):
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(text)
    return [(name, msg) for _, name, msg, _ in proofread.check_file(Path(f.name))]


def names(text):
    return {n for n, _ in issues(text)}


class EachRuleFires(unittest.TestCase):
    def test_double_space(self):
        self.assertIn("double-space", names("The cat sat  on the mat today."))

    def test_space_before_punct(self):
        self.assertIn("space-before-punct", names("The cat sat on the mat , today."))

    def test_no_space_after_punct(self):
        self.assertIn("no-space-after-punct", names("The cat sat,then it slept on the mat."))

    def test_no_space_after_period(self):
        self.assertIn("no-space-after-period", names("The cat sat.Then it slept on the mat."))

    def test_double_punct(self):
        self.assertIn("double-punct", names("The cat sat on the mat,, then slept."))

    def test_lowercase_i(self):
        self.assertIn("lowercase-i", names("Yesterday i sat on the mat all day."))

    def test_lowercase_sentence(self):
        self.assertIn("lowercase-sentence", names("The cat sat. then it slept on the mat."))

    def test_repeated_word(self):
        self.assertIn("repeated-word", names("The cat sat on the the mat all day."))

    def test_a_vs_an(self):
        self.assertIn("a-vs-an", names("The cat ate a apple on the mat today."))
        self.assertIn("a-vs-an", names("The cat ate an banana on the mat today."))

    def test_unbalanced_quotes(self):
        self.assertIn("unbalanced-quotes", names('"The cat sat, said the owner on the mat.'))

    def test_unbalanced_parens(self):
        self.assertIn("unbalanced-parens", names("The cat (a ginger one sat on the mat today."))

    def test_trailing_space(self):
        self.assertIn("trailing-space", names("The cat sat on the mat today.   "))

    def test_spelling(self):
        self.assertIn(("spelling", "'definately' → 'definitely'"), issues("The cat definately sat on the mat."))
        self.assertIn(("spelling", "'dont' → 'don't'"), issues("Cats dont sit on mats very often."))

    def test_confusables(self):
        msgs = {m for _, m in issues("Supporters replied that your going to accept it.")}
        self.assertTrue(any("you're" in m for m in msgs))
        msgs = {m for _, m in issues("Voters said its a good sign for the town.")}
        self.assertTrue(any("it's" in m for m in msgs))
        msgs = {m for _, m in issues("The cat should of stayed on the mat all day.")}
        self.assertTrue(any("should have" in m for m in msgs))

    def test_missing_end_punct(self):
        self.assertIn("missing-end-punct", names("The cat sat on the mat and then it slept for hours"))


class CorrectProseIsNotFlagged(unittest.TestCase):
    CLEAN = [
        'In a decision that surprised everyone, the council voted 7–2 on Saturday night.',
        '"We ran the numbers," said Council President Dana Okafor, holding up a spreadsheet.',
        'The developer, identified only as "R.," has since been given commit rights.',
        '"I\'ve read the pamphlet," R. said. "I\'ve read it twice."',
        'The loaf sold out by 8:15 a.m. on Saturday, according to Dr. Berg.',
        'Wait... is that a spoon? Yes! It is a spoon (a small one).',
        'Run `python3 scripts/proofread.py` and see [CONTRIBUTING.md](CONTRIBUTING.md) for details.',
        '**On the spoon.** Five millilitres is too many. — *A Reader Who Takes Their Tea Seriously*',
        '### NEW KEYBOARD SHIPS WITH A DEDICATED "UNDO THAT, PLEASE" KEY',
        '*By Priya Raman, Civic Affairs Desk*',
        'Its orbit takes 14 hours; the moon has its own fan account.',
        'She spent an hour at a university with a European friend and an heir.',
        'It\'s a rock, but it\'s a nice one, and an honest one at that.',
        'A survey of 12 million messages found that 60 percent said "fix."',
        '| Time | Sky | Temp |',
        '- a bullet point with a lowercase start is fine',
        '> A blockquote that ends properly with a full stop.',
    ]

    def test_each_clean_line(self):
        for line in self.CLEAN:
            with self.subTest(line=line):
                self.assertEqual(names(line), set(), f"false positive on: {line}")

    def test_code_fence_is_skipped(self):
        text = "Fine sentence here.\n```\ni  sat , here.. wierd\n```\nAnother fine sentence."
        self.assertEqual(names(text), set())

    def test_repo_readme_is_clean(self):
        self.assertEqual(proofread.check_file(proofread.REPO / "README.md"), [])

    def test_bad_draft_is_caught(self):
        probs = proofread.check_file(proofread.REPO / "newsroom" / "example-bad-draft.md.txt")
        found = {n for _, n, _, _ in probs}
        for expected in ["space-before-punct", "no-space-after-period", "repeated-word",
                         "lowercase-i", "a-vs-an", "spelling", "confusable", "missing-end-punct"]:
            self.assertIn(expected, found)


class ExitCodes(unittest.TestCase):
    def test_clean_returns_zero(self):
        self.assertEqual(proofread.main([str(proofread.REPO / "README.md")]), 0)

    def test_dirty_returns_one(self):
        self.assertEqual(proofread.main([str(proofread.REPO / "newsroom" / "example-bad-draft.md.txt")]), 1)

    def test_missing_file_returns_one(self):
        self.assertEqual(proofread.main(["does-not-exist.md"]), 1)


if __name__ == "__main__":
    unittest.main()
