import logging
import os
import random
import tempfile
import traceback
import subprocess
import shutil
import json
import threading
import requests
from typing import Dict, List
import traceback
import hashlib
from config import DocumentConfig
from HelperClasses.Project import Project
from utils.GitHubUtils import GitHubUtils
from Enums.Enum_data import StatusCodes, TypescriptAssistants
from utils.utils import handle_exception, run_terminal_commands
from VERTEX_CODE.EGPT_AI import error_to_message
from VERTEX_CODE.Pipelines_AI import long_code_refactor


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')



def get_files_diff_ssh_list(owner: str, repo: str, pull_request: int, token: str, changed_files_list: list) -> list:
    """
    Generate GitHub diff links for files in a pull request and return as dictionaries with paths and hashes.

    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.
        pull_request (int): The pull request number.
        token (str): GitHub personal access token for authentication.
        changed_files_list (list): List of file paths to include in the result.

    Returns:
        list: A list of dictionaries with "path" and "hash" for each file.
    """
    try:
        result = []
        url = "https://api.github.com/graphql"
        headers = {"Authorization": f"Bearer {token}"}

        query = """
        query ($owner: String!, $repo: String!, $pullRequest: Int!, $endCursor: String) {
        repository(owner: $owner, name: $repo) {
            pullRequest(number: $pullRequest) {
            files(first: 100, after: $endCursor) {
                totalCount
                pageInfo {
                endCursor
                hasNextPage
                }
                nodes {
                path
                }
            }
            }
        }
        }
        """    

        variables = {
            "owner": owner,
            "repo": repo,
            "pullRequest": pull_request,
            "endCursor": None,
        }

        file_paths = []

        while True:
            response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
            response.raise_for_status()
            data = response.json()

            nodes = data["data"]["repository"]["pullRequest"]["files"]["nodes"]
            file_paths.extend(node["path"] for node in nodes)

            page_info = data["data"]["repository"]["pullRequest"]["files"]["pageInfo"]
            if not page_info["hasNextPage"]:
                break
            variables["endCursor"] = page_info["endCursor"]

        filtered_files = [path for path in file_paths if path in changed_files_list]

        for path in filtered_files:
            sha256_hash = hashlib.sha256(path.encode("utf-8")).hexdigest()
            diff_link = f"https://github.com/{owner}/{repo}/pull/{pull_request}/files#diff-{sha256_hash}"

            result.append({"path": path, "hash_link": diff_link})

        return result

    except Exception as e:
        handle_exception("Error in get_files_diff_ssh_list", locals(), e, traceback.format_exc(), error_code=0)
        return []



def get_final_comment_body(owner: str, repo: str, pull_request: int, 
                         code_explanation_dict: List[Dict], 
                         diff_ssh_dict: List[Dict], 
                         changed_files_list: List[str]) -> str:
    """
    Generates a comprehensive pull request explanation with detailed code changes,
    organizing explanations per file.
    
    Args:
        owner: Repository owner
        repo: Repository name
        pull_request: Pull request number
        code_explanation_dict: List of dictionaries containing code change explanations
        diff_ssh_dict: List of dictionaries containing diff links
        changed_files_list: List of changed file paths
        
    Returns:
        str: Formatted PR explanation
    """
    try:
        comment_body = "# 🔍 Pull Request Change Analysis\n\n"
        
        diff_link_map = {item['path']: item['hash_link'] for item in diff_ssh_dict}
        
        for explanation in code_explanation_dict:
            changes_list = explanation.get('changes', [])
            
            for file_path in changed_files_list:
                comment_body += f"## 📁 `{file_path}`\n\n"
                diff_link = diff_link_map.get(file_path, '#')
                
                overview = explanation.get('overview', {})
                detailed_explanation = overview.get('detailed_explanation', 'No detailed explanation provided')
                

                comment_body += "### 🔎 Changes Overview\n"
                comment_body += f"{detailed_explanation}\n\n"
                
                comment_body += "### 🛠 Implementation Details\n\n"
                
                for change in changes_list:
                    type_emoji = {
                        'feature': '✨',
                        'refactor': '♻️',
                        'enhancement': '⚡',
                        'removal': '🗑️',
                    }.get(change['type'], '📝')
                    
                    comment_body += (
                        f"#### {type_emoji} Change from Lines {change['line_start']}-{change['line_end']} "
                        f"[View Diff]({diff_link}R{change['line_start']})\n"
                        f"- **What Changed:** {change['summary']}\n"
                        f"- **Type:** `{change['type']}`\n\n"
                    )
                
                comment_body += "---\n\n"
        
        comment_body += (
            "## 📊 Change Statistics\n"
            f"- Total files modified: {len(changed_files_list)}\n"
            f"- Repository: {owner}/{repo}\n"
            f"- Pull Request: #{pull_request}\n"
        )
        
        return comment_body
    
    except Exception as e:
        error_msg = f"Error generating PR explanation: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        return f"⚠️ {error_msg}"
    
    
