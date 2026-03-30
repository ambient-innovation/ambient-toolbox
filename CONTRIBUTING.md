# Contribute

## Setup package for development

- Create a Python virtualenv and activate it
- Install "uv" with `pip install -U uv`
- Sync the requirements with `uv sync --frozen --extra dev --extra drf --extra graphql --extra import-linter --extra bleacher --extra gitlab-coverage --extra sentry --extra view-layer`

## Add functionality

- Create a new branch for your feature
- Change the dependency in your requirements.txt to a local (editable) one that points to your local file system:
  `-e /Users/workspace/ambient-toolbox` or via pip  `pip install -e /Users/workspace/ambient-toolbox`
- Ensure the code passes the tests
- Create a pull request

## Run tests

- Run tests
  ````
  pytest --ds settings tests
  ````

- Check coverage
  ````
  coverage run -m pytest --ds settings tests
  coverage report -m
  ````

## Git hooks (via pre-commit)

We use pre-push hooks to ensure that only linted code reaches our remote repository and pipelines aren't triggered in
vain.

To enable the configured pre-push hooks, you need to [install](https://pre-commit.com/) pre-commit and run once:

    pre-commit install -t pre-push -t pre-commit --install-hooks

This will permanently install the git hooks for both, frontend and backend, in your local
[`.git/hooks`](./.git/hooks) folder.
The hooks are configured in the [`.pre-commit-config.yaml`](templates/.pre-commit-config.yaml.tpl).

You can check whether hooks work as intended using the [run](https://pre-commit.com/#pre-commit-run) command:

    pre-commit run [hook-id] [options]

Example: run single hook

    pre-commit run ruff --all-files

Example: run all hooks of pre-push stage

    pre-commit run --all-files

## Releasing a new version

Releases are fully automated. Pushing a version tag to GitHub triggers the
[`release.yml`](.github/workflows/release.yml) pipeline, which:

1. Builds the wheel and source distribution with `uv build`
2. Signs every artifact with [Sigstore](https://www.sigstore.dev/) (OIDC-based,
   no private keys involved) and attaches `.sigstore.json` bundles to the release
3. Creates a [GitHub Release](https://github.com/ambient-innovation/ambient-toolbox/releases)
   with all signed files attached
4. Publishes to [PyPI](https://pypi.org/project/ambient-toolbox/) via
   [Trusted Publishing](https://docs.pypi.org/trusted-publishers/) (no API token
   needed — authentication uses the GitHub OIDC token)

### Tag format

Tags **must** start with `v` (e.g. `v12.9.0`). This is enforced in two places:

- The workflow trigger in `.github/workflows/release.yml` only fires on `v*` tags
- The `pypi` GitHub Environment has a deployment protection rule that restricts
  deployments to tags matching `v*` — any publish attempt from a non-`v*` tag
  will be blocked

> **Note:** Tags without the `v` prefix (e.g. `12.9.0`) will **not** trigger the
> pipeline. If GitHub shows "Currently applies to 0 tags" for the `v*` rule, it
> just means no matching tags exist yet — the rule is still active and will apply
> to the next `v*` tag you push.

### How to cut a release

```bash
git tag v<version>          # e.g. git tag v12.9.0
git push origin v<version>
```

That's it. Monitor progress in the
[Actions tab](https://github.com/ambient-innovation/ambient-toolbox/actions).

### First-time setup checklist

Before the pipeline can run for the first time, a human must complete these
steps (they require repository/PyPI admin access and cannot be automated):

- [ ] **Create GitHub Environment `pypi`**
  - Go to https://github.com/ambient-innovation/ambient-toolbox/settings/environments
    → **New environment** → name it exactly `pypi`
  - Under **Deployment branches and tags** → **Add deployment branch or tag rule**
    → type **Tag**, pattern `v*`
  - Optionally add **Required reviewers** for a manual approval gate before each publish

- [ ] **Configure PyPI Trusted Publisher**
  - Go to https://pypi.org/manage/project/ambient-toolbox/settings/publishing/
    → **Add a new publisher**
  - Fill in:
    - Owner: `ambient-innovation`
    - Repository: `ambient-toolbox`
    - Workflow filename: `release.yml`
    - Environment name: `pypi`

- [ ] *(Optional)* **Configure TestPyPI Trusted Publisher**
  - Same steps at https://test.pypi.org/manage/project/ambient-toolbox/settings/publishing/

- [ ] **Ensure all release tags use the `v*` format** (e.g. `v12.9.0`) —
  see [Tag format](#tag-format) below

### Modifying the release pipeline

**File to edit:** `.github/workflows/release.yml`

The pipeline uses four actions — here are the canonical docs for each:

| Action | Purpose | Docs |
|--------|---------|------|
| `sigstore/gh-action-sigstore-python@v3.2.0` | Sigstore signing | https://github.com/sigstore/gh-action-sigstore-python |
| `softprops/action-gh-release@v2` | Create GitHub Release | https://github.com/softprops/action-gh-release |
| `pypa/gh-action-pypi-publish@release/v1` | Publish to PyPI | https://github.com/pypa/gh-action-pypi-publish |
| `astral-sh/setup-uv@v5` | Install uv | https://github.com/astral-sh/setup-uv |

#### Changing or rotating the PyPI Trusted Publisher

The pipeline authenticates with PyPI via a Trusted Publisher (OIDC) — there is
no API token stored in GitHub Secrets. If you rename the workflow file, move
the repository, or change the GitHub Environment name, you must update the
Trusted Publisher config on PyPI to match:

- **PyPI:** https://pypi.org/manage/project/ambient-toolbox/settings/publishing/
- **TestPyPI:** https://test.pypi.org/manage/project/ambient-toolbox/settings/publishing/

The current config expects:
- Owner: `ambient-innovation`
- Repository: `ambient-toolbox`
- Workflow filename: `release.yml`
- Environment name: `pypi`

#### Changing the GitHub Environment

The `publish-pypi` job runs inside the `pypi` GitHub Environment, which can
require manual approval before a publish proceeds. Manage it here:

https://github.com/ambient-innovation/ambient-toolbox/settings/environments

**Initial setup:** When creating the environment for the first time:
1. Go to the URL above → **New environment** → name it exactly `pypi`
2. Under **Deployment branches and tags** → **Add deployment branch or tag rule**
3. Select **Tag** as the type and enter `v*` as the pattern
4. Optionally add required reviewers under **Required reviewers**

> GitHub will show "Currently applies to 0 tags" if no `v*` tags exist yet —
> this is expected and the rule is still active.

If you rename the environment, update the `environment:` key in `release.yml`
**and** the environment name in the PyPI Trusted Publisher config above.

#### Verifying signatures

Anyone can verify a downloaded artifact against its `.sigstore.json` bundle
using the [sigstore Python client](https://github.com/sigstore/sigstore-python):

```bash
pip install sigstore
sigstore verify github \
  --cert-identity https://github.com/ambient-innovation/ambient-toolbox/.github/workflows/release.yml@refs/tags/v<version> \
  ambient_toolbox-<version>-py3-none-any.whl
```

PyPI also displays Sigstore provenance directly on the release page under the
"Provenance" tab.

## Update documentation

- To build the documentation, run: `sphinx-build docs/ docs/_build/html/`.
- Open `docs/_build/html/index.html` to see the documentation.

### Translation files

If you have added custom text, make sure to wrap it in `_()` where `_` is
gettext_lazy (`from django.utils.translation import gettext_lazy as _`).

How to create translation file:

* Navigate to `ambient_toolbox`
* `python manage.py makemessages -l de`
* Have a look at the new/changed files within `ambient_toolbox/locale`

How to compile translation files:

* Navigate to `ambient_toolbox`
* `python manage.py compilemessages`
* Have a look at the new/changed files within `ambient_toolbox/locale`
