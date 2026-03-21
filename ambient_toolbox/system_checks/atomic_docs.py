import re
from pathlib import Path

from django.core import checks

from ambient_toolbox.system_checks.settings import (
    get_atomic_docs_base_dir,
    get_atomic_docs_dir,
    get_atomic_docs_readme_path,
)


def check_atomic_docs(*args, **kwargs) -> list[checks.Warning]:
    """
    Checks that all Markdown files in the docs directory are linked in the README.
    Ensures documentation stays discoverable and prevents orphaned docs from accumulating.
    """
    base_dir = get_atomic_docs_base_dir()
    docs_path = base_dir / get_atomic_docs_dir()
    readme_path = base_dir / get_atomic_docs_readme_path()

    # If docs dir doesn't exist, nothing to check
    if not docs_path.exists():
        return []

    # If README doesn't exist, warn about it
    if not readme_path.exists():
        return [
            checks.Warning(
                f"README file not found at '{readme_path}'.",
                hint="Create a README file or adjust the ATOMIC_DOCS_README_PATH setting.",
                id="ambient_toolbox.W004",
            )
        ]

    # Collect all markdown files in docs directory
    md_files: list[Path] = sorted(docs_path.rglob("*.md"))

    if not md_files:
        return []

    # Read README and extract all markdown link targets
    readme_content = readme_path.read_text(encoding="utf-8")
    raw_targets = re.findall(r"\[.*?\]\((.*?)\)", readme_content)

    # Strip anchors from link targets
    link_targets = {target.split("#")[0] for target in raw_targets}

    issue_list = []

    for md_file in md_files:
        relative_path = md_file.relative_to(base_dir).as_posix()
        prefixed_path = f"./{relative_path}"

        if relative_path not in link_targets and prefixed_path not in link_targets:
            issue_list.append(
                checks.Warning(
                    f"Markdown file '{relative_path}' is not linked in the README.",
                    hint="Add a link to this file in the README or remove the file if it's no longer needed.",
                    id="ambient_toolbox.W004",
                )
            )

    return issue_list
