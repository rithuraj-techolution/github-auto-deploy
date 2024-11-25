
import subprocess
import traceback
import uuid
from typing import List, Tuple
import  json
import base64
import tiktoken
import requests

from Enums.Enum_data import StatusCodes
from VERTEX_CODE.prompt_storage import get_read_me_prompt
import os
import re

def send_to_ellm_agent(query, system_prompt):
    url = "https://dev-egpt.techo.camp/predict"

    payload = json.dumps({
    "conciergeId": "8c445e42-e6ce-47d4-b8e7-f8b90c9db8ce",
    "conciergeName": "generatereadme",
    "organizationId": "d73b4e26-10f0-4f57-8b11-5a6e33c632b1",
    "organizationName": "techolution",
    "guestId": "techolution-generatereadme-716ccd67-3098-486a-9480-c071566ce53c",
    "userId": "11b17fe5-d3e1-475d-8a7c-35fdc8788fea",
    "userName": "rithuraj nambiar",
    "assistant_type": "normal",
    "question": query,
    "prompt": system_prompt,
    "referenceDocsCount": 19,
    "proposals_file": "",
    "proposals_section": "",
    "proposals_template": "",
    "images": [],
    "model_names": {
        "openai": "gpt-4o-2024-08-06",
        "google": "gemini-1.5-pro-001"
    },
    "isStreamResponseOn": True,
    "is_generative": False,
    "isAgentsOn": False,
    "confidenceScoreThreshold": 90,
    "chatHistory": [],
    "modelType": "bestai",
    "pinecone_index": "techolution-generatereadme",
    "databaseType": "alloydb",
    "database_index": "techolution-generatereadme",
    "isCoPilotOn": True,
    "slack_webhook_url": "",
    "requestId": f"requestId-{uuid.uuid4()}",
    "chatLowConfidenceMessage": "This is a readme file",
    "autoai": "673f3c0b2827327b51fdfdf1",
    "documentRetrieval": "673f3c0b2827327b51fdfdd6",
    "answerEvaluation": "673f3c0b2827327b51fdfddf",
    "bestAnswer": "673f3c0b2827327b51fdfde8",
    "metadata": {
        "userName": "rithuraj nambiar",
        "userEmailId": "rithuraj.nambiar@techolution.com",
        "llm": "gpt-4o-2024-08-06"
    },
    "source": "",
    "target": "",
    "evaluationCriteria": {
        "completeness": {
        "prompt": "Ensure that the 'response' answers the entire user 'question'; including all the necessary information from the 'context'",
        "weightage": 25
        },
        "correctness": {
        "prompt": "Ensure that the 'response' is Correct, and present in the 'context' -> Corectness implies, that the data which was taken from the context, was correctly utilized to give the 'response' -> The answer can also be a mix of some correct parts, along with some incorrect parts. Ensure appropriate scoring for these situations",
        "weightage": 25
        },
        "information overlap": {
        "prompt": "Calculate the degree of information overlap between the provided 'response' and 'context'",
        "weightage": 25
        },
        "relevancy": {
        "prompt": "-> Ensure that the 'response' is related to the user 'question' -> If the 'response' accepts not being able to answer the question, it is still relevant, and should get a score of 9 -> Partially correct answers should still get some points -> Irrespective of the *Correctness*, if the 'response' relates to the user 'question'; it should get a high",
        "weightage": 25
        }
    },
    "include_link": False,
    "isInternetSearchOn": False,
    "intermediate_model": "gpt-4-32k",
    "isSpt": False,
    "sptProject": "gnc",
    "numberOfCitations": 1,
    "sptNote": "Note: The current response is below the confidence threshold. Please use the information carefully.",
    "wordsToReplace": {},
    "number_of_next_query_suggestions": 0,
    "agents": [],
    "isSelfharmOn": False,
    "selfharmDefaultResponse": "",
    "multiAgentToggle": False,
    "useAgent": {},
    "isPlanBeforeOrchestrator": True,
    "isDocumentRetrieval": False,
    "isRESTrequest": False
    })
    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    response = response.json()
    response = response["Answer"]
        

    return response

