import os
import re
import uuid
import random
import traceback
import subprocess

from openai import AzureOpenAI

from config import PythonConfig
from utils.utils import run_terminal_commands, handle_exception
from Enums.Enum_data import StatusCodes, PythonAssistants
from VERTEX_CODE.EGPT_AI import error_to_message
from HelperClasses.Project import Project
from utils.GitHubUtils import GitHubUtils
from utils.utils import update_readme


def post_feedback_test_pipeline():
    """docstring"""
    pass


def post_feedback_refactor_pipeline():
    """docstring"""
    pass




def process_undeclared_elements_python(output: str) -> str:
    """
    Process the output of a code analysis tool to extract undeclared elements.

    Args:
        output (str): The output from the code analysis tool.

    Returns:
        str: Comma-separated string of undeclared elements.
    """
    try:
        undeclared_elements = []

        # Split the output into lines
        lines = output.split('\n')

        # Regular expression to match lines containing undeclared elements
        undeclared_pattern = re.compile(r'.*undefined name \'([^\']+)\' \[pyflakes\].*')

        for line in lines:
            match = undeclared_pattern.match(line)
            if match:
                undeclared_elements.append(match.group(1))

        unique_elements = set(undeclared_elements)
        combined_elements = ', '.join(unique_elements)

        return combined_elements
    except Exception as e:
        data = {"output": output}
        handle_exception("Error in process undeclared element function", data, e, traceback.print_exc(), error_code=0)


def error_check(code: str) -> tuple:
    """
    Check Python code for errors and return error messages along with status codes.

    Args:
        code (str): The Python code to check.

    Returns:
        tuple: A tuple containing a dictionary with error information and a status code.

    """
    response_packet = {}
    try:
        filename = f"error_check_{str(uuid.uuid4())}.py"
        with open(filename, 'w', encoding="utf-8") as code_file:
            code_file.write(code)
        path_of_file = os.path.dirname(os.path.abspath(filename))
        os.chdir(path_of_file)
        
        # performing beautification on beaitification on code. 
        cmd = ['black', filename]
        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
            print(result.stdout)
        except Exception as e:
            print("Error while running black code check", e)

        try:
            with open(filename, "r", encoding="utf-8") as file:
                code = file.read()
            compile(code, filename, "exec")
        except SyntaxError as e:
            error_line = code.splitlines()[e.lineno - 1]
            err_msg = "Found syntax errors in the code :" + error_line
            ai_response = error_to_message(err_msg, code, "Python", PythonConfig)
            # print(ai_response)
            response = {"error": ai_response}
            return response, StatusCodes.COMPILE_ERROR.value

        cmd = ['pylama', filename]
        try:
            try:
                result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
            except subprocess.CalledProcessError as e:
                data = {}
                handle_exception("Error while running pylama code check", data, e, traceback.print_exc(), error_code=0)
            except Exception as subporcess_error:
                print("Subprocess error: ", subporcess_error)

            output = result.stdout

            undeclared_elements = process_undeclared_elements_python(output)

            if "ERROR" in output or undeclared_elements:
                err_msg = "Found undeclared elements in the code : " + undeclared_elements
                ai_response = error_to_message(err_msg, code, "Python", PythonConfig)
                print(ai_response)
                response_packet["answer"] = ai_response
                response = {"error": ai_response}
                return response, StatusCodes.COMPILE_ERROR.value

        except Exception as pylint_exception:
            print("pylint error:", pylint_exception)
            err_msg = "Error - there was an error with Pylint analysis"
            response_packet["answer"] = err_msg
            return response_packet, StatusCodes.COMPILE_ERROR.value

        err_msg = "No syntax errors"
        response = {"error": err_msg}
        return response, StatusCodes.SUCCESS.value

    except Exception as e:
        data = {"code (truncated)": code[:20]}
        handle_exception("Error in error check python", data, e, traceback.print_exc(), error_code=0)
        return {"status": "failed", "error": str(e)}, StatusCodes.INTERNAL_SERVER_ERROR.value
    finally:
        os.remove(filename)
        print("Temp error check file deleted")


