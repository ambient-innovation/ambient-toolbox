import shutil
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

SAMPLE_MODULE = textwrap.dedent(
    """
    def executed():  # pragma: no cover
        return 1


    def never_called():  # pragma: no cover
        return 2


    def partly(x):  # pragma: no cover
        if x:
            return 1
        return 2


    def single_line(x):
        if x:
            return 1  # pragma: no cover
        return 2


    def branch_only(x):
        if x:  # pragma: no cover
            return 1
        return 2


    def else_case(x):
        if x:
            return 1
        else:  # pragma: no cover
            return 2


    class NeverUsed:  # pragma: no cover
        def method(self):
            return 1


    TEXT = "# pragma: no cover"  # A comment without the pragma
    # pragma: no cover
    """
)

SAMPLE_RUNNER = textwrap.dedent(
    """
    import sample

    sample.executed()
    sample.partly(1)
    sample.single_line(0)
    sample.branch_only(1)
    sample.else_case(1)
    """
)


class SampleProject:
    """
    Creates a small project in a temporary directory and records its coverage data in a subprocess, so the coverage
    measurement of the test run itself stays untouched.
    """

    def __init__(self, *, branch: bool = True) -> None:
        self.path = Path(tempfile.mkdtemp())
        (self.path / "sample.py").write_text(SAMPLE_MODULE, encoding="utf-8")
        (self.path / "omitted.py").write_text("x = 1  # pragma: no cover\n", encoding="utf-8")
        (self.path / "never_imported.py").write_text("y = 2  # pragma: no cover\n", encoding="utf-8")
        # An unclosed bracket makes the file impossible to tokenize, so it has to be skipped.
        (self.path / "broken.py").write_text("z = (  # pragma: no cover\n", encoding="utf-8")
        (self.path / "runner.py").write_text(SAMPLE_RUNNER, encoding="utf-8")
        (self.path / ".coveragerc").write_text(
            f"[run]\nbranch = {str(branch).lower()}\nomit = omitted.py\n", encoding="utf-8"
        )
        subprocess.run(
            [sys.executable, "-m", "coverage", "run", "runner.py"],
            cwd=self.path,
            check=True,
            capture_output=True,
        )

    def cleanup(self) -> None:
        shutil.rmtree(self.path, ignore_errors=True)