def update_readme(base_dir, changed_files):
    try:
        root_readme_path = os.path.join(base_dir, "README.md")
        print("Generating README files for the root directory....")
        # Handle the root README
        if not os.path.exists(root_readme_path):
            print(f"Creating README in {base_dir}")
            with open(root_readme_path, "w", encoding="utf-8") as f:
                content = gather_directory_contents(base_dir)
                readme_content = generate_readme_content(content)
                f.write(readme_content)  # Create a README with generated content
        else:
            print(f"Updating root README in {base_dir}")
            content = gather_directory_contents(base_dir)
            readme_content = generate_readme_content(content)
            with open(root_readme_path, "w", encoding="utf-8") as f:
                f.write(readme_content)

        print("Base Directory : ", base_dir)
        # Handle subdirectories
        for root, dirs, files in os.walk(base_dir):
            print("Handling subdirectories... ", root)
            # Exclude hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for dir_name in dirs:
                print("Directory Name - ", dir_name)
                dir_path = os.path.join(root, dir_name)
                readme_path = os.path.join(dir_path, "README.md")

                # Check if README exists
                if not os.path.exists(readme_path):
                    print(f"Creating README in {dir_path}")
                    with open(readme_path, "w", encoding="utf-8") as f:
                        content = gather_directory_contents(dir_path)
                        readme_content = generate_readme_content(content)
                        f.write(readme_content)
                else:
                    # Check if any changed file exists in the current directory
                    for changed_file in changed_files:
                        if os.path.commonpath([dir_path, os.path.join(base_dir, changed_file)]) == dir_path:
                            print(f"Updating README in {dir_path}")
                            content = gather_directory_contents(dir_path)
                            readme_content = generate_readme_content(content)
                            with open(readme_path, "w", encoding="utf-8") as f:
                                f.write(readme_content)
                            break

        return "Successfully updated README files."
    except Exception as e:
        data = {}
        # handle_exception("Error while updating README files", data, e, traceback.print_exc(), error_code=0)
        return "Failed to update README files."


def gather_directory_contents(directory):
    """
    Gather the contents of all files in the specified directory, excluding hidden directories.

    Args:
        directory: The path of the directory.

    Returns:
        str: A concatenated string of all file contents.
    """
    contents = []
    for root, dirs, files in os.walk(directory):
        # Exclude hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if os.path.isfile(file_path):  # Ensure it's a regular file
                try:
                    with open(file_path, 'r', encoding="utf-8") as file:
                        contents.append(f"File: {file_name}\n{file.read()}\n")
                except UnicodeDecodeError:
                    print(f"Error reading file {file_path}: UnicodeDecodeError")
                except Exception as e:
                    print(f"Error reading file {file_path}: {e}")
    return "\n".join(contents)


def generate_readme_content(contents: str) -> str:
    """
    Generate README content based on folder contents.

    Args:
        contents : The contents of the folder.

    Returns:
        str: The generated README content.
    """
    try:
        response = send_to_ellm_agent(system_prompt=get_read_me_prompt(), query=contents)
        return response
    except Exception as e:
        data = {"contents": contents}
        print("Error while generating README content. ", e)
        return "Error generating README content."

def handle_exception(error: str, data: dict, exception: Exception, trace: str, error_code: int = 0) -> None:
    """
    Handles exceptions and prints error details.

    Args:
        error (str): Error message.
        data (dict): Data related to the error.
        exception (Exception): Exception object.
        trace (str): Traceback of the error.
        error_code (int, optional): Error code. Defaults to 0.
    """
    print("################## ERROR ##################")
    print(error)
    print('Data: ', data)
    print('Exception: ', exception)
    print('Traceback: ', trace)
    print('Error Code: ', error_code)
    print("################## ERROR ##################")


def run_terminal_commands(cmd_list: List[str] = None, cmd: str = None) -> None:
    """
    Runs terminal commands.

    Args:
        cmd_list (List[str], optional): List of commands to run. Defaults to None.
        cmd (str, optional): Single command to run. Defaults to None.
    """
    try:
        if cmd:
            subprocess.run(cmd, shell=True, check=False)

        if cmd_list:
            for cmd in cmd_list:
                subprocess.run(cmd, shell=True, check=False)
    except subprocess.CalledProcessError as e:
        data = {}
        handle_exception("Error in executing terminal command", data, e, traceback.print_exc(), error_code=0)
    except Exception as e:
        data = {
            "command list": cmd_list,
            "command": cmd,
        }
        handle_exception("Error while running commands in terminal", data, e, traceback.print_exc(), error_code=0)


