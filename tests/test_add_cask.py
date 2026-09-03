"""Tests for ``scripts/add_cask.py`` (stdlib ``unittest``, no network).

Only the pure helpers are exercised — the GitHub API calls and the asset
download (sha256) are left to a real scaffold run. Run with
``python -m unittest discover -s tests`` from the repo root.
"""

from __future__ import annotations

import io
import sys
import unittest
from contextlib import redirect_stderr
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import add_cask as ac  # noqa: E402


class NameTest(unittest.TestCase):
    def test_normalize(self) -> None:
        self.assertEqual(ac.normalize("My_App.Name"), "my-app-name")


class ParseRepoTest(unittest.TestCase):
    def test_owner_repo(self) -> None:
        self.assertEqual(ac.parse_repo("o/r"), ("o", "r"))

    def test_github_url(self) -> None:
        self.assertEqual(ac.parse_repo("https://github.com/o/r"), ("o", "r"))

    def test_strips_git_suffix(self) -> None:
        self.assertEqual(ac.parse_repo("https://github.com/o/r.git"), ("o", "r"))

    def test_garbage_exits(self) -> None:
        with self.assertRaises(SystemExit):
            ac.parse_repo("not-a-repo")


class DescTest(unittest.TestCase):
    def test_capitalizes_and_strips(self) -> None:
        self.assertEqual(ac.clean_desc("a neat app."), "A neat app")

    def test_empty(self) -> None:
        self.assertEqual(ac.clean_desc(""), "")


class SelectAssetTest(unittest.TestCase):
    def test_lone_dmg(self) -> None:
        dmg = {"name": "App.dmg"}
        self.assertIs(ac.select_asset([dmg, {"name": "notes.txt"}], None), dmg)

    def test_explicit_artifact(self) -> None:
        a, b = {"name": "App-arm64.dmg"}, {"name": "App-x64.dmg"}
        self.assertIs(ac.select_asset([a, b], "App-x64.dmg"), b)

    def test_preference_dmg_before_zip(self) -> None:
        dmg, zipp = {"name": "App.dmg"}, {"name": "App.zip"}
        self.assertIs(ac.select_asset([zipp, dmg], None), dmg)

    def test_multiple_same_suffix_exits(self) -> None:
        with self.assertRaises(SystemExit):
            ac.select_asset([{"name": "a.dmg"}, {"name": "b.dmg"}], None)

    def test_no_assets_exits(self) -> None:
        with self.assertRaises(SystemExit):
            ac.select_asset([], None)


class TemplatizeTest(unittest.TestCase):
    def test_replaces_version(self) -> None:
        self.assertEqual(ac.templatize("App-1.2.3.dmg", "1.2.3"), "App-#{version}.dmg")

    def test_warns_when_absent(self) -> None:
        buf = io.StringIO()
        with redirect_stderr(buf):
            self.assertEqual(ac.templatize("static.dmg", "1.2.3"), "static.dmg")
        self.assertIn("won't auto-update", buf.getvalue())


class RbStrTest(unittest.TestCase):
    def test_escapes_backslash_and_quote(self) -> None:
        self.assertEqual(ac._rb_str('a"b\\c'), 'a\\"b\\\\c')


class StanzaTest(unittest.TestCase):
    def test_pkg_stanza_no_hint(self) -> None:
        line, hint = ac.stanza_for("x.pkg", "x.pkg", "tok")
        self.assertEqual(line, '  pkg "x.pkg"')
        self.assertEqual(hint, "")

    def test_dmg_stanza_guesses_app_with_hint(self) -> None:
        line, hint = ac.stanza_for("x.dmg", "x.dmg", "tok")
        self.assertEqual(line, '  app "tok.app"')
        self.assertTrue(hint)


if __name__ == "__main__":
    unittest.main()
