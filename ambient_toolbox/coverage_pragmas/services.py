import ast
import io
import os
import re
import tokenize
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from coverage import Coverage
from coverage.config import DEFAULT_EXCLUDE
from coverage.files import GlobMatcher, prep_patterns
from coverage.parser import PythonParser

# The pattern coverage.py itself uses to recognise the "no cover" pragma in all its spellings.
PRAGMA_REGEX = re.compile(DEFAULT_EXCLUDE[0])

SKIPPED_DIRECTORIES = {
    "__pycache__",
    "build",
    "dist",
    "env",
    "htmlcov",
    "node_modules",
    "site-packages",
    "venv",
}


class PragmaStatus(Enum):
    # Every line and branch the pragma excludes was executed - the pragma can be removed.
    UNNEEDED = "unneeded"
    # The file is excluded from the report via "omit", so the pragma has no effect at all.
    INEFFECTIVE = "ineffective"
    # All lines were executed, but removing the pragma would leave a partial branch.
    BRANCH_MISSING = "branch_missing"
    # Some of the excluded lines were executed - the pragma covers more than necessary.
    PARTIAL = "partial"
    # Nothing the pragma excludes was executed - the pragma does its job.
    NEEDED = "needed"
    # The file has no coverage data, usually because the tests never import it.
    NOT_MEASURED = "not_measured"


@dataclass
class PragmaFinding:
    filename: str
    line: int
    status: PragmaStatus
    missing_lines: list[int] = field(default_factory=list)


@dataclass
class _ParsedFile:
    text: str
    pragma_spans: list[tuple[int, int, int]]