def run_testcases(original_code: str, original_filename: str, test_code: str) -> tuple[str, int]:
    """
    Run unit tests on the provided code.

    Args:
    - original_code (str): The original code to be tested.
    - original_filename (str): The name of the file containing the original code.
    - unit_test_filename (str): The name of the file containing the unit tests.

    Returns:
    - output (str): The result of running the unit tests.
    - status (int): Status code indicating success or error.
    """
    try:

        testing_file = f"{original_filename}_run_unittest.py"
        code = f"""{original_code} \n\n\n {test_code}"""

        print("final code \n", code)
        # TODO : add __init__.py file to create the folder package
        with open(testing_file, 'w', encoding="utf-8") as f:
            f.write(code)
            print("Testing File Created")
        print("Check testing file content and try to run it")

        cmd = ['pytest', '-v', testing_file]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True, check=False)

        output = result.stdout
        error = result.stderr

        print('Test Cases Result', output)
        print('Test Cases Error', error)
        # with open(f"{original_filename}_unittest_result.txt", 'w', encoding="utf-8") as temp_file:
        #     temp_file.write(output)

        return output, StatusCodes.SUCCESS.value
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return {"status": "failed", "error": str(e)}, StatusCodes.COMPILE_ERROR.value
    finally:
        os.remove(testing_file)
        print("Temp error check file deleted")


