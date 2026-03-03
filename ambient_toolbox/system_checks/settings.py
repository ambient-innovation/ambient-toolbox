from pathlib import Path

from django.conf import settings


def get_atomic_docs_base_dir() -> Path:
    """
    Base directory for resolving relative paths of the docs directory and README file.
    """
    base_dir = getattr(settings, "ATOMIC_DOCS_BASE_DIR", None)
    if base_dir is None:
        base_dir = settings.BASE_DIR
    return Path(base_dir)


def get_atomic_docs_dir() -> str:
    """
    Docs directory path, relative to ``ATOMIC_DOCS_BASE_DIR``.
    """
    return getattr(settings, "ATOMIC_DOCS_DIR", "docs")


def get_atomic_docs_readme_path() -> str:
    """
    README file path, relative to ``ATOMIC_DOCS_BASE_DIR``.
    """
    return getattr(settings, "ATOMIC_DOCS_README_PATH", "README.md")