class UnneededCoveragePragmaService:
    """
    Detects "# pragma: no cover" comments which are not required, based on the data of a finished coverage run.

    coverage.py records every executed line, including the excluded ones, and applies exclusions only when reporting.
    Therefore, a single regular test run is enough: for each pragma, the lines it excludes are compared to the lines
    that were actually executed.
    """

    FAILING_STATUSES = (PragmaStatus.UNNEEDED, PragmaStatus.INEFFECTIVE)

    def __init__(self, *, paths: list[str] | None = None, data_file: str | None = None) -> None:
        self.paths = [Path(path).resolve() for path in (paths or ["."])]
        self.coverage = Coverage(data_file=data_file or ".coverage")
        self.coverage.load()
        self.data = self.coverage.get_data()

        config = self.coverage.config
        self.exclude_regex = "|".join(f"(?:{pattern})" for pattern in config.exclude_list)
        omit_patterns = [*config.run_omit, *(config.report_omit or [])]
        self.omit_matcher = GlobMatcher(prep_patterns(omit_patterns), "omit") if omit_patterns else None

    @staticmethod
    def _normalise(filename: str | Path) -> str:
        return os.path.normcase(os.path.abspath(filename))

    def _get_measured_files(self) -> dict[str, str]:
        return {self._normalise(filename): filename for filename in self.data.measured_files()}

    def _get_candidate_files(self, measured_files: dict[str, str]) -> set[str]:
        roots = [self._normalise(root) for root in self.paths]
        candidates = {
            normalised
            for normalised in measured_files
            if normalised.endswith(".py")
            and os.path.exists(normalised)
            and any(normalised == root or normalised.startswith(root + os.sep) for root in roots)
        }
        for root in self.paths:
            if root.is_file():
                candidates.add(self._normalise(root))
                continue
            for dirpath, dirnames, filenames in os.walk(root):
                dirnames[:] = [
                    dirname
                    for dirname in dirnames
                    if not dirname.startswith(".") and dirname not in SKIPPED_DIRECTORIES
                ]
                candidates.update(
                    self._normalise(Path(dirpath) / filename) for filename in filenames if filename.endswith(".py")
                )
        return candidates

    @staticmethod
    def _parse_file(filename: str) -> _ParsedFile | None:
        """
        Returns the source and the position of every pragma inside a real comment as (line, start, end) tuples.
        Using the tokenizer ensures that a pragma inside a string literal is not mistaken for one.
        """
        try:
            text = Path(filename).read_text(encoding="utf-8")
            tokens = list(tokenize.generate_tokens(io.StringIO(text).readline))
        except (OSError, UnicodeDecodeError, SyntaxError, tokenize.TokenError):
            return None

        pragma_spans = []
        for token in tokens:
            if token.type != tokenize.COMMENT:
                continue
            match = PRAGMA_REGEX.search(token.string)
            if match:
                line, column = token.start
                pragma_spans.append((line, column + match.start(), column + match.end()))
        return _ParsedFile(text=text, pragma_spans=pragma_spans) if pragma_spans else None

    @staticmethod
    def _blank_pragmas(text: str, spans: list[tuple[int, int, int]]) -> str:
        """
        Replaces the given pragmas with spaces. Line and column numbers stay unchanged, so the result can be compared
        line by line with the coverage data of the original file.
        """
        lines = text.splitlines(keepends=True)
        for line, start, end in spans:
            source_line = lines[line - 1]
            lines[line - 1] = source_line[:start] + " " * (end - start) + source_line[end:]
        return "".join(lines)

    def _build_parser(self, text: str, filename: str) -> PythonParser:
        parser = PythonParser(text=text, filename=filename, exclude=self.exclude_regex)
        parser.parse_source()
        return parser

    @staticmethod
    def _indentation(text_lines: list[str], line: int) -> int:
        source_line = text_lines[line - 1]
        return len(source_line) - len(source_line.lstrip())

    @staticmethod
    def _get_definition_lines(text: str, parser: PythonParser) -> set[int]:
        """
        Returns the lines which run when a module or class is loaded, even if no function defined there is ever called:
        decorators and "def"/"class" lines, as well as all statements directly inside a class body.
        """
        lines = set()
        for node in ast.walk(ast.parse(text)):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                lines.update(decorator.lineno for decorator in node.decorator_list)
                lines.add(node.lineno)
            if isinstance(node, ast.ClassDef):
                lines.update(statement.lineno for statement in node.body)
        return parser.first_lines(lines)

    def _get_unexecuted_arcs(
        self, *, block: set[int], base_parser: PythonParser, executed_arcs: set[tuple[int, int]]
    ) -> list[int]:
        """
        Returns the lines which would become partial branches if the pragma was removed. These are branch points inside
        the block and branch points leading into it, since arcs into excluded lines are not counted as exits.
        """
        possible_arcs = {
            (start, end) for start, end in base_parser.arcs() if start > 0 and end not in base_parser.excluded
        }
        affected_lines = {start for start, end in possible_arcs if start in block or end in block}
        exit_counts = base_parser.exit_counts()

        return sorted(
            line
            for line in affected_lines
            if exit_counts.get(line, 0) > 1 and any(arc not in executed_arcs for arc in possible_arcs if arc[0] == line)
        )

    def _analyse_file(self, filename: str, parsed_file: _ParsedFile, measured_name: str) -> list[PragmaFinding]:
        base_parser = self._build_parser(self._blank_pragmas(parsed_file.text, parsed_file.pragma_spans), filename)
        executed_lines = base_parser.translate_lines(self.data.lines(measured_name) or [])
        has_arcs = self.data.has_arcs()
        if has_arcs:
            # Calculating the arcs first is required, as it prepares the parser for translating the recorded arcs.
            base_parser.arcs()
            executed_arcs = base_parser.translate_arcs(self.data.arcs(measured_name) or [])
        text_lines = parsed_file.text.splitlines()
        definition_lines = self._get_definition_lines(parsed_file.text, base_parser)

        findings = []
        for pragma_span in parsed_file.pragma_spans:
            pragma_line = pragma_span[0]
            other_spans = [span for span in parsed_file.pragma_spans if span != pragma_span]
            pragma_parser = self._build_parser(self._blank_pragmas(parsed_file.text, other_spans), filename)
            block = (pragma_parser.excluded - base_parser.excluded) & base_parser.statements

            # The header of a block (e.g. "def", "if" or a decorator) runs even if its body never does, and so do
            # definitions nested inside it. Only the remaining statements indented deeper than the pragma's line tell
            # whether the block itself was entered.
            header_indentation = self._indentation(text_lines, base_parser.first_line(pragma_line))
            body = {
                line for line in block - definition_lines if self._indentation(text_lines, line) > header_indentation
            } or block

            missing_lines = sorted(block - executed_lines)
            if not missing_lines:
                missing_branches = (
                    self._get_unexecuted_arcs(block=block, base_parser=base_parser, executed_arcs=executed_arcs)
                    if has_arcs
                    else []
                )
                if missing_branches:
                    findings.append(PragmaFinding(filename, pragma_line, PragmaStatus.BRANCH_MISSING, missing_branches))
                else:
                    findings.append(PragmaFinding(filename, pragma_line, PragmaStatus.UNNEEDED))
            elif body & executed_lines:
                findings.append(PragmaFinding(filename, pragma_line, PragmaStatus.PARTIAL, missing_lines))
            else:
                findings.append(PragmaFinding(filename, pragma_line, PragmaStatus.NEEDED, missing_lines))
        return findings

    def _is_omitted(self, filename: str) -> bool:
        return self.omit_matcher is not None and self.omit_matcher.match(filename)

    def get_findings(self) -> list[PragmaFinding]:
        measured_files = self._get_measured_files()
        if not measured_files:
            raise ValueError(
                "No coverage data found. Run your tests with coverage first "
                "(and 'coverage combine' if you run them in parallel mode)."
            )

        findings = []
        for filename in sorted(self._get_candidate_files(measured_files)):
            parsed_file = self._parse_file(filename)
            if parsed_file is None:
                continue

            pragma_lines = [span[0] for span in parsed_file.pragma_spans]
            if self._is_omitted(filename):
                findings.extend(PragmaFinding(filename, line, PragmaStatus.INEFFECTIVE) for line in pragma_lines)
            elif filename not in measured_files:
                findings.extend(PragmaFinding(filename, line, PragmaStatus.NOT_MEASURED) for line in pragma_lines)
            else:
                findings.extend(self._analyse_file(filename, parsed_file, measured_files[filename]))
        return findings
