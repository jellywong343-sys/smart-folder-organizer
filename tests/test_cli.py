import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from smart_folder_organizer.cli import apply_plan, build_plan, undo

class OrganizerTests(unittest.TestCase):
    def test_category_plan_and_undo(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "photo.jpg").write_bytes(b"image")
            (root / "notes.txt").write_text("notes", encoding="utf-8")
            moves = build_plan(root, "category")
            self.assertEqual({m.target.parent.name for m in moves}, {"images", "documents"})
            manifest = root / ".organizer-manifest.json"
            apply_plan(moves, manifest)
            self.assertTrue((root / "images" / "photo.jpg").exists())
            self.assertEqual(undo(manifest), 2)
            self.assertTrue((root / "photo.jpg").exists())

    def test_preview_does_not_move(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "data.csv"
            source.write_text("a,b", encoding="utf-8")
            build_plan(root, "extension")
            self.assertTrue(source.exists())

if __name__ == "__main__":
    unittest.main()
