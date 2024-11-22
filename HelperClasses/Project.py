
import logging
import os
import traceback
from typing import List, Tuple

from utils.Code_Difference import get_changed_part
from HelperClasses.Interface import Interface
from Enums.Enum_data import StatusCodes
from utils.GitHubUtils import GitHubUtils
from utils.FolderUtils import FolderUtils
from utils.utils import handle_exception, update_readme
from VERTEX_CODE.Pipelines_AI import get_differnce_explanation, perform_refactoring, generate_unit_test, feedback_refactor



logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')



class Project(Interface):
    """
    A class to represent a project.
    """

    def __init__(self, config, git_utils: GitHubUtils) -> None:
        """
        Initialize the Project class.

        Args:
            config: The configuration object.
            git_utils (GitHubUtils): The GitHub utilities object.
        """
        try:
            self.BASE_PATH = config.BASE_PATH
            self.git_utils = git_utils
            self.ans = {'status': 'success'}
            self.file_path = ""
            self.changed_file_path = ""
            self.changed_folder_path = ""
            self.changed_file_name = ""
            self.file_name = ""
            self.parent_folder_name = ""
        except Exception as e:
            data = {
                "config class": config,
                "git utils object": git_utils
            }
            handle_exception("Error in constructor of Project", data, e, traceback.print_exc(), error_code=0)

    def initialize_file_folder_paths(self, file_path: str) -> None:
        """
        Initialize file and folder paths.

        Args:
            file_path (str): The file path.
        """
        try:
            self.file_path = FolderUtils.modify_filepath_for_os(file_path)
            self.changed_file_path = os.path.join(self.BASE_PATH, file_path)
            self.changed_folder_path = os.path.abspath(os.path.join(self.changed_file_path, os.pardir))
            self.changed_file_name = os.path.basename(self.changed_file_path)
            self.file_name = os.path.splitext(self.changed_file_name)[0]
            self.parent_folder_name = os.path.basename(self.changed_folder_path)
        except Exception as e:
            data = {"file path": file_path}
            handle_exception("Error while initializing files and folders name", data, e, traceback.print_exc(), error_code=0)
            
            
    def refactor_unittest_pipeline(self, data: dict, file_extensions: list, repo_directory, assistants) -> Tuple[List[Tuple[str, int]], List[Tuple[str, int]], List[str]]:
        """
        Perform refactoring and unit testing pipeline.

        Args:
            commit_id (str): The commit ID.
            commit_msg (str): The commit message.
            file_extension (list): The file extensions.
            source_branch (str): The source branch.
            assistants: The assistants object.

        Returns:
            Tuple[List[Tuple[str, int]], List[Tuple[str, int]], List[str]]: The refactored code list, test case list, and new changed files list.
        """
        try:
            # extracting data
            repo_name = data['repo_name']
            commit_id=data["commit id"]
            commit_msg=data['commit msg']
            source_branch=data["branch"]
            default_branch=data["default_branch"]


            # get changed files from the source branch
            self.git_utils.git_checkout_and_pull(source_branch)
            files_to_ignore = self.git_utils.get_files_to_ignore(commit_msg)
            if files_to_ignore and files_to_ignore[0].lower()=='all':
                return [], [], []
            changed_files = self.git_utils.get_files_changed(commit_id)
            print("changes files list", changed_files)
            print("Commit message", commit_msg)

            # iterate over changed file to generate refactored code and test cases
            refactored_code_list = []
            test_case_list = []
            new_changed_files = []
            
            for file_path in changed_files:
                self.initialize_file_folder_paths(file_path)
                
                

                # check if current file needs to be processed further
                if (self.changed_file_name in files_to_ignore) or (not any(self.changed_file_name.endswith(ext) for ext in file_extensions)):
                    print(f"File '{self.file_path}' does not have an extension from {file_extensions} or is in the skip list. Skipping refactoring of it.")
                    continue

                # TODO : add skip file flag here with commit msg
                current_file_extension = os.path.splitext(self.changed_file_name)[1]
                new_changed_files.append(self.file_path)
                changed_content = get_changed_part(git_utils= self.git_utils, repo_name=repo_name, default_branch=default_branch, source_branch=source_branch, file_path=self.file_path)
                if "--norefactoring" in commit_msg:
                    refactored_code_list.append(("", StatusCodes.SKIP_PIPELINE.value))
                
                elif "--onlychanged" in commit_msg:
                    refactored_code, explanations_str, status_code = perform_refactoring(data, file_path=self.file_path, assistant_name= assistants.REFACTOR.value,
                                                                       approach="changed content", changed_content= changed_content, file_extension=current_file_extension) # TODO : move this enum data to enum file
                    refactored_code_list.append((refactored_code,explanations_str, status_code))
                    print("refactored code generated for only changed code")
                    
                else:
                    refactored_code,explanations_str, status_code = perform_refactoring(data, file_path= self.file_path, assistant_name=assistants.REFACTOR.value,
                                                                       approach="whole file", changed_content=changed_content, file_extension=current_file_extension) # TODO : move this enum data to enum file
                    refactored_code_list.append((refactored_code,explanations_str, status_code))
                    print("refactored code generated for whole file")

                # check for test flag to skip pipeline
                if "--test" in commit_msg:
                    test_case_code, status_code = generate_unit_test(self.file_path, assistants.UNITTEST.value)
                    test_case_list.append((test_case_code, status_code))
                    print("test code generated")
                else:
                    test_case_list.append(("", StatusCodes.SKIP_PIPELINE.value))
                    
            readme_status = "False"
            data['readme'] = "True"
            if data['readme'] == "True":
                readme_status = update_readme(repo_directory, changed_files)
                
            return refactored_code_list, test_case_list, new_changed_files, readme_status
        except Exception as e:
            data = {
                "commit id": commit_id,
                "commit msg": commit_msg,
                "file extention": file_extensions,
                "source branch": source_branch,
            }
            handle_exception("Error in refactor unittest pipeline", data, e, traceback.print_exc(), error_code=0)
            return [], [], []
        
        
    def document_change_explanation_pipeline(self, data: dict) -> Tuple[dict, int]:
        """
        Perform document pipeline.

        Args:
            data (dict): The data dictionary.

        Returns:
            Tuple[dict, int]: The status dictionary and status code.
        """
        try:
            # extracting data
            repo_name = data['repo_name']
            commit_id = data["commit id"]
            commit_msg = data['commit msg']
            head_branch = data["branch"]
            base_branch = data["default_branch"]
            
            logging.info(f"Commit ID: {commit_id}")
            logging.info(f"Commit Message: {commit_msg}")
            logging.info(f"Head Branch: {head_branch}")
            logging.info(f"Base Branch: {base_branch}")

            # get changed files from the source branch
            self.git_utils.git_checkout_and_pull(head_branch)
            files_to_ignore = self.git_utils.get_files_to_ignore(commit_msg)
            logging.info(f"Files to ignore: {files_to_ignore}")
            
            if files_to_ignore and files_to_ignore[0].lower() == 'all':
                return {"status": "success"}, StatusCodes.SUCCESS.value
            
            changed_files = self.git_utils.get_files_changed(commit_id)

            
            logging.info(f"Changed files: {changed_files}")
            
            
            new_changed_files = []
            code_difference_explanations = []
            
            for file_path in changed_files:
                self.initialize_file_folder_paths(file_path)
                
                if (self.changed_file_name in files_to_ignore):
                    continue

                current_file_extension = os.path.splitext(self.changed_file_name)[1]
                changed_content = get_changed_part(git_utils= self.git_utils, repo_name=repo_name, default_branch=base_branch, source_branch=head_branch, file_path=self.file_path)
                
                logging.info(f"Changed content: {changed_content}")
                
                code_difference_explanation, status =  get_differnce_explanation(code_difference=changed_content, path = file_path)
                
                logging.info(f"Code difference explanation: {code_difference_explanation}")

                if status == StatusCodes.SUCCESS.value:
                    
                    code_difference_explanations.append((code_difference_explanation))
                    new_changed_files.append(self.file_path)
            
            
            return code_difference_explanations, new_changed_files

        except Exception as e:
            data = {
                "commit id": data["commit id"],
                "commit msg": data["commit msg"],
                "head_branch": data["branch"],
                "base_branch": data["default_branch"],
            }
            handle_exception("Error in document pipeline", data, e, traceback.print_exc(), error_code=0)
            return {"status": "failed"}, StatusCodes.INTERNAL_SERVER_ERROR.value









    def feedback_unittest_pipeline(self):
        """
        Perform feedback unittest pipeline.
        """
        try:
            pass
        except Exception as e:
            data = {}
            handle_exception("Error in feedback unittest pipeline", data, e, traceback.print_exc(), error_code=0)

    def feedback_refactor_pipeline(self, source_branch: str, ai_branch , file_extention:str,  feedback: list):
        """
        Perform feedback refactor pipeline.
        """

        try:
            updated_code_list = []
            new_changed_files = []
            for file_path, comments in feedback[0].items():
                print("File Path:", file_path)
                self.initialize_file_folder_paths(file_path)

                if not self.changed_file_name.endswith(file_extention):
                    print(f"File '{file_path}' does not have extension {file_extention}")
                    continue


                complete_feedback_list = [f"{comment} at Line: {line_number}" for comment, line_number in
                                          comments.items()]
                complete_feedback_str = ", ".join(complete_feedback_list)
                print(f"Feedback for file {file_path}: {complete_feedback_str}")

                # Checkout to Source branch for Source-refactored code
                self.git_utils.git_checkout_and_pull(source_branch)
                with open(file_path, 'r', encoding='utf-8-sig') as file:
                    original_code = file.read()
                    if original_code:
                        print("Original code took")

                # Checkout to AI branch for AI-refactored code
                self.git_utils.git_checkout_and_pull(ai_branch)
                with open(file_path, 'r', encoding='utf-8-sig') as file:
                    refactored_code = file.read()
                    if refactored_code:
                        print("AI refactored code took")

                updated_code, status_code = feedback_refactor(original_code,refactored_code, feedback, file_extention)
                updated_code_list.append((updated_code, status_code))
                new_changed_files.append(self.file_path)

            return updated_code_list, new_changed_files
        except Exception as e:
            data = {}
            handle_exception("Error in feedback unittest pipeline", data, e, traceback.print_exc(), error_code=0)
            
            
