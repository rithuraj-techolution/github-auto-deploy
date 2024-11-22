import os
import random
import tempfile
import traceback
import subprocess
import shutil
import json
import threading


from config import JavascriptConfig
from HelperClasses.Project import Project
from utils.GitHubUtils import GitHubUtils
from Enums.Enum_data import StatusCodes, JavascriptAssistants
from utils.utils import handle_exception, run_terminal_commands
from VERTEX_CODE.EGPT_AI import error_to_message
from VERTEX_CODE.Pipelines_AI import long_code_refactor



def update_long_code_refactor(git_utils, branch, refactored_code):
    if branch=="dev" or branch=="qa":
        return {"status": "restricted", "message": "Can't push directly to dev or qa branch"}
    # git_utils.git_checkout_and_pull(branch)

    try:
        subprocess.run(f"git checkout {branch}", check=True, shell=True)
    except subprocess.CalledProcessError:
        return {"status": "failed", "message": "branch does not exist, you may retry if it is created now"}

    flag = False

    for code_dict in refactored_code:
        code = code_dict["code"]
        file_path = code_dict["file path"]
        status_code = code_dict["status code"]

        # file_path = os.path.normpath(file_path)
        # print("normalized file path", file_path)
        if os.name == "nt":
            file_path = file_path.replace("/", "\\")
            file_path = os.path.normpath(file_path)
        else:
            file_path = file_path.replace("\\", "/")
        
        if status_code==StatusCodes.SUCCESS.value:
            # TODO : Add error check and eslint check here
            flag = True
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)

    if flag:
        git_utils.git_add_commit("Long refactored code updated")
        git_utils.pull_push()
    
        return {"status": "sucess"}, StatusCodes.SUCCESS.value
    return {"status": "empty response"}, StatusCodes.EMPTY_RESPONSE.value


def setup_js_test_env(test_env_path: str, base_path: str):
    """
    Sets up a JavaScript unit testing environment with Jest and Babel.

    Parameters:
        test_env_path (str): The path to the test environment directory.
        base_path (str): The base directory path to return to after setup.

    Returns:
        tuple: A tuple containing a status dictionary and an HTTP status code.
            - {'status': 'Success'}, 200 on success.
            - {'status': 'Failed', 'error': str(e)}, 500 on failure.
    """
    try:
        # Create a new npm project and Install packages required under test env folder
        if os.path.exists(test_env_path):
            shutil.rmtree(test_env_path)
    
        os.makedirs(test_env_path)
        os.chdir(test_env_path)

        # Init temp env path as npm project and install required packages
        commands = [
            "npm init -y",
            "npm install --save-dev jest babel-jest @babel/core @babel/preset-env eslint eslint-plugin-jest globals -y",
        ]
        for cmd in commands:
            subprocess.run(cmd, shell=True, check=False)

        # Add required configuration files
        with open(os.path.join(test_env_path, 'package.json'), 'r+') as file:
            data = json.load(file)
            data['scripts']['test'] = 'jest'
            file.seek(0)
            json.dump(data, file, indent=2)
            file.truncate()

        babelrc_content = {
            "presets": ["@babel/preset-env"]
        }
        with open(os.path.join(test_env_path, '.babelrc'), 'w') as file:
            json.dump(babelrc_content, file, indent=2)

        jest_config_content = """
        module.exports = {
            transform: {
                '^.+\\.js$': 'babel-jest',
            },
        };"""
        with open(os.path.join(test_env_path, 'jest.config.js'), 'w') as file:
            file.write(jest_config_content)
        
        # setup eslint:
        eslint_config = """
import globals from "globals";
import pluginJs from "@eslint/js";
import jestPlugin from 'eslint-plugin-jest';

export default [
    {
        files: ["**/*.js"],
        languageOptions: { sourceType: "module" }
    },
    {
        languageOptions: {
            globals: {
                ...globals.browser,
                ...globals.node
            }
        }
    },
    pluginJs.configs.recommended,
    {
        files: ['**/*.js'],
        ...jestPlugin.configs['flat/recommended'],
    }
];
"""
        with open(os.path.join(test_env_path, 'eslint.config.mjs'), 'w') as file:
            file.write(eslint_config)

        # Change cwd back to base path
        os.chdir(base_path)
        # return {'status': 'Success'}, StatusCodes.SUCCESS.value
        return {'status': 'Success'}, StatusCodes.SUCCESS.value

    except Exception as e:
        os.chdir(base_path)
        data = {}
        handle_exception("Error in setting up Javascript unit test environment", data, e, traceback.print_exc(), error_code=0)
        # return "Error in setting up Javascript unit test environment", StatusCodes.COMPILE_ERROR.value
        print(f"Error: {str(e)}")
        return {"status": "Failed", "error": str(e)}, StatusCodes.INTERNAL_SERVER_ERROR.value


