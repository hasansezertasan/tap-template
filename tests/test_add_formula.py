"""Tests for ``scripts/add_formula.py`` (stdlib ``unittest``, no network).

Only the pure helpers are exercised — the network-bound resolution
(``pip --dry-run``, PyPI fetches) is left to a real scaffold run. Run with
``python -m unittest discover -s tests`` from the repo root.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import add_formula as af  # noqa: E402


class NameTest(unittest.TestCase):
    def test_normalize(self) -> None:
        self.assertEqual(af.normalize("Markdown_It.Py"), "markdown-it-py")

    def test_class_name(self) -> None:
        self.assertEqual(af.class_name("markdown-it-py"), "MarkdownItPy")


class LicenseTest(unittest.TestCase):
    def test_expression_wins(self) -> None:
        self.assertEqual(
            af.spdx_license({"license_expression": "Apache-2.0", "license": "ignored"}),
            "Apache-2.0",
        )

    def test_osi_classifier_mapping(self) -> None:
        info = {"classifiers": ["License :: OSI Approved :: MIT License"]}
        self.assertEqual(af.spdx_license(info), "MIT")

    def test_short_raw_license(self) -> None:
        self.assertEqual(af.spdx_license({"license": "MIT"}), "MIT")

    def test_todo_fallback(self) -> None:
        self.assertEqual(af.spdx_license({}), "TODO-set-SPDX-license")

    def test_long_raw_license_is_not_used(self) -> None:
        info = {"license": "x" * 80}
        self.assertEqual(af.spdx_license(info), "TODO-set-SPDX-license")


class DescTest(unittest.TestCase):
    """`brew audit --strict` wants no leading article and a capital first letter.

    Both rules live in Homebrew's ``rubocops/shared/desc_helper.rb``; the article
    check there is case-insensitive, so this helper's must be too.
    """

    def test_strips_article_and_period(self) -> None:
        self.assertEqual(af.clean_desc("A neat tool."), "Neat tool")

    def test_strips_lowercase_article(self) -> None:
        self.assertEqual(af.clean_desc("a tool for things."), "Tool for things")
        self.assertEqual(af.clean_desc("the widget"), "Widget")

    def test_capitalizes_a_lowercase_summary(self) -> None:
        self.assertEqual(af.clean_desc("generic CLI"), "Generic CLI")

    def test_leaves_body_untouched(self) -> None:
        self.assertEqual(af.clean_desc("Android build helper"), "Android build helper")
        self.assertEqual(af.clean_desc(""), "")


class ClassNameTest(unittest.TestCase):
    def test_derives_from_hyphenated_name(self) -> None:
        self.assertEqual(af.class_name("markdown-it-py"), "MarkdownItPy")

    def test_rejects_a_leading_digit(self) -> None:
        """`class 2to3 < Formula` is a Ruby syntax error, so refuse to write it."""
        with self.assertRaises(ValueError) as caught:
            af.class_name("2to3")
        self.assertIn("2to3", str(caught.exception))


class PythonSeriesTest(unittest.TestCase):
    def test_min_python_lower_bound(self) -> None:
        self.assertEqual(af.min_python(">=3.10"), "3.10")

    def test_min_python_with_upper_bound(self) -> None:
        self.assertEqual(af.min_python(">=3.10,<3.14"), "3.10")

    def test_min_python_none(self) -> None:
        self.assertIsNone(af.min_python(None))

    def test_max_python_strict_upper(self) -> None:
        self.assertEqual(af.max_python("<3.14"), "3.13")

    def test_max_python_inclusive_upper(self) -> None:
        self.assertEqual(af.max_python("<=3.12"), "3.12")

    def test_max_python_major_cap_ignored(self) -> None:
        self.assertIsNone(af.max_python("<4"))

    def test_series_tuple(self) -> None:
        self.assertEqual(af._series_tuple("3.14"), (3, 14))
        self.assertLess(af._series_tuple("3.13"), af._series_tuple("3.14"))



class RubyEscapeTest(unittest.TestCase):
    def test_escapes_quote_and_backslash(self) -> None:
        self.assertEqual(af._rb_str('say "hi"'), 'say \\"hi\\"')
        self.assertEqual(af._rb_str("back\\slash"), "back\\\\slash")

    def test_escapes_interpolation_marker(self) -> None:
        """`#{...}` in a double-quoted Ruby string runs code when the formula loads."""
        self.assertEqual(af._rb_str("x #{system('rm -rf /')}"),
                         "x \\#{system('rm -rf /')}")

    def test_hostile_pypi_metadata_stays_inside_the_literal(self) -> None:
        info = {"summary": 'A "quoted" #{system("boom")} tool', "project_urls": {},
                "home_page": "", "license": "MIT", "classifiers": []}
        rendered = af.render("foo", info, "https://e/x.tar.gz", "abc",
                             "python@3.14", [("bar", "https://e/b.tar.gz", "def")], [])
        desc = next(ln for ln in rendered.splitlines() if ln.startswith("  desc "))
        # Every quote is backslash-escaped and the interpolation marker is inert,
        # so the whole summary stays inside one Ruby string literal.
        self.assertEqual(
            desc,
            '  desc "\\"quoted\\" \\#{system(\\"boom\\")} tool"',
        )


class TestCommandTest(unittest.TestCase):
    def test_default_is_the_documented_guess(self) -> None:
        self.assertEqual(af.default_test_command("foo"), "#{bin}/foo --version")

    def test_override_is_used_verbatim(self) -> None:
        info = {"summary": "Tool", "project_urls": {}, "home_page": "",
                "license": "MIT", "classifiers": []}
        rendered = af.render("foo", info, "https://e/x.tar.gz", "abc", "python@3.14",
                             [], [], "#{bin}/foo version")
        self.assertIn('shell_output("#{bin}/foo version")', rendered)
        self.assertNotIn("--version", rendered)


if __name__ == "__main__":
    unittest.main()
