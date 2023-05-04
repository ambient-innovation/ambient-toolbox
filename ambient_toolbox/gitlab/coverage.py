import json
import os
import subprocess
import sys
from typing import Optional

import httpx


class CoverageService:
    """
    Class to be used in the gitlab-ci to ensure pipeline test coverage is not dropping on commit
    """

    def __init__(self) -> None:
        super().__init__()

        # Get ENV variables
        self.current_pipeline_id: int = int(os.environ.get('CI_PIPELINE_ID'))
        self.base_api_url: str = os.environ.get('CI_API_V4_URL')
        self.current_branch: str = os.environ.get('CI_COMMIT_REF_NAME')
        self.token: str = os.environ.get('GITLAB_CI_COVERAGE_PIPELINE_TOKEN')
        self.project_id: int = int(os.environ.get('CI_PROJECT_ID'))
        self.job_name: str = os.environ.get('CI_COVERAGE_JOB_NAME', '')
        self.target_branch: str = os.environ.get('GITLAB_CI_COVERAGE_TARGET_BRANCH')
        self.pipelines_url = (
            f'{self.base_api_url}/projects/{self.project_id}/pipelines?ref={self.target_branch}&status=success'
        )
        self.pipelines_url_with_token = f'{self.pipelines_url}&private_token={self.token}'

        self.disable_coverage: bool = os.environ.get('GITLAB_CI_DISABLE_COVERAGE', False)

    def get_latest_target_branch_commit_sha(self) -> str:
        """
        Get the latest commit which is in the current branch and the target compare branch.
        """
        result = subprocess.run(
            ['git', 'merge-base', '--fork-point', f'origin/{self.target_branch}'], stdout=subprocess.PIPE
        )
        return result.stdout.decode("utf-8").strip()

    def get_pipeline_id_by_commit_sha(self, sha: str) -> Optional[int]:
        pipeline_url = f'{self.pipelines_url_with_token}&sha={sha}'
        response = httpx.get(pipeline_url)
        status_code = response.status_code

        if status_code == 200:
            pipelines = json.loads(response.content)
            if pipelines and len(pipelines) > 0:
                return pipelines[0].get('id', None)
            else:
                print('\n### ERROR: No pipelines found for SHA1 ###\n')
                print(f'Pipeline URL: {self.pipelines_url}&sha={sha}')
                print(response.content)
        return None

    def get_coverage_from_pipeline(self, pipeline_id: int, job_name: str) -> (float, float):
        """
        Get coverage from given pipeline (by id)
        """
        jobs_url = f'{self.base_api_url}/projects/{self.project_id}/pipelines/{pipeline_id}/jobs'
        jobs_with_token_url = f'{jobs_url}?private_token={self.token}'

        print(f'Jobs-API-URL: {jobs_url}')
        jobs_response = httpx.get(jobs_with_token_url)
        jobs_status_code = jobs_response.status_code

        if jobs_status_code != 200:
            raise ConnectionError(f'Call to jobs api endpoint failed with status code {jobs_status_code}')

        jobs = json.loads(jobs_response.content)
        coverages = {
            job['name']: {'coverage': float(job['coverage']), 'web_url': job['web_url']}
            for job in jobs
            if job.get('coverage')
        }

        pipeline_url = f'{self.base_api_url}/projects/{self.project_id}/pipelines/{pipeline_id}'
        pipeline_with_token_url = f'{pipeline_url}?private_token={self.token}'
        pipeline_response = httpx.get(pipeline_with_token_url)
        pipeline_status_code = pipeline_response.status_code

        if pipeline_status_code != 200:
            raise ConnectionError(f'Call to pipeline api endpoint failed with status code {pipeline_status_code}')

        pipeline = json.loads(pipeline_response.content)
        coverages_total = float(pipeline['coverage'] if pipeline['coverage'] else 0.0)
        print(f'Pipeline-API-URL: {pipeline_url}')
        print(f'Pipeline-URL: {pipeline["web_url"]}')

        if job_name == '':
            return coverages_total, coverages_total

        coverage_job = coverages.get(job_name)

        print(f'Job-URL: {coverage_job["web_url"]}')
        return coverage_job['coverage'] if coverage_job else 0.0, coverages_total

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
            -1: {'text': 'dropped', 'color': '\033[91m'},
            0: {'text': 'unchanged', 'color': ''},
            1: {'text': 'climbed', 'color': '\033[92m'},
        }
        return (
            f'{change[sign]["color"]} {prefix} {change[sign]["text"]} '
            f'from {target:2.2f}% to {current:2.2f}% (Diff: {diff:2.2f}%).\033[0m'
        )

    def process(self):
        """
        Compare coverage from target branch (latest develop) with the current one.
        At first, we try to get a successfully finished pipeline for the "self.target_branch" (usually "develop")
        """

        # Check, if coverage is supposed to run. If not, inform the user and return early.
        if self.disable_coverage:
            print('Coverage was skipped!')
            sys.exit(0)

        print('\n###########################################################################\n')
        print('DEBUG INFO:')

        # Get the latest commit SHA which is also in develop
        commit_sha = self.get_latest_target_branch_commit_sha()

        # Try to find the latest successful pipeline for "TARGET_BRANCH" where our SHA was in
        print('Trying base branch for comparison.')
        target_pipeline_id = None
        if commit_sha:
            print(f'Found latest target branch commit SHA "{commit_sha}".')
            target_pipeline_id = self.get_pipeline_id_by_commit_sha(commit_sha)
            print(f'Target branch pipeline ID identified: {target_pipeline_id}.')

        # Get target pipeline id (from develop branch) if we were not successful the first time
        if not target_pipeline_id:
            print("Didn't work. Using default branch for comparison.")
            response = httpx.get(self.pipelines_url_with_token)
            status_code = response.status_code
            print(f'Pipelines-API-URL: {self.pipelines_url}')

            # Ensure call did not go sideways
            if status_code != 200:
                raise ConnectionError(f'Call to global pipeline api endpoint failed with status code {status_code}')

            # Read target pipeline ID from content
            target_pipeline_id = json.loads(response.content)[0]['id']
            print(f'Default branch pipeline ID identified: {target_pipeline_id}.')

        # Get coverage from target pipeline
        print(f'Target Pipeline ID: {target_pipeline_id}')
        target_job_coverage, target_total_coverage = self.get_coverage_from_pipeline(target_pipeline_id, self.job_name)

        # Get coverage from this pipeline
        print(f'Current pipeline ID: {self.current_pipeline_id}')
        current_job_coverage, current_total_coverage = self.get_coverage_from_pipeline(
            self.current_pipeline_id, self.job_name
        )

        # numeric value of the coverage diff sign
        sign_job_coverage = (current_job_coverage > target_job_coverage) - (current_job_coverage < target_job_coverage)
        sign_total_coverage = (current_total_coverage > target_total_coverage) - (
            current_total_coverage < target_total_coverage
        )

        # difference between current and target coverage
        diff_job_coverage = current_job_coverage - target_job_coverage
        diff_total_coverage = current_total_coverage - target_total_coverage

        coverage = {
            'total': {
                'target': target_total_coverage,
                'current': current_total_coverage,
                'sign': sign_total_coverage,
                'diff': diff_total_coverage,
                'prefix': 'Total coverage',
            },
            'job': {
                'target': target_job_coverage,
                'current': current_job_coverage,
                'sign': sign_job_coverage,
                'diff': diff_job_coverage,
                'prefix': 'Job coverage',
            },
        }

        print('\n###########################################################################\n')

        # Print results
        print(
            self.color_text(
                coverage['total']['sign'],
                coverage['total']['prefix'],
                coverage['total']['target'],
                coverage['total']['current'],
                coverage['total']['diff'],
            )
        )
        print(
            self.color_text(
                coverage['job']['sign'],
                coverage['job']['prefix'],
                coverage['job']['target'],
                coverage['job']['current'],
                coverage['job']['diff'],
            )
        )
        if coverage['job']['sign'] == -1:
            sys.exit(1)