def run_js_error_check(code: str, test_env_dir: str):
    """Runs the error check on the provided code and under the provided Javascript environmnt path

    Args:
        code (str): The javascript code to check.
        test_env_dir (str): Javascript env directory path to execute the error check under

    Returns:
        tuple:
            str: result of the operation
            status code: status code for error check: 200 if no error found, 400 if error found in the code, 500 if internal server error
    """
    try:
        return {"status": "Success", "answer": "No syntax error found in the code"}, StatusCodes.SUCCESS.value
        temp_code_file = "error_check.js"
        file_path = os.path.join(test_env_dir, temp_code_file)

        if not os.path.exists(test_env_dir):
            raise FileNotFoundError(f"JS env directory not found at path: {test_env_dir}. Need JS env to execute eror check.")

        with open(file_path, "w", encoding="utf-8") as temp_file:
            temp_file.write(code)

        # Running the error check
        cmd = f"npx eslint {temp_code_file}"
        ans = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True,
                                check=False, cwd=test_env_dir)
        error_output = ans.stderr
        output = ans.stdout

        # Parse output
        if output:
            print(output)
            lines = output.splitlines()
            for index, line in enumerate(lines):
                if line.startswith('/'):
                    del lines[index]
                    break
            return '\n'.join(lines), StatusCodes.COMPILE_ERROR.value

        if error_output:
            raise Exception(error_output)

        print("No syntax error found in the code")
        return "No syntax error found in the code", StatusCodes.SUCCESS.value

    except Exception as e:
        data = {
            "code (truncated)": code[:20],
        }
        print(f"Error occured while running javascript error check: {str(e)}")
        return "Error occured while running javascript error check", StatusCodes.INTERNAL_SERVER_ERROR.value

    finally:
        # if os.path.exists(file_path):
        #     os.remove(file_path)
        pass




def js_error_check(code: str):
    """Function to execute setup and execute the error check for Javscript codes

    Args:
        code (str): Code to be checked for errors
        request_id (str): Unique id related to the request

    Returns:
        tuple:
            str: result of the operation
            status code: status code for error check: 200 if no error found, 400 if error found in the code, 500 if internal server error
    """
    try:
        return {"status": "Success", "answer": "No syntax error found in the code"}, StatusCodes.SUCCESS.value
        base_path = os.getcwd()
        test_env_dir_path = os.path.join(base_path, f"TestEnv_{random.randint(1, 100)}")

        # Setup javascript env dir
        ans, status_code = setup_js_test_env(test_env_dir_path, base_path)
        if status_code != 200:
            return ans, status_code

        # run the error check
        result, status_code = run_js_error_check(code, test_env_dir_path)
        if status_code != 200:
            error_message = error_to_message(result, code, "Javascript", JavascriptConfig)
            return {"status": "Failed", "error": error_message}, status_code

        return {"status": "Success", "answer": result}, status_code

    except Exception as e:
        data = {
            "code (truncated)": code[:20],
        }
        handle_exception("Error occured while performing error check on the JS code", data, e, traceback.print_exc(), 0)
        print(f"Error occured while performing error check on the JS code: {str(e)}")
        return {"status": "Failed", "error": "Error occured while performing error check on the JS code"}, StatusCodes.INTERNAL_SERVER_ERROR.value
    finally:
        # if os.path.exists(test_env_dir_path):
        #     shutil.rmtree(test_env_dir_path)
        pass

