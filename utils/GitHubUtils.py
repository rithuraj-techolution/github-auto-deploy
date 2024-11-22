
import logging
import os
import subprocess
import traceback
from typing import List, Any
import shlex

from utils.utils import handle_exception, run_terminal_commands
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

class GitHubUtils:
    """
    A utility class for handling various GitHub operations such as cloning repositories,
    checking out branches, committing changes, and more.
    """
    def __init__(self, config: Any, path=os.getcwd()) -> None:
        """
        Initialize the GitHubUtils object.

        Args:
            urls (list): A list of repository URLs to clone.
            path (str, optional): The path to the directory where the repositories should be cloned. Defaults to None.
        """
        try:
            self.urls = config.GIT_CLONE_URLS
            
            git_initialization = ['git config --global core.longpaths true',
                                  f'git config --global user.name "{config.GIT_USERNAME}"',
                                  f'git config --global user.email "{config.GIT_EMAIL}"',
                                  ]
            run_terminal_commands(cmd_list=git_initialization)
            os.environ["GH_TOKEN"] = config.TOKEN
            # TODO : set git credentials as well either here or in config

            self.path = os.path.join(os.getcwd(), "Repos")
            if os.path.exists(self.path):
                self.remove_repo()
            os.mkdir(self.path)
            os.chdir(self.path)
            for url in self.urls:
                run_terminal_commands(cmd=f"git clone {url}")
        except Exception as e:
            data = {
                "path": path
            }
            handle_exception("Error in GitHubUtils Constructor", data, e, traceback.print_exc(), error_code=0)


    def get_files_changed(self, commit_id: str) -> List[str]:
        """
        Get the list of files changed in a specific commit.

        Args:
            commit_id (str): The ID of the commit.

        Returns:
            list: A list of file paths that were changed in the commit.
        """
        try:
            cmd = f'git diff-tree --no-commit-id --name-only -r {commit_id}'
            logging.info(f"Command to fetch changed files: {cmd}")
            cmd_run = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True, check=False)
            logging.info(f"Changed files: {cmd_run.stdout}")
            logging.error(f"Error in fetching changed files: {cmd_run.stderr}")
            return cmd_run.stdout.split('\n')[:-1]
        except subprocess.CalledProcessError as e:
            data = {'commit id': commit_id}
            handle_exception("Error while fetching changed files list with commit id", data, e, traceback.print_exc(), error_code=0)
        except Exception as e:
            data = {'commit id': commit_id}
            handle_exception("Error while fetching changed files list with commit id", data, e, traceback.print_exc(), error_code=0)


    def git_checkout_and_pull(self, branch_name: str) -> None:
        """
        Checkout to a specific branch and pull the latest changes.

        Args:
            branch_name (str): The name of the branch.
        """
        try:
            commands = [f'git checkout {branch_name}', 'git pull']
            run_terminal_commands(cmd_list=commands)
        except Exception as e:
            data = {'branch name': branch_name}
            handle_exception("Error while git checkout and pull", data, e, traceback.print_exc(), error_code=0)


    def git_add_commit(self, msg: str) -> None:
        """
        Add all changes to the staging area and commit them.

        Args:
            msg (str): The commit message.
        """
        try:
            commands = ['git add .', f'git commit -m "{msg}"']
            run_terminal_commands(cmd_list=commands)
        except Exception as e:
            data = {"commit msg": msg}
            handle_exception("Error while git commit", data, e, traceback.print_exc(), error_code=0)


    def pull_push(self) -> None:
        """
        Pull the latest changes from the remote repository and push local changes.
        """
        try:
            commands = ['git pull', 'git push']
            run_terminal_commands(cmd_list=commands)
        except Exception as e:
            handle_exception("Error while git pull and push", {}, e, traceback.print_exc(), error_code=0)


    def get_files_to_ignore(self, commit_msg: str) -> list:
        """
        Parse the commit message to find any files that should be ignored.

        Args:
            commit_msg (str): The commit message.

        Returns:
            list: A list of file paths to ignore.
        """
        try:
            flag = '--skip'
            flag_ind = commit_msg.find(flag)
            if flag_ind != -1:
                content_after_skip = commit_msg[flag_ind + len(flag):].strip()
                return content_after_skip.split(' ')
            return []
        except Exception as e:
            data = {'commit msg': commit_msg}
            handle_exception("Error while parsing skip flag", data, e, traceback.print_exc(), error_code=0)
            return []


    def checkout_commit_raise_PR(self, source_branch: str, refactor_branch: str, username: str, title_message: str) -> str:
        """
        Checks out a new branch, commits changes, and raises a pull request (PR) after closing any existing PRs to the source branch.

        Args:
            source_branch (str): The name of the source branch to base the new PR on.
            refactor_branch (str): The name of the new branch for the refactored code.
            username (str): The GitHub username of the reviewer.
            title_message (str): The title message for the PR.

        Returns:
            str: Returns the PR URL if successful, otherwise an empty string.
        """
        try:
            # Delete previous PR, if exists
            pr_list_cmd = f'gh pr list --base "{source_branch}"'
            ans = subprocess.run(shlex.split(pr_list_cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
            output = ans.stdout
            pr_numbers = [line.split()[0] for line in output.strip().split('\n') if line]
            
            print(f"PR list: {pr_numbers}")
            for pr_number in pr_numbers:
                subprocess.run(shlex.split(f"gh pr close {pr_number}"), check=True)

            # Label details
            label = "PR Reviewer"
            label_color = "82D882"

            subprocess.run(
                shlex.split(f'gh label create "{label}" --color {label_color} --description "Label for PR reviewer GitHub Pipeline" --force'),
                check=True
            )

            # Prepare PR body
            pr_body = title_message.replace('"', '\\"')  # Escape double quotes in the body

            pr_cmd = shlex.split(f"""
                gh pr create 
                --title "Refactored Code for {source_branch}"
                --body "{pr_body}"
                --base {source_branch} 
                --head {refactor_branch}
                --reviewer "{username}" 
                --label "{label}"
            """)

            print(f"PR command: {' '.join(pr_cmd)}")

            process = subprocess.run(pr_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            pr_url = process.stdout.strip()
            print(f"Pull request URL: {pr_url}")
            return pr_url

        except subprocess.CalledProcessError as e:
            print(f"Error in PR creation: {e.stderr}")
            return None
        except Exception as e:
            data = {'source branch': source_branch, "refactor branch": refactor_branch}
            handle_exception("Error in committing and raising PR", data, e, traceback.print_exc(), error_code=0)
            return None


    def remove_repo(self) -> bool:
        """
        Remove the cloned repository.

        Returns:
            bool: True if the repository was successfully removed, False otherwise.
        """
        try:
            if os.path.exists(self.path):
                os.chdir(os.path.abspath(os.path.join(self.path, os.pardir)))
                if os.name == 'nt':
                    run_terminal_commands(cmd_list=[f'rmdir /S /Q "{self.path}"'])
                else:
                    run_terminal_commands(cmd_list=['whoami', 'ls', f'rm -rf {self.path}'])
                return True
            return False
        except Exception as e:
            data = {'repo_path': self.path}
            handle_exception("Error in removing repo", data, e, traceback.print_exc(), error_code=0)
            return False


    def get_changed_content(self, commit_id: str):
        """Fetches the detail for provided commit id.

        Args:
            commit_id (str): ID of the commit for which data has to be fetched
        
        Returns:
            str: Details for provided commit id | Empty string when failed to fetch.
        """
        try:
            cmd = f"git show {commit_id}"
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True, check=False)
            filtered_output = '\n'.join(result.stdout.splitlines()[3:])
            return filtered_output
        except subprocess.CalledProcessError as e:
            data = {'commit id': commit_id}
            handle_exception("Error while fetching details from commit id", data, e, traceback.print_exc(), error_code=0)
            return ''
        except Exception as e:
            data = {'commit id': commit_id}
            handle_exception("Error while fetching details from commit id", data, e, traceback.print_exc(), error_code=0)
            return ''
