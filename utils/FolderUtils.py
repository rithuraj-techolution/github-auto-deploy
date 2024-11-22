
import os
import traceback
from queue import Queue

from utils.utils import handle_exception, run_terminal_commands


class FolderUtils:
    """
    A utility class for handling folder and file related operations.
    """

    @staticmethod
    # def check_file_present(name: str = None, ext: str = None, directory: str = os.getcwd()) -> bool:
    #     """
    #     Check if a file with a specific name or extension is present in a directory.
    #
    #     Args:
    #         name (str): The name of the file to check.
    #         ext (str): The extension of the file to check.
    #         directory (str): The directory to check in.
    #
    #     Returns:
    #         bool: True if the file is present, False otherwise.
    #     """
    #     try:
    #         for root, dirs, files in os.walk(directory):
    #             for file in files:
    #                 print(os.path.join(root, file))
    #
    #         files = os.listdir(directory)
    #         print("File present in folder - \n", files)
    #         for file in files:
    #             if '.' in file:
    #                 if name and file.startswith(name):
    #                     return True
    #                 if ext and file.endswith(ext):
    #                     return True
    #         return False
    #     except FileNotFoundError as error:
    #         data = {
    #             "directory": directory,
    #             "message": "This directory path not found! Please check the path and be careful if using relative paths",
    #         }
    #         handle_exception(f"Error! directory path {directory} not exists", data, error, traceback.print_exc(), error_code=0)
    #         return False
    def check_file_present(name: str = None, ext: str = None, directory: str = os.getcwd()) -> bool:
        """
        Check if a file with a specific name or extension is present in a directory.

        Args:
            name (str): The name of the file to check.
            ext (str): The extension of the file to check.
            directory (str): The directory to check in.

        Returns:
            bool: True if the file is present, False otherwise.
        """
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    # print(os.path.join(root, file))  # Optional: print file path for debugging
                    if name and file.startswith(name):
                        return True
                    if ext and file.endswith(ext):
                        return True
            return False
        except FileNotFoundError as error:
            data = {
                "directory": directory,
                "message": "This directory path not found! Please check the path and be careful if using relative paths",
            }
            handle_exception(f"Error! directory path {directory} not exists", data, error, traceback.print_exc(),
                             error_code=0)
            return False

    @staticmethod
    def search_file_folder_iteratively(file: str = None, ext: str = None, folder: str = None,
                                       dir_path: str = os.getcwd(), top_or_down: str = 'top') -> str:
        """
        Search for a file or folder iteratively in a directory.

        Args:
            file (str): The name of the file to search for.
            ext (str): The extension of the file to search for.
            folder (str): The name of the folder to search for.
            dir_path (str): The directory to start the search from.
            top_or_down (str): The direction of the search, either 'top' or 'down'.

        Returns:
            str: The path of the found file or folder, or an empty string if not found.
        """
        try:
            # For path correction
            slash = '/' if '/' in dir_path else '\\'
            if top_or_down == 'top':
                folder_list = [part for part in dir_path.split(slash) if part]
                while len(folder_list) > 0: # TODO I have changed 1 to 0
                    if file and ext:
                        if file + '.' + ext in folder_list:
                            return dir_path
                    elif folder:
                        if folder in folder_list:
                            return dir_path
                    else:
                        if FolderUtils.check_file_present(file, ext, dir_path):
                            return dir_path
                        else:
                            dir_path = os.path.abspath(os.path.join(dir_path, os.pardir))
                            folder_list = [part for part in dir_path.split(slash) if part]
            elif top_or_down == 'down':
                folder_queue = Queue()
                folder_queue.put(dir_path)
                while folder_queue.qsize() > 0:
                    current_folder = folder_queue.get()
                    if file and ext:
                        if file + '.' + ext in current_folder:
                            return dir_path
                    elif folder:
                        if folder in current_folder:
                            return dir_path
                    else:
                        if FolderUtils.check_file_present(file, ext, current_folder):
                            return dir_path
                        else:
                            for file_or_folder in current_folder:
                                if os.path.isdir(file_or_folder):
                                    folder_queue.put(file_or_folder)
        except Exception as e:
            data = {
                "file": file,
                "extension": ext,
                "folder": folder,
                "dir_path": dir_path,
                "top_or_down": top_or_down
            }
            handle_exception("Error while searching file or folder iteratively", data, e, traceback.print_exc(), error_code=0)
            return ""

    @staticmethod
    def modify_filepath_for_os(file_path: str) -> str:
        """
        Modify the file path according to the operating system.

        Args:
            file_path (str): The original file path.

        Returns:
            str: The modified file path.
        """
        try:
            if os.name == 'nt':
                modified_file_path = file_path.replace('/', '\\')
            else:
                modified_file_path = file_path.replace('\\', '/')
            return modified_file_path
        except Exception as e:
            data = {"file_path": file_path}
            handle_exception("Error while changing file path with respect to OS", data, e, traceback.print_exc(), error_code=0)
            return file_path

    @staticmethod
    def code_file_path_feedback(path: str, code_or_test: str) -> str:
        """
        Modifies the file path based on whether it's for code or test file.

        Args:
            path (str): Original file path.
            code_or_test (str): Specifies whether the file is for code or test.

        Returns:
            str: Modified file path.
        """
        try:
            delimiter = '/' if '/' in path else '\\'
            components = path.split(delimiter)

            # Modify components based on code_or_test
            if code_or_test == 'code':
                if '.Tests' in components[-2]:
                    components[-2] = components[-2].replace('.Tests', '')
                if 'Tests.cs' in components[-1]:
                    components[-1] = components[-1].replace("Tests.cs", '.cs')
                return f'{delimiter}'.join(components).replace('.Tests', '')
            else:
                if '.Tests' not in components[-2]:
                    components[-2] += ".Tests"
                if 'Tests.cs' not in components[-1]:
                    components[-1] = components[-1].replace(".cs", "Tests.cs")
                return f'{delimiter}'.join(components)
        except Exception as e:
            data = {
                "path": path,
                "code_or_test": code_or_test,
            }
            handle_exception("Error while changing path according to test or code", data, e, traceback.print_exc(), error_code=0)
            return path

    @staticmethod
    def add_tests_to_path(path: str, folder_name: str) -> str:
        """
        Add '.Tests' to the path after a specific folder name.

        Args:
            path (str): The original path.
            folder_name (str): The folder name after which to add '.Tests'.

        Returns:
            str: The modified path.
        """
        try:
            components = path.split(os.sep)
            modified_path = ""
            index = len(components) - 1
            while index >= 0:
                if components[index] == folder_name:
                    break
                modified_path = os.path.join(components[index] + ".Tests", modified_path)
                index -= 1
            return modified_path
        except Exception as e:
            data = {
                "path": path,
                "folder_name": folder_name,
            }
            handle_exception("Error while adding test to path", data, e, traceback.print_exc(), error_code=0)

    @staticmethod
    def create_folders(path: str) -> None:
        """
        Create folders according to a given path.

        Args:
            path (str): The path for which to create folders.
        """
        try:
            folders = path.split('/')
            current_path = ''
            for folder in folders:
                current_path = os.path.join(current_path, folder)
                if not os.path.exists(current_path):
                    os.makedirs(current_path)
        except Exception as e:
            data = {"path": path}
            handle_exception("Error while creating folders according to path", data, e, traceback.print_exc(), error_code=0)
    

    @staticmethod
    def delete_folder(path: str) -> bool:
        """
        """
        try:
            if os.path.exists(path):
                os.chdir(os.path.abspath(os.path.join(path, os.pardir)))
                if os.name == 'nt':
                    run_terminal_commands(cmd_list=[f'rmdir /S /Q "{path}"'])
                else:
                    run_terminal_commands(cmd_list=['whoami', 'ls', f'rm -rf {self.path}'])
                return True
            return False
        except Exception as e:
            pass


