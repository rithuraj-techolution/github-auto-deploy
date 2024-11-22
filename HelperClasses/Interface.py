from abc import ABC, abstractmethod


class Interface(ABC):
    @abstractmethod
    def __init__(self, config, git_utils):
        pass

    @abstractmethod
    def initialize_file_folder_paths(self, file_path):
        pass

    @abstractmethod
    def refactor_unittest_pipeline(self, commit_id, commit_msg, file_extention, source_branch, assistants):
        pass

    @abstractmethod
    def feedback_unittest_pipeline(self):
        pass

    @abstractmethod
    def feedback_refactor_pipeline(self):
        pass