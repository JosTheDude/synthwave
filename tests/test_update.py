import unittest

from synthwave.update import installed, outdated


class UpdateTest(unittest.TestCase):
    def test_homebrew_commit_from_cellar_path(self):
        found = installed("/opt/homebrew/Cellar/synthwave/0.1.0-a30dbc8/libexec")
        self.assertEqual(found, ("a30dbc8", ["brew", "upgrade", "synthwave"]))

    def test_only_app_changes_count(self):
        self.assertFalse(outdated([{"filename": "README.md"}, {"filename": "Formula/synthwave.rb"}]))
        self.assertTrue(outdated([{"filename": "synthwave/app.py"}]))
        self.assertFalse(outdated([]))


if __name__ == "__main__":
    unittest.main()