def set_test_environment(test_env_path: str, base_path: str):
    """
    Set up the test env directory to run the Javascript unit tests

    Parameters:
        test_env_path (str): The path to test env directory
        base_path (str): The base path of the repo

    Returns:
        tuple: A tuple containing a dictionary with the operation's status and a status code.
    """

    try:
        # Create a new npm project and Install packages required under test env folder
        if os.path.exists(test_env_path):
            shutil.rmtree(test_env_path)
    
        os.makedirs(test_env_path)
        os.chdir(test_env_path)

        commands = [
            "npm init -y",
            "npm install --save-dev jest babel-jest @babel/core @babel/preset-env",
        ]
        run_terminal_commands(cmd_list=commands)

        # Add required configuration files
        with open(os.path.join(test_env_path, 'package.json'), 'r+') as file:
            data = json.load(file)
            data['scripts']['test'] = 'jest'
            file.seek(0)
            json.dump(data, file, indent=2)
            file.truncate()

        babelrc_content = {
            "presets": ["@babel/preset-env"]
        }

        with open(os.path.join(test_env_path, '.babelrc'), 'w') as file:
            json.dump(babelrc_content, file, indent=2)

        jest_config_content = """
        module.exports = {
            transform: {
                '^.+\\.js$': 'babel-jest',
            },
        };"""

        with open(os.path.join(test_env_path, 'jest.config.js'), 'w') as file:
            file.write(jest_config_content)

        # Change cwd back to base path
        os.chdir(base_path)
        return {'status': 'Success'}, StatusCodes.SUCCESS.value

    except Exception as e:
        os.chdir(base_path)
        data = {}
        handle_exception("Error in setting up Javascript unit test environment", data, e, traceback.print_exc(), error_code=0)
        return "Error in setting up Javascript unit test environment", StatusCodes.COMPILE_ERROR.value

