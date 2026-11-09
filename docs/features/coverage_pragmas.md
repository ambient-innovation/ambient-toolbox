# Coverage pragmas

## Find unneeded "pragma: no cover"

### Motivation

`# pragma: no cover` comments tend to outlive their reason: a test is added later, the code gets executed, but the
pragma stays and hides the line from the coverage report. If the line breaks again, nobody notices.

The management command `validate_coverage_pragmas` finds those pragmas. coverage.py records every executed line,
including excluded ones, and applies exclusions only when building the report. Therefore, the command needs no extra
test run: it compares the lines (and branches) each pragma excludes with what your regular test run executed.

### Installation

```bash
pip install ambient-toolbox[coverage-pragmas]
```

### Usage

Run your tests with coverage first, then call the command from the same directory:

```bash
coverage run -m pytest  # or: pytest --cov
coverage combine        # only if you use "parallel = true"
python manage.py validate_coverage_pragmas
```

By default, the command searches the current directory for pragmas. Pass files or directories to narrow it down and
`--data-file` to read a different data file than the one your coverage configuration (or `COVERAGE_FILE`) points to:

```bash
python manage.py validate_coverage_pragmas apps/ --data-file reports/.coverage
```

The command reads your regular coverage configuration (`pyproject.toml`, `.coveragerc`, `setup.cfg` or `tox.ini`),
so other exclusion patterns like `exclude_also` and the `omit` lists are respected.

### Running it in your pipeline

The command does not have to run right after the tests, but it needs the combined coverage data and the source files
at the same absolute paths as during the test run, since the data file stores absolute paths. The simplest setup is
the same job, right after combining the data:

```bash
coverage run --parallel-mode manage.py test && coverage combine && coverage report && python manage.py validate_coverage_pragmas
```

A separate job works as well if it uses the same image and checkout path and receives the data file as an artifact.

### Results

| Category           | Meaning                                                                                                                              | Fails |
|--------------------|--------------------------------------------------------------------------------------------------------------------------------------|-------|
| Unneeded           | Removing the pragma does not change the report: everything it excludes was executed, or another exclusion pattern already covers it. | Yes   |
| Ineffective        | The file is excluded via `omit`, so the pragma has no effect. Remove the pragma.                                                     | Yes   |
| Partial branch     | All lines were executed, but removing the pragma leaves a partial branch on the listed lines.                                        | No    |
| Partially executed | Parts of the excluded block were executed. Move the pragma closer to the code that never runs.                                       | No    |
| No coverage data   | The file was never imported during the tests, so nothing can be said about its pragmas.                                              | No    |
| Needed             | Nothing the pragma excludes was executed. Only listed with `--verbosity 2`.                                                          | No    |

The command exits with status 1 if it finds unneeded or ineffective pragmas, so you can use it in your pipeline.
Files containing pragmas which cannot be read or parsed are listed separately as skipped and do not fail the command.

### Limitations

* The result is only as good as the test run it is based on. Code that runs only on another platform, Python or
  Django version, or only with certain settings, may be reported as "unneeded" although a different environment needs
  the pragma. Only use the command on projects whose tests run in a single environment, or combine the coverage data of
  all environments first.
* Flaky tests that only sometimes execute a line lead to unstable results.
* Code running in subprocesses is only recorded if coverage is set up for them. Missing data makes pragmas look
  needed, never unneeded.
* The command relies on the parser of coverage.py, which is not part of its public API. A future coverage release
  might require an update of this package.