def authorize_github_user(pat: str, repo_name: str, config: object) -> Tuple[bool, int]: # TODO modify it for github
    """
    Authorizes access to GitHub using Personal Access Token (PAT).

    Args:
        pat (str): Personal Access Token.
        repo_name (str): Repository name.
        config (object): Configuration object.

    Returns:
        Tuple[bool, int]: Authorization status and status code.
    """
    try:
        url = config.AUTH_URL
        username = config.AUTH_USERNAME

        pat = pat.replace("Basic ", "")
        decoded_token = base64.b64decode(pat).decode('utf-8')

        combined_pat_token = username + decoded_token if decoded_token.startswith(':') else username + ":" + decoded_token

        headers = {
            'Content-Type': "Application/json",
            'Authorization': 'Basic ' + base64.b64encode(combined_pat_token.encode('utf-8')).decode('utf-8')
        }

        response = requests.get(url, headers=headers)
        print('authorization', response.status_code)

        if response.status_code == 200:
            return True, StatusCodes.SUCCESS.value
        else:
            return False, StatusCodes.INVALID_OR_EXPIRED_TOKEN.value
    except Exception as e:
        data = {
            "config class": config
        }
        handle_exception("Error while authorizing github user", data, e, traceback.print_exc(), error_code=0)
        return False, StatusCodes.INTERNAL_SERVER_ERROR.value


def authorize_azure_user(pat: str, repo_name: str, config: object) -> Tuple[bool, int]:
    """
    Authorizes access to Azure API using Personal Access Token (PAT).

    Args:
        pat (str): Personal Access Token.
        repo_name (str): Repository name.
        config (object): Configuration object.

    Returns:
        Tuple[bool, int]: Authorization status and status code.
    """
    try:
        url = config.AUTH_URL
        username = config.AUTH_USERNAME

        pat = pat.replace("Basic ", "")
        decoded_token = base64.b64decode(pat).decode('utf-8')

        combined_pat_token = username + decoded_token if decoded_token.startswith(':') else username + ":" + decoded_token

        headers = {
            'Content-Type': "Application/json",
            'Authorization': 'Basic ' + base64.b64encode(combined_pat_token.encode('utf-8')).decode('utf-8')
        }

        response = requests.get(url, headers=headers)
        print('authorization', response.status_code)

        if response.status_code == 200:
            return True, StatusCodes.SUCCESS.value
        else:
            return False, StatusCodes.INVALID_OR_EXPIRED_TOKEN.value
    except Exception as e:
        data = {
            "config class": config
        }
        handle_exception("Error while authorizing azure user", data, e, traceback.print_exc(), error_code=0)


def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """
    Returns the number of tokens from a string using a specific encoding.

    Args:
        string (str): Input string.
        encoding_name (str): Encoding name.

    Returns:
        int: Number of tokens.
    """
    try:
        encoding = tiktoken.get_encoding(encoding_name)
        num_tokens = len(encoding.encode(string))
        return num_tokens
    except Exception as e:
        data = {
            "string": string,
            "encoding name": encoding_name
        }
        handle_exception("Error while authorizing azure user", data, e, traceback.print_exc(), error_code=0)

def format_coding_standards(data):
    formatted_coding_standards = ""
    for item in data:
        title = item.get("title", "")
        rules = item.get("rules", "")
        severity = item.get("severity", "")
        scope = item.get("scope_option", "")
        formatted_coding_standards += f"Title:{title} Rules:{rules} Severity:{severity} Scope:{scope}\n"

    return formatted_coding_standards, StatusCodes.SUCCESS.value

def get_coding_standards(repo_name):
    appmod_backend_url = "https://dev-appmod.techo.camp/api/get_project_profile"
    print("Repo Name Received - ", repo_name)
    repo_url = f"https://github.com/Techolution/{repo_name}.git"
    print("Repo URL =", repo_url)
    payload = json.dumps({
        "project_url": repo_url
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", appmod_backend_url, headers=headers, data=payload)
    # print(response.status_code, response.text)
    if response.status_code == StatusCodes.SUCCESS.value:
        coding_standard_json = response.json()  # Parse the response as JSON
        print("Coding Standard JSON received - ", coding_standard_json)
        formatted_coding_standards, status_code = format_coding_standards(coding_standard_json)
        if status_code == StatusCodes.SUCCESS.value:
            return formatted_coding_standards
    else:
        return " "
