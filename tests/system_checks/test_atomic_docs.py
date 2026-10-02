import tempfile
from pathlib import Path

from django.test import SimpleTestCase, override_settings

from ambient_toolbox.system_checks.atomic_docs import check_atomic_docs


class CheckAtomicDocsTestCase(SimpleTestCase):
    def test_all_docs_linked_no_warnings(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            docs_dir = base_dir / "docs"
            docs_dir.mkdir()
            (docs_dir / "guide.md").write_text("# Guide", encoding="utf-8")
            (docs_dir / "api.md").write_text("# API", encoding="utf-8")

            readme = base_dir / "README.md"
            readme.write_text(
                "# Project\n[Guide](docs/guide.md)\n[API](docs/api.md)\n",
                encoding="utf-8",
            )

            with override_settings(ATOMIC_DOCS_BASE_DIR=base_dir):
                result = check_atomic_docs()

            self.assertEqual(result, [])

    def test_base_dir_defaults_to_settings_base_dir(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            docs_dir = base_dir / "docs"
            docs_dir.mkdir()
            (docs_dir / "guide.md").write_text("# Guide", encoding="utf-8")

            readme = base_dir / "README.md"
            readme.write_text("# Project\n[Guide](docs/guide.md)\n", encoding="utf-8")

            with override_settings(BASE_DIR=base_dir):
                result = check_atomic_docs()

            self.assertEqual(result, [])

    def test_unlinked_file_emits_warning(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            docs_dir = base_dir / "docs"
            docs_dir.mkdir()
            (docs_dir / "guide.md").write_text("# Guide", encoding="utf-8")
            (docs_dir / "orphan.md").write_text("# Orphan", encoding="utf-8")

            readme = base_dir / "README.md"
            readme.write_text("# Project\n[Guide](docs/guide.md)\n", encoding="utf-8")

            with override_settings(ATOMIC_DOCS_BASE_DIR=base_dir):
                result = check_atomic_docs()

            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].id, "ambient_toolbox.W004")
            self.assertIn("docs/orphan.md", result[0].msg)

    def test_docs_dir_does_not_exist_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            # No docs dir created

            with override_settings(ATOMIC_DOCS_BASE_DIR=base_dir):
                result = check_atomic_docs()

            self.assertEqual(result, [])

    def test_readme_does_not_exist_returns_warning(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            docs_dir = base_dir / "docs"
            docs_dir.mkdir()
            (docs_dir / "guide.md").write_text("# Guide", encoding="utf-8")
            # No README created

            with override_settings(ATOMIC_DOCS_BASE_DIR=base_dir):
                result = check_atomic_docs()

            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].id, "ambient_toolbox.W004")
            self.assertIn("README", result[0].msg)

    def test_link_with_dot_slash_prefix_is_matched(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            docs_dir = base_dir / "docs"
            docs_dir.mkdir()
            (docs_dir / "guide.md").write_text("# Guide", encoding="utf-8")

            readme = base_dir / "README.md"
            readme.write_text("# Project\n[Guide](./docs/guide.md)\n", encoding="utf-8")

            with override_settings(ATOMIC_DOCS_BASE_DIR=base_dir):
                result = check_atomic_docs()

            self.assertEqual(result, [])

    def test_link_with_anchor_suffix_is_matched(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            docs_dir = base_dir / "docs"
            docs_dir.mkdir()
            (docs_dir / "guide.md").write_text("# Guide", encoding="utf-8")

            readme = base_dir / "README.md"
            readme.write_text("# Project\n[Guide](docs/guide.md#section)\n", encoding="utf-8")

            with override_settings(ATOMIC_DOCS_BASE_DIR=base_dir):
                result = check_atomic_docs()

            self.assertEqual(result, [])

    def test_multiple_unlinked_files_emit_multiple_warnings(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            docs_dir = base_dir / "docs"
            docs_dir.mkdir()
            (docs_dir / "orphan_a.md").write_text("# A", encoding="utf-8")
            (docs_dir / "orphan_b.md").write_text("# B", encoding="utf-8")
            (docs_dir / "linked.md").write_text("# Linked", encoding="utf-8")

            readme = base_dir / "README.md"
            readme.write_text("# Project\n[Linked](docs/linked.md)\n", encoding="utf-8")

            with override_settings(ATOMIC_DOCS_BASE_DIR=base_dir):
                result = check_atomic_docs()

            self.assertEqual(len(result), 2)
            warning_messages = {w.msg for w in result}
            self.assertIn("Markdown file 'docs/orphan_a.md' is not linked in the README.", warning_messages)
            self.assertIn("Markdown file 'docs/orphan_b.md' is not linked in the README.", warning_messages)
            self.assertTrue(all(w.id == "ambient_toolbox.W004" for w in result))

    def test_nested_docs_are_checked(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            docs_dir = base_dir / "docs"
            sub_dir = docs_dir / "sub"
            sub_dir.mkdir(parents=True)
            (sub_dir / "nested.md").write_text("# Nested", encoding="utf-8")

            readme = base_dir / "README.md"
            readme.write_text("# Project\n[Nested](docs/sub/nested.md)\n", encoding="utf-8")

            with override_settings(ATOMIC_DOCS_BASE_DIR=base_dir):
                result = check_atomic_docs()

            self.assertEqual(result, [])

    def test_empty_docs_dir_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            docs_dir = base_dir / "docs"
            docs_dir.mkdir()
            # No markdown files

            readme = base_dir / "README.md"
            readme.write_text("# Project\n", encoding="utf-8")

            with override_settings(ATOMIC_DOCS_BASE_DIR=base_dir):
                result = check_atomic_docs()

            self.assertEqual(result, [])
