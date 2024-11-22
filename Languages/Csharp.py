import os
import traceback

from utils.utils import run_terminal_commands, handle_exception, authorize_azure_user
from Enums.Enum_data import StatusCodes
from HelperClasses.Project import Project
from utils.GitHubUtils import GitHubUtils


def post_test_pipeline(test_case_list, changed_files, git_utils):
    pass
   
def post_feedback_test_pipeline():
    pass

def post_feedback_refactor_pipeline():
    pass

def error_check():
    pass

def post_refactor_pipeline(refactored_code_list, changed_files, git_utils):
    try:
        # git_utils.git_checkout_and_pull(CsharpConfig.REFACTOR_BRANCH)
        # i = 0
        # for file_path in changed_files:
        #     with open(file_path, 'w') as file:
        #         file.write(refactored_code_list[i][0])
        #     i+=1
        # git_utils.git_add_commit('updated file')
        # print('changes commited')
        # git_utils.pull_push()
        return True, StatusCodes.SUCCESS.value
    except Exception as e: # TODO handle specific exceptions
        pass


def main_function(data, flow):
    try:
        # authorised, status_code = authorize_azure_user(data["pat"], data["repo_name"], CsharpConfig)
        # if not authorised:
        #     return {'status': 'You are not authorized'}, status_code
        # input('authorization done')
        
        # git_utils = GitHubUtils(CsharpConfig.GIT_CLONE_URLS, path=CsharpConfig.BASE_PATH)
        # project = Project(CsharpConfig, git_utils)

        # if flow == "refactor":
        #     refactored_code_list, changed_files = project.refactor_pipeline(commit_id=data["commit id"], commit_msg=data['commit msg'],
        #                                                                      file_extention=".cs", repo_name=CsharpConfig.REPO_NAME)
        #     input('refactoring pipeline executed')
        #     status, status_code = post_refactor_pipeline(refactored_code_list, changed_files, git_utils)
        #     input('post refactoring work done')
        # elif flow == "test":
        #     test_case_list, changed_files = project.unit_test_pipeline(commit_id=data["commit id"], commit_msg=data['commit msg'],
        #                                                                      file_extention=".cs", repo_name=CsharpConfig.REPO_NAME)
        #     post_test_pipeline(test_case_list, changed_files, git_utils)
        # elif flow == "feedback_refactor":
        #     post_feedback_refactor_pipeline()
        # elif flow == "feedback_test":
        #     post_feedback_test_pipeline()
        # else:
        #     return {"status": "Wrong flow defined. pls choose from \
        #             'refactor', 'test', 'feedback_refactor' or 'feedback_test'"}, StatusCodes.WRONG_PAYLOAD_DATA
        
        # error_check()

        # # send objects to garbage
        # git_utils.remove_repo()
        # input('repo removed')
        pass
    except Exception as e:
        handle_exception("Error", data, e, traceback.print_exc(), error_code=0)
