import logging
from Enums.Enum_data import StatusCodes
from utils.FolderUtils import FolderUtils
import os


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')



def get_changed_part(git_utils, repo_name: str, default_branch: str, source_branch: str, file_path):
    base_name = os.path.basename(file_path).split('.')[0]
    print("Base Name - ", base_name)
    extension = os.path.splitext(file_path)[1]
    print("Extension - ", extension)
    current_dir = os.getcwd()
    print("Current DIR: ", current_dir)
    parent_dir = os.path.dirname(current_dir)
    print("Patent DIR: ", parent_dir)

    git_utils.git_checkout_and_pull(default_branch)

    # os.chdir(parent_dir)
    if FolderUtils.check_file_present(name=base_name, ext=extension, directory=parent_dir):
        # os.chdir(current_dir)

        # result, status_code = git_utils.file_exists_in_branch(default_branch, file_path)
        # if status_code == StatusCodes.SUCCESS.value:
        print("File exist in Default Branch")
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            original_code = file.read().splitlines()
            # print("Original Code -- \n ", original_code)
            flag_original = True
    else:
        print("File do not exist in Default Branch")
        original_code = ['No Code']
        # print("Original Code -- \n", original_code)
        flag_original = False

    git_utils.git_checkout_and_pull(source_branch)
    # os.chdir(parent_dir)
    if FolderUtils.check_file_present(name=base_name, ext=extension, directory=parent_dir):

        print("File exist in Source Branch")
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            new_code = file.read().splitlines()
            # print("New Code -- \n", new_code)
            flag_new = True

    else:
        print("File do not exist in Source Branch")
        new_code = ['No Code']
        # print("New Code -- \n", new_code)
        flag_new = False

    if flag_original or flag_new == True:
        code_difference = get_code_difference(original_code=original_code, new_code=new_code)
    else:
        code_difference = ""

    return code_difference


def get_code_difference(original_code, new_code):
    result = []
    max_lines = max(len(original_code), len(new_code))
    
    i = 0
    while i < max_lines:
        line1 = original_code[i] if i < len(original_code) else ''
        line2 = new_code[i] if i < len(new_code) else ''
        
        if line1 != line2:
            change_block = {
                'start_line': i + 1,
                'original_lines': [],
                'new_lines': []
            }
            
            start_idx = i
            while i < max_lines and (original_code[i] if i < len(original_code) else '') != (new_code[i] if i < len(new_code) else ''):
                change_block['original_lines'].append(original_code[i] if i < len(original_code) else '')
                change_block['new_lines'].append(new_code[i] if i < len(new_code) else '')
                i += 1
            end_idx = i
            
            result.append(f"Changes from line {start_idx + 1} to {end_idx}:\n")
            result.append("Original (lines {}-{}):\n".format(start_idx + 1, end_idx))
            result.append("\n".join(f"\t{line}" for line in change_block['original_lines']) + "\n")
            result.append("New (lines {}-{}):\n".format(start_idx + 1, end_idx))
            result.append("\n".join(f"\t{line}" for line in change_block['new_lines']) + "\n")
            result.append("-" * 80 + "\n")  
        else:
            i += 1
            
    logging.info(f"Code Difference: {result}")
    
    return result
