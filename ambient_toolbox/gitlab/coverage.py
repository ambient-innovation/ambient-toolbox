import json
import os
import re
import subprocess
import sys
from difflib import ndiff
from http import HTTPStatus

import httpx


class CoverageService:
    """
    Class to be used in the gitlab-ci to ensure pipeline test coverage is not dropping on commit
    """

    def __init__(self) -> None:
        super().__init__()

        # Get ENV variables
        self.current_pipeline_id: int = int(os.environ.get("CI_PIPELINE_ID"))
        self.base_api_url: str = os.environ.get("CI_API_V4_URL")
        self.current_branch: str = os.environ.get("CI_COMMIT_REF_NAME")
        self.token: str = os.environ.get("GITLAB_CI_COVERAGE_PIPELINE_TOKEN")
        self.project_id: int = int(os.environ.get("CI_PROJECT_ID"))
        self.job_name: str = os.environ.get("CI_COVERAGE_JOB_NAME", "")
        self.target_branch: str = os.environ.get("GITLAB_CI_COVERAGE_TARGET_BRANCH", "develop")
        self.pipelines_url = (
            f"{self.base_api_url}/projects/{self.project_id}/pipelines?ref={self.target_branch}&status=success"
        )
        self.pipelines_url_with_token = f"{self.pipelines_url}&private_token={self.token}"

        self.disable_coverage: bool = os.environ.get("GITLAB_CI_DISABLE_COVERAGE", False)

    def get_latest_target_branch_commit_sha(self) -> str:
        """
        Get the latest commit which is in the current branch and the target compare branch.
        """
        result = subprocess.run(  # noqa: PLW1510
            ["git", "merge-base", "--fork-point", f"origin/{self.target_branch}"],
            stdout=subprocess.PIPE,
        )
        return result.stdout.decode("utf-8").strip()

    def get_pipeline_id_by_commit_sha(self, sha: str) -> int | None:
        pipeline_url = f"{self.pipelines_url_with_token}&sha={sha}"
        response = httpx.get(pipeline_url)
        status_code = response.status_code

        if status_code == HTTPStatus.OK:
            pipelines = json.loads(response.content)
            if pipelines and len(pipelines) > 0:
                return pipelines[0].get("id", None)
            else:
                print("\n### ERROR: No pipelines found for SHA1 ###\n")
                print(f"Pipeline URL: {self.pipelines_url}&sha={sha}")
                print(response.content)
        return None

    def get_coverage_from_pipeline(self, pipeline_id: int, job_name: str) -> (float, float):
        """
        Get coverage from given pipeline (by id)
        """
        jobs_url = f"{self.base_api_url}/projects/{self.project_id}/pipelines/{pipeline_id}/jobs"
        jobs_with_token_url = f"{jobs_url}?private_token={self.token}"

        print(f"Jobs-API-URL: {jobs_url}")
        jobs_response = httpx.get(jobs_with_token_url)
        jobs_status_code = jobs_response.status_code

        if jobs_status_code != HTTPStatus.OK:
            raise ConnectionError(f"Call to jobs api endpoint failed with status code {jobs_status_code}")

        jobs = json.loads(jobs_response.content)
        coverages = {
            job["name"]: {"id": job["id"], "coverage": float(job["coverage"]), "web_url": job["web_url"]}
            for job in jobs
            if job.get("coverage")
        }

        pipeline_url = f"{self.base_api_url}/projects/{self.project_id}/pipelines/{pipeline_id}"
        pipeline_with_token_url = f"{pipeline_url}?private_token={self.token}"
        pipeline_response = httpx.get(pipeline_with_token_url)
        pipeline_status_code = pipeline_response.status_code

        if pipeline_status_code != HTTPStatus.OK:
            raise ConnectionError(f"Call to pipeline api endpoint failed with status code {pipeline_status_code}")

        pipeline = json.loads(pipeline_response.content)
        coverages_total = float(pipeline["coverage"] if pipeline["coverage"] else 0.0)
        print(f"Pipeline-API-URL: {pipeline_url}")
        print(f'Pipeline-URL: {pipeline["web_url"]}')

        if job_name == "":
            print(
                "\033[91mATTN: No CI_COVERAGE_JOB_NAME provided, using Total Coverage and skipping Coverage Diff\033[0m"
            )
            return coverages_total, coverages_total, None

        coverage_job = coverages.get(job_name)

        print(f'Job-URL: {coverage_job["web_url"]}')

        job_url = f'{self.base_api_url}/projects/{self.project_id}/jobs/{coverage_job["id"]}/trace'
        job_with_token_url = f"{job_url}?private_token={self.token}"
        job_response = httpx.get(job_with_token_url)
        job_status_code = job_response.status_code

        if job_status_code != HTTPStatus.OK:
            raise ConnectionError(f"Call to job api endpoint failed with status code {job_status_code}")

        print(f"Job-Log-URL: {job_url}")

        job_log = re.search(
            r"Name\s+Stmts\s+Miss\s+Branch\s+BrPart\s+Cover\s+Missing.*files skipped due to complete coverage\.",
            job_response.content.decode("utf-8"),
            re.DOTALL | re.MULTILINE,
        )
        # print(job_log.group())

        return coverage_job["coverage"] if coverage_job else 0.0, coverages_total, job_log.group()

    @staticmethod
    def color_text(sign: int, prefix: str, target: float, current: float, diff: float):
        """
        function to return colored in text according to the template:
        "{Total|Job} coverage {change_text} from {target}% to {current}% (Diff: {diff}%)"
        Red color: coverage dropped
        White/No color: coverage unchanged
        Green color: coverage climbed
        :param sign: numeric value of the coverage diff sign
        :param prefix: text prefix (i.e.: Total coverage, Job Coverage)
        :param target: target percentage
        :param current: current percentage
        :param diff: difference between current and target percentage
        :return: fully assembled and colored summary text
        """
        change = {
            -1: {"text": "dropped", "color": "\033[91m"},
            0: {"text": "unchanged", "color": ""},
            1: {"text": "climbed", "color": "\033[92m"},
        }
        return (
            f'{change[sign]["color"]} {prefix} {change[sign]["text"]} '
            f'from {target:2.2f}% to {current:2.2f}% (Diff: {diff:2.2f}%).\033[0m'
        )

    @staticmethod
    def print_diff(target_job_log, current_job_log):
        """
        Print a diff between the coverage reports of Current and Target branch
        """
        diff = ndiff(target_job_log.splitlines(keepends=True), current_job_log.splitlines(keepends=True))
        print("\n############################## Coverage Diff ##############################")
        print("# \033[91m- Target Branch\033[0m                                                         #")
        print("# \033[92m+ Current Branch\033[0m                                                        #")
        print("###########################################################################")
        for _idx, line in enumerate(diff):
            match = re.match(
                r"^\s*-+\s*$|"
                r"^\s*Name\s+Stmts\s+Miss\s+Branch\s+BrPart\s+Cover\s+Missing|"  # first line of the report
                r"^.*files skipped due to complete coverage.$|"  # Final line of the report
                r"^[+\-?]",  # Line starts with +,-,$ to indicate changes
                line,
            )
            if match:
                if line[0] == "-":
                    print("\033[91m", end="")
                if line[0] == "+":
                    print("\033[92m", end="")
                print(line, end="")
                if line[0] in ["+", "-"]:
                    print("\033[0m", end="")

        print("\n###########################################################################")
        print("# \033[91m- Target Branch\033[0m                                                         #")
        print("# \033[92m+ Current Branch\033[0m                                                        #")
        print("############################## Coverage Diff ##############################\n")

    def process(self):
        """
        Compare coverage from target branch (latest develop) with the current one.
        At first, we try to get a successfully finished pipeline for the "self.target_branch" (usually "develop")
        """

        # Check, if coverage is supposed to run. If not, inform the user and return early.
        if self.disable_coverage:
            print("Coverage was skipped!")
            sys.exit(0)

        print("\n###########################################################################\n")
        print("DEBUG INFO:")

        # Get the latest commit SHA which is also in develop
        commit_sha = self.get_latest_target_branch_commit_sha()

        # Try to find the latest successful pipeline for "TARGET_BRANCH" where our SHA was in
        print("Trying base branch for comparison.")
        target_pipeline_id = None
        if commit_sha:
            print(f'Found latest target branch commit SHA "{commit_sha}".')
            target_pipeline_id = self.get_pipeline_id_by_commit_sha(commit_sha)
            print(f"Target branch pipeline ID identified: {target_pipeline_id}.")

        # Get target pipeline id (from develop branch) if we were not successful the first time
        if not target_pipeline_id:
            print("Didn't work. Using default branch for comparison.")
            response = httpx.get(self.pipelines_url_with_token)
            status_code = response.status_code
            print(f"Pipelines-API-URL: {self.pipelines_url}")

            # Ensure call did not go sideways
            if status_code != HTTPStatus.OK:
                raise ConnectionError(f"Call to global pipeline api endpoint failed with status code {status_code}")

            # Read target pipeline ID from content
            try:
                target_pipeline_id = json.loads(response.content)[0]["id"]
            except IndexError:
                # This happens when there are zero `target_branch` pipelines
                target_pipeline_id = 0
            print(f"Default branch pipeline ID identified: {target_pipeline_id}.")

        # Get coverage from target pipeline
        print(f"Target Pipeline ID: {target_pipeline_id}")
        target_job_coverage, target_total_coverage, target_job_log = self.get_coverage_from_pipeline(
            target_pipeline_id, self.job_name
        )

        # Get coverage from this pipeline
        print(f"Current pipeline ID: {self.current_pipeline_id}")
        current_job_coverage, current_total_coverage, current_job_log = self.get_coverage_from_pipeline(
            self.current_pipeline_id, self.job_name
        )

        if target_job_log is None or current_job_log is None:
            print("\n\n\033[91m***************************************************************************\033[0m")
            print("        \033[91m**/!\\** Coverage log not found. Skipping diff. **/!\\**\033[0m             ")
            print("\033[91m***************************************************************************\033[0m\n\n")
        else:
            self.print_diff(target_job_log, current_job_log)

        # numeric value of the coverage diff sign
        sign_job_coverage = (current_job_coverage > target_job_coverage) - (current_job_coverage < target_job_coverage)
        sign_total_coverage = (current_total_coverage > target_total_coverage) - (
            current_total_coverage < target_total_coverage
        )

        # difference between current and target coverage
        diff_job_coverage = current_job_coverage - target_job_coverage
        diff_total_coverage = current_total_coverage - target_total_coverage

        coverage = {
            "total": {
                "target": target_total_coverage,
                "current": current_total_coverage,
                "sign": sign_total_coverage,
                "diff": diff_total_coverage,
                "prefix": "Total coverage",
            },
            "job": {
                "target": target_job_coverage,
                "current": current_job_coverage,
                "sign": sign_job_coverage,
                "diff": diff_job_coverage,
                "prefix": "Job coverage",
            },
        }

        # Print results
        print(
            self.color_text(
                coverage["total"]["sign"],
                coverage["total"]["prefix"],
                coverage["total"]["target"],
                coverage["total"]["current"],
                coverage["total"]["diff"],
            )
        )
        print(
            self.color_text(
                coverage["job"]["sign"],
                coverage["job"]["prefix"],
                coverage["job"]["target"],
                coverage["job"]["current"],
                coverage["job"]["diff"],
            )
        )

        if coverage["job"]["sign"] == -1:
            sys.exit(1)
