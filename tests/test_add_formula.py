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
    def test_strips_article_and_period(self) -> None:
        self.assertEqual(af.clean_desc("A neat tool."), "neat tool")

    def test_leaves_body_untouched(self) -> None:
        self.assertEqual(af.clean_desc("generic CLI"), "generic CLI")


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


if __name__ == "__main__":
    unittest.main()
