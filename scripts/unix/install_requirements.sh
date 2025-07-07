#!/bin/bash
pip install -U pip-tools
pip-compile --extra dev,drf,graphql,import-linter,bleacher,gitlab-coverage,sentry,view-layer, -o requirements.txt pyproject.toml --resolver=backtracking
pip-sync
