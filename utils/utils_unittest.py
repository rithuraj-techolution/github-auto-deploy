
# Necessary Imports
import pytest
import subprocess
import traceback
from typing import List
import base64
import tiktoken
import requests
from unittest.mock import patch, Mock
from utils import handle_exception, run_terminal_commands, authorize_github_user, authorize_azure_user, num_tokens_from_string
from Enums.Enum_data import StatusCodes

# Test cases generated

def test_handle_exception():
    # Test case for the handle_exception function
    with patch('builtins.print') as mocked_print:
        handle_exception("error", "data", "exception", "trace", error_code=0)
    assert mocked_print.call_count == 7

def test_run_terminal_commands():
    # Test case for the run_terminal_commands function
    with patch('subprocess.run') as mocked_run:
        run_terminal_commands(cmd_list=["ls", "pwd"], cmd="ls")
    assert mocked_run.call_count == 3

def test_authorize_github_user():
    # Test case for the authorize_github_user function
    class Config:
        AUTH_URL = "https://api.github.com"
        AUTH_USERNAME = "username"
    config = Config()
    with patch('requests.get') as mocked_get:
        mocked_get.return_value.status_code = 200
        result, status = authorize_github_user("Basic dXNlcm5hbWU6cGFzc3dvcmQ=", "repo_name", config)
    assert result == True
    assert status == StatusCodes.SUCCESS.value

def test_authorize_azure_user():
    # Test case for the authorize_azure_user function
    class Config:
        AUTH_URL = "https://dev.azure.com"
        AUTH_USERNAME = "username"
    config = Config()
    with patch('requests.get') as mocked_get:
        mocked_get.return_value.status_code = 200
        result, status = authorize_azure_user("Basic dXNlcm5hbWU6cGFzc3dvcmQ=", "repo_name", config)
    assert result == True
    assert status == StatusCodes.SUCCESS.value

def test_num_tokens_from_string():
    # Test case for the num_tokens_from_string function
    with patch('tiktoken.get_encoding') as mocked_get_encoding:
        mocked_get_encoding.return_value.encode.return_value = [1, 2, 3]
        result = num_tokens_from_string("string", "utf-8")
    assert result == 3