def publish_comment_on_pr(owner: str, repo: str, pull_request: int, comment_body: str, token: str) -> bool:
    try:
        url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pull_request}/comments"

        payload = json.dumps({
        "body": f"{comment_body}"
        })
        headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': f'Bearer {token}',
        'X-GitHub-Api-Version': '2022-11-28',
        'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        logging.info(f"Response: {response.text}")
        logging.info(f"Response status code: {response.status_code}")
        
        if response.status_code == 201:
            return True
        else:
            return False
    except Exception as e:
        logging.error(f"Error in publish_comment_on_pr: {str(e)}")
        handle_exception("Error in publish_comment_on_pr", locals(), e, traceback.format_exc(), error_code=0)
        return False
    
    

def post_document_pipeline(data: dict, code_explanation_dict: dict, changed_files_list: list) -> tuple:
    try:
        
        logging.info("In post_document_pipeline")
        logging.info(f"Changed files list: {changed_files_list}")
        
        logging.info(f"Pull request number: {data['pull_request_number']}")
        logging.info(f"Organization: {data['organization']}")
        logging.info(f"Repo name: {data['repo_name']}")
        logging.info(f"token: {data['pat']}")
        
        diff_ssh_dict = get_files_diff_ssh_list(data['organization'], data['repo_name'], data['pull_request_number'], data['pat'], changed_files_list)
        
        
        logging.info(f"Diff SSH dict: {diff_ssh_dict}")
        
        
        comment_body = get_final_comment_body(data['organization'], data['repo_name'], data['pull_request_number'], code_explanation_dict, diff_ssh_dict, changed_files_list)
        
        logging.info(f"Comment body: {comment_body}")
        
        
        comment_publish_status = publish_comment_on_pr(data['organization'], data['repo_name'], data['pull_request_number'], comment_body, data['pat'])
        if not comment_publish_status:
            return {"status": "failed"}, StatusCodes.INTERNAL_SERVER_ERROR.value
        
        
        return {"status": "success", "comment_body": comment_body}, StatusCodes.SUCCESS.value
    
    except Exception as e:
        handle_exception("Error in post_document_pipeline", data, e, traceback.print_exc(), error_code=0)
        return {"status": "failed"}, StatusCodes.INTERNAL_SERVER_ERROR.value
    
    

def main_function(data: dict, flow: str) -> tuple:
    """
    Orchestrates different pipelines based on the provided flow.

    Args:
        data (dict): Dictionary containing necessary data for the operation.
        flow (str): Flow of the operation, choose from 'normal', 'feedback_refactor', or 'feedback_test'.

    Returns:
        tuple: A tuple containing a dictionary with the operation's status and a status code.

    """
    ans = {"status": "success"}
    status_code = StatusCodes.SUCCESS.value
    try:
        DocumentConfig.set_creds(data["repo_name"], data["pat"], data["organization"])
        git_utils = GitHubUtils(config=DocumentConfig)
        os.chdir(data["repo_name"])
        document_project = Project(DocumentConfig, git_utils)
        file_extensions = DocumentConfig.FILE_EXTENSIONS

            
        code_explanation_dict, changed_files_list = document_project.document_change_explanation_pipeline(data=data)
        status = StatusCodes.SUCCESS.value

        ans, status_code = post_document_pipeline(data, code_explanation_dict, changed_files_list)
        result = {
            "code_explanation_dict": code_explanation_dict,
            "changed_files_list": changed_files_list,
            "comment_body": ans["comment_body"]
        }
        return result, status_code
    except Exception as e:
        handle_exception("Error in main function of JavaScript File", data, e, traceback.print_exc(), error_code=0)
        ans["status"] = "failed"
        return ans, StatusCodes.INTERNAL_SERVER_ERROR.value
    finally:
        # send objects to garbage
        git_utils.remove_repo()
