import kfp
from kfp import dsl
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get GitHub username and token from environment variables
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Define configuration variables
REPO_URL = "https://github.com/danilonicioka/mlops-workflow.git"
CLONED_DIR = "mlops-workflow"
BRANCH_NAME = "tests"
PIPELINE_ID = "my-pipeline-id"
PIPELINE_NAME = "Clone_and_Pull_Pipeline"
KFP_HOST = "http://localhost:3000"  # KFP host URL

# Define a KFP component factory function for cloning repository with token
@dsl.component(packages_to_install=['gitpython'])
def clone_repo_and_dvc_pull(
    repo_url: str,
    cloned_dir: str,
    branch_name: str,
    github_username: str,
    github_token: str
) -> str:
    from git import Repo
    from subprocess import run

    def clone_repository_with_token(repo_url, cloned_dir, branch_name, github_username, github_token):
        """Clone a Git repository using a GitHub token in the URL and specifying the branch."""
        try:
            # Construct the URL with the GitHub username and token
            url_with_token = f"https://{github_username}:{github_token}@{repo_url.split('//')[1]}"
            
            # Clone the repository from the specified branch
            repo = Repo.clone_from(url_with_token, cloned_dir, branch=branch_name)
            return "Repository cloned successfully"
        except Exception as e:
            return f"Error occurred during repository cloning: {e}"

    def perform_dvc_pull(cloned_dir):
        """Perform a DVC pull to synchronize local data with the remote repository."""
        try:
            # Run the `dvc pull` command
            result = run(['dvc', 'pull'], cwd=cloned_dir, capture_output=True, text=True)
            
            # Check if the command executed successfully
            if result.returncode != 0:
                # Log and raise an error if the command failed
                error_message = f"dvc pull failed with error: {result.stderr}"
                raise Exception(error_message)
            
            # Log successful operation
            return "Successfully pulled data from remote DVC repository"
            
        except Exception as e:
            # Log and handle the error
            return f"Error occurred during dvc pull: {e}"

    # Call the functions
    clone_result = clone_repository_with_token(repo_url, cloned_dir, branch_name, github_username, github_token)
    dvc_pull_result = perform_dvc_pull(cloned_dir)
    return f"{clone_result}, {dvc_pull_result}"

# Define pipeline function with parameterization
@dsl.pipeline
def my_pipeline(
    repo_url: str,
    cloned_dir: str,
    branch_name: str,
    github_username: str,
    github_token: str
) -> str:
    ingestion_task = clone_repo_and_dvc_pull(repo_url=repo_url, cloned_dir=cloned_dir, branch_name=branch_name, github_username=github_username, github_token=github_token)
    return ingestion_task.output

# Compile the pipeline
pipeline_filename = f"{PIPELINE_NAME}.yaml"
kfp.compiler.Compiler().compile(
    pipeline_func=my_pipeline,
    package_path=pipeline_filename)

# Submit the pipeline to the KFP cluster
client = kfp.Client(host=KFP_HOST)  # Use the configured KFP host
client.create_run_from_pipeline_func(
    my_pipeline,
    arguments={
        'repo_url': REPO_URL,
        'cloned_dir': CLONED_DIR,
        'branch_name': BRANCH_NAME,
        'github_username': GITHUB_USERNAME,
        'github_token': GITHUB_TOKEN
    })