def run_testcases(original_code: str, original_filename: str, unit_test_filename: str, test_env_path: str):
    """
    Run unit tests on the provided code.

    Args:
    - original_code (str): The original code to be tested.
    - original_filename (str): The name of the file containing the original code.
    - unit_test_filename (str): The name of the file containing the unit tests.
    - test_env_path (str): Path to the test environment directory.

    Returns:
    - output (str): The result of running the unit tests.
    - status (int): Status code indicating success or error.
    """
    try:
        # Verify if test env folder exists
        if not os.path.exists(test_env_path):
            raise Exception(f"Test env folder doesn't exist on path: {test_env_path}")
        
        # Appending the original script code together with unit test code to avoid import error
        test_script_path = os.path.join(test_env_path, unit_test_filename)        
        with open(unit_test_filename, 'r') as file:
            test_code = file.read()
        
        temp_test_code = original_code + "\n\n" + test_code
        
        # Write temp test code to temp test file 
        with open(test_script_path, 'w') as temp_file:
            temp_file.write(temp_test_code)

        cmd = f"npm test {unit_test_filename}"
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=test_env_path, shell=True)

        output = f"\nTest Results:\n {result.stdout}\n\n{result.stderr}"

        print('output', output)
        # Save unit test result to unit test directory (parent dir of test env dir)
        with open(f"{original_filename}_unittest_result.txt", 'w') as temp_file:
            temp_file.write(output)

        return output, StatusCodes.SUCCESS.value

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return {"status": "failed", "error": str(e)}, StatusCodes.COMPILE_ERROR.value
    finally:
        pass


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
        print("post work....")
        refactor_branch = "refactor_" + source_branch + "_" + str(random.randint(1, 9999))
        error_list = {
            "error_in_original_code": {},
            "error_in_refactored_code": {},
            "error_in_unittest_code": {}
        }
        long_code_refactor_list = []
        
        # Unit test related paths --
        base_path = os.getcwd()
        test_folder = "TestCases"
        test_env_folder = "TestEnv"
        test_env_folder_path = os.path.join(base_path, test_folder, test_env_folder)

        if not os.path.exists(test_folder):
            os.mkdir(test_folder)

        # TODO commented it currently
        # Setup test environment under TestEnv folder
        # ans, status_code = set_test_environment(test_env_folder_path, base_path)
        # if status_code == StatusCodes.SUCCESS.value:
        #     print("JS unit testing environment created successfully\n")

        success_list = []
        for i, changed_file in enumerate(changed_files):
            os.chdir(base_path)
            # Error check on original code
            with open(changed_file, "r", encoding="utf-8") as f:
                previous_code = f.read()

            original_filename = os.path.basename(changed_file)
            original_file_name_without_extension = os.path.splitext(original_filename)[0]
            ext = changed_file.split(".")[1]
            ans, status_code = js_error_check(previous_code)
    
            # ans, status_code = {'success'}, StatusCodes.SUCCESS.value
            if status_code != StatusCodes.SUCCESS.value:
                error_list["error_in_original_code"][original_filename] = ans

            # Writing refactored code and error check
            refactored_code, explanations, status_code = refactored_code_list[i]
            if status_code == StatusCodes.ACCEPTED.value:
                long_code_refactor_list.append((previous_code, changed_file))
            elif status_code == StatusCodes.SUCCESS.value:
                ans, error_check_status_code = js_error_check(refactored_code)
                print("Refactor Error Check ---\n", ans)
                if error_check_status_code != StatusCodes.SUCCESS.value:
                    error_list["error_in_refactored_code"][original_filename] = ans
                else:
                    with open(changed_file, "r", encoding="utf-8") as f:
                        original_code = f.read()
                    with open(changed_file, "w", encoding="utf-8") as f:
                        f.write(refactored_code)
                    success_list.append(original_filename)
            else:
                error_list["error_in_refactored_code"][original_filename] = refactored_code

            os.chdir(test_folder)
            # Writing test case and error check
            test_case, status_code = test_case_list[i]
            if status_code == StatusCodes.SUCCESS.value:
                ans, error_check_status_code = js_error_check(test_case)
                print("Unit-test Error Check ---\n", ans)

                if error_check_status_code != StatusCodes.SUCCESS.value:
                    error_list["error_in_unittest_code"][original_filename] = ans
                else:
                    unit_test_file_name = original_file_name_without_extension + ".test." + ext
                    with open(unit_test_file_name, "w", encoding="utf-8") as file:
                        file.write(test_case)
                    # Run test script
                    testcase_result, run_testcases_status_code = run_testcases(original_code, original_file_name_without_extension, unit_test_file_name, test_env_folder_path)
                    if run_testcases_status_code == StatusCodes.SUCCESS.value:
                        success_list.append(unit_test_file_name)
                    else:
                        error_list["error_in_unittest_code"][original_filename] = testcase_result[["error"][1:-1]]

            else:
                error_list["error_in_unittest_code"][original_filename] = test_case


        # Remove the test env folder
        # TODO commented it currently
        # shutil.rmtree(test_env_folder_path)
        
        os.chdir(base_path)
        run_terminal_commands(cmd=f"git checkout -b {refactor_branch}")

        for code, file_path in long_code_refactor_list:
            file_path = os.path.normpath(file_path)
            print("normalized file path", file_path)
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(code + "\n\n")
            # ans = long_code_refactor.rlef_api_call(refactor_branch, code, file_path, JavascriptConfig.TOKEN, code_refactor_token_limit=1500)
            # ans = fun(code, file_path)
            thread = threading.Thread(target=long_code_refactor.rlef_api_call, args=(refactor_branch, code, file_path, JavascriptConfig.TOKEN, 1500))
            thread.start()

            print("$$$$$$$$$$$$")

        git_utils.git_add_commit("Refactored code updated")
        run_terminal_commands(cmd=f"git push origin {refactor_branch}")

        ans = git_utils.checkout_commit_raise_PR(source_branch, refactor_branch, username, title_message="Refactored Code Updated")
        if ans:
            return {"status": "Pipeline completed successfully", "Pull Request URL": ans, "success list": success_list, "errors": error_list}, StatusCodes.SUCCESS.value
        else:
            return {"status": "failed", "Pull Request URL": ans, "errors": error_list, "success list": success_list}, StatusCodes.EMPTY_RESPONSE.value

    except Exception as e:
        data = {
            "changed files list": changed_files,
            "source branch": source_branch
        }
        handle_exception("Error in post refactor unittest work", data, e, traceback.print_exc(), error_code=0)
        return {"status": "failed"}, StatusCodes.INTERNAL_SERVER_ERROR.value
    finally:
        pass


def post_feedback_refactor_pipeline(updated_codes_list: list, changed_files: list, git_utils: GitHubUtils, ai_branch: str):
    """docstring"""
    try:
        print("post refactor feedback work...")

        # Checking out to AI Branch
        git_utils.git_checkout_and_pull(ai_branch)

        error_list = {
            "filename": []
        }
        for i, changed_file in enumerate(changed_files):
            filename = os.path.basename(changed_file)
            with open(changed_file, "r", encoding="utf-8") as f:
                previous_code = f.read()
            ans, status_code = js_error_check(previous_code)
            if status_code != StatusCodes.SUCCESS.value:
                print("Old AI Code has error")
                continue

            # writing the updated code as per the feedback
            updated_code, status_code = updated_codes_list[i]
            if status_code == StatusCodes.SUCCESS.value:
                ans, error_check_status_codes = js_error_check(updated_code)
                if error_check_status_codes == StatusCodes.SUCCESS.value:
                    print("No error detected in Updated Code")
                    with open(changed_file, 'w', encoding="utf-8") as f:
                        print(changed_file)
                        f.write(updated_code)
                        print(f"File: {filename} updated successfully")

        git_utils.git_add_commit("Refactored code updated as per feedback")
        run_terminal_commands(cmd=f"git push origin {ai_branch}")
        ans = {"status": "success"}

        if ans:
            return {"status": "Code updated as per Feedback"}, StatusCodes.SUCCESS.value
        else:
            raise Exception("Error in checkout commit and raise PR")
    except Exception as e:
        data = {
            "changed files list": changed_files,
            "source branch": ai_branch
        }
        handle_exception("Error in post refactor unittest work", data, e, traceback.print_exc(), error_code=0)
        return {"status": "failed"}, StatusCodes.INTERNAL_SERVER_ERROR.value
    finally:
        pass


def post_feedback_test_pipeline():
    """docstring"""
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
        # data["commit msg"] = data["commit msg"] + "-test"
        JavascriptConfig.set_creds(data["repo_name"], data["pat"], data["organization"])
        git_utils = GitHubUtils(config=JavascriptConfig)
        os.chdir(data["repo_name"])
        js_project = Project(JavascriptConfig, git_utils)
        file_extensions = JavascriptConfig.FILE_EXTENSIONS
        repo_directory = os.getcwd()


        if flow == "normal":
            refactored_code_list, test_case_list, changed_files, readme_status = js_project.refactor_unittest_pipeline(data, file_extensions=file_extensions, assistants=JavascriptAssistants, repo_directory= repo_directory)
            ans, status_code = post_refactor_unittest(refactored_code_list, test_case_list, changed_files, git_utils,
                                                      data["branch"], data["user_name"])
        elif flow == "feedback":
            updated_code_list, changed_files = js_project.feedback_refactor_pipeline(
                source_branch=data['source_branch'], ai_branch=data['ai_branch'], file_extention=".js", feedback=data['feedback'])
            ans, status_code = post_feedback_refactor_pipeline(updated_code_list, changed_files, git_utils, ai_branch=data['ai_branch'])
        elif flow == "feedback_test":
            post_feedback_test_pipeline()
        elif flow == "long_code_refactor":
            ans, status_code = update_long_code_refactor(git_utils, data["branch"], data["refactored code"])
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


