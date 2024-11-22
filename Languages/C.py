import random
import os
import random
import tempfile
import traceback
import subprocess
import shutil
import json
import threading
from time import sleep


from config import CConfig
from HelperClasses.Project import Project
from utils.GitHubUtils import GitHubUtils
from Enums.Enum_data import StatusCodes, CAssistant
from utils.utils import handle_exception, run_terminal_commands
from VERTEX_CODE.EGPT_AI import error_to_message
from VERTEX_CODE.Pipelines_AI import long_code_refactor
from HelperClasses.Compiler import Compiler
from Enums.Enum_data import StatusCodes
from utils.FolderUtils import FolderUtils


def post_feedback_refactor_pipeline():
    pass


def post_feedback_test_pipeline():
    pass


def fun():
    task_id = str(random.randint(1, 100))
    compiler_name = "c-compiler-3889"
    gcc_11 = Compiler(task_id, compiler_name)
    ans = gcc_11.run_command_in_compiler("gcc /opt/12345/Factorial.c -o /opt/12345/Factorial | /opt/12345/Factorial")
    print(ans)
    print(ans.json())
    print(ans.text)
    print(ans.status_code)


def upload_files_to_compiler(changed_files, refactored_code_list, compiler):
    prev_path = os.getcwd()
    new_folder = "new_folder"+str(random.randint(1, 100))
    files_to_upload = []
    try:
        os.mkdir(new_folder)
        os.chdir(new_folder)
        for changed_file, explanations, code in zip(changed_files, refactored_code_list):
            file_name = os.path.basename(changed_file)
            with open(file_name, "w", encoding="utf-8") as code_file:
                code_file.write(code)
            files_to_upload.append(
                ("files", (file_name, open(file_name, "rb"), 'application/octet-stream'))
            )
        response = compiler.upload_files(files_to_upload)
        print("File upload response", response.text)
        print("status code", response.status_code)
        if response.status_code == 200:
            path = response.json()["message"]
            print("here is the path", path)
            return path, StatusCodes.SUCCESS.value
        return "", response.status_code
    except Exception as e:
        pass
    finally:
        FolderUtils.delete_folder(new_folder)
        os.chdir(prev_path)


def c_error_check(file_name, path, compiler):
    try:
         file_name_without_exension = os.path.splitext(file_name)[0]
         command = f"gcc {path}{file_name} -o {path}{file_name_without_exension} | {path}{file_name_without_exension}"
         responce = compiler.run_command_in_compiler(command)
         return responce.json(), responce.status_code
    except Exception as e:
        pass
    finally:
        pass



def post_refactor_unittest(refactored_code_list, test_case_list, changed_files, git_utils,
                           source_branch, username):
    try:
        refactor_branch = "refactor_" + source_branch + "_" + str(random.randint(1, 9999))
        original_code = ""
        error_list = {
            "error_in_original_code": {},
            "error_in_refactored_code": {},
            "error_in_unittest_code": {}
        }
        base_path = os.getcwd()
        compiler_name = CAssistant.COMPILER.value
        task_id = str(random.randint(1, 100))
        gcc_11 = Compiler(task_id, compiler_name)
        retry = 3
        status_code = 0
        while status_code!=StatusCodes.SUCCESS.value or retry<=0:
            path, status_code = upload_files_to_compiler(changed_files, refactored_code_list, gcc_11)
            retry -= 1
        if status_code!=StatusCodes.SUCCESS.value:
            return {"status": "Compiler in heavy load"}, StatusCodes.EMPTY_RESPONSE.value

        success_list = []
        for i, changed_file in enumerate(changed_files):
            output, status_code = c_error_check(changed_file, path, gcc_11)
            print("output", output)
            print("status code", status_code)
        return {"status": "Pipeline completed successfully"}, StatusCodes.SUCCESS.value
    
    except Exception as e:
        data = {
            "changed files list": changed_files,
            "source branch": source_branch
        }
        handle_exception("Error in post refactor unittest work", data, e, traceback.print_exc(), error_code=0)
        return {"status": "failed"}, StatusCodes.INTERNAL_SERVER_ERROR.value
    finally:
        pass


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
        CConfig.set_creds(data["repo_name"], data["pat"], data["organization"])
        git_utils = GitHubUtils(config=CConfig)
        os.chdir(data["repo_name"])
        c_project = Project(CConfig, git_utils)
        file_extensions = CConfig.FILE_EXTENSIONS

        if flow == "normal":
            refactored_code_list, test_case_list, changed_files = c_project.refactor_unittest_pipeline(
                data, file_extensions=file_extensions, assistants=CAssistant
            )
            ans, status_code = post_refactor_unittest(refactored_code_list, test_case_list, changed_files, git_utils,
                                                    data["branch"], data["user_name"])
        elif flow == "feedback_refactor":
            post_feedback_refactor_pipeline()
        elif flow == "feedback_test":
            post_feedback_test_pipeline()
        else:
            ans = {"status": "Wrong flow defined. pls choose from 'normal', 'feedback_refactor' or 'feedback_test'"}
            status_code = StatusCodes.WRONG_PAYLOAD_DATA
        return ans, status_code        
    except Exception as e:
        handle_exception("Error in main function of JavaScript File", data, e, traceback.print_exc(), error_code=0)
        ans["status"] = "failed"
        return ans, StatusCodes.INTERNAL_SERVER_ERROR.value
    finally:
        # send objects to garbage
        git_utils.remove_repo()

