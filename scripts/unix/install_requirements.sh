#!/bin/bash
pip install -U pip-tools
pip-compile --extra dev,drf,graphql,bleacher,gitlab-coverage,sentry,view-layer, -o requirements.txt pyproject.toml --resolver=backtracking
pip-sync
