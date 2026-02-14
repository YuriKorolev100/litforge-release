#!/usr/bin/env python3
"""Unit tests for LitForge security primitives.

Tests:
  - YAML alias rejection in extract_frontmatter
  - Frontmatter size cap (bounded read)
  - atomic_write_text blocks symlink targets
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Ensure tools/ is importable
TOOLS_DIR = Path(__file__).resolve().parent.parent / "tools"
sys.path.insert(0, str(TOOLS_DIR))

from lf_safe import atomic_write_text, read_text_limited, MAX_FRONTMATTER_BYTES


class TestYAMLAliasRejection(unittest.TestCase):
    """extract_frontmatter must reject YAML aliases/anchors."""

    def test_alias_returns_none(self):
        from lf_validate import extract_frontmatter

        content = (
            "---\n"
            "base: &base\n"
            "  key: value\n"
            "alias: *base\n"
            "---\n"
            "# Body\n"
        )
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)
        try:
            result = extract_frontmatter(path)
            self.assertIsNone(result)
        finally:
            path.unlink()

    def test_normal_yaml_works(self):
        from lf_validate import extract_frontmatter

        content = (
            "---\n"
            "key: value\n"
            "num: 42\n"
            "---\n"
            "# Body\n"
        )
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)
        try:
            result = extract_frontmatter(path)
            self.assertIsNotNone(result)
            self.assertEqual(result["key"], "value")
            self.assertEqual(result["num"], 42)
        finally:
            path.unlink()


class TestFrontmatterSizeCap(unittest.TestCase):
    """Frontmatter parser must refuse files larger than the size cap."""

    def test_oversized_file_returns_none(self):
        from lf_validate import extract_frontmatter

        # Create a file just over MAX_FRONTMATTER_BYTES with valid frontmatter
        # that would parse fine if size weren't capped
        padding = "x" * (MAX_FRONTMATTER_BYTES + 1024)
        content = f"---\nkey: value\npadding: \"{padding}\"\n---\n# Body\n"
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)
        try:
            result = extract_frontmatter(path)
            # The bounded read truncates, so the closing --- is never found
            self.assertIsNone(result)
        finally:
            path.unlink()


class TestAtomicWriteBlocksSymlink(unittest.TestCase):
    """atomic_write_text must refuse to write through symlinks."""

    def test_symlink_raises(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "real.txt"
            target.write_text("original", encoding="utf-8")
            link = Path(td) / "link.txt"
            link.symlink_to(target)

            with self.assertRaises(PermissionError):
                atomic_write_text(link, "evil content")

            # Verify original is untouched
            self.assertEqual(target.read_text(), "original")

    def test_normal_write_works(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "normal.txt"
            atomic_write_text(path, "hello")
            self.assertEqual(path.read_text(), "hello")


class TestReadTextLimited(unittest.TestCase):
    """read_text_limited must cap reads."""

    def test_large_file_returns_none(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            f.write("x" * 100)
            f.flush()
            path = Path(f.name)
        try:
            result = read_text_limited(path, max_bytes=50)
            self.assertIsNone(result)
        finally:
            path.unlink()

    def test_small_file_returns_content(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            f.write("hello")
            f.flush()
            path = Path(f.name)
        try:
            result = read_text_limited(path, max_bytes=1024)
            self.assertEqual(result, "hello")
        finally:
            path.unlink()


if __name__ == "__main__":
    unittest.main()
