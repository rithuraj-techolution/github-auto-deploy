
# Necessary Imports
import pytest
import os
import subprocess
from unittest.mock import patch, MagicMock
from GitHubUtils import GitHubUtils

# Test cases generated
def test_constructor():
    # Test case for the constructor
    with patch('utils.utils.run_terminal_commands') as mock_run:
        git_utils = GitHubUtils(['https://github.com/test/repo.git'])
        assert git_utils.urls == ['https://github.com/test/repo.git']
        assert git_utils.path == os.path.join(os.getcwd(), "Repos")
        mock_run.assert_called()

def test_get_files_changed():
    # Test case for the get_files_changed method
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.stdout = 'file1\nfile2\n'
        git_utils = GitHubUtils(['https://github.com/test/repo.git'])
        result = git_utils.get_files_changed('123456')
        assert result == ['file1', 'file2']

def test_git_checkout_and_pull():
    # Test case for the git_checkout_and_pull method
    with patch('utils.utils.run_terminal_commands') as mock_run:
        git_utils = GitHubUtils(['https://github.com/test/repo.git'])
        git_utils.git_checkout_and_pull('master')
        mock_run.assert_called_with(cmd_list=['git checkout master', 'git pull'])

def test_git_add_commit():
    # Test case for the git_add_commit method
    with patch('utils.utils.run_terminal_commands') as mock_run:
        git_utils = GitHubUtils(['https://github.com/test/repo.git'])
        git_utils.git_add_commit('Initial commit')
        mock_run.assert_called_with(cmd_list=['git add .', 'git commit -m "Initial commit"'])

def test_pull_push():
    # Test case for the pull_push method
    with patch('utils.utils.run_terminal_commands') as mock_run:
        git_utils = GitHubUtils(['https://github.com/test/repo.git'])
        git_utils.pull_push()
        mock_run.assert_called_with(cmd_list=['git pull', 'git push'])

def test_get_files_to_ignore():
    # Test case for the get_files_to_ignore method
    git_utils = GitHubUtils(['https://github.com/test/repo.git'])
    result = git_utils.get_files_to_ignore('Initial commit --skip file1 file2')
    assert result == ['file1', 'file2']

def test_remove_repo():
    # Test case for the remove_repo method
    with patch('os.path.exists') as mock_exists, patch('utils.utils.run_terminal_commands') as mock_run:
        mock_exists.return_value = True
        git_utils = GitHubUtils(['https://github.com/test/repo.git'])
        result = git_utils.remove_repo()
        assert result == True
        mock_run.assert_called()