def post_refactor_unittest(refactored_code_list: list, test_case_list: list, changed_files: list,
                           git_utils: GitHubUtils, source_branch: str, username: str) -> tuple:
    """
    Handle post-refactor and unit test process.

    Args:
        refactored_code_list (list): List of tuples containing refactored code and status code.
        test_case_list (list): List of tuples containing test cases and status code.
        changed_files (list): List of changed files.
        git_utils (GitHubUtils): GitHub utility object.
        source_branch (str): Source branch for the refactoring.
        username (str): Name of the user who triggered pipeline

    Returns:
        tuple: A tuple containing a dictionary with the operation's status and a status code.

    """
    try:
        print("Post pipeline starts")
        refactor_branch = "refactor_" + source_branch + "_" + str(random.randint(1, 9999))
        original_code = ""
        error_list = {
            "error_in_original_code": {},
            "error_in_refactored_code": {},
            "error_in_unittest_code": {}
        }
        test_folder = "TestCases"
        if not os.path.exists(test_folder):
            os.mkdir(test_folder)
        base_path = os.getcwd()
        success_list = []
        for i, changed_file in enumerate(changed_files):
            os.chdir(base_path)
            # Error check on original code
            with open(changed_file, "r", encoding="utf-8") as f:
                previous_code = f.read()
            original_code = previous_code
            original_filename = os.path.basename(changed_file)
            original_file_name_without_extension = os.path.splitext(original_filename)[0]
            ext = changed_file.split(".")[1]
            ans, status_code = error_check(previous_code)
            print("prev code error check", ans)
            # ans, status_code = {'success'}, StatusCodes.SUCCESS.value
            if status_code != StatusCodes.SUCCESS.value:
                error_list["error_in_original_code"][original_filename] = ans["error"][1:-1]


            # Writing refactored code and error check
            refactored_code,explanations, status_code = refactored_code_list[i]
            # print("refactored code", refactored_code)
            if status_code == StatusCodes.SUCCESS.value:
                ans, error_check_status_code = error_check(refactored_code)
                print("Refactor Error Check ---\n", ans)
                if error_check_status_code != StatusCodes.SUCCESS.value:
                    error_list["error_in_refactored_code"][original_filename] = ans["error"][1:-1]
                else:
                    with open(changed_file, "w", encoding="utf-8") as f:
                        f.write(refactored_code)
                    success_list.append(original_filename)
            else:
                error_list["error_in_refactored_code"][original_filename] = ans["error"][1:-1]

            os.chdir(test_folder)
            # Writing test case and error check
            test_case, status_code = test_case_list[i]
            if status_code == StatusCodes.SUCCESS.value:
                ans, error_check_status_code = error_check(test_case)
                print("Unit-test Error Check ---\n", ans)
                error_check_status_code = StatusCodes.SUCCESS.value

                if error_check_status_code != StatusCodes.SUCCESS.value:
                    error_list["error_in_unittest_code"][original_filename] = ans["error"][1:-1]
                else:
                    unit_test_file_name = original_file_name_without_extension + "_unittest." + ext
                    with open(unit_test_file_name, "w", encoding="utf-8") as file:
                        file.write(test_case)
                    os.chdir(base_path)
                    file_name_for_test_case = changed_file.split(".")[0] + "_temp"
                    testcase_result, run_testcases_status_code = run_testcases(original_code,file_name_for_test_case, test_case)
                    if run_testcases_status_code == StatusCodes.SUCCESS.value:
                        success_list.append(unit_test_file_name)
                    else:
                        error_list["error_in_unittest_code"][original_filename] = testcase_result[["error"][1:-1]]
                    os.chdir(test_folder)
                    with open(f"{original_filename}_unittest_result.txt", 'w', encoding="utf-8") as temp_file:
                        temp_file.write(testcase_result)

            else:
                error_list["error_in_unittest_code"][original_filename] = test_case

        os.chdir(base_path)
        run_terminal_commands(cmd=f"git checkout -b {refactor_branch}")
        git_utils.git_add_commit("Refactored code updated")
        run_terminal_commands(cmd=f"git push origin {refactor_branch}")

        label = "PR Reviewer"
        label_color = "82D882"  # Remove the '#' from the hex color code

        # Create or update the label
        run_terminal_commands(cmd=f'gh label create "{label}" '
                                f'--color {label_color} '
                                f'--description "Label for PR reviewer GitHub Pipeline" '
                                f'--force')

        pr_cmd = f"gh pr create --title \"**Refactored Code for {source_branch}\" \
                            --body \"**Refactored Code for {source_branch}\" --base {source_branch}\
                            --head {refactor_branch} --reviewer \"{username}\" --label \"{label}\""
                            
                            
        process = subprocess.run(pr_cmd, shell=True, check=False, capture_output=True, text=True)
        pr_url = process.stdout.strip()
        print("Pull request URL:", pr_url)

        return {"status": "Pipeline completed successfully", "Pull Request URL": pr_url, "success": success_list,
                "errors": error_list}, StatusCodes.SUCCESS.value

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
        # add authorization
        PythonConfig.set_creds(data['repo_name'], data["pat"], data["organization"])
        git_utils = GitHubUtils(config=PythonConfig)
        os.chdir(data["repo_name"])
        repo_directory = os.getcwd()
    
        project = Project(PythonConfig, git_utils)
        file_extensions = PythonConfig.FILE_EXTENSIONS

        if flow == "normal":
            refactored_code_list, test_case_list, changed_files, readme_status = project.refactor_unittest_pipeline(data, file_extensions=file_extensions, repo_directory=repo_directory, assistants=PythonAssistants)
            ans, status_code = post_refactor_unittest(refactored_code_list, test_case_list, changed_files, git_utils, data["branch"], data['user_name'])
        elif flow == "feedback_refactor":
            post_feedback_refactor_pipeline()
        elif flow == "feedback_test":
            post_feedback_test_pipeline()
        else:
            ans = {"status": "Wrong flow defined. pls choose from 'normal', 'feedback_refactor' or 'feedback_test'"}
            status_code = StatusCodes.WRONG_PAYLOAD_DATA

        return ans, status_code
    except Exception as e:
        handle_exception("Error", data, e, traceback.print_exc(), error_code=0)
        ans["status"] = "failed"
        return ans, StatusCodes.INTERNAL_SERVER_ERROR.value
    finally:
        # send objects to garbage
        git_utils.remove_repo()
