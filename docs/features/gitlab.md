# GitLab

## Test coverage service

### Motivation

When using GitLab, you can query your projects test coverage via the GitLab API. This package contains a service which
you can utilise within your pipeline as follows.

The script will try to get the last commit inside your branch which came from your default branch (usually "develop")
and looks for a successfully run pipeline. From there, it will query the code coverage and compare it to your coverage.
If it has dropped, the step will return "1" which causes your pipeline to fail. If it can't find a valid pipeline, it
will fall back to the default branches most recent successful pipeline.

Take care that you have to set up Gitalb to recognise your coverage before you can use this functionality.

### Installation

* Create a file called `scripts/validate_coverage.py` and add the following:

```python
from ambient_toolbox.gitlab.coverage import CoverageService

service = CoverageService()
service.process()
```

* Add this step to your `gitlab-ci.yml`. Make sure that you set the correct python version and that this stage is
  defined after the unittest stage.

```yaml
# POST-TEST STAGE
check coverage:
  image: ${CI_DEPENDENCY_PROXY_GROUP_IMAGE_PREFIX}/python:3.12
  stage: posttest
  needs:
    - unittest
  tags:
    - low-load
  except:
    - develop
    - master
  before_script:
    - pip install -U pip httpx ambient_toolbox
  script:
    - python scripts/validate_coverage.py
```

* Create an access token for your repo having `developer` role and `read_api` permission (Settings -> Access Tokens)

* Add two variables to your CI/CD inside your GitLab repository (Settings -> CI/CD -> Variables). Insert the token from
  step 3 and define your default branch for comparison. Usually, this will be "develop".

> GITLAB_CI_COVERAGE_PIPELINE_TOKEN = [token]

> GITLAB_CI_COVERAGE_TARGET_BRANCH = develop

* Done. Enjoy!

Hint: For merge-commits (i.e.: Merge develop into master), or hotfixes into branches that are not your default, manually
run a Pipeline on your source-branch (i.e.: `develop` if you want to merge `develop` into `master`) with the _Input
variable key_ set to `GITLAB_CI_COVERAGE_TARGET_BRANCH` and the _Input variable value_ set to the target branch (
i.e.: `master` if you want to merge `develop` into `master`).

Hint: If you wish to not run coverage for a specific pipeline for whatever reason, simply run the pipeline
with `GITLAB_CI_DISABLE_COVERAGE = True` and no coverage will be collected.
