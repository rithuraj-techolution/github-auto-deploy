import json
import requests
from config import COMPILER_RUN_COMMAND, COMPILER_UPLOAD_FILE


class Compiler:
    def __init__(self, task_id, compiler_name):
        self.task_id = task_id
        self.compiler_name = compiler_name


    def upload_files(self, files):
        payload = {
            "task_id": self.task_id,
            "compiler_name": self.compiler_name,
        }
        response = requests.post(COMPILER_UPLOAD_FILE, data=payload, files=files)
        print("Upload file in compiler", response.status_code)
        return response


    def run_command_in_compiler(self, command):
        payload = json.dumps({
            "compiler_name": self.compiler_name,
            "task_id": self.task_id,
            "command": command
        })
        response = requests.post(COMPILER_RUN_COMMAND, data=payload)
        print("Run command in compiler", response.status_code)
        return response